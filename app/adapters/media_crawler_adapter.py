from __future__ import annotations

import asyncio
import json
import math
import os
import re
import socket
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from app.config import Settings, portable_artifact_path
from app.schemas import (
    ComponentStatus,
    MarketPost,
    ProductFormHotness,
    ProductFormHotnessReport,
    SourceRef,
    TrendDNA,
)

MARKET_PLATFORMS = ("xhs", "dy", "bili", "wb")
PLATFORM_LABELS = {
    "xhs": "小红书",
    "dy": "抖音",
    "bili": "B站",
    "wb": "微博",
}

# The same compact keyword pool is used on every platform. Six keywords at the
# upstream page sizes yield roughly 60-120 records per platform before cleaning.
UNIFIED_MARKET_KEYWORDS = [
    "非遗文创",
    "博物馆文创",
    "文创包挂",
    "文创冰箱贴",
    "文创徽章",
    "新中式文创",
    "国风文创",
    "城市文创",
    "景区文创",
    "文创挂件",
    "文创丝巾",
    "文创首饰",
    "文创毛绒",
    "文创潮玩",
    "文创香氛",
    "文创盲盒",
    "文创伴手礼",
    "文创帆布袋",
    "苗绣文创",
    "民族文创",
    "非遗包挂",
    "非遗首饰",
    "非遗冰箱贴",
]

# Backward-compatible import name used by the first-phase tests and scripts.
XHS_MVP_KEYWORDS = UNIFIED_MARKET_KEYWORDS

PRODUCT_FORM_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("冰箱贴", ("冰箱贴", "磁贴", "fridge magnet")),
    ("徽章", ("徽章", "吧唧", "胸章", "badge")),
    ("包挂", ("包挂", "包包挂", "包饰")),
    ("丝巾", ("丝巾", "方巾", "领巾")),
    ("首饰", ("首饰", "耳饰", "耳环", "项链", "手链", "戒指", "银饰")),
    ("毛绒", ("毛绒", "玩偶", "公仔", "布偶")),
    ("潮玩", ("潮玩", "手办", "摆件玩具", "艺术玩具")),
    ("香氛", ("香氛", "香薰", "香水", "线香")),
    ("盲盒", ("盲盒", "隐藏款")),
    ("帆布袋", ("帆布袋", "托特包", "布袋")),
    ("伴手礼", ("伴手礼", "礼盒", "礼物套装", "旅游礼物")),
    ("家居摆件", ("家居摆件", "桌面摆件", "装饰摆件", "家居装饰")),
    ("挂件", ("挂件", "挂饰", "钥匙扣", "手机挂饰", "手机链")),
]

PLATFORM_METRIC_WEIGHTS: dict[str, dict[str, float]] = {
    "xhs": {
        "likes": 0.28,
        "favorites": 0.32,
        "comments": 0.20,
        "shares": 0.05,
        "views": 0.05,
        "freshness": 0.10,
    },
    "dy": {
        "likes": 0.25,
        "favorites": 0.05,
        "comments": 0.20,
        "shares": 0.20,
        "views": 0.20,
        "freshness": 0.10,
    },
    "bili": {
        "likes": 0.20,
        "favorites": 0.20,
        "comments": 0.15,
        "shares": 0.10,
        "views": 0.25,
        "freshness": 0.10,
    },
    "wb": {
        "likes": 0.30,
        "favorites": 0.00,
        "comments": 0.25,
        "shares": 0.30,
        "views": 0.05,
        "freshness": 0.10,
    },
}

LoginState = Literal["authorized", "missing", "expired"]
SourceMode = Literal["live", "cache", "unavailable"]


class MediaCrawlerAdapter:
    """Use the existing MediaCrawler runtime for four authorized market sources."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def research(self, topic: str) -> tuple[TrendDNA, ComponentStatus]:
        payload = json.loads(self.settings.market_signals_path.read_text(encoding="utf-8"))
        source_map = {
            source["source_id"]: SourceRef.model_validate(source)
            for source in payload.get("sources", [])
        }
        curated_posts = [MarketPost.model_validate(item) for item in payload.get("signals", [])]
        for post in curated_posts:
            self._classify_cached_evidence(post, source_map.get(post.source_ref))

        platforms = self._selected_platforms()
        keywords = self._keywords(topic)
        auth_method = _auth_method(self.settings.mediacrawler_login_method)
        platform_posts: list[MarketPost] = []
        market_platforms: dict[str, dict[str, Any]] = {}
        attempted_any = False

        for platform in platforms:
            cached_posts = self._load_platform_snapshot(platform)
            live_posts: list[MarketPost] = []
            raw_paths: list[Path] = []
            login_state: LoginState = "missing"
            detail = ""
            attempted = False

            if self.settings.live_mode and self.settings.mediacrawler_live_enabled:
                can_run, readiness = self._live_readiness(platform, auth_method)
                if can_run:
                    attempted = True
                    attempted_any = True
                    try:
                        live_posts, raw_paths, crawl_note = await self._run_live_crawler(
                            platform, topic, auth_method
                        )
                        login_state = "authorized"
                        detail = crawl_note or (
                            f"{PLATFORM_LABELS[platform]}登录与关键词搜索均通过，"
                            f"本次保存 {len(live_posts)} 条真实结果。"
                        )
                    except Exception as exc:  # noqa: BLE001 - source failure is manifest data
                        login_state = self._failure_login_state(platform, auth_method, exc)
                        detail = f"实时搜索失败：{_safe_error(exc)}"
                else:
                    detail = readiness
            elif self.settings.live_mode:
                detail = "MEDIACRAWLER_LIVE_ENABLED=false，未发起平台访问。"
            else:
                detail = "演示模式不发起平台访问。"

            if live_posts:
                selected_posts = live_posts
                source_status: SourceMode = "live"
                canonical_path = self._platform_snapshot_path(platform)
                login_ok = True
                search_ok = True
            elif cached_posts:
                selected_posts = cached_posts
                source_status = "cache"
                canonical_path = self._platform_snapshot_path(platform)
                login_ok = False
                search_ok = False
                detail = f"{detail} 使用 {len(cached_posts)} 条历史真实抓取快照。".strip()
            else:
                selected_posts = []
                source_status = "unavailable"
                canonical_path = self._platform_snapshot_path(platform)
                login_ok = False
                search_ok = False
                detail = f"{detail} 没有可用的该平台真实快照。".strip()

            platform_posts.extend(selected_posts)
            market_platforms[platform] = {
                "status": source_status,
                "login_state": login_state,
                "auth_method": auth_method,
                "platform": platform,
                "adapter_discovered": True,
                "login_ok": login_ok,
                "search_ok": search_ok,
                "sample_size": len(selected_posts),
                "live_post_count": len(live_posts),
                "cache_post_count": len(cached_posts) if not live_posts else 0,
                "keyword_count": len(keywords),
                "keywords": keywords,
                "raw_paths": [
                    portable_artifact_path(path, self.settings.root_dir) for path in raw_paths
                ],
                "canonical_path": (
                    portable_artifact_path(canonical_path, self.settings.root_dir)
                    if canonical_path.exists()
                    else ""
                ),
                "derived_path": "",
                "detail": detail,
                "crawl_attempted": attempted,
            }

        posts = self._clean_posts([*platform_posts, *curated_posts])
        self._score_posts(posts)
        scored_platform_posts = [post for post in posts if post.platform in MARKET_PLATFORMS]
        ranking = self._product_form_hotness(scored_platform_posts)
        hotness_report, hotness_path = self._write_product_form_hotness(
            scored_platform_posts, ranking
        )

        live_count = sum(item["live_post_count"] for item in market_platforms.values())
        platform_cache_count = sum(
            item["cache_post_count"] for item in market_platforms.values()
        )
        if live_count:
            mode: SourceMode = "live"
            engine = "MediaCrawler four-platform authorized market signals"
            ok = True
        elif platform_cache_count or curated_posts:
            mode = "cache"
            engine = "QianCraft verified market evidence cache"
            ok = True
        else:
            mode = "unavailable"
            engine = "market evidence unavailable"
            ok = False

        aggregate_login_state: LoginState
        if market_platforms and all(
            item["login_state"] == "authorized" for item in market_platforms.values()
        ):
            aggregate_login_state = "authorized"
        elif any(item["login_state"] == "expired" for item in market_platforms.values()):
            aggregate_login_state = "expired"
        else:
            aggregate_login_state = "missing"

        platform_summary = "；".join(
            f"{code}={market_platforms[code]['status']}"
            f"({market_platforms[code]['sample_size']})"
            for code in platforms
        )
        market_source = {
            "status": mode,
            "login_state": aggregate_login_state,
            "auth_method": auth_method,
            "platform": "multi",
            "platforms": list(platforms),
            "live_post_count": live_count,
            "cache_post_count": platform_cache_count + len(curated_posts),
            "keyword_count": len(keywords),
            "keywords": keywords,
            "raw_paths": [
                path
                for item in market_platforms.values()
                for path in item["raw_paths"]
            ],
            "derived_path": "",
            "hotness_path": portable_artifact_path(hotness_path, self.settings.root_dir),
            "detail": f"四平台状态：{platform_summary}。",
        }
        derived_path = self._write_derived(posts, market_source, market_platforms)

        used_source_ids = {post.source_ref for post in posts if post.source_ref}
        trend = self._summarize(
            posts=posts,
            platform_posts=scored_platform_posts,
            curated_sources=[
                source_map[source_id]
                for source_id in used_source_ids
                if source_id in source_map
            ],
            time_window=payload.get("time_window", ""),
            ranking=ranking,
            platforms=platforms,
        )
        trend.retrieval = {
            "mode": mode,
            "engine": engine,
            "live_post_count": live_count,
            "platform_cache_count": platform_cache_count,
            "verified_baseline_count": len(curated_posts),
            "crawl_attempted": attempted_any,
            "market_source": market_source,
            "market_platforms": market_platforms,
            "product_form_hotness": hotness_report.model_dump(mode="json"),
            "product_form_hotness_path": portable_artifact_path(
                hotness_path, self.settings.root_dir
            ),
            "derived_path": portable_artifact_path(derived_path, self.settings.root_dir),
        }
        status = ComponentStatus(
            component="market_research",
            mode=mode,
            engine=engine,
            ok=ok,
            detail=market_source["detail"],
        )
        return trend, status

    def _selected_platforms(self) -> tuple[str, ...]:
        selected = tuple(
            platform
            for platform in MARKET_PLATFORMS
            if platform in self.settings.mediacrawler_platforms
        )
        return selected or MARKET_PLATFORMS

    def _keywords(self, topic: str) -> list[str]:
        topic_keyword = f"{topic}文创" if topic.strip() else ""
        ordered = [topic_keyword, *UNIFIED_MARKET_KEYWORDS]
        return _ordered_unique(ordered)[: self.settings.mediacrawler_keyword_limit]

    def _platform_cookie(self, platform: str) -> str:
        configured = self.settings.mediacrawler_cookies.get(platform, "")
        if configured:
            return configured
        if platform == "xhs":
            return self.settings.mediacrawler_cookie
        return ""

    def _live_readiness(self, platform: str, method: str) -> tuple[bool, str]:
        if platform not in MARKET_PLATFORMS:
            return False, f"QianCraft 未注册平台 {platform}。"
        if not self.settings.mediacrawler_path.joinpath("main.py").exists():
            return False, "MediaCrawler 上游入口不存在。"
        if not self.settings.mediacrawler_python.exists():
            return False, "MediaCrawler 隔离运行时不存在。"
        if method == "cookie" and not self._platform_cookie(platform):
            return False, f"{platform} Cookie 未配置；login_state=missing。"
        if method == "qrcode" and not self.settings.mediacrawler_interactive_login:
            return False, "二维码登录需由用户显式运行四平台探测脚本的 --authorize。"
        if method == "cdp":
            browser_ready = _port_open("127.0.0.1", self.settings.mediacrawler_cdp_port)
            if not browser_ready and not self.settings.mediacrawler_interactive_login:
                return False, "未发现用户授权的 CDP 浏览器；未自动打开登录窗口。"
        return True, "授权前置条件允许发起验证。"

    def _failure_login_state(
        self, platform: str, method: str, exc: Exception
    ) -> LoginState:
        credential_present = (
            bool(self._platform_cookie(platform))
            if method == "cookie"
            else _port_open("127.0.0.1", self.settings.mediacrawler_cdp_port)
        )
        if _looks_like_auth_failure(exc) and credential_present:
            return "expired"
        return "missing"

    async def _run_live_crawler(
        self, platform: str, topic: str, auth_method: str
    ) -> tuple[list[MarketPost], list[Path], str]:
        root = self.settings.mediacrawler_path
        run_token = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        output_root = self.settings.market_raw_dir / "_upstream" / run_token / platform
        output_root.mkdir(parents=True, exist_ok=True)
        started_ns = datetime.now(UTC).timestamp()
        keywords = self._keywords(topic)
        login_type = "cookie" if auth_method == "cookie" else "qrcode"
        command = [
            str(self.settings.mediacrawler_python),
            str(Path(__file__).with_name("mediacrawler_runner.py")),
            "--platform",
            platform,
            "--lt",
            login_type,
            "--type",
            "search",
            "--keywords",
            ",".join(keywords),
            "--get_comment",
            "no",
            "--get_sub_comment",
            "no",
            "--headless",
            "yes" if self.settings.mediacrawler_headless else "no",
            "--save_data_option",
            "jsonl",
            "--crawler_max_notes_count",
            str(self.settings.mediacrawler_max_results),
            "--max_concurrency_num",
            "1",
            "--save_data_path",
            str(output_root),
        ]
        child_environment = os.environ.copy()
        child_environment["QIANCRAFT_MEDIACRAWLER_ROOT"] = str(root)
        child_environment["QIANCRAFT_MEDIACRAWLER_LOGIN_METHOD"] = auth_method
        child_environment["QIANCRAFT_MEDIACRAWLER_CDP_PORT"] = str(
            self.settings.mediacrawler_cdp_port
        )
        child_environment["QIANCRAFT_MEDIACRAWLER_CDP_CONNECT_EXISTING"] = (
            "true" if self.settings.mediacrawler_cdp_connect_existing else "false"
        )
        child_environment["QIANCRAFT_MEDIACRAWLER_HEADLESS"] = (
            "true" if self.settings.mediacrawler_headless else "false"
        )
        platform_cookie = self._platform_cookie(platform)
        if platform_cookie:
            child_environment["QIANCRAFT_MEDIACRAWLER_COOKIE"] = platform_cookie

        interactive = self.settings.mediacrawler_interactive_login
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(root),
            env=child_environment,
            stdout=(asyncio.subprocess.DEVNULL if interactive else asyncio.subprocess.PIPE),
            stderr=(
                asyncio.subprocess.DEVNULL
                if interactive
                else asyncio.subprocess.STDOUT
            ),
        )
        timed_out = False
        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(), timeout=self.settings.mediacrawler_timeout_seconds
            )
        except TimeoutError:
            process.kill()
            await process.wait()
            timed_out = True
            stdout = b""
        if process.returncode != 0 and not timed_out:
            output = (stdout or b"").decode("utf-8", errors="replace")[-1600:]
            raise RuntimeError(f"MediaCrawler exit={process.returncode}: {output}")

        files = sorted(
            (
                file
                for file in output_root.rglob("*contents*.json*")
                if file.is_file() and file.stat().st_mtime >= started_ns - 2
            ),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )
        if not files:
            if timed_out:
                raise RuntimeError(
                    "MediaCrawler timed out before producing any content records"
                )
            raise RuntimeError("MediaCrawler completed but produced no content records")
        raw_items: list[dict[str, Any]] = []
        for file in files:
            raw_items.extend(_read_json_records(file))
        normalized = [self._normalize_post(platform, item) for item in raw_items]
        posts = self._clean_posts(
            [post for post in normalized if post.post_id and post.metrics_verified]
        )[: self.settings.mediacrawler_platform_record_limit]
        if len(posts) < 5:
            if timed_out:
                raise RuntimeError(
                    "MediaCrawler timed out and produced fewer than 5 valid records"
                )
            raise RuntimeError(
                "MediaCrawler returned fewer than 5 valid records with IDs and engagement fields"
            )
        canonical_path = self._write_platform_snapshot(platform, posts)
        crawl_note = ""
        if timed_out:
            crawl_note = (
                f"{PLATFORM_LABELS[platform]}达到单平台时间上限；"
                f"已终止继续翻页，并保存 {len(posts)} 条本轮真实返回记录。"
            )
        return posts, [canonical_path, *files], crawl_note

    def _normalize_post(self, platform: str, item: dict[str, Any]) -> MarketPost:
        post_id = _pick(item, "note_id", "aweme_id", "video_id", "content_id", "id")
        title = _pick(item, "title", "note_title")
        content = _pick(item, "desc", "content", "note_desc", "text")
        if not title and platform == "dy":
            title = content
        author = _pick(item, "nickname", "user_nickname", "author", "user_name")
        published = _normalize_time(
            _pick(
                item,
                "time",
                "create_time",
                "publish_time",
                "pub_ts",
                "last_modify_ts",
            )
        )
        tags_raw = item.get("tag_list") or item.get("tags") or []
        if isinstance(tags_raw, str):
            try:
                tags_raw = json.loads(tags_raw)
            except json.JSONDecodeError:
                tags_raw = re.split(r"[,，#\s]+", tags_raw)
        if not isinstance(tags_raw, list):
            tags_raw = []
        tags = [
            str(tag.get("name", "")) if isinstance(tag, dict) else str(tag)
            for tag in tags_raw
        ]
        combined = f"{title} {content} {' '.join(tags)}"
        product_form = _detect_product_form(combined)
        raw_url = str(
            _pick(item, "note_url", "aweme_url", "video_url", "content_url", "url")
        )
        url = _platform_url(platform, str(post_id)) if post_id else raw_url
        metric_keys = {
            "liked_count",
            "like_count",
            "digg_count",
            "collected_count",
            "collect_count",
            "favorite_count",
            "video_favorite_count",
            "comment_count",
            "comments_count",
            "video_comment",
            "share_count",
            "shared_count",
            "video_share_count",
            "video_play_count",
            "play_count",
            "view_count",
            "views",
        }
        retrieved_at = datetime.now(UTC).isoformat()
        return MarketPost(
            platform=platform,
            post_id=str(post_id),
            title=str(title),
            content=str(content),
            author=str(author),
            published_at=published,
            url=url,
            likes=_as_non_negative_int(
                _pick(item, "liked_count", "like_count", "digg_count")
            ),
            favorites=_as_non_negative_int(
                _pick(
                    item,
                    "collected_count",
                    "collect_count",
                    "favorite_count",
                    "video_favorite_count",
                )
            ),
            comments=_as_non_negative_int(
                _pick(item, "comment_count", "comments_count", "video_comment")
            ),
            shares=_as_non_negative_int(
                _pick(item, "share_count", "shared_count", "video_share_count")
            ),
            views=_as_non_negative_int(
                _pick(item, "video_play_count", "play_count", "view_count", "views")
            ),
            tags=[tag for tag in tags if tag],
            search_keyword=str(
                item.get("source_keyword") or item.get("search_keyword") or ""
            ),
            product_form=product_form,
            product_category=_product_category(product_form),
            styles=_detect_terms(
                combined, ["国风", "新中式", "轻国风", "萌化", "极简", "复古"]
            ),
            colors=_detect_terms(
                combined, ["红", "蓝", "绿", "金", "银", "黑", "白", "靛蓝"]
            ),
            materials=_detect_terms(
                combined, ["刺绣", "金属", "木", "毛绒", "纸", "银", "竹", "织物"]
            ),
            target_audiences=["18-30岁年轻消费者"],
            usage_scenarios=_detect_terms(
                combined, ["通勤", "旅行", "礼赠", "家居", "收藏", "穿戴"]
            ),
            emotional_values=_detect_terms(
                combined, ["治愈", "祝福", "个性", "收藏", "文化认同", "可爱", "送礼"]
            ),
            metrics_verified=bool(metric_keys.intersection(item)),
            evidence_type="social_signal",
            evidence_quality_score=_live_quality(item, post_id, published, url),
            evidence_quality_reasons=[
                f"用户授权的{PLATFORM_LABELS[platform]}搜索记录",
                "互动字段按平台原始返回保存，缺失字段为0",
            ],
            source_ref=_live_source_id(platform, str(post_id), url),
            retrieved_at=retrieved_at,
        )

    def _platform_snapshot_path(self, platform: str) -> Path:
        return self.settings.market_raw_dir / f"{platform}.jsonl"

    def _load_platform_snapshot(self, platform: str) -> list[MarketPost]:
        path = self._platform_snapshot_path(platform)
        records = _read_json_records(path) if path.exists() else []
        if not records:
            derived_path = self.settings.market_derived_dir / "latest.json"
            if derived_path.exists():
                payload = json.loads(derived_path.read_text(encoding="utf-8-sig"))
                if isinstance(payload, dict) and isinstance(payload.get("records"), list):
                    records = [item for item in payload["records"] if isinstance(item, dict)]
        posts: list[MarketPost] = []
        for item in records:
            try:
                post = MarketPost.model_validate(item)
            except ValueError:
                continue
            if post.platform != platform:
                continue
            posts.append(post)
        return self._clean_posts(posts)[: self.settings.mediacrawler_platform_record_limit]

    def _write_platform_snapshot(
        self, platform: str, posts: list[MarketPost]
    ) -> Path:
        path = self._platform_snapshot_path(platform)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(
            json.dumps(post.model_dump(mode="json"), ensure_ascii=False) + "\n"
            for post in posts
        )
        _atomic_write(path, content)
        return path

    @staticmethod
    def _classify_cached_evidence(post: MarketPost, source: SourceRef | None) -> None:
        descriptor = " ".join(
            [
                post.platform,
                post.verified_market_signal,
                source.source_type if source else "",
                source.publisher if source else "",
            ]
        )
        if any(
            term in descriptor
            for term in ("销量", "订单", "产品发布", "品牌官方", "市场发布")
        ):
            post.evidence_type = "product_signal"
        elif any(term in descriptor for term in ("政府", "博物馆", "调查", "产业")):
            post.evidence_type = "institutional_signal"
        else:
            post.evidence_type = "media_signal"
        base = post.verified_signal_strength or 50
        traceability = 10 if source and source.source_url else 0
        specificity = 10 if any(char.isdigit() for char in post.verified_market_signal) else 0
        post.evidence_quality_score = min(
            100, int(0.75 * base + traceability + specificity)
        )
        post.evidence_quality_reasons = [
            f"证据类型：{post.evidence_type}",
            "来源链接可追溯" if traceability else "来源链接缺失",
            "包含可核对数量或时间" if specificity else "为方向性公开信号",
        ]

    @staticmethod
    def _clean_posts(posts: list[MarketPost]) -> list[MarketPost]:
        seen_ids: set[str] = set()
        seen_text: set[str] = set()
        clean: list[MarketPost] = []
        spam = re.compile(
            r"(加微|代理招募|刷单|返现|博彩|贷款|全网最低.*私聊)", re.IGNORECASE
        )
        for post in posts:
            text = f"{post.title} {post.content}".strip()
            if (
                not text
                or spam.search(text)
                or re.match(r"^(转发微博|轉發微博)(\s|$)", text)
            ):
                continue
            key = post.post_id or post.url or hashlib_key(text)
            identity = f"{post.platform}:{key}"
            fingerprint = f"{post.platform}:" + re.sub(r"\s+", "", text).lower()
            if identity in seen_ids or (len(fingerprint) >= 12 and fingerprint in seen_text):
                continue
            seen_ids.add(identity)
            if len(fingerprint) >= 12:
                seen_text.add(fingerprint)
            for field in ("likes", "favorites", "comments", "shares", "views"):
                setattr(post, field, min(getattr(post, field), 2_000_000_000))
            if not post.product_form:
                post.product_form = _detect_product_form(text)
            if not post.product_category:
                post.product_category = _product_category(post.product_form)
            clean.append(post)
        return clean

    @staticmethod
    def _score_platform_hotness(posts: list[MarketPost]) -> None:
        now = datetime.now(UTC)
        grouped: dict[str, list[MarketPost]] = defaultdict(list)
        for post in posts:
            if post.platform in MARKET_PLATFORMS and post.metrics_verified:
                grouped[post.platform].append(post)

        for platform, platform_posts in grouped.items():
            metric_values: dict[str, list[float]] = {
                field: [float(getattr(post, field)) for post in platform_posts]
                for field in ("likes", "favorites", "comments", "shares", "views")
            }
            metric_values["freshness"] = [
                _freshness_score(post.published_at, now) for post in platform_posts
            ]
            weights = PLATFORM_METRIC_WEIGHTS[platform]
            active = {
                field: weight
                for field, weight in weights.items()
                if weight > 0 and max(metric_values[field], default=0) > 0
            }
            denominator = sum(active.values())
            for index, post in enumerate(platform_posts):
                if denominator == 0:
                    score = 0.0
                else:
                    score = sum(
                        weight
                        * _positive_percentile(
                            metric_values[field][index], metric_values[field]
                        )
                        for field, weight in active.items()
                    ) / denominator
                post.platform_hot_score = round(min(100.0, max(0.0, score)), 1)
                post.real_engagement_score = post.platform_hot_score

    @classmethod
    def _score_posts(cls, posts: list[MarketPost]) -> None:
        if not posts:
            return
        cls._score_platform_hotness(posts)
        category_counts = Counter(post.product_category or "未分类" for post in posts)
        max_frequency = max(category_counts.values(), default=1)
        now = datetime.now(UTC)
        for post in posts:
            post.institutional_signal_score = (
                float(post.verified_signal_strength or post.evidence_quality_score)
                if post.evidence_type == "institutional_signal"
                else 0
            )
            primary_signal = {
                "social_signal": post.platform_hot_score,
                "institutional_signal": post.institutional_signal_score,
                "media_signal": float(post.verified_signal_strength),
                "product_signal": float(post.verified_signal_strength),
            }[post.evidence_type]
            recency = _freshness_score(post.published_at, now)
            frequency = (
                100
                * category_counts[post.product_category or "未分类"]
                / max_frequency
            )
            post.derived_viral_score = round(
                min(
                    100.0,
                    0.45 * primary_signal
                    + 0.25 * post.evidence_quality_score
                    + 0.15 * recency
                    + 0.15 * frequency,
                ),
                1,
            )
            post.viral_score = post.derived_viral_score
            reasons = [
                f"{post.evidence_type} 与证据质量分开计分",
                "Derived Viral Score 是策划推导值，不是平台原生指标",
            ]
            if post.platform_hot_score:
                reasons.append("Platform Hot Score 只在同平台样本内做百分位比较")
            if post.institutional_signal_score:
                reasons.append("机构信号来自可追溯公开来源")
            if category_counts[post.product_category or "未分类"] > 1:
                reasons.append("同类形态在多个来源重复出现")
            if post.verified_market_signal:
                reasons.append(post.verified_market_signal)
            post.viral_reasons = reasons

    @staticmethod
    def _product_form_hotness(posts: list[MarketPost]) -> list[ProductFormHotness]:
        eligible = [post for post in posts if post.product_form != "未识别"]
        grouped: dict[str, list[MarketPost]] = defaultdict(list)
        for post in eligible:
            grouped[post.product_form].append(post)
        if not grouped:
            return []

        form_counts = [len(items) for items in grouped.values()]
        now = datetime.now(UTC)
        candidates: list[dict[str, Any]] = []
        for product_form, form_posts in grouped.items():
            by_platform: dict[str, list[MarketPost]] = defaultdict(list)
            for post in form_posts:
                by_platform[post.platform].append(post)
            platform_scores = {
                platform: round(
                    sum(post.platform_hot_score for post in items) / len(items), 1
                )
                for platform, items in by_platform.items()
            }
            platform_counts = {
                platform: len(items) for platform, items in by_platform.items()
            }
            coverage = len(platform_scores)
            mean_platform_score = sum(platform_scores.values()) / coverage
            frequency_score = _positive_percentile(len(form_posts), form_counts)
            coverage_score = 100 * coverage / len(MARKET_PLATFORMS)
            freshness_score = sum(
                _freshness_score(post.published_at, now) for post in form_posts
            ) / len(form_posts)

            # Cross-platform Hot Score (0-100): 60% mean within-platform hotness,
            # 15% form frequency percentile, 15% platform coverage, 10% freshness.
            cross_score = min(
                100.0,
                0.60 * mean_platform_score
                + 0.15 * frequency_score
                + 0.15 * coverage_score
                + 0.10 * freshness_score,
            )
            high_ratio = sum(
                post.platform_hot_score >= 75 for post in form_posts
            ) / len(form_posts)
            best_platform = max(platform_scores, key=platform_scores.get)
            why_hot = [
                f"覆盖 {coverage}/4 个平台",
                (
                    f"{PLATFORM_LABELS[best_platform]}平台内平均热度"
                    f" {platform_scores[best_platform]:.1f}"
                ),
                f"高热帖子占比 {high_ratio:.0%}",
                f"共识别 {len(form_posts)} 条相关真实记录",
            ]
            if freshness_score >= 50:
                why_hot.append("近期内容占比较高")
            candidates.append(
                {
                    "product_form": product_form,
                    "cross_platform_hot_score": round(cross_score, 1),
                    "platform_coverage": coverage,
                    "platform_scores": platform_scores,
                    "platform_post_counts": platform_counts,
                    "sample_size": len(form_posts),
                    "high_hot_post_ratio": round(high_ratio, 3),
                    "freshness_score": round(freshness_score, 1),
                    "why_hot": why_hot,
                    "representative_posts": _representative_posts(form_posts),
                }
            )

        candidates.sort(
            key=lambda item: (
                -item["cross_platform_hot_score"],
                -item["platform_coverage"],
                -item["sample_size"],
                item["product_form"],
            )
        )
        return [
            ProductFormHotness(rank=index, **item)
            for index, item in enumerate(candidates[:10], 1)
        ]

    def _write_product_form_hotness(
        self,
        posts: list[MarketPost],
        ranking: list[ProductFormHotness],
    ) -> tuple[ProductFormHotnessReport, Path]:
        sample_sizes = Counter(post.platform for post in posts)
        report = ProductFormHotnessReport(
            generated_at=datetime.now(UTC).isoformat(),
            platforms=list(MARKET_PLATFORMS),
            total_sample_size=len(posts),
            platform_sample_sizes={
                platform: sample_sizes.get(platform, 0)
                for platform in MARKET_PLATFORMS
            },
            ranking=ranking,
            priority_product_forms=[item.product_form for item in ranking[:5]],
            methodology={
                "name": "跨平台市场热度与爆款潜力信号",
                "platform_hot_score": (
                    "各平台分别对可用互动字段与近期性做正值百分位排名；"
                    "按平台权重加权，并对实际可用字段重新归一化到0-100。"
                ),
                "cross_platform_hot_score": (
                    "60%各覆盖平台的平均Platform Hot Score + 15%形态出现次数百分位 + "
                    "15%平台覆盖率 + 10%近期性。"
                ),
                "high_hot_threshold": 75,
                "claim_boundary": "不是销量预测、价格预测或AI爆款预测模型。",
            },
        )
        path = self.settings.market_derived_dir / "product_form_hotness.json"
        _atomic_write(
            path,
            json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
            + "\n",
        )
        return report, path

    def _write_derived(
        self,
        posts: list[MarketPost],
        market_source: dict[str, Any],
        market_platforms: dict[str, dict[str, Any]],
    ) -> Path:
        self.settings.market_derived_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_path = self.settings.market_derived_dir / f"market_evidence_{timestamp}.json"
        resolved = portable_artifact_path(run_path, self.settings.root_dir)
        market_source["derived_path"] = resolved
        for item in market_platforms.values():
            item["derived_path"] = resolved
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "market_source": market_source,
            "market_platforms": market_platforms,
            "records": [post.model_dump(mode="json") for post in posts],
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        _atomic_write(run_path, content)
        _atomic_write(self.settings.market_derived_dir / "latest.json", content)
        return run_path

    @staticmethod
    def _summarize(
        posts: list[MarketPost],
        platform_posts: list[MarketPost],
        curated_sources: list[SourceRef],
        time_window: str,
        ranking: list[ProductFormHotness],
        platforms: tuple[str, ...],
    ) -> TrendDNA:
        ranked_posts = sorted(
            platform_posts or posts,
            key=lambda post: post.derived_viral_score,
            reverse=True,
        )
        category_counts = Counter(post.product_category or "未分类" for post in posts)

        def ranked_list(field: str, limit: int = 10) -> list[str]:
            counter: Counter[str] = Counter(
                value
                for post in posts
                for value in getattr(post, field, [])
                if value and value != "多样"
            )
            return [value for value, _ in counter.most_common(limit)]

        representative_ids = {
            post.source_ref
            for item in ranking
            for post in item.representative_posts
            if post.source_ref
        }
        representative_ids.update(
            post.source_ref for post in ranked_posts[:8] if post.source_ref
        )
        source_by_id = {source.source_id: source for source in curated_sources}
        for post in platform_posts:
            if post.source_ref in representative_ids:
                source_by_id[post.source_ref] = _source_from_live_post(post)

        return TrendDNA(
            time_window=time_window,
            platforms=list(platforms),
            sample_size=len(platform_posts),
            hot_categories=[value for value, _ in category_counts.most_common(8)],
            rising_categories=[
                "可交互/可拆装收藏品",
                "手机挂饰、包挂与高频科技生活配件",
                "毛绒与真实刺绣结合的触感产品",
                "非遗手作体验与可追溯套件",
                "天然材料驱动的纸艺、灯饰与香氛",
            ],
            hot_styles=ranked_list("styles"),
            hot_colors=ranked_list("colors"),
            hot_materials=ranked_list("materials"),
            target_audiences=ranked_list("target_audiences"),
            price_ranges=_ordered_unique(
                post.price_range for post in posts if post.price_range
            ),
            usage_scenarios=ranked_list("usage_scenarios"),
            emotional_values=ranked_list("emotional_values"),
            viral_mechanisms=[
                "高辨识文化母题 + 小尺度精工细节形成第一眼触点",
                "旋转、抽拉、可替换、可集齐等动作延长把玩与内容拍摄时间",
                "限定联动和系列化让单次购买变成跨地点收集与社交分享",
                "把文化变成日常高频物件，形成持续曝光而非一次性纪念",
                "传承人共同署名、工艺过程和溯源故事提升信任",
                "爆款母题向毛绒、首饰、文具和体验延展形成长尾",
            ],
            visual_patterns=[
                "高饱和传统色与中性日常底色并置",
                "浮雕、流苏、绣线和毛绒构成可拍摄的立体层次",
                "核心符号简化但保留来源、原型轮廓或工艺触感",
                "模块化、成对、系列编号和故事卡构成收藏秩序",
            ],
            saturated_categories=[
                "只做静态平面贴图、没有材料或互动差异的普通冰箱贴",
                "只替换纹样、缺少出处和工艺说明的同质化帆布袋",
                "廉价批量印花却笼统标注‘非遗手工’的旅游纪念品",
            ],
            white_space_opportunities=[
                "用可替换绣片解释花溪、剑河、松桃、雷山差异的收藏系统",
                "真实绣线触感与可维修、可升级科技配件的结合",
                "产品二维码连接来源、绣娘、针法、工时和文化边界",
                "把苗绣与贵州皮纸、银饰等材料做透明、双方共创的小批量实验",
                "非仪式纹样的个性化共创体验，而不是未经许可生成‘苗绣风’图案",
            ],
            hot_product_forms=ranking,
            priority_product_forms=[item.product_form for item in ranking[:5]],
            representative_cases=ranked_posts[:8],
            source_refs=sorted(source_by_id.values(), key=lambda source: source.source_id),
            methodology_notes=[
                "四个平台使用同一关键词池与统一MarketPost字段；缺失互动字段保持0。",
                "Platform Hot Score 只在同平台样本内做百分位比较，不横比绝对点赞数。",
                (
                    "Cross-platform Hot Score = 60%平台内平均热度 + 15%出现次数百分位 + "
                    "15%平台覆盖 + 10%近期性。"
                ),
                "该分数只表示跨平台市场热度与爆款潜力信号，不是销量或价格预测。",
                "公开研究基线不会进入产品形态热度榜；榜单只使用真实抓取或其快照。",
            ],
        )


def _read_json_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if line.strip():
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    records.append(item)
        return records
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return [payload] if isinstance(payload, dict) else []


def _auth_method(value: str) -> Literal["cookie", "qrcode", "cdp"]:
    normalized = value.strip().lower()
    if normalized == "cookie":
        return "cookie"
    if normalized == "qrcode":
        return "qrcode"
    return "cdp"


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


def _looks_like_auth_failure(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(
        term in text
        for term in (
            "login",
            "cookie",
            "qrcode",
            "unauthorized",
            "扫码",
            "登录",
            "验证",
            "风控",
        )
    )


def _live_quality(item: dict[str, Any], post_id: Any, published_at: str, url: str) -> int:
    score = 55
    score += 15 if post_id else 0
    score += 10 if published_at else 0
    score += 10 if url else 0
    score += 10 if _pick(item, "nickname", "user_nickname", "author") else 0
    return min(100, score)


def _pick(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return ""


def _as_non_negative_int(value: Any) -> int:
    try:
        text = str(value).replace(",", "").strip().lower()
        multiplier = 1
        if text.endswith(("万", "w")):
            multiplier = 10_000
            text = text[:-1]
        return max(0, int(float(text) * multiplier))
    except (TypeError, ValueError):
        return 0


def _normalize_time(value: Any) -> str:
    if not value:
        return ""
    text = str(value).strip()
    if text.isdigit():
        timestamp = int(text)
        if timestamp > 10_000_000_000:
            timestamp //= 1000
        try:
            return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
        except (OSError, OverflowError, ValueError):
            return text
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat()


def _detect_product_form(text: str) -> str:
    lowered = text.lower()
    for product_form, terms in PRODUCT_FORM_KEYWORDS:
        if any(term.lower() in lowered for term in terms):
            return product_form
    return "未识别"


def _product_category(product_form: str) -> str:
    categories = {
        "冰箱贴": "互动冰箱贴",
        "徽章": "随身挂饰",
        "包挂": "随身挂饰",
        "挂件": "随身挂饰",
        "丝巾": "首饰与穿戴",
        "首饰": "首饰与穿戴",
        "毛绒": "毛绒与触感产品",
        "潮玩": "毛绒与触感产品",
        "香氛": "家居与香氛",
        "盲盒": "收藏与潮玩",
        "帆布袋": "包袋与织物",
        "伴手礼": "礼赠产品",
        "家居摆件": "家居与香氛",
    }
    return categories.get(product_form, "文创生活产品")


def _detect_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def _age_days(value: str, now: datetime) -> int | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return max(0, (now - parsed.astimezone(UTC)).days)
    except ValueError:
        return None


def _freshness_score(value: str, now: datetime) -> float:
    days = _age_days(value, now)
    return 0.0 if days is None else 100 * math.exp(-days / 365)


def _positive_percentile(value: float, values: list[float] | list[int]) -> float:
    positive = [float(item) for item in values if item > 0]
    if value <= 0 or not positive:
        return 0.0
    lower = sum(item < value for item in positive)
    equal = sum(item == value for item in positive)
    return 100 * (lower + 0.5 * equal) / len(positive)


def _representative_posts(posts: list[MarketPost]) -> list[MarketPost]:
    ordered = sorted(posts, key=lambda post: post.platform_hot_score, reverse=True)
    result: list[MarketPost] = []
    seen_platforms: set[str] = set()
    for post in ordered:
        if post.platform not in seen_platforms:
            result.append(post)
            seen_platforms.add(post.platform)
        if len(result) == 4:
            break
    return result


def _platform_url(platform: str, post_id: str) -> str:
    templates = {
        "xhs": "https://www.xiaohongshu.com/explore/{post_id}",
        "dy": "https://www.douyin.com/video/{post_id}",
        "bili": "https://www.bilibili.com/video/av{post_id}",
        "wb": "https://m.weibo.cn/detail/{post_id}",
    }
    return templates[platform].format(post_id=post_id)


def _live_source_id(platform: str, post_id: str, url: str) -> str:
    return f"MPL-{platform.upper()}-{hashlib_key(post_id or url).upper()}"


def _source_from_live_post(post: MarketPost) -> SourceRef:
    return SourceRef(
        source_id=post.source_ref,
        source_url=post.url,
        source_title=post.title or post.content[:80],
        source_type="authorized_social_search",
        publisher=PLATFORM_LABELS.get(post.platform, post.platform),
        published_at=post.published_at,
        retrieved_at=post.retrieved_at,
        supports=[
            f"产品形态：{post.product_form}",
            f"Platform Hot Score：{post.platform_hot_score}",
        ],
    )


def _ordered_unique(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def hashlib_key(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _safe_error(exc: Exception) -> str:
    message = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(exc))
    message = re.sub(
        r"(?i)(cookie|token|session|sessdata)(\s*[=:]\s*)[^\s;,]+",
        r"\1\2<redacted>",
        message,
    )
    return f"{type(exc).__name__}: {message[:1000]}"
