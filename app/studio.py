from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from collections.abc import Iterable
from datetime import UTC, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

SCHEMA_VERSION = "1.0"
SHANGHAI = timezone(timedelta(hours=8), name="Asia/Shanghai")
DAILY_LIMIT = 3
HEARTBEAT_MAX_AGE_SECONDS = 45

FORM_ARCHETYPES: dict[str, dict[str, str]] = {
    "冰箱贴": {"renderer": "modular-magnet", "label": "模块冰箱贴", "group": "flat"},
    "徽章": {"renderer": "layered-badge", "label": "层叠徽章", "group": "flat"},
    "盲盒": {"renderer": "story-box", "label": "叙事盲盒", "group": "object"},
    "包挂": {"renderer": "tactile-charm", "label": "触感包挂", "group": "soft"},
    "伴手礼": {"renderer": "archive-gift", "label": "档案伴手礼", "group": "package"},
    "潮玩": {"renderer": "abstract-figure", "label": "抽象潮玩", "group": "object"},
    "香氛": {"renderer": "material-scent", "label": "材料香氛", "group": "vessel"},
    "挂件": {"renderer": "layered-charm", "label": "层叠挂件", "group": "soft"},
    "首饰": {"renderer": "structural-pendant", "label": "结构首饰", "group": "jewelry"},
    "毛绒": {"renderer": "tactile-plush", "label": "触感毛绒", "group": "soft"},
}

CATEGORY_COMPATIBILITY: dict[str, dict[str, float]] = {
    "传统美术": {
        "flat": 94,
        "soft": 91,
        "package": 86,
        "jewelry": 82,
        "object": 78,
        "vessel": 63,
    },
    "传统技艺": {
        "flat": 88,
        "soft": 84,
        "package": 91,
        "jewelry": 86,
        "object": 87,
        "vessel": 74,
    },
    "传统音乐": {
        "flat": 76,
        "soft": 82,
        "package": 86,
        "jewelry": 69,
        "object": 88,
        "vessel": 65,
    },
    "民俗": {
        "flat": 75,
        "soft": 80,
        "package": 91,
        "jewelry": 68,
        "object": 86,
        "vessel": 64,
    },
    "传统戏剧": {
        "flat": 79,
        "soft": 82,
        "package": 83,
        "jewelry": 72,
        "object": 92,
        "vessel": 61,
    },
    "民间文学": {
        "flat": 76,
        "soft": 80,
        "package": 94,
        "jewelry": 67,
        "object": 85,
        "vessel": 63,
    },
    "曲艺": {
        "flat": 75,
        "soft": 81,
        "package": 88,
        "jewelry": 68,
        "object": 89,
        "vessel": 62,
    },
}

PALETTES: dict[str, dict[str, tuple[int, int, int]]] = {
    "slate": {
        "ink": (31, 38, 45),
        "primary": (52, 92, 125),
        "accent": (154, 103, 87),
        "surface": (240, 238, 233),
        "shell": (230, 226, 218),
        "line": (196, 200, 199),
    },
    "indigo": {
        "ink": (26, 34, 49),
        "primary": (43, 65, 92),
        "accent": (181, 132, 76),
        "surface": (238, 239, 236),
        "shell": (218, 225, 226),
        "line": (184, 194, 196),
    },
    "vermilion": {
        "ink": (39, 37, 35),
        "primary": (111, 74, 64),
        "accent": (174, 72, 57),
        "surface": (242, 238, 230),
        "shell": (229, 221, 210),
        "line": (201, 190, 177),
    },
}


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def _local_date(value: datetime | None = None) -> str:
    return (value or _now()).astimezone(SHANGHAI).date().isoformat()


def _parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, ValueError):
        return fallback
    return payload if isinstance(payload, dict) else fallback


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex[:8]}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _safe_text(value: object, limit: int = 800) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value)).strip()[:limit]


def _unique(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf" if bold else "C:/Windows/Fonts/simsun.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path(
            "/System/Library/Fonts/"
            + ("STHeiti Medium.ttc" if bold else "STHeiti Light.ttc")
        ),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
        Path(
            "/usr/share/fonts/opentype/noto/"
            + ("NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc")
        ),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size, index=0)
    raise RuntimeError(
        "缺少中文字体，不能生成会把汉字显示成方框的设计稿；"
        "请安装 Noto Sans CJK、微软雅黑、黑体或系统华文字体。"
    )


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and draw.textlength(candidate, font=font) > width:
                lines.append(current)
                current = character
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def _draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    line_height: int,
    max_lines: int,
) -> int:
    lines = _wrap(draw, text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and draw.textlength(last + "…", font=font) > width:
            last = last[:-1]
        lines[-1] = last + "…"
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


class StudioStore:
    """Persistent documents, design records and automation state."""

    def __init__(self, runtime_dir: Path) -> None:
        self.runtime_dir = runtime_dir.resolve()
        self.designs_path = self.runtime_dir / "designs.json"
        self.schedule_path = self.runtime_dir / "schedule.json"
        self.state_path = self.runtime_dir / "state.json"
        self.events_path = self.runtime_dir / "events.json"
        self.assets_dir = self.runtime_dir / "assets"
        self.runs_dir = self.runtime_dir / "runs"
        self._lock = threading.RLock()

    def load_designs(self) -> list[dict[str, Any]]:
        with self._lock:
            payload = _load_json(self.designs_path, {"designs": []})
            rows = payload.get("designs", [])
            return rows if isinstance(rows, list) else []

    def save_designs(self, rows: list[dict[str, Any]]) -> None:
        with self._lock:
            _atomic_json(
                self.designs_path,
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "updatedAt": _iso(),
                    "designs": rows[:500],
                },
            )

    def get_design(self, design_id: str) -> dict[str, Any]:
        match = next(
            (item for item in self.load_designs() if item.get("designId") == design_id),
            None,
        )
        if match is None:
            raise FileNotFoundError(f"设计不存在：{design_id}")
        return match

    def upsert_design(self, design: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            rows = self.load_designs()
            rows = [item for item in rows if item.get("designId") != design["designId"]]
            rows.insert(0, design)
            self.save_designs(rows)
        return design

    def designs_for_date(self, local_date: str, *, active_only: bool = True) -> list[dict[str, Any]]:
        rows = [
            item
            for item in self.load_designs()
            if item.get("dailyDate") == local_date and item.get("origin") == "daily"
        ]
        if active_only:
            rows = [item for item in rows if not item.get("superseded", False)]
        return sorted(rows, key=lambda item: int(item.get("dailyRank", 99)))

    def default_config(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "enabled": _bool_env("QIANCRAFT_DAILY_DESIGN_ENABLED", True),
            "hour": _int_env("QIANCRAFT_DAILY_DESIGN_HOUR", 7, 0, 23),
            "minute": _int_env("QIANCRAFT_DAILY_DESIGN_MINUTE", 0, 0, 59),
            "timezone": "Asia/Shanghai",
            "limit": DAILY_LIMIT,
            "updatedAt": _iso(),
        }

    def load_config(self) -> dict[str, Any]:
        with self._lock:
            fallback = self.default_config()
            payload = _load_json(self.schedule_path, fallback)
            return {
                **fallback,
                "enabled": bool(payload.get("enabled", fallback["enabled"])),
                "hour": max(0, min(23, int(payload.get("hour", fallback["hour"])))),
                "minute": max(0, min(59, int(payload.get("minute", fallback["minute"])))),
                "limit": DAILY_LIMIT,
                "timezone": "Asia/Shanghai",
                "updatedAt": str(payload.get("updatedAt", fallback["updatedAt"])),
            }

    def save_config(self, candidate: dict[str, Any]) -> dict[str, Any]:
        current = self.load_config()
        merged = {
            **current,
            **{key: candidate[key] for key in ("enabled", "hour", "minute") if key in candidate},
            "updatedAt": _iso(),
        }
        hour = int(merged["hour"])
        minute = int(merged["minute"])
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError("每日生成时间无效。")
        merged.update({"hour": hour, "minute": minute, "limit": DAILY_LIMIT})
        _atomic_json(self.schedule_path, merged)
        return merged

    def default_state(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "scheduler": {
                "status": "starting",
                "instanceId": "",
                "startedAt": "",
                "heartbeatAt": "",
            },
            "daily": {
                "status": "scheduled",
                "lastAttemptAt": "",
                "lastSuccessAt": "",
                "lastBatchId": "",
                "nextRunAt": _iso(_now() + timedelta(seconds=4)),
                "detail": "等待首次自动生成。",
                "runCount": 0,
                "consecutiveFailures": 0,
                "generatedCount": 0,
            },
        }

    def load_state(self) -> dict[str, Any]:
        with self._lock:
            fallback = self.default_state()
            payload = _load_json(self.state_path, fallback)
            payload.setdefault("scheduler", fallback["scheduler"])
            payload.setdefault("daily", fallback["daily"])
            return payload

    def save_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            _atomic_json(self.state_path, payload)
            return payload

    def add_event(
        self,
        *,
        event: str,
        status: str,
        detail: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            payload = _load_json(self.events_path, {"events": []})
            events = payload.get("events", [])
            if not isinstance(events, list):
                events = []
            item = {
                "id": f"STEV-{uuid4().hex[:12].upper()}",
                "at": _iso(),
                "event": event,
                "status": status,
                "detail": _safe_text(detail, 1200),
                "metadata": metadata or {},
            }
            events.insert(0, item)
            _atomic_json(self.events_path, {"events": events[:500]})
            return item

    def list_events(self, limit: int = 60) -> list[dict[str, Any]]:
        payload = _load_json(self.events_path, {"events": []})
        rows = payload.get("events", [])
        return rows[: max(1, min(limit, 200))] if isinstance(rows, list) else []


class StudioEngine:
    """Evidence-locked culture × product-form combination and design renderer."""

    def __init__(self, store: StudioStore, culture_path: Path, forms_path: Path) -> None:
        self.store = store
        self.culture_path = culture_path.resolve()
        self.forms_path = forms_path.resolve()
        self._lock = threading.RLock()

    def culture_library(self) -> dict[str, Any]:
        payload = _load_json(self.culture_path, {"records": [], "sources": []})
        sources = {
            str(item.get("source_id", "")): item
            for item in payload.get("sources", [])
            if item.get("source_id")
        }
        records = []
        for item in payload.get("records", []):
            declared_source_refs = _unique(item.get("source_refs", []))
            source_refs = [ref for ref in declared_source_refs if ref in sources]
            evidence = self._culture_evidence(item, len(source_refs))
            records.append(
                {
                    "id": str(item.get("culture_id", "")),
                    "name": str(item.get("culture_name", "")),
                    "aliases": item.get("aliases", []),
                    "category": str(item.get("category", "")),
                    "region": item.get("region", []),
                    "crafts": item.get("crafts", []),
                    "materials": item.get("materials", []),
                    "modernizableElements": item.get("modernizable_elements", []),
                    "nonTransferableElements": item.get("non_transferable_elements", []),
                    "culturalTaboos": item.get("cultural_taboos", []),
                    "sourceRefs": source_refs,
                    "missingSourceRefs": [
                        ref for ref in declared_source_refs if ref not in sources
                    ],
                    "sourceDetails": [sources[ref] for ref in source_refs if ref in sources],
                    "evidenceScore": evidence["overall"],
                    "evidenceScoreBreakdown": evidence,
                }
            )
        return {
            "schemaVersion": SCHEMA_VERSION,
            "kind": "culture",
            "title": "在地文化内容库",
            "updatedAt": str(payload.get("updated_at", "")),
            "recordCount": len(records),
            "sourceCount": len(sources),
            "records": records,
            "promotionPolicy": (
                "自动巡检只产生候选；人工完成来源核验、字段映射与文化边界检查后，"
                "记录才进入本库。"
            ),
            "evidenceScorePolicy": (
                "50% 来源充分度 + 20% 地域具体度 + 30% 可转译字段完整度；"
                "缺失来源不会计分或进入自动设计。"
            ),
        }

    def form_library(self) -> dict[str, Any]:
        payload = _load_json(self.forms_path, {"ranking": []})
        records = []
        for item in payload.get("ranking", []):
            name = str(item.get("product_form", ""))
            archetype = FORM_ARCHETYPES.get(name)
            representative = item.get("representative_posts", [])
            source_refs = _unique(
                str(post.get("source_ref", ""))
                for post in representative
                if post.get("url")
            )
            evidence_ready = bool(source_refs and int(item.get("sample_size", 0)) > 0)
            records.append(
                {
                    "id": name,
                    "name": name,
                    "rank": int(item.get("rank", 0)),
                    "hotScore": float(item.get("cross_platform_hot_score", 0)),
                    "sampleSize": int(item.get("sample_size", 0)),
                    "platformCoverage": int(item.get("platform_coverage", 0)),
                    "platformScores": item.get("platform_scores", {}),
                    "platformPostCounts": item.get("platform_post_counts", {}),
                    "freshnessScore": float(item.get("freshness_score", 0)),
                    "whyHot": item.get("why_hot", []),
                    "representativePosts": representative,
                    "sourceRefs": source_refs,
                    "renderer": archetype["renderer"] if archetype else "",
                    "rendererLabel": archetype["label"] if archetype else "未支持",
                    "executable": bool(archetype and int(item.get("sample_size", 0)) > 0),
                    "evidenceReady": evidence_ready,
                }
            )
        return {
            "schemaVersion": SCHEMA_VERSION,
            "kind": "product_form",
            "title": "爆款产品形态库",
            "generatedAt": str(payload.get("generated_at", "")),
            "sampleSize": int(payload.get("total_sample_size", 0)),
            "platforms": payload.get("platforms", []),
            "recordCount": len(records),
            "records": records,
            "methodology": payload.get("methodology", {}),
            "evidenceBoundary": (
                f"当前排序来自已保存的 {int(payload.get('total_sample_size', 0))} 条"
                "历史真实平台快照；它不是今日实时销量，"
                "每条形态均可回看代表原记录和检索时间。"
            ),
        }

    @staticmethod
    def _culture_evidence(item: dict[str, Any], source_count: int) -> dict[str, Any]:
        source_component = min(100, 45 + source_count * 9)
        specificity = 100 if len(item.get("region", [])) <= 3 else 68
        structured = min(100, 55 + len(item.get("modernizable_elements", [])) * 8)
        return {
            "overall": round(
                source_component * 0.5 + specificity * 0.2 + structured * 0.3,
                1,
            ),
            "verifiedSourceCount": source_count,
            "sourceSufficiency": source_component,
            "regionalSpecificity": specificity,
            "translationCompleteness": structured,
            "formula": "来源充分度50% + 地域具体度20% + 可转译字段完整度30%",
        }

    def _culture_map(self) -> dict[str, dict[str, Any]]:
        return {item["id"]: item for item in self.culture_library()["records"]}

    def _form_map(self) -> dict[str, dict[str, Any]]:
        return {item["id"]: item for item in self.form_library()["records"]}

    def _pair_score(
        self,
        culture: dict[str, Any],
        form: dict[str, Any],
        max_hot_score: float,
    ) -> dict[str, Any]:
        archetype = FORM_ARCHETYPES.get(form["id"], {})
        group = archetype.get("group", "")
        compatibility = CATEGORY_COMPATIBILITY.get(culture["category"], {}).get(group, 60)
        market_normalized = round(
            (float(form["hotScore"]) / max_hot_score * 100) if max_hot_score else 0,
            1,
        )
        translation = min(100.0, 55 + len(culture["modernizableElements"]) * 9)
        safety = max(45.0, 100 - len(culture["nonTransferableElements"]) * 8)
        overall = round(
            float(culture["evidenceScore"]) * 0.25
            + market_normalized * 0.25
            + compatibility * 0.25
            + translation * 0.15
            + safety * 0.10,
            1,
        )
        return {
            "overall": overall,
            "cultureEvidence": float(culture["evidenceScore"]),
            "marketEvidence": market_normalized,
            "observedHotScore": float(form["hotScore"]),
            "compatibility": compatibility,
            "translationSpace": translation,
            "boundarySafety": safety,
            "formula": (
                "文化证据25% + 形态热度25% + 品类兼容25% + 转译空间15% + 边界安全10%"
            ),
            "scoreVersion": "studio-combination-1.0",
        }

    def ranked_combinations(
        self,
        *,
        culture_ids: list[str] | None = None,
        form_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        cultures = self._culture_map()
        forms = self._form_map()
        selected_culture_ids = culture_ids or list(cultures)
        selected_form_ids = form_ids or list(forms)
        unknown_cultures = [item for item in selected_culture_ids if item not in cultures]
        unknown_forms = [item for item in selected_form_ids if item not in forms]
        if unknown_cultures:
            raise ValueError("不存在的文化记录：" + "、".join(unknown_cultures))
        if unknown_forms:
            raise ValueError("不存在的产品形态：" + "、".join(unknown_forms))
        max_hot = max((float(item["hotScore"]) for item in forms.values()), default=0)
        rows: list[dict[str, Any]] = []
        for culture_id in selected_culture_ids:
            culture = cultures[culture_id]
            if (
                len(culture["sourceRefs"]) < 2
                or culture["missingSourceRefs"]
                or not culture["modernizableElements"]
            ):
                continue
            for form_id in selected_form_ids:
                form = forms[form_id]
                if (
                    not form["executable"]
                    or not form["evidenceReady"]
                    or form["sampleSize"] <= 0
                ):
                    continue
                rows.append(
                    {
                        "cultureId": culture_id,
                        "cultureName": culture["name"],
                        "productFormId": form_id,
                        "productFormName": form["name"],
                        "scores": self._pair_score(culture, form, max_hot),
                    }
                )
        rows.sort(
            key=lambda item: (
                float(item["scores"]["overall"]),
                float(item["scores"]["observedHotScore"]),
                item["cultureName"],
            ),
            reverse=True,
        )
        return rows

    def _select_daily(self, limit: int = DAILY_LIMIT) -> list[dict[str, Any]]:
        candidates = self.ranked_combinations()
        selected: list[dict[str, Any]] = []
        used_cultures: set[str] = set()
        used_forms: set[str] = set()
        for candidate in candidates:
            if candidate["cultureId"] in used_cultures or candidate["productFormId"] in used_forms:
                continue
            selected.append(candidate)
            used_cultures.add(candidate["cultureId"])
            used_forms.add(candidate["productFormId"])
            if len(selected) >= limit:
                break
        return selected

    def generate_daily(self, *, trigger: str = "schedule", force: bool = False) -> dict[str, Any]:
        with self._lock:
            daily_date = _local_date()
            existing = self.store.designs_for_date(daily_date)
            if existing and not force:
                return {
                    "batchId": str(existing[0].get("batchId", "")),
                    "dailyDate": daily_date,
                    "generatedCount": len(existing),
                    "designs": existing,
                    "reused": True,
                }
            selected = self._select_daily(DAILY_LIMIT)
            if not selected:
                raise RuntimeError(
                    "没有同时通过文化证据、市场样本和显式形态生成器门槛的组合。"
                )
            batch_id = f"DAY-{daily_date.replace('-', '')}-{uuid4().hex[:8].upper()}"
            designs = []
            for rank, candidate in enumerate(selected, 1):
                designs.append(
                    self._create_design(
                        culture_ids=[candidate["cultureId"]],
                        form_ids=[candidate["productFormId"]],
                        origin="daily",
                        batch_id=batch_id,
                        daily_date=daily_date,
                        daily_rank=rank,
                        trigger=trigger,
                        scores=candidate["scores"],
                        persist=False,
                    )
                )
            all_rows = self.store.load_designs()
            if existing:
                existing_ids = {item["designId"] for item in existing}
                for row in all_rows:
                    if row.get("designId") in existing_ids:
                        row["superseded"] = True
            new_ids = {item["designId"] for item in designs}
            self.store.save_designs(
                [*designs, *[item for item in all_rows if item.get("designId") not in new_ids]]
            )
            run_dir = self.store.runs_dir / batch_id
            _atomic_json(
                run_dir / "manifest.json",
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "batchId": batch_id,
                    "trigger": trigger,
                    "dailyDate": daily_date,
                    "generatedAt": _iso(),
                    "requestedLimit": DAILY_LIMIT,
                    "generatedCount": len(designs),
                    "designIds": [item["designId"] for item in designs],
                    "selectionPolicy": (
                        "按可解释组合分降序，文化记录与产品形态均做去重；Top 3 是上限，"
                        "门槛不足时不会补假结果。"
                    ),
                },
            )
            return {
                "batchId": batch_id,
                "dailyDate": daily_date,
                "generatedCount": len(designs),
                "designs": designs,
                "reused": False,
            }

    def generate_manual(self, candidate: dict[str, Any]) -> dict[str, Any]:
        culture_ids = _unique(candidate.get("cultureIds", []))
        form_ids = _unique(candidate.get("productFormIds", []))
        if not 1 <= len(culture_ids) <= 3:
            raise ValueError("自由组合必须选择 1–3 条文化内容。")
        if not 1 <= len(form_ids) <= 3:
            raise ValueError("自由组合必须选择 1–3 个产品形态。")
        combinations = self.ranked_combinations(culture_ids=culture_ids, form_ids=form_ids)
        if not combinations:
            raise ValueError("所选组合没有通过证据或生成器门槛。")
        scores = self._aggregate_scores(combinations)
        return self._create_design(
            culture_ids=culture_ids,
            form_ids=form_ids,
            origin="manual",
            batch_id=f"MANUAL-{_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:6].upper()}",
            daily_date="",
            daily_rank=0,
            trigger="manual",
            scores=scores,
            overrides=candidate,
        )

    @staticmethod
    def _aggregate_scores(combinations: list[dict[str, Any]]) -> dict[str, Any]:
        score_keys = (
            "overall",
            "cultureEvidence",
            "marketEvidence",
            "observedHotScore",
            "compatibility",
            "translationSpace",
            "boundarySafety",
        )
        result = {
            key: round(
                sum(float(item["scores"][key]) for item in combinations) / len(combinations),
                1,
            )
            for key in score_keys
        }
        result.update(
            {
                "formula": combinations[0]["scores"]["formula"],
                "scoreVersion": combinations[0]["scores"]["scoreVersion"],
            }
        )
        return result

    def revise_design(self, design_id: str, candidate: dict[str, Any]) -> dict[str, Any]:
        current = self.store.get_design(design_id)
        culture_ids = _unique(
            candidate.get("cultureIds", [item["id"] for item in current["cultureItems"]])
        )
        form_ids = _unique(
            candidate.get("productFormIds", [item["id"] for item in current["productForms"]])
        )
        if not 1 <= len(culture_ids) <= 3 or not 1 <= len(form_ids) <= 3:
            raise ValueError("编辑后仍需保留 1–3 条文化内容和 1–3 个产品形态。")
        combinations = self.ranked_combinations(culture_ids=culture_ids, form_ids=form_ids)
        if not combinations:
            raise ValueError("编辑后的组合没有通过证据或生成器门槛。")
        overrides = {
            "title": candidate.get("title", current["title"]),
            "concept": candidate.get("concept", current["concept"]["statement"]),
            "audience": candidate.get("audience", current["concept"]["audience"]),
            "useScenario": candidate.get(
                "useScenario", current["concept"]["useScenarios"][0]
            ),
            "designNotes": candidate.get("designNotes", current["concept"]["designNotes"]),
            "palette": candidate.get("palette", current["visualDirection"]["palette"]),
        }
        return self._create_design(
            culture_ids=culture_ids,
            form_ids=form_ids,
            origin=current["origin"],
            batch_id=current["batchId"],
            daily_date=str(current.get("dailyDate", "")),
            daily_rank=int(current.get("dailyRank", 0)),
            trigger="edit_regenerate",
            scores=self._aggregate_scores(combinations),
            overrides=overrides,
            design_id=design_id,
            version=int(current.get("version", 1)) + 1,
            created_at=str(current.get("createdAt", _iso())),
            revision_history=[
                *current.get("revisionHistory", []),
                {
                    "version": int(current.get("version", 1)),
                    "at": str(current.get("updatedAt", "")),
                    "title": str(current.get("title", "")),
                    "cultureNames": [
                        str(item.get("name", ""))
                        for item in current.get("cultureItems", [])
                    ],
                    "productFormNames": [
                        str(item.get("name", ""))
                        for item in current.get("productForms", [])
                    ],
                    "concept": str(current.get("concept", {}).get("statement", "")),
                    "palette": str(
                        current.get("visualDirection", {}).get("palette", "slate")
                    ),
                    "scoreOverall": float(current.get("scores", {}).get("overall", 0)),
                    "assetSha256": str(current.get("asset", {}).get("sha256", "")),
                    "imageUrl": str(current.get("asset", {}).get("imageUrl", "")),
                },
            ][-20:],
        )

    def _create_design(
        self,
        *,
        culture_ids: list[str],
        form_ids: list[str],
        origin: str,
        batch_id: str,
        daily_date: str,
        daily_rank: int,
        trigger: str,
        scores: dict[str, Any],
        overrides: dict[str, Any] | None = None,
        design_id: str = "",
        version: int = 1,
        created_at: str = "",
        revision_history: list[dict[str, Any]] | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        overrides = overrides or {}
        cultures = self._culture_map()
        forms = self._form_map()
        culture_items = [cultures[item] for item in culture_ids]
        form_items = [forms[item] for item in form_ids]
        if not design_id:
            seed = f"{batch_id}|{'|'.join(culture_ids)}|{'|'.join(form_ids)}"
            design_id = "QCD-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12].upper()
        culture_name = " × ".join(item["name"] for item in culture_items)
        form_name = " + ".join(item["name"] for item in form_items)
        primary_culture = culture_items[0]
        primary_form = form_items[0]
        translated = _unique(
            feature
            for item in culture_items
            for feature in item["modernizableElements"][:2]
        )
        boundary = _unique(
            feature
            for item in culture_items
            for feature in item["nonTransferableElements"][:2]
        )
        materials = _unique(
            material for item in culture_items for material in item["materials"][:2]
        )
        title = _safe_text(
            overrides.get("title")
            or f"{primary_culture['name']}｜{FORM_ARCHETYPES[primary_form['id']]['label']}",
            80,
        )
        default_statement = (
            f"把{culture_name}中可公开转译的“{translated[0] if translated else '结构与节奏'}”"
            f"赋予{form_name}，以结构、材料和使用动作表达文化内容；"
            "不复制完整传统纹样，也不把概念稿写成量产成品。"
        )
        statement = _safe_text(overrides.get("concept") or default_statement, 500)
        palette = str(overrides.get("palette", "slate"))
        if palette not in PALETTES:
            raise ValueError("视觉配色必须是 slate、indigo 或 vermilion。")
        generated_at = _iso()
        design = {
            "schemaVersion": SCHEMA_VERSION,
            "designId": design_id,
            "batchId": batch_id,
            "origin": origin,
            "trigger": trigger,
            "dailyDate": daily_date,
            "dailyRank": daily_rank,
            "superseded": False,
            "status": "generated",
            "version": version,
            "createdAt": created_at or generated_at,
            "updatedAt": generated_at,
            "title": title,
            "subtitle": f"{culture_name} × {form_name}",
            "cultureItems": culture_items,
            "productForms": form_items,
            "scores": scores,
            "selection": {
                "policy": (
                    "系统按组合分排序并执行文化与形态去重。"
                    if origin == "daily"
                    else "用户手动选择内容与形态，系统只执行证据门和兼容评分。"
                ),
                "rank": daily_rank,
                "candidateGate": "来源≥2、存在可转译元素、形态样本>0、显式渲染器已注册",
            },
            "concept": {
                "statement": statement,
                "audience": _safe_text(overrides.get("audience") or "18–35 岁旅行者与文化消费者", 120),
                "useScenarios": [
                    _safe_text(overrides.get("useScenario") or "旅行纪念与日常使用", 120)
                ],
                "contentTranslation": translated[:5],
                "formExpression": [
                    FORM_ARCHETYPES[item["id"]]["label"] for item in form_items
                ],
                "materials": materials[:5] or ["材料由首样验证后确定"],
                "interaction": self._interaction_for_forms(form_ids),
                "designNotes": _safe_text(overrides.get("designNotes", ""), 500),
                "doNotUse": boundary[:5],
            },
            "visualDirection": {
                "palette": palette,
                "renderer": FORM_ARCHETYPES[primary_form["id"]]["renderer"],
                "rendererLabel": FORM_ARCHETYPES[primary_form["id"]]["label"],
                "style": "结构概念板 / 非摄影效果图",
            },
            "workflow": {
                "lastRegeneratedFrom": "content_and_form" if version > 1 else "automatic_selection",
                "stages": [
                    {"id": "content", "label": "文化内容", "status": "verified", "editable": True},
                    {"id": "form", "label": "产品形态", "status": "verified_snapshot", "editable": True},
                    {"id": "fusion", "label": "融合方案", "status": "generated", "editable": True},
                    {"id": "visual", "label": "设计稿", "status": "generated_local", "editable": True},
                    {"id": "production", "label": "生产前验证", "status": "not_ready", "editable": False},
                ],
            },
            "provenance": {
                "cultureRecordIds": culture_ids,
                "cultureSourceRefs": _unique(
                    ref for item in culture_items for ref in item["sourceRefs"]
                ),
                "marketSourceRefs": _unique(
                    ref for item in form_items for ref in item["sourceRefs"]
                ),
                "marketSampleSize": sum(int(item["sampleSize"]) for item in form_items),
                "marketSnapshotGeneratedAt": self.form_library()["generatedAt"],
                "renderer": "QianCraft deterministic form renderer",
                "imageGenerationUsed": False,
                "claim": (
                    "图像是本次真实生成的本地结构概念板；不是图像模型效果图，"
                    "也没有使用 reference_only 馆藏像素。"
                ),
            },
            "production": {
                "status": "concept_only",
                "massProductionReady": False,
                "boundary": (
                    "仅用于方向选择和后续工作流编辑；社区共审、文化授权、材料、"
                    "结构、成本、法规与工厂验证完成前不可直接量产。"
                ),
            },
            "revisionHistory": revision_history or [],
        }
        asset_dir = self.store.assets_dir / design_id
        asset_path = asset_dir / f"v{version}.png"
        self._render_design(design, asset_path)
        design["asset"] = {
            "imageUrl": f"/assets/studio/{design_id}/v{version}.png",
            "filename": asset_path.name,
            "sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
            "width": 1440,
            "height": 960,
            "generatedAt": generated_at,
        }
        if persist:
            self.store.upsert_design(design)
        return design

    @staticmethod
    def _interaction_for_forms(form_ids: list[str]) -> list[str]:
        mapping = {
            "冰箱贴": "吸附、组合与替换",
            "徽章": "佩戴与系列收集",
            "盲盒": "拆盒、识别与档案收集",
            "包挂": "随身悬挂与触摸",
            "伴手礼": "打开、阅读与分享",
            "潮玩": "陈列、把玩与系列组合",
            "香氛": "嗅闻、空间记忆与补充装",
            "挂件": "悬挂、触摸与替换",
            "首饰": "佩戴、组合与溯源",
            "毛绒": "触摸、陪伴与可替换部件",
        }
        return [mapping[item] for item in form_ids if item in mapping]

    def _render_design(self, design: dict[str, Any], path: Path) -> None:
        palette = PALETTES[design["visualDirection"]["palette"]]
        canvas = Image.new("RGB", (1440, 960), palette["shell"])
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1440, 78), fill=palette["primary"])
        draw.text((48, 22), "QIANCRAFT / CONCEPT SHEET", font=_font(24, True), fill=(248, 248, 245))
        draw.text(
            (1110, 24),
            f"V{design['version']} · {design['updatedAt'][:10]}",
            font=_font(20),
            fill=(235, 237, 236),
        )
        draw.rounded_rectangle(
            (42, 112, 870, 914), radius=24, fill=palette["surface"], outline=palette["line"], width=2
        )
        draw.rounded_rectangle(
            (898, 112, 1398, 914), radius=24, fill=palette["surface"], outline=palette["line"], width=2
        )
        draw.text((82, 150), design["subtitle"], font=_font(22), fill=palette["accent"])
        title_y = _draw_text(
            draw,
            (82, 190),
            design["title"],
            _font(52, True),
            palette["ink"],
            720,
            66,
            2,
        )
        product_box = (98, max(330, title_y + 32), 814, 810)
        self._draw_product(draw, product_box, design["productForms"][0]["id"], palette)
        draw.rounded_rectangle((112, 824, 800, 878), radius=16, fill=palette["shell"])
        draw.text(
            (138, 840),
            "本地结构概念板 · 不含馆藏像素 · 非量产工程图",
            font=_font(20, True),
            fill=palette["ink"],
        )
        y = 148
        sections = [
            ("01 文化内容", "、".join(item["name"] for item in design["cultureItems"])),
            ("02 产品形态", "、".join(item["name"] for item in design["productForms"])),
            ("03 融合方案", design["concept"]["statement"]),
            (
                "04 组合评分",
                f"{design['scores']['overall']:.1f} / 100 · {design['scores']['formula']}",
            ),
            (
                "05 文化边界",
                "；".join(design["concept"]["doNotUse"][:2])
                or "保持地域、工艺和来源清晰；不复制完整传统纹样。",
            ),
            ("06 生产状态", design["production"]["boundary"]),
        ]
        for label, value in sections:
            draw.text((936, y), label, font=_font(20, True), fill=palette["primary"])
            y = _draw_text(
                draw,
                (936, y + 34),
                value,
                _font(20),
                palette["ink"],
                420,
                30,
                4 if label == "03 融合方案" else 3,
            )
            y += 24
            if y < 870:
                draw.line((936, y - 10, 1358, y - 10), fill=palette["line"], width=1)
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, format="PNG", optimize=True)

    @staticmethod
    def _draw_product(
        draw: ImageDraw.ImageDraw,
        box: tuple[int, int, int, int],
        form: str,
        palette: dict[str, tuple[int, int, int]],
    ) -> None:
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        ink = palette["ink"]
        primary = palette["primary"]
        accent = palette["accent"]
        shell = palette["shell"]
        if form == "冰箱贴":
            for index, offset in enumerate((-150, 0, 150)):
                top = cy - 155 + (index % 2) * 55
                draw.rounded_rectangle(
                    (cx + offset - 92, top, cx + offset + 92, top + 255),
                    radius=36,
                    fill=primary if index != 1 else accent,
                    outline=ink,
                    width=4,
                )
                for row in range(4):
                    draw.line(
                        (cx + offset - 54, top + 58 + row * 38, cx + offset + 54, top + 42 + row * 38),
                        fill=shell,
                        width=7,
                    )
        elif form == "徽章":
            for radius, color in ((190, ink), (170, primary), (112, shell), (58, accent)):
                draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
            for angle_offset in (-110, -35, 40, 115):
                draw.rounded_rectangle(
                    (cx + angle_offset - 18, cy - 118, cx + angle_offset + 18, cy + 118),
                    radius=16,
                    outline=ink,
                    width=5,
                )
        elif form == "盲盒":
            draw.polygon(
                [(cx - 210, cy - 120), (cx, cy - 235), (cx + 210, cy - 120), (cx, cy - 5)],
                fill=shell,
                outline=ink,
            )
            draw.polygon(
                [(cx - 210, cy - 120), (cx, cy - 5), (cx, cy + 240), (cx - 210, cy + 115)],
                fill=primary,
                outline=ink,
            )
            draw.polygon(
                [(cx + 210, cy - 120), (cx, cy - 5), (cx, cy + 240), (cx + 210, cy + 115)],
                fill=accent,
                outline=ink,
            )
            draw.ellipse((cx - 55, cy + 45, cx + 55, cy + 155), fill=shell, outline=ink, width=4)
        elif form in {"包挂", "挂件"}:
            draw.arc((cx - 90, cy - 270, cx + 90, cy - 80), 180, 360, fill=ink, width=18)
            draw.rounded_rectangle(
                (cx - 155, cy - 110, cx + 155, cy + 225),
                radius=120,
                fill=primary,
                outline=ink,
                width=5,
            )
            draw.rounded_rectangle(
                (cx - 92, cy - 22, cx + 92, cy + 126),
                radius=32,
                fill=shell,
                outline=accent,
                width=8,
            )
        elif form == "伴手礼":
            draw.rounded_rectangle(
                (cx - 245, cy - 160, cx + 245, cy + 190),
                radius=26,
                fill=shell,
                outline=ink,
                width=5,
            )
            draw.rectangle((cx - 245, cy - 160, cx + 245, cy - 80), fill=primary)
            draw.rectangle((cx - 38, cy - 160, cx + 38, cy + 190), fill=accent)
            draw.line((cx - 170, cy + 58, cx + 170, cy + 58), fill=ink, width=4)
        elif form == "潮玩":
            draw.ellipse((cx - 145, cy - 230, cx + 145, cy + 20), fill=primary, outline=ink, width=5)
            draw.rounded_rectangle(
                (cx - 185, cy - 10, cx + 185, cy + 230),
                radius=105,
                fill=shell,
                outline=ink,
                width=5,
            )
            draw.ellipse((cx - 72, cy - 145, cx - 34, cy - 107), fill=accent)
            draw.ellipse((cx + 34, cy - 145, cx + 72, cy - 107), fill=accent)
        elif form == "香氛":
            draw.rounded_rectangle(
                (cx - 155, cy - 145, cx + 155, cy + 240),
                radius=58,
                fill=shell,
                outline=ink,
                width=5,
            )
            draw.rectangle((cx - 68, cy - 235, cx + 68, cy - 145), fill=primary, outline=ink, width=4)
            draw.rounded_rectangle((cx - 96, cy - 20, cx + 96, cy + 125), radius=22, fill=accent)
        elif form == "首饰":
            draw.arc((cx - 235, cy - 285, cx + 235, cy + 185), 190, 350, fill=ink, width=9)
            draw.polygon(
                [(cx, cy - 55), (cx + 125, cy + 95), (cx, cy + 245), (cx - 125, cy + 95)],
                fill=primary,
                outline=ink,
            )
            draw.polygon(
                [(cx, cy - 4), (cx + 68, cy + 95), (cx, cy + 185), (cx - 68, cy + 95)],
                fill=shell,
            )
        else:  # 毛绒是唯一剩余且有显式注册的形态。
            draw.ellipse((cx - 128, cy - 270, cx - 12, cy - 92), fill=primary, outline=ink, width=5)
            draw.ellipse((cx + 12, cy - 270, cx + 128, cy - 92), fill=primary, outline=ink, width=5)
            draw.rounded_rectangle(
                (cx - 205, cy - 165, cx + 205, cy + 250),
                radius=170,
                fill=primary,
                outline=ink,
                width=5,
            )
            draw.rounded_rectangle(
                (cx - 112, cy - 35, cx + 112, cy + 150),
                radius=55,
                fill=shell,
                outline=accent,
                width=8,
            )


class StudioScheduler:
    """Single-process daily design scheduler with persistent state and catch-up."""

    def __init__(self, store: StudioStore, engine: StudioEngine, tick_seconds: float = 10.0) -> None:
        self.store = store
        self.engine = engine
        self.tick_seconds = max(0.2, tick_seconds)
        self.instance_id = f"studio-{uuid4().hex[:10]}"
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._worker: threading.Thread | None = None
        self._lock = threading.RLock()
        self._force_next = False

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            state = self.store.load_state()
            if state["daily"].get("status") == "running":
                state["daily"].update(
                    {
                        "status": "interrupted",
                        "detail": "API 进程重启；旧批次未被冒充为成功，已重新排队。",
                    }
                )
            if not self.store.designs_for_date(_local_date()):
                state["daily"]["nextRunAt"] = _iso(_now() + timedelta(seconds=3))
                state["daily"]["detail"] = "今日尚无设计，启动后执行补跑。"
            state["scheduler"] = {
                "status": "running",
                "instanceId": self.instance_id,
                "startedAt": _iso(),
                "heartbeatAt": _iso(),
            }
            self.store.save_state(state)
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._loop,
                daemon=True,
                name="qiancraft-daily-design",
            )
            self._thread.start()
            self.store.add_event(
                event="scheduler_started",
                status="running",
                detail="每日 Top 3 设计调度器已启动。",
                metadata={"instanceId": self.instance_id},
            )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=min(5.0, self.tick_seconds + 0.5))
        state = self.store.load_state()
        state["scheduler"].update({"status": "stopped", "heartbeatAt": _iso()})
        self.store.save_state(state)

    def _loop(self) -> None:
        self.tick()
        while not self._stop_event.wait(self.tick_seconds):
            try:
                self.tick()
            except Exception as exc:  # noqa: BLE001
                self.store.add_event(
                    event="scheduler_tick_failed",
                    status="error",
                    detail=str(exc),
                )

    def tick(self) -> None:
        with self._lock:
            config = self.store.load_config()
            state = self.store.load_state()
            state["scheduler"].update(
                {
                    "status": "running" if config["enabled"] else "paused",
                    "instanceId": self.instance_id,
                    "heartbeatAt": _iso(),
                }
            )
            if not config["enabled"]:
                if state["daily"].get("status") != "running":
                    state["daily"].update({"status": "paused", "detail": "每日生成已暂停。"})
                self.store.save_state(state)
                return
            due = _parse_time(str(state["daily"].get("nextRunAt", "")))
            running = bool(self._worker and self._worker.is_alive())
            if not running and (due is None or due <= _now()):
                force = self._force_next
                self._force_next = False
                state["daily"].update(
                    {
                        "status": "running",
                        "lastAttemptAt": _iso(),
                        "detail": "正在读取双库、评分并生成最多 3 个设计。",
                    }
                )
                self.store.save_state(state)
                self._worker = threading.Thread(
                    target=self._run_worker,
                    args=("manual" if force else "schedule", force),
                    daemon=True,
                    name="qiancraft-daily-design-worker",
                )
                self._worker.start()
                return
            self.store.save_state(state)

    def _run_worker(self, trigger: str, force: bool) -> None:
        try:
            result = self.engine.generate_daily(trigger=trigger, force=force)
            config = self.store.load_config()
            state = self.store.load_state()
            state["daily"].update(
                {
                    "status": "healthy",
                    "lastSuccessAt": _iso(),
                    "lastBatchId": result["batchId"],
                    "nextRunAt": _iso(self._next_run(config)),
                    "detail": f"已生成 {result['generatedCount']} 个可审计设计。",
                    "runCount": int(state["daily"].get("runCount", 0)) + 1,
                    "consecutiveFailures": 0,
                    "generatedCount": result["generatedCount"],
                }
            )
            self.store.save_state(state)
            self.store.add_event(
                event="daily_design_completed",
                status="healthy",
                detail=state["daily"]["detail"],
                metadata={
                    "batchId": result["batchId"],
                    "generatedCount": result["generatedCount"],
                    "trigger": trigger,
                    "reused": result["reused"],
                },
            )
        except Exception as exc:  # noqa: BLE001
            config = self.store.load_config()
            state = self.store.load_state()
            failures = int(state["daily"].get("consecutiveFailures", 0)) + 1
            retry = min(240, max(15, failures * 15))
            state["daily"].update(
                {
                    "status": "failed",
                    "detail": f"每日生成失败：{_safe_text(exc, 500)}",
                    "nextRunAt": _iso(_now() + timedelta(minutes=retry)),
                    "consecutiveFailures": failures,
                    "generatedCount": 0,
                }
            )
            self.store.save_state(state)
            self.store.add_event(
                event="daily_design_failed",
                status="failed",
                detail=state["daily"]["detail"],
                metadata={"retryMinutes": retry, "scheduledHour": config["hour"]},
            )

    @staticmethod
    def _next_run(config: dict[str, Any], now: datetime | None = None) -> datetime:
        current = (now or _now()).astimezone(SHANGHAI)
        scheduled = datetime.combine(
            current.date(),
            time(hour=int(config["hour"]), minute=int(config["minute"])),
            tzinfo=SHANGHAI,
        )
        if scheduled <= current:
            scheduled += timedelta(days=1)
        return scheduled.astimezone(UTC)

    def run_now(self) -> dict[str, Any]:
        with self._lock:
            if self._worker and self._worker.is_alive():
                raise RuntimeError("每日设计任务正在运行。")
            state = self.store.load_state()
            state["daily"].update(
                {
                    "status": "scheduled",
                    "nextRunAt": _iso(_now() - timedelta(seconds=1)),
                    "detail": "已请求立即重新生成今日 Top 3。",
                }
            )
            self._force_next = True
            self.store.save_state(state)
        self.tick()
        return self.status()

    def configure(self, candidate: dict[str, Any]) -> dict[str, Any]:
        config = self.store.save_config(candidate)
        state = self.store.load_state()
        if config["enabled"]:
            state["daily"].update(
                {
                    "status": "scheduled",
                    "nextRunAt": _iso(self._next_run(config)),
                    "detail": "每日生成计划已更新。",
                }
            )
        elif state["daily"].get("status") != "running":
            state["daily"].update({"status": "paused", "detail": "每日生成已暂停。"})
        self.store.save_state(state)
        self.store.add_event(
            event="schedule_updated",
            status="running" if config["enabled"] else "paused",
            detail="每日设计计划已更新。",
            metadata={"hour": config["hour"], "minute": config["minute"]},
        )
        return self.status()

    def status(self) -> dict[str, Any]:
        config = self.store.load_config()
        state = self.store.load_state()
        today = self.store.designs_for_date(_local_date())
        return {
            "schemaVersion": SCHEMA_VERSION,
            "enabled": config["enabled"],
            "schedule": {
                "hour": config["hour"],
                "minute": config["minute"],
                "timezone": config["timezone"],
                "limit": DAILY_LIMIT,
            },
            "scheduler": {
                **state["scheduler"],
                "threadAlive": bool(self._thread and self._thread.is_alive()),
            },
            "daily": state["daily"],
            "today": {
                "date": _local_date(),
                "designCount": len(today),
                "designIds": [item["designId"] for item in today],
            },
            "policy": (
                "每天最多 3 个；只有通过证据与显式生成器门槛的组合才生成，"
                "不足时如实少于 3 个。"
            ),
        }

    def health(self, *, now: datetime | None = None) -> dict[str, Any]:
        state = self.store.load_state()
        heartbeat_at = str(state.get("scheduler", {}).get("heartbeatAt", ""))
        heartbeat = _parse_time(heartbeat_at)
        current = now or _now()
        age = max(0.0, (current - heartbeat).total_seconds()) if heartbeat else None
        fresh = age is not None and age <= HEARTBEAT_MAX_AGE_SECONDS
        alive = bool(self._thread and self._thread.is_alive())
        return {
            "ok": alive and fresh,
            "online": alive,
            "heartbeatAt": heartbeat_at,
            "heartbeatFresh": fresh,
            "heartbeatAgeSeconds": round(age, 3) if age is not None else None,
            "maxHeartbeatAgeSeconds": HEARTBEAT_MAX_AGE_SECONDS,
            "status": "healthy" if alive and fresh else "unhealthy",
            "enabled": self.store.load_config()["enabled"],
        }
