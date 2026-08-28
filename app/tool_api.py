from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import socket
import threading
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from app.adapters.image_generation_adapter import image_provider_status
from app.config import MARKET_PLATFORM_CODES, load_settings
from app.designer import DesignAgent, render_design_package_markdown, render_design_poster
from app.pipeline import run_pipeline
from app.schemas import DemoRequest, DesignerHandoff, DesignPackage
from app.workbench import (
    BUNDLED_GENERATED_DIR,
    DESIGN_RUNS_DIR,
    GENERATED_DIR,
    create_workbench_workspace,
    duplicate_concept,
    generate_more_concept,
    list_workbench_workspaces,
    load_workbench_workspace,
    node_detail,
    promote_research_run,
    regenerate_concept,
    run_workbench_node,
    save_workbench_workspace,
    set_active_concept,
    update_decision_profile,
    update_design_brief,
    workbench_bootstrap,
    workbench_design_package,
    workspace_strategy_path,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
CULTURE_PATH = ROOT_DIR / "data" / "culture" / "knowledge_graph.json"
MARKET_VERIFIED_PATH = ROOT_DIR / "data" / "market" / "verified_signals.json"
MARKET_DERIVED_DIR = ROOT_DIR / "data" / "market" / "derived"
STRATEGY_PATH = ROOT_DIR / "data" / "outputs" / "pre_design_strategy.json"
HANDOFF_PATH = ROOT_DIR / "data" / "outputs" / "designer_handoff.json"
DESIGN_PATH = ROOT_DIR / "data" / "outputs" / "design_specification.json"
RUN_MANIFEST_PATH = ROOT_DIR / "data" / "outputs" / "run_manifest.json"
WORKSPACE_DIR = Path(
    os.environ.get(
        "QIANCRAFT_TOOL_WORKSPACE_DIR",
        str(ROOT_DIR / "data" / "runtime" / "tool_workspace"),
    )
).expanduser().resolve()
WORKSPACE_PATH = WORKSPACE_DIR / "workspace.json"
TOOL_RUNS_DIR = WORKSPACE_DIR / "design_runs"
RESEARCH_RUNS_DIR = WORKSPACE_DIR / "research_runs"

DESIGN_LOCK = threading.Lock()
RESEARCH_LOCK = threading.Lock()
RESEARCH_JOB_STATE_LOCK = threading.Lock()
ACTIVE_RESEARCH_JOB_ID = ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _historical_market_snapshot() -> tuple[Path | None, dict[str, Any], dict[str, int]]:
    candidates: list[tuple[str, Path, dict[str, Any], dict[str, int]]] = []
    for path in MARKET_DERIVED_DIR.glob("market_evidence_*.json"):
        try:
            payload = _load_json(path)
        except (OSError, ValueError):
            continue
        counts = Counter(
            str(item.get("platform", ""))
            for item in payload.get("records", [])
            if item.get("evidence_type") == "social_signal"
            and item.get("platform") in MARKET_PLATFORM_CODES
        )
        if counts:
            generated_at = str(payload.get("generated_at", path.stem))
            candidates.append((generated_at, path, payload, dict(counts)))
    if not candidates:
        return None, {}, {}
    _, path, payload, counts = max(
        candidates,
        key=lambda item: (sum(item[3].values()), item[0]),
    )
    return path, payload, counts


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.35):
            return True
    except OSError:
        return False


def _strict_preflight(*, allow_interactive: bool = False) -> dict[str, Any]:
    settings = load_settings()
    image_status = image_provider_status(settings)
    crawler_entry = settings.mediacrawler_path / "main.py"
    explicit_crawl = allow_interactive and os.name == "nt"
    checks = [
        {
            "id": "llm",
            "label": "策划模型凭证",
            "ok": settings.has_llm_key,
            "detail": "已配置" if settings.has_llm_key else "缺少 LLM_API_KEY",
        },
        {
            "id": "crawler_switch",
            "label": "实时市场采集开关",
            "ok": settings.mediacrawler_live_enabled or explicit_crawl,
            "detail": (
                "网页本轮显式授权启动"
                if explicit_crawl and not settings.mediacrawler_live_enabled
                else "已启用"
                if settings.mediacrawler_live_enabled
                else "MEDIACRAWLER_LIVE_ENABLED=false"
            ),
        },
        {
            "id": "crawler_runtime",
            "label": "市场采集运行时",
            "ok": settings.mediacrawler_python.exists() and crawler_entry.exists(),
            "detail": (
                "可用"
                if settings.mediacrawler_python.exists() and crawler_entry.exists()
                else "MediaCrawler 源码或独立 Python 环境不存在"
            ),
        },
        {
            "id": "lightrag",
            "label": "文化检索运行时",
            "ok": (settings.lightrag_path / "lightrag").is_dir(),
            "detail": (
                "源码可用"
                if (settings.lightrag_path / "lightrag").is_dir()
                else "LightRAG 运行模块不存在"
            ),
        },
        {
            "id": "image_provider",
            "label": "主视觉生成服务",
            "ok": image_status["configured"],
            "detail": image_status["detail"],
        },
    ]
    method = settings.mediacrawler_login_method
    cdp_ready = _port_open("127.0.0.1", settings.mediacrawler_cdp_port)
    platform_checks: list[dict[str, Any]] = []
    for platform in MARKET_PLATFORM_CODES:
        cookie_ready = bool(settings.mediacrawler_cookies.get(platform, ""))
        if method == "cookie":
            ok = cookie_ready
            detail = "Cookie 已配置" if ok else "缺少该平台 Cookie"
        elif method == "cdp":
            ok = cdp_ready or explicit_crawl
            detail = (
                "已连接授权浏览器"
                if cdp_ready
                else "将启动本机已保存的授权浏览器资料"
                if explicit_crawl
                else "没有已连接的授权浏览器"
            )
        else:
            ok = explicit_crawl
            detail = "将打开本人二维码授权" if ok else "二维码授权未显式开启"
        platform_checks.append(
            {
                "id": f"auth_{platform}",
                "label": f"{platform.upper()} 授权入口",
                "ok": ok,
                "detail": detail,
            }
        )
    checks.extend(platform_checks)
    blockers = [
        f"{item['label']}：{item['detail']}"
        for item in checks
        if item["id"] != "image_provider" and not item["ok"]
    ]
    return {
        "research_ready": not blockers,
        "image_generation_ready": image_status["configured"],
        "interactive_launch": explicit_crawl,
        "login_method": method,
        "checks": checks,
        "blockers": blockers,
    }


def audit_summary() -> dict[str, Any]:
    culture = _load_json(CULTURE_PATH)
    strategy = _load_json(STRATEGY_PATH)
    manifest = _load_json(RUN_MANIFEST_PATH)
    visual = _load_json(ROOT_DIR / "data" / "culture" / "visual_references.json")
    benchmark = _load_json(ROOT_DIR / "data" / "benchmark" / "cases.json")
    historical_path, historical, platform_counts = _historical_market_snapshot()
    social_count = sum(platform_counts.values())
    current_market = manifest.get("market_source", {})
    opportunity_count = len(strategy.get("opportunity_signals", []))
    generated_count = int(strategy.get("metadata", {}).get("generated_opportunities_accepted", 0))
    raw_dir = ROOT_DIR / "data" / "market" / "raw"
    raw_file_count = sum(
        (raw_dir / f"{code}.jsonl").is_file() for code in MARKET_PLATFORM_CODES
    )
    return {
        "project": {
            "topic": strategy.get("project", {}).get("topic", ""),
            "run_id": manifest.get("run_id", ""),
            "finished_at": manifest.get("finished_at", ""),
        },
        "repositories": [
            {
                "id": "culture",
                "name": "文化知识仓库",
                "count": len(culture.get("records", [])),
                "unit": "条记录",
                "secondary": f"{len(culture.get('sources', []))} 个登记来源",
                "status": "file_verified",
                "source_file": str(CULTURE_PATH.relative_to(ROOT_DIR)),
            },
            {
                "id": "market",
                "name": "历史市场快照",
                "count": social_count,
                "unit": "条社交平台记录",
                "secondary": " / ".join(
                    f"{code} {platform_counts.get(code, 0)}" for code in MARKET_PLATFORM_CODES
                ),
                "status": "historical_snapshot" if social_count else "unavailable",
                "source_file": (
                    str(historical_path.relative_to(ROOT_DIR)) if historical_path else ""
                ),
            },
            {
                "id": "benchmarks",
                "name": "对标案例仓库",
                "count": len(benchmark.get("cases", [])),
                "unit": "个案例",
                "secondary": "结构化案例文件",
                "status": "file_verified",
                "source_file": "data/benchmark/cases.json",
            },
            {
                "id": "visuals",
                "name": "视觉参考仓库",
                "count": len(visual.get("references", [])),
                "unit": "条参考",
                "secondary": "全部 reference_only",
                "status": "file_verified",
                "source_file": "data/culture/visual_references.json",
            },
        ],
        "truth_audit": {
            "culture": {
                "claimed": 22,
                "actual": len(culture.get("records", [])),
                "verified": len(culture.get("records", [])) == 22,
            },
            "market": {
                "claimed": 378,
                "actual": social_count,
                "verified": social_count == 378,
                "meaning": "历史派生快照中的社交平台记录，不是本次实时抓取",
                "raw_files_present": raw_file_count > 0,
                "raw_file_count": raw_file_count,
                "raw_files_complete": raw_file_count == len(MARKET_PLATFORM_CODES),
            },
            "opportunities": {
                "actual": opportunity_count,
                "model_generated": generated_count,
                "rule_baseline": max(0, opportunity_count - generated_count),
                "meaning": (
                    "当前 8 条均来自代码中的证据规则基线，随后被真实评分与二次核验；"
                    "不能标成模型从网上新生成的机会。"
                    if generated_count == 0
                    else "当前机会池同时含模型建议和规则基线。"
                ),
            },
        },
        "current_run": {
            "market_status": current_market.get("status", "unavailable"),
            "live_post_count": int(current_market.get("live_post_count", 0)),
            "cache_post_count": int(current_market.get("cache_post_count", 0)),
            "components": manifest.get("components", []),
        },
        "preflight": _strict_preflight(),
        "historical_snapshot": {
            "generated_at": historical.get("generated_at", ""),
            "file": str(historical_path.relative_to(ROOT_DIR)) if historical_path else "",
            "platform_counts": platform_counts,
            "social_record_count": social_count,
            "public_baseline_count": sum(
                item.get("evidence_type") != "social_signal"
                for item in historical.get("records", [])
            ),
        },
    }


def culture_records() -> dict[str, Any]:
    payload = _load_json(CULTURE_PATH)
    sources = {item["source_id"]: item for item in payload.get("sources", [])}
    records = []
    for item in payload.get("records", []):
        records.append(
            {
                **item,
                "source_details": [
                    sources[source_id]
                    for source_id in item.get("source_refs", [])
                    if source_id in sources
                ],
            }
        )
    return {
        "count": len(records),
        "source_count": len(sources),
        "updated_at": payload.get("updated_at", ""),
        "records": records,
    }


def market_records(params: dict[str, list[str]]) -> dict[str, Any]:
    source = params.get("source", ["historical"])[0]
    platform = params.get("platform", [""])[0].strip().lower()
    query = params.get("q", [""])[0].strip().lower()
    offset = max(0, int(params.get("offset", ["0"])[0]))
    limit = max(1, min(100, int(params.get("limit", ["30"])[0])))
    if source == "current":
        payload = _load_json(MARKET_DERIVED_DIR / "latest.json")
        source_file = "data/market/derived/latest.json"
    else:
        path, payload, _ = _historical_market_snapshot()
        source_file = str(path.relative_to(ROOT_DIR)) if path else ""
    records = payload.get("records", [])
    if platform:
        records = [item for item in records if item.get("platform") == platform]
    if query:
        records = [
            item
            for item in records
            if query
            in " ".join(
                str(item.get(key, ""))
                for key in ("title", "content", "search_keyword", "product_form")
            ).lower()
        ]
    return {
        "source": source,
        "source_file": source_file,
        "total": len(records),
        "offset": offset,
        "limit": limit,
        "records": records[offset : offset + limit],
    }


def _design_capability(item: dict[str, Any]) -> str | None:
    text = " ".join(str(value) for value in item.get("potential_product_categories", []))
    if any(term in text for term in ("毛绒", "玩偶", "织品")):
        return "plush"
    if any(term in text for term in ("冰箱贴", "徽章", "包挂", "收藏", "绣片")):
        return "magnet"
    if any(
        term in text
        for term in ("学习卡", "互动学习", "体验套件", "档案", "故事型礼赠")
    ):
        return "provenance"
    return None


def opportunities() -> dict[str, Any]:
    strategy = _load_json(STRATEGY_PATH)
    culture = _load_json(CULTURE_PATH)
    market = _load_json(MARKET_VERIFIED_PATH)
    sources = {
        item["source_id"]: item
        for item in [*culture.get("sources", []), *market.get("sources", [])]
    }
    generated_count = int(strategy.get("metadata", {}).get("generated_opportunities_accepted", 0))
    weights = strategy.get("metadata", {}).get("opportunity_scoring", {}).get("weights", {})
    result = []
    for item in strategy.get("opportunity_signals", []):
        verification = item.get("verification", {}).get("status", "warning")
        expected = round(
            item.get("culture_fit", 0) * 0.20
            + item.get("market_pull", 0) * 0.20
            + item.get("novelty", 0) * 0.20
            + item.get("visual_potential", 0) * 0.15
            + item.get("social_shareability", 0) * 0.15
            + item.get("product_feasibility", 0) * 0.10
            - item.get("cultural_risk", 0) * 0.20
            - (5 if verification == "warning" else 0),
            1,
        )
        if verification == "rejected":
            expected = 0
        result.append(
            {
                **item,
                "origin": "rule_baseline" if generated_count == 0 else "mixed_run",
                "design_generator": _design_capability(item),
                "score_audit": {
                    "stored": item.get("overall_score", 0),
                    "recomputed": expected,
                    "matches": abs(float(item.get("overall_score", 0)) - expected) < 0.01,
                },
                "evidence_details": [
                    sources[ref] for ref in item.get("evidence_refs", []) if ref in sources
                ],
            }
        )
    return {
        "count": len(result),
        "generated_accepted": generated_count,
        "baseline_count": len(result) - generated_count,
        "weights": weights,
        "ranked_ids": strategy.get("metadata", {})
        .get("opportunity_scoring", {})
        .get("ranked_opportunity_ids", []),
        "auto_top3_ids": strategy.get("metadata", {})
        .get("opportunity_scoring", {})
        .get("designer_top3_ids", []),
        "opportunities": result,
    }


def _workspace_default() -> dict[str, Any]:
    opportunity_payload = opportunities()
    return {
        "selection_mode": "auto",
        "selected_opportunity_ids": opportunity_payload["auto_top3_ids"],
        "primary_opportunity_id": "",
        "opportunity_edits": {},
        "design_overrides": {},
        "manual_brief": "",
        "last_design_run_id": "",
        "updated_at": "",
    }


def load_workspace() -> dict[str, Any]:
    default = _workspace_default()
    if not WORKSPACE_PATH.exists():
        return default
    stored = _load_json(WORKSPACE_PATH)
    return {**default, **stored}


def save_workspace(candidate: dict[str, Any]) -> dict[str, Any]:
    valid_ids = {
        item["opportunity_id"] for item in opportunities().get("opportunities", [])
    }
    current = load_workspace()
    allowed = {
        "selection_mode",
        "selected_opportunity_ids",
        "primary_opportunity_id",
        "opportunity_edits",
        "design_overrides",
        "manual_brief",
        "last_design_run_id",
    }
    merged = {**current, **{key: value for key, value in candidate.items() if key in allowed}}
    if merged["selection_mode"] not in {"auto", "manual"}:
        raise ValueError("selection_mode must be auto or manual")
    selected = [str(item) for item in merged.get("selected_opportunity_ids", [])]
    if not 1 <= len(selected) <= 3 or len(selected) != len(set(selected)):
        raise ValueError("必须选择 1 到 3 个不重复的机会")
    if any(item not in valid_ids for item in selected):
        raise ValueError("选择中包含不存在的机会")
    primary = str(merged.get("primary_opportunity_id", ""))
    if merged["selection_mode"] == "manual" and primary not in selected:
        raise ValueError("人工模式必须在已选机会中指定主机会")
    merged["selected_opportunity_ids"] = selected
    merged["updated_at"] = datetime.now(UTC).isoformat()
    _atomic_json(WORKSPACE_PATH, merged)
    return merged


def _priority_payload(
    item: dict[str, Any], rank: int, edits: dict[str, Any]
) -> dict[str, Any]:
    payload = {
        "rank": rank,
        "opportunity_id": item["opportunity_id"],
        "title": f"{item['culture_element']} × {item['trend_element']}",
        "culture_element": item["culture_element"],
        "trend_element": item["trend_element"],
        "why_now": item["match_reason"],
        "potential_product_categories": item.get("potential_product_categories", []),
        "design_keywords": item.get("design_keywords", []),
        "cultural_constraints": item.get("cultural_constraints", []),
        "score_breakdown": {
            key: item.get(key, 0)
            for key in (
                "culture_fit",
                "market_pull",
                "novelty",
                "visual_potential",
                "social_shareability",
                "product_feasibility",
                "cultural_risk",
            )
        },
        "overall_score": item["overall_score"],
        "verification": item["verification"],
        "evidence_refs": item.get("evidence_refs", []),
    }
    for key in (
        "title",
        "why_now",
        "potential_product_categories",
        "design_keywords",
        "cultural_constraints",
    ):
        if edits.get(key):
            payload[key] = edits[key]
    return payload


def _build_handoff_draft(
    workspace: dict[str, Any],
    path: Path,
    strategy_path: Path = STRATEGY_PATH,
) -> tuple[str | None, Path]:
    strategy = _load_json(strategy_path)
    items = {
        item["opportunity_id"]: item for item in strategy.get("opportunity_signals", [])
    }
    if workspace["selection_mode"] == "auto":
        selected = strategy["metadata"]["opportunity_scoring"]["designer_top3_ids"]
        primary = None
    else:
        selected = workspace["selected_opportunity_ids"]
        primary = workspace["primary_opportunity_id"]
    edits = workspace.get("opportunity_edits", {})
    handoff = strategy["handoff_to_designer"]
    handoff["priority_opportunities"] = [
        _priority_payload(items[item_id], index, edits.get(item_id, {}))
        for index, item_id in enumerate(selected, 1)
    ]
    manual_brief = str(workspace.get("manual_brief", "")).strip()
    if manual_brief:
        chosen = "、".join(items[item_id]["culture_element"] for item_id in selected)
        brief = (
            f"本轮由用户人工选择{chosen}作为设计方向。{manual_brief}"
            "设计必须保留原文化和市场证据编号，不复制馆藏完整纹样，"
            "不虚构授权、传承人联名、工艺、材料或量产就绪状态。"
        )
        if len(brief) < 150:
            brief += "所有尺寸、BOM、装配和质检要求均只是首样假设，进入工厂前需重新核对。"
        handoff["creative_brief"] = brief[:350]
    DesignerHandoff.model_validate(handoff)
    _atomic_json(path, handoff)
    return primary, path


def _apply_design_overrides(
    package: DesignPackage, overrides: dict[str, Any]
) -> DesignPackage:
    string_fields = {
        "product_name": "product_name",
        "product_type": "product_type",
        "target_audience": "target_audience",
        "concept_statement": "concept_statement",
        "form_description": "form_description",
    }
    changed: list[str] = []
    for source_key, target_key in string_fields.items():
        value = str(overrides.get(source_key, "")).strip()
        if value:
            setattr(package.product, target_key, value)
            changed.append(source_key)
    for key in ("use_scenarios", "interaction", "visual_style", "color_direction"):
        value = overrides.get(key)
        if isinstance(value, list) and value:
            setattr(package.product, key, [str(item).strip() for item in value if str(item).strip()])
            changed.append(key)
    if overrides.get("poster_title"):
        package.poster_request.exact_copy["title"] = str(overrides["poster_title"]).strip()
        changed.append("poster_title")
    elif overrides.get("product_name"):
        package.poster_request.exact_copy["title"] = package.product.product_name.split("｜")[0]
    if overrides.get("poster_subtitle"):
        package.poster_request.exact_copy["subtitle"] = str(
            overrides["poster_subtitle"]
        ).strip()
        changed.append("poster_subtitle")
    if changed:
        package.validation.checks.append(
            "本次应用用户手动编辑字段：" + "、".join(changed) + "。"
        )
    return DesignPackage.model_validate(package.model_dump(mode="json"))


def generate_design() -> dict[str, Any]:
    if not DESIGN_LOCK.acquire(blocking=False):
        raise RuntimeError("已有设计生成任务在运行")
    try:
        workspace = load_workspace()
        started = datetime.now(UTC)
        run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-design"
        run_dir = TOOL_RUNS_DIR / run_id
        handoff_path = run_dir / "designer_handoff_draft.json"
        primary_id, _ = _build_handoff_draft(workspace, handoff_path)
        package, design_status = DesignAgent(load_settings()).create_from_file(
            handoff_path,
            primary_opportunity_id=primary_id,
        )
        package = _apply_design_overrides(package, workspace.get("design_overrides", {}))
        specification_path = run_dir / "design_specification.json"
        markdown_path = run_dir / "design_specification.md"
        poster_request_path = run_dir / "poster_render_request.json"
        poster_path = run_dir / "design_poster.png"
        render_manifest_path = run_dir / "design_render_manifest.json"
        _atomic_json(specification_path, package.model_dump(mode="json"))
        markdown_path.write_text(
            render_design_package_markdown(package), encoding="utf-8", newline="\n"
        )
        _atomic_json(
            poster_request_path,
            package.poster_request.model_dump(mode="json"),
        )
        render_manifest, render_status = render_design_poster(
            package,
            poster_path,
            generated_now=True,
        )
        _atomic_json(render_manifest_path, render_manifest.model_dump(mode="json"))
        result = {
            "run_id": run_id,
            "started_at": started.isoformat(),
            "finished_at": datetime.now(UTC).isoformat(),
            "selection_mode": workspace["selection_mode"],
            "selected_opportunity_ids": package.input_contract.selected_opportunity_ids,
            "primary_opportunity_id": package.selection.primary_opportunity_id,
            "source_handoff_sha256": package.input_contract.source_sha256,
            "design_id": package.design_id,
            "design_engine": design_status.engine,
            "render_engine": render_status.engine,
            "render_kind": "deterministic_local_structure_render",
            "image_generation_used": False,
            "reference_only_images_used": False,
            "product_name": package.product.product_name,
            "paths": {
                "handoff": str(handoff_path.relative_to(ROOT_DIR)),
                "specification": str(specification_path.relative_to(ROOT_DIR)),
                "poster": str(poster_path.relative_to(ROOT_DIR)),
                "render_manifest": str(render_manifest_path.relative_to(ROOT_DIR)),
            },
        }
        _atomic_json(run_dir / "tool_run.json", result)
        workspace["last_design_run_id"] = run_id
        save_workspace(workspace)
        return {**result, "design": package.model_dump(mode="json")}
    finally:
        DESIGN_LOCK.release()


def _workbench_design_selection(workspace: dict[str, Any]) -> dict[str, Any]:
    metadata = workspace.get("metadata", {})
    profile = metadata.get("decision_profile", {})
    selected = [str(item) for item in profile.get("opportunityIds", [])][:3]
    if not selected:
        raise ValueError("请先在人工决策中选择 1 到 3 条机会。")
    manual_rows = metadata.get("decision_output", {}).get("manualRanking", [])
    ranked_selected = [
        str(item.get("id", ""))
        for item in manual_rows
        if item.get("selected") and item.get("id") in selected
    ]
    primary = ranked_selected[0] if ranked_selected else selected[0]
    brief_node = next(
        (node for node in workspace["nodes"] if node["type"] == "DesignBriefNode"),
        None,
    )
    poster_node = next(
        (node for node in workspace["nodes"] if node["type"] == "PosterBoardNode"),
        None,
    )
    brief = brief_node.get("data", {}).get("brief", {}) if brief_node else {}
    poster = poster_node.get("data", {}).get("poster", {}) if poster_node else {}
    intent = profile.get("designIntent", {})
    manual_brief = " ".join(
        str(value).strip()
        for value in (
            brief.get("objective", ""),
            f"目标人群：{brief.get('audience', '')}" if brief.get("audience") else "",
            f"产品形态：{brief.get('productType', '')}" if brief.get("productType") else "",
            f"使用场景：{'、'.join(brief.get('scenarios', []))}"
            if brief.get("scenarios")
            else "",
        )
        if str(value).strip()
    )
    return {
        "selection_mode": "manual",
        "selected_opportunity_ids": selected,
        "primary_opportunity_id": primary,
        "opportunity_edits": {},
        "manual_brief": manual_brief,
        "design_overrides": {
            "product_name": str(brief.get("title", "")).strip(),
            "product_type": str(brief.get("productType", "")).strip(),
            "target_audience": str(brief.get("audience", "")).strip(),
            "use_scenarios": brief.get("scenarios", []),
            "visual_style": brief.get("style", []),
            "color_direction": profile.get("visualDirection", {}).get(
                "styleKeywords", []
            ),
            "poster_title": str(poster.get("title", "")).strip(),
            "poster_subtitle": str(poster.get("subtitle", "")).strip(),
            "interaction": intent.get("useScenarios", []),
        },
    }


def _workbench_concept_hero(workspace: dict[str, Any]) -> Path | None:
    active = next(
        (
            node
            for node in workspace["nodes"]
            if node["type"] == "ConceptNode" and node["data"].get("active")
        ),
        None,
    )
    image_url = str(active.get("data", {}).get("imageUrl", "")) if active else ""
    prefix = f"/assets/workbench/{workspace['workspace_id']}/"
    if not image_url.startswith(prefix):
        return None
    filename = image_url.removeprefix(prefix)
    if not filename or Path(filename).name != filename:
        return None
    candidates = (
        GENERATED_DIR / workspace["workspace_id"] / filename,
        BUNDLED_GENERATED_DIR / workspace["workspace_id"] / filename,
    )
    return next((path for path in candidates if path.is_file()), None)


def generate_workbench_design(workspace_id: str) -> dict[str, Any]:
    if not DESIGN_LOCK.acquire(blocking=False):
        raise RuntimeError("已有设计生成任务在运行")
    try:
        workspace = load_workbench_workspace(workspace_id)
        selection = _workbench_design_selection(workspace)
        started = datetime.now(UTC)
        run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
        run_dir = DESIGN_RUNS_DIR / workspace_id / run_id
        handoff_path = run_dir / "designer_handoff_draft.json"
        primary_id, _ = _build_handoff_draft(
            selection,
            handoff_path,
            workspace_strategy_path(workspace),
        )
        package, design_status = DesignAgent(load_settings()).create_from_file(
            handoff_path,
            primary_opportunity_id=primary_id,
        )
        package = _apply_design_overrides(
            package,
            selection.get("design_overrides", {}),
        )
        specification_path = run_dir / "design_specification.json"
        markdown_path = run_dir / "design_specification.md"
        poster_request_path = run_dir / "poster_render_request.json"
        poster_path = run_dir / "design_poster.png"
        render_manifest_path = run_dir / "design_render_manifest.json"
        _atomic_json(specification_path, package.model_dump(mode="json"))
        markdown_path.write_text(
            render_design_package_markdown(package), encoding="utf-8", newline="\n"
        )
        _atomic_json(poster_request_path, package.poster_request.model_dump(mode="json"))
        render_manifest, render_status = render_design_poster(
            package,
            poster_path,
            _workbench_concept_hero(workspace),
            generated_now=True,
        )
        _atomic_json(render_manifest_path, render_manifest.model_dump(mode="json"))
        finished = datetime.now(UTC)
        result = {
            "run_id": run_id,
            "workspace_id": workspace_id,
            "status": "design_generated",
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "primary_opportunity_id": package.selection.primary_opportunity_id,
            "selected_opportunity_ids": package.input_contract.selected_opportunity_ids,
            "source_handoff_sha256": package.input_contract.source_sha256,
            "design_id": package.design_id,
            "design_engine": design_status.engine,
            "render_engine": render_status.engine,
            "image_generation_used": False,
            "reference_only_images_used": False,
            "paths": {
                "handoff": handoff_path.name,
                "specification": specification_path.name,
                "poster": poster_path.name,
                "render_manifest": render_manifest_path.name,
            },
        }
        _atomic_json(run_dir / "tool_run.json", result)

        workspace["metadata"].update(
            {
                "design_run_id": run_id,
                "design_generated_at": finished.isoformat(),
                "design_primary_opportunity_id": package.selection.primary_opportunity_id,
            }
        )
        for node in workspace["nodes"]:
            if node["type"] == "DesignBriefNode":
                node["data"]["status"] = "success"
                node["data"].setdefault("history", []).insert(
                    0,
                    {
                        "at": finished.isoformat(),
                        "event": f"Design Agent 真实生成 {run_id}",
                    },
                )
            elif node["type"] == "VisualGenerationNode":
                node["data"]["status"] = "stale"
            elif node["type"] == "ConceptNode":
                node["data"]["status"] = "stale"
            elif node["type"] == "PosterBoardNode":
                node["data"].update(
                    {
                        "status": "success",
                        "version": int(node["data"].get("version", 0)) + 1,
                        "imageUrl": (
                            f"/assets/workbench-design/{workspace_id}/{run_id}/"
                            "design_poster.png"
                        ),
                        "generation": {
                            "engine": render_status.engine,
                            "mode": render_status.mode,
                            "runId": run_id,
                        },
                    }
                )
                node["data"].setdefault("history", []).insert(
                    0,
                    {
                        "at": finished.isoformat(),
                        "event": f"从当前人工决策生成海报 {run_id}",
                    },
                )
        return save_workbench_workspace(workspace_id, workspace)
    finally:
        DESIGN_LOCK.release()


def design_state() -> dict[str, Any]:
    official = _load_json(DESIGN_PATH)
    workspace = load_workspace()
    runs = []
    if TOOL_RUNS_DIR.exists():
        for path in sorted(TOOL_RUNS_DIR.glob("*/tool_run.json"), reverse=True):
            try:
                runs.append(_load_json(path))
            except (OSError, ValueError):
                continue
    selected = official
    selected_run = "official"
    if workspace.get("last_design_run_id"):
        candidate = TOOL_RUNS_DIR / workspace["last_design_run_id"] / "design_specification.json"
        if candidate.exists():
            selected = _load_json(candidate)
            selected_run = workspace["last_design_run_id"]
    return {
        "selected_run_id": selected_run,
        "design": selected,
        "runs": runs,
        "poster_url": (
            "/assets/official/design-poster.png"
            if selected_run == "official"
            else f"/assets/design-runs/{selected_run}/design-poster.png"
        ),
        "image_generation": {
            "available": False,
            "reason": "未接入可由本地网页调用的图像生成服务；不会伪装成已生成。",
        },
    }


def run_strict_research(
    workspace_id: str = "guizhou-miao-demo",
    *,
    allow_interactive: bool = False,
) -> dict[str, Any]:
    if not RESEARCH_LOCK.acquire(blocking=False):
        raise RuntimeError("已有实时研究任务在运行")
    try:
        preflight = _strict_preflight(allow_interactive=allow_interactive)
        if not preflight["research_ready"]:
            raise ValueError("严格实时研究未就绪：" + "；".join(preflight["blockers"]))
        started = datetime.now(UTC)
        run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-research"
        run_dir = RESEARCH_RUNS_DIR / run_id
        base_settings = load_settings().with_mode("live")
        settings = replace(
            base_settings,
            outputs_dir=run_dir / "outputs",
            demo_cache_dir=run_dir / "no_fallback_cache",
            market_raw_dir=run_dir / "market" / "raw",
            market_derived_dir=run_dir / "market" / "derived",
            mediacrawler_live_enabled=(
                True if allow_interactive else base_settings.mediacrawler_live_enabled
            ),
            mediacrawler_interactive_login=(
                True if allow_interactive else base_settings.mediacrawler_interactive_login
            ),
            mediacrawler_cdp_connect_existing=(
                False if allow_interactive else base_settings.mediacrawler_cdp_connect_existing
            ),
        )
        request = DemoRequest()
        _, manifest = asyncio.run(
            run_pipeline(request, settings, include_design=False)
        )
        required = {"culture_knowledge", "market_research", "strategist"}
        component_modes = {
            item.component: item.mode for item in manifest.components if item.component in required
        }
        platform_modes = {
            code: status.status for code, status in manifest.market_platforms.items()
        }
        if set(component_modes.values()) != {"live"} or any(
            mode != "live" for mode in platform_modes.values()
        ):
            failure = {
                "run_id": run_id,
                "workspace_id": workspace_id,
                "status": "failed_no_fallback",
                "component_modes": component_modes,
                "platform_modes": platform_modes,
                "detail": "实时组件未全部成功，本轮不晋级为可用结果。",
            }
            _atomic_json(run_dir / "strict_result.json", failure)
            return failure
        promoted = promote_research_run(
            workspace_id,
            run_dir,
            manifest.model_dump(mode="json"),
        )
        success = {
            "run_id": run_id,
            "source_run_id": manifest.run_id,
            "workspace_id": workspace_id,
            "status": "live_verified",
            "component_modes": component_modes,
            "platform_modes": platform_modes,
            "output_count": len(manifest.outputs),
            "workspace_updated_at": promoted["updated_at"],
            "detail": "文化、四平台、策划均为本轮 live；结果已回写到当前工作区。",
        }
        _atomic_json(run_dir / "strict_result.json", success)
        return success
    finally:
        RESEARCH_LOCK.release()


def _research_job_path(job_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9-]{1,96}", job_id):
        raise ValueError("研究任务编号无效。")
    return RESEARCH_RUNS_DIR / job_id / "job.json"


def _save_research_job(job: dict[str, Any]) -> dict[str, Any]:
    _atomic_json(_research_job_path(str(job["job_id"])), job)
    return job


def _load_research_job(job_id: str) -> dict[str, Any]:
    path = _research_job_path(job_id)
    if not path.is_file():
        raise FileNotFoundError(f"研究任务不存在：{job_id}")
    return _load_json(path)


def _latest_research_job(workspace_id: str) -> dict[str, Any] | None:
    jobs: list[dict[str, Any]] = []
    if not RESEARCH_RUNS_DIR.exists():
        return None
    for path in RESEARCH_RUNS_DIR.glob("*/job.json"):
        try:
            job = _load_json(path)
        except (OSError, ValueError):
            continue
        if job.get("workspace_id") == workspace_id:
            jobs.append(job)
    return max(jobs, key=lambda item: str(item.get("created_at", "")), default=None)


def research_runtime_status(
    workspace_id: str,
    *,
    allow_interactive: bool = False,
) -> dict[str, Any]:
    with RESEARCH_JOB_STATE_LOCK:
        active_job_id = ACTIVE_RESEARCH_JOB_ID
    active = None
    if active_job_id:
        try:
            active = _load_research_job(active_job_id)
        except FileNotFoundError:
            active = None
    last = _latest_research_job(workspace_id)
    if active is None and last and last.get("status") in {"queued", "running"}:
        last.update(
            {
                "status": "error",
                "stage": "interrupted",
                "finished_at": datetime.now(UTC).isoformat(),
                "detail": "API 进程在任务完成前重启；该轮没有晋级，也没有回写旧结果。",
            }
        )
        _save_research_job(last)
    return {
        "preflight": _strict_preflight(allow_interactive=allow_interactive),
        "activeJob": active,
        "lastJob": last,
    }


def _research_job_worker(
    job_id: str,
    workspace_id: str,
    allow_interactive: bool,
) -> None:
    global ACTIVE_RESEARCH_JOB_ID
    job = _load_research_job(job_id)
    job.update(
        {
            "status": "running",
            "stage": "culture_market_strategy",
            "started_at": datetime.now(UTC).isoformat(),
            "detail": "正在执行知识检索、四平台采集和模型策划。",
        }
    )
    _save_research_job(job)
    try:
        result = run_strict_research(
            workspace_id,
            allow_interactive=allow_interactive,
        )
        job.update(
            {
                **result,
                "job_id": job_id,
                "status": result["status"],
                "stage": "complete",
                "finished_at": datetime.now(UTC).isoformat(),
            }
        )
    except Exception as exc:  # noqa: BLE001 - persisted as an explicit failed job
        public_error = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(exc))[:1600]
        job.update(
            {
                "status": "error",
                "stage": "failed",
                "finished_at": datetime.now(UTC).isoformat(),
                "detail": public_error,
            }
        )
    finally:
        _save_research_job(job)
        with RESEARCH_JOB_STATE_LOCK:
            if ACTIVE_RESEARCH_JOB_ID == job_id:
                ACTIVE_RESEARCH_JOB_ID = ""


def start_research_job(candidate: dict[str, Any]) -> dict[str, Any]:
    global ACTIVE_RESEARCH_JOB_ID
    workspace_id = str(candidate.get("workspace_id", "guizhou-miao-demo"))
    load_workbench_workspace(workspace_id)
    allow_interactive = bool(candidate.get("allow_interactive", False))
    preflight = _strict_preflight(allow_interactive=allow_interactive)
    if not preflight["research_ready"]:
        raise ValueError("严格实时研究未就绪：" + "；".join(preflight["blockers"]))
    with RESEARCH_JOB_STATE_LOCK:
        if ACTIVE_RESEARCH_JOB_ID:
            raise RuntimeError(f"已有实时研究任务在运行：{ACTIVE_RESEARCH_JOB_ID}")
        now = datetime.now(UTC)
        job_id = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
        ACTIVE_RESEARCH_JOB_ID = job_id
    job = {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "status": "queued",
        "stage": "queued",
        "created_at": now.isoformat(),
        "started_at": "",
        "finished_at": "",
        "allow_interactive": allow_interactive,
        "detail": "任务已进入真实运行队列。",
        "component_modes": {},
        "platform_modes": {},
    }
    _save_research_job(job)
    worker = threading.Thread(
        target=_research_job_worker,
        args=(job_id, workspace_id, allow_interactive),
        daemon=True,
        name=f"qiancraft-research-{job_id}",
    )
    worker.start()
    return job


class ToolRequestHandler(BaseHTTPRequestHandler):
    server_version = "QianCraftTool/0.2"

    def _cors(self) -> None:
        origin = self.headers.get("Origin", "")
        allowed_origins = {
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        self.send_header(
            "Access-Control-Allow-Origin",
            origin if origin in allowed_origins else "http://localhost:3000",
        )
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict[str, Any]:
        length = min(int(self.headers.get("Content-Length", "0")), 1_000_000)
        if not length:
            return {}
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("request body must be a JSON object")
        return payload

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/summary":
                self._send_json(audit_summary())
            elif parsed.path == "/api/culture":
                self._send_json(culture_records())
            elif parsed.path == "/api/market":
                self._send_json(market_records(parse_qs(parsed.query)))
            elif parsed.path == "/api/opportunities":
                self._send_json(opportunities())
            elif parsed.path == "/api/workspace":
                self._send_json(load_workspace())
            elif parsed.path == "/api/design":
                self._send_json(design_state())
            elif parsed.path == "/api/research/status":
                params = parse_qs(parsed.query)
                workspace_id = params.get("workspace_id", ["guizhou-miao-demo"])[0]
                allow_interactive = params.get("allow_interactive", ["false"])[0].lower() in {
                    "1",
                    "true",
                    "yes",
                }
                self._send_json(
                    research_runtime_status(
                        workspace_id,
                        allow_interactive=allow_interactive,
                    )
                )
            elif parsed.path.startswith("/api/research/jobs/"):
                job_id = parsed.path.removeprefix("/api/research/jobs/")
                self._send_json(_load_research_job(job_id))
            elif parsed.path == "/api/workbench/bootstrap":
                workspace_id = parse_qs(parsed.query).get(
                    "workspace_id", ["guizhou-miao-demo"]
                )[0]
                payload = workbench_bootstrap(workspace_id)
                payload["researchRuntime"] = research_runtime_status(
                    workspace_id,
                    allow_interactive=True,
                )
                self._send_json(payload)
            elif parsed.path == "/api/workbench/workspaces":
                self._send_json({"workspaces": list_workbench_workspaces()})
            elif parsed.path == "/api/workbench/image-provider":
                self._send_json(image_provider_status())
            elif parsed.path.startswith("/api/workbench/workspaces/"):
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) == 4:
                    self._send_json(load_workbench_workspace(parts[3]))
                elif len(parts) == 5 and parts[4] == "design-package":
                    self._send_json(workbench_design_package(parts[3]))
                elif (
                    len(parts) == 7
                    and parts[4] == "nodes"
                    and parts[6] == "detail"
                ):
                    self._send_json(node_detail(parts[3], parts[5]))
                else:
                    self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            elif parsed.path == "/api/health":
                self._send_json({"ok": True, "root": str(ROOT_DIR)})
            elif parsed.path.startswith("/assets/"):
                self._send_asset(parsed.path)
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except FileNotFoundError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001 - API converts failures to explicit JSON
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/workspace":
                self._send_json(save_workspace(self._read_json()))
            elif parsed.path.startswith("/api/workbench/workspaces/"):
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) == 4:
                    self._send_json(save_workbench_workspace(parts[3], self._read_json()))
                else:
                    self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except (TypeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.UNPROCESSABLE_ENTITY)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/design/generate":
                self._send_json(generate_design(), HTTPStatus.CREATED)
            elif parsed.path == "/api/research/run":
                self._send_json(start_research_job(self._read_json()), HTTPStatus.ACCEPTED)
            elif parsed.path == "/api/workbench/workspaces":
                self._send_json(
                    create_workbench_workspace(self._read_json()), HTTPStatus.CREATED
                )
            elif parsed.path.startswith("/api/workbench/workspaces/"):
                parts = [part for part in parsed.path.split("/") if part]
                body = self._read_json()
                if len(parts) == 5 and parts[4] == "decisions":
                    self._send_json(
                        update_decision_profile(
                            parts[3], body.get("decision_profile", body)
                        )
                    )
                elif len(parts) == 5 and parts[4] == "brief":
                    self._send_json(update_design_brief(parts[3], body.get("brief", {})))
                elif len(parts) == 6 and parts[4:] == ["design", "run"]:
                    self._send_json(generate_workbench_design(parts[3]), HTTPStatus.CREATED)
                elif len(parts) == 5 and parts[4] == "active-concept":
                    self._send_json(
                        set_active_concept(parts[3], str(body.get("concept_id", "")))
                    )
                elif len(parts) == 7 and parts[4] == "nodes" and parts[6] == "run":
                    self._send_json(run_workbench_node(parts[3], parts[5]))
                elif (
                    len(parts) == 7
                    and parts[4] == "concepts"
                    and parts[6] == "duplicate"
                ):
                    self._send_json(duplicate_concept(parts[3], parts[5]))
                elif (
                    len(parts) == 7
                    and parts[4] == "concepts"
                    and parts[6] == "regenerate"
                ):
                    self._send_json(regenerate_concept(parts[3], parts[5]))
                elif (
                    len(parts) == 7
                    and parts[4] == "concepts"
                    and parts[6] == "generate-more"
                ):
                    self._send_json(generate_more_concept(parts[3], parts[5]))
                else:
                    self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            elif parsed.path == "/api/design/image":
                provider = image_provider_status()
                self._send_json(
                    {
                        "error": (
                            "图像服务已配置；请通过 VisualGenerationNode 运行 A/B/C。"
                            if provider["configured"]
                            else provider["detail"]
                        ),
                        "provider": provider,
                    },
                    (
                        HTTPStatus.UNPROCESSABLE_ENTITY
                        if provider["configured"]
                        else HTTPStatus.NOT_IMPLEMENTED
                    ),
                )
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except (TypeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.UNPROCESSABLE_ENTITY)
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.CONFLICT)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _send_asset(self, url_path: str) -> None:
        parts = [part for part in url_path.split("/") if part]
        path: Path | None = None
        if parts == ["assets", "official", "design-poster.png"]:
            path = ROOT_DIR / "data" / "outputs" / "design_poster.png"
        elif parts == ["assets", "official", "product-hero.png"]:
            path = ROOT_DIR / "data" / "design" / "assets" / "huaxi_grid_magnet_hero_v1.png"
        elif len(parts) == 4 and parts[:2] == ["assets", "design-runs"]:
            run_id, filename = parts[2], parts[3]
            if run_id.replace("-", "").isalnum() and filename == "design-poster.png":
                path = TOOL_RUNS_DIR / run_id / filename
        elif len(parts) == 4 and parts[:2] == ["assets", "workbench"]:
            workspace_id, filename = parts[2], parts[3]
            safe_workspace = workspace_id.replace("-", "").isalnum()
            safe_filename = (
                filename.endswith(".png")
                and filename.replace("-", "").replace(".", "").isalnum()
            )
            if safe_workspace and safe_filename:
                candidates = (
                    GENERATED_DIR / workspace_id / filename,
                    BUNDLED_GENERATED_DIR / workspace_id / filename,
                )
                path = next(
                    (candidate for candidate in candidates if candidate.is_file()),
                    None,
                )
        elif len(parts) == 5 and parts[:2] == ["assets", "workbench-design"]:
            workspace_id, run_id, filename = parts[2], parts[3], parts[4]
            safe_workspace = workspace_id.replace("-", "").isalnum()
            safe_run = run_id.replace("-", "").isalnum()
            if (
                safe_workspace
                and safe_run
                and filename in {"design_poster.png"}
            ):
                path = DESIGN_RUNS_DIR / workspace_id / run_id / filename
        if path is None or not path.is_file():
            self._send_json({"error": "asset not found"}, HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self._cors()
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[tool-api] {self.address_string()} - {format % args}")


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    server = ThreadingHTTPServer((host, port), ToolRequestHandler)
    print(f"QianCraft Tool API: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local QianCraft tool API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
