from __future__ import annotations

import argparse
import asyncio
import json
import os
import threading
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from app.config import MARKET_PLATFORM_CODES, load_settings
from app.designer import DesignAgent, render_design_package_markdown, render_design_poster
from app.pipeline import run_pipeline
from app.schemas import DemoRequest, DesignPackage, DesignerHandoff

ROOT_DIR = Path(__file__).resolve().parents[1]
CULTURE_PATH = ROOT_DIR / "data" / "culture" / "knowledge_graph.json"
MARKET_VERIFIED_PATH = ROOT_DIR / "data" / "market" / "verified_signals.json"
MARKET_DERIVED_DIR = ROOT_DIR / "data" / "market" / "derived"
STRATEGY_PATH = ROOT_DIR / "data" / "outputs" / "pre_design_strategy.json"
HANDOFF_PATH = ROOT_DIR / "data" / "outputs" / "designer_handoff.json"
DESIGN_PATH = ROOT_DIR / "data" / "outputs" / "design_specification.json"
RUN_MANIFEST_PATH = ROOT_DIR / "data" / "outputs" / "run_manifest.json"
WORKSPACE_DIR = ROOT_DIR / "data" / "tool_workspace"
WORKSPACE_PATH = WORKSPACE_DIR / "workspace.json"
TOOL_RUNS_DIR = WORKSPACE_DIR / "design_runs"
RESEARCH_RUNS_DIR = WORKSPACE_DIR / "research_runs"

DESIGN_LOCK = threading.Lock()
RESEARCH_LOCK = threading.Lock()


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
    _, path, payload, counts = max(candidates, key=lambda item: item[0])
    return path, payload, counts


def _strict_preflight() -> dict[str, Any]:
    settings = load_settings()
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
            "ok": settings.mediacrawler_live_enabled,
            "detail": (
                "已启用"
                if settings.mediacrawler_live_enabled
                else "MEDIACRAWLER_LIVE_ENABLED=false"
            ),
        },
        {
            "id": "crawler_runtime",
            "label": "市场采集运行时",
            "ok": settings.mediacrawler_python.exists(),
            "detail": (
                "可用"
                if settings.mediacrawler_python.exists()
                else "MediaCrawler 独立 Python 环境不存在"
            ),
        },
        {
            "id": "lightrag",
            "label": "文化检索运行时",
            "ok": settings.lightrag_path.exists(),
            "detail": "源码可用" if settings.lightrag_path.exists() else "LightRAG 路径不存在",
        },
        {
            "id": "image_provider",
            "label": "主视觉生成服务",
            "ok": False,
            "detail": "当前仓库未接入可由网页调用的图像生成服务",
        },
    ]
    blockers = [item["detail"] for item in checks[:4] if not item["ok"]]
    return {
        "research_ready": not blockers,
        "image_generation_ready": False,
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
                "raw_files_present": raw_dir.exists(),
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
        if key in edits and edits[key]:
            payload[key] = edits[key]
    return payload


def _build_handoff_draft(workspace: dict[str, Any], path: Path) -> tuple[str | None, Path]:
    strategy = _load_json(STRATEGY_PATH)
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


def run_strict_research() -> dict[str, Any]:
    if not RESEARCH_LOCK.acquire(blocking=False):
        raise RuntimeError("已有实时研究任务在运行")
    try:
        preflight = _strict_preflight()
        if not preflight["research_ready"]:
            raise ValueError("严格实时研究未就绪：" + "；".join(preflight["blockers"]))
        started = datetime.now(UTC)
        run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-research"
        run_dir = RESEARCH_RUNS_DIR / run_id
        settings = replace(
            load_settings().with_mode("live"),
            outputs_dir=run_dir / "outputs",
            demo_cache_dir=run_dir / "no_fallback_cache",
        )
        request = DemoRequest()
        _, manifest = asyncio.run(run_pipeline(request, settings))
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
                "status": "failed_no_fallback",
                "component_modes": component_modes,
                "platform_modes": platform_modes,
                "detail": "实时组件未全部成功，本轮不晋级为可用结果。",
            }
            _atomic_json(run_dir / "strict_result.json", failure)
            return failure
        success = {
            "run_id": run_id,
            "status": "live_verified",
            "component_modes": component_modes,
            "platform_modes": platform_modes,
            "manifest": manifest.model_dump(mode="json"),
        }
        _atomic_json(run_dir / "strict_result.json", success)
        return success
    finally:
        RESEARCH_LOCK.release()


class ToolRequestHandler(BaseHTTPRequestHandler):
    server_version = "QianCraftTool/0.1"

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "http://localhost:3000")
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
            raise ValueError("request body must be a JSON object")
        return payload

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
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
            elif parsed.path == "/api/health":
                self._send_json({"ok": True, "root": str(ROOT_DIR)})
            elif parsed.path.startswith("/assets/"):
                self._send_asset(parsed.path)
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001 - API converts failures to explicit JSON
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_PUT(self) -> None:  # noqa: N802
        try:
            if self.path == "/api/workspace":
                self._send_json(save_workspace(self._read_json()))
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.UNPROCESSABLE_ENTITY)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/api/design/generate":
                self._send_json(generate_design(), HTTPStatus.CREATED)
            elif self.path == "/api/research/run":
                self._send_json(run_strict_research(), HTTPStatus.CREATED)
            elif self.path == "/api/design/image":
                self._send_json(
                    {
                        "error": "未接入真实图像生成服务，请先配置 provider。"
                    },
                    HTTPStatus.NOT_IMPLEMENTED,
                )
            else:
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
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
