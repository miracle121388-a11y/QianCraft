from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import uuid
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.adapters.image_generation_adapter import ImageGenerationAdapter
from app.designer import render_design_poster
from app.schemas import DesignPackage

ROOT_DIR = Path(__file__).resolve().parents[1]
BUNDLED_WORKBENCH_DIR = ROOT_DIR / "data" / "workbench"
WORKBENCH_DIR = (
    Path(
        os.environ.get(
            "QIANCRAFT_WORKBENCH_DIR",
            str(ROOT_DIR / "data" / "runtime" / "workbench"),
        )
    )
    .expanduser()
    .resolve()
)
BUNDLED_WORKSPACES_DIR = BUNDLED_WORKBENCH_DIR / "workspaces"
BUNDLED_GENERATED_DIR = BUNDLED_WORKBENCH_DIR / "generated"
WORKSPACES_DIR = WORKBENCH_DIR / "workspaces"
GENERATED_DIR = WORKBENCH_DIR / "generated"
RESEARCH_DIR = WORKBENCH_DIR / "research"
DESIGN_RUNS_DIR = WORKBENCH_DIR / "design_runs"
DEFAULT_WORKSPACE_ID = "guizhou-miao-demo"

NODE_TYPES = (
    "CultureGraphNode",
    "MarketRadarNode",
    "StrategyNode",
    "DesignBriefNode",
    "VisualGenerationNode",
    "ConceptNode",
    "PosterBoardNode",
)
NODE_STATUSES = ("idle", "running", "success", "warning", "error", "cached", "stale")
POSTER_SECTIONS = ("hero", "culture", "breakdown", "bom", "process")
DECISION_MODES = ("guided", "manual")
MARKET_PLATFORMS = ("xhs", "dy", "bili", "wb")
SCORE_FIELDS = (
    "culture_fit",
    "market_pull",
    "novelty",
    "visual_potential",
    "social_shareability",
    "product_feasibility",
)
DEFAULT_SCORE_WEIGHTS = {
    "culture_fit": 0.20,
    "market_pull": 0.20,
    "novelty": 0.20,
    "visual_potential": 0.15,
    "social_shareability": 0.15,
    "product_feasibility": 0.10,
}
POSTER_THEMES = ("editorial", "workshop", "exhibition")
VISUAL_SIZES = ("1024x1024", "1536x1024", "1024x1536")
_WORKSPACE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9TZ-]{0,95}$")

CULTURE_PATH = ROOT_DIR / "data" / "culture" / "knowledge_graph.json"
HOTNESS_PATH = ROOT_DIR / "data" / "market" / "derived" / "product_form_hotness.json"
MARKET_VERIFIED_PATH = ROOT_DIR / "data" / "market" / "verified_signals.json"
STRATEGY_PATH = ROOT_DIR / "data" / "outputs" / "pre_design_strategy.json"
DESIGN_PATH = ROOT_DIR / "data" / "outputs" / "design_specification.json"
MANIFEST_PATH = ROOT_DIR / "data" / "outputs" / "run_manifest.json"
VISUAL_REFERENCES_PATH = ROOT_DIR / "data" / "culture" / "visual_references.json"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bundled_concept_asset(filename: str) -> dict[str, Any] | None:
    candidates = (
        GENERATED_DIR / DEFAULT_WORKSPACE_ID / filename,
        BUNDLED_GENERATED_DIR / DEFAULT_WORKSPACE_ID / filename,
    )
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return None
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "imageUrl": f"/assets/workbench/{DEFAULT_WORKSPACE_ID}/{filename}",
        "version": 1,
        "status": "success",
        "generation": {
            "provider": "codex_builtin_imagegen",
            "mode": "project_asset",
            "sha256": digest,
        },
    }


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _workspace_path(workspace_id: str) -> Path:
    if not _WORKSPACE_ID.fullmatch(workspace_id):
        raise ValueError("workspace_id 只能包含小写字母、数字和短横线。")
    return WORKSPACES_DIR / f"{workspace_id}.json"


def _research_artifact_path(
    workspace: dict[str, Any],
    filename: str,
    fallback: Path,
) -> Path:
    run_id = str(workspace.get("metadata", {}).get("research_run_id", ""))
    workspace_id = str(workspace.get("workspace_id", ""))
    if not _WORKSPACE_ID.fullmatch(workspace_id) or not _RUN_ID.fullmatch(run_id):
        return fallback
    candidate = RESEARCH_DIR / workspace_id / run_id / filename
    return candidate if candidate.is_file() else fallback


def workspace_strategy_path(workspace: dict[str, Any]) -> Path:
    """Return the promoted strategy for this workspace, never a client-supplied path."""

    return _research_artifact_path(
        workspace,
        "pre_design_strategy.json",
        STRATEGY_PATH,
    )


def _workspace_hotness_path(workspace: dict[str, Any]) -> Path:
    return _research_artifact_path(
        workspace,
        "product_form_hotness.json",
        HOTNESS_PATH,
    )


def _workspace_manifest_path(workspace: dict[str, Any]) -> Path:
    return _research_artifact_path(workspace, "run_manifest.json", MANIFEST_PATH)


def _manifest_artifact_path(value: object) -> Path:
    raw = str(value or "")
    if not raw:
        return ROOT_DIR / ".missing-manifest-artifact"
    path = Path(raw)
    return path if path.is_absolute() else ROOT_DIR / path


def _workspace_design_path(workspace: dict[str, Any]) -> Path:
    run_id = str(workspace.get("metadata", {}).get("design_run_id", ""))
    workspace_id = str(workspace.get("workspace_id", ""))
    if _WORKSPACE_ID.fullmatch(workspace_id) and _RUN_ID.fullmatch(run_id):
        candidate = DESIGN_RUNS_DIR / workspace_id / run_id / "design_specification.json"
        if candidate.is_file():
            return candidate
    return _research_artifact_path(
        workspace,
        "design_specification.json",
        DESIGN_PATH,
    )


def _node(
    node_id: str,
    node_type: str,
    x: float,
    y: float,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "position": {"x": x, "y": y},
        "data": data,
    }


def _edge(edge_id: str, source: str, target: str, relation: str) -> dict[str, Any]:
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "type": "smoothstep",
        "data": {"relation": relation},
    }


def _default_brief(design: dict[str, Any]) -> dict[str, Any]:
    product = design.get("product", {})
    manufacturing = design.get("manufacturing", {})
    return {
        "title": product.get("product_name", "贵州文化文创概念"),
        "objective": product.get("concept_statement", ""),
        "audience": product.get("target_audience", "18-30岁年轻消费者"),
        "productType": product.get("product_type", "文创产品"),
        "scenarios": product.get("use_scenarios", []),
        "style": product.get("visual_style", []),
        "constraints": [
            *product.get("claims", []),
            *manufacturing.get("safety_and_compliance", [])[:2],
        ],
        "factoryBoundary": "当前仅用于概念视觉、工厂询价与首样沟通，不构成量产定稿。",
    }


def _clean_string_list(
    value: Any,
    field: str,
    *,
    max_items: int,
    max_length: int = 240,
) -> list[str]:
    if not isinstance(value, list) or len(value) > max_items:
        raise ValueError(f"{field} 必须是不超过 {max_items} 项的数组。")
    return list(
        dict.fromkeys(str(item).strip()[:max_length] for item in value if str(item).strip())
    )


def _default_decision_profile(
    concept_ids: list[str] | None = None,
    workspace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace) if workspace else HOTNESS_PATH)
    strategy = _load_json(workspace_strategy_path(workspace) if workspace else STRATEGY_PATH)
    design = _load_json(_workspace_design_path(workspace) if workspace else DESIGN_PATH)
    visual = _load_json(VISUAL_REFERENCES_PATH)
    culture_ids = {str(item.get("culture_id", "")) for item in culture.get("records", [])}
    preferred_culture = [
        item
        for item in (
            "GZ-MIAO-HUAXI",
            "GZ-MIAO-JIANHE-TIN",
            "GZ-MIAO-SONGTAO",
            "GZ-MIAO-EMBROIDERY",
        )
        if item in culture_ids
    ]
    ranked = sorted(
        strategy.get("opportunity_signals", []),
        key=lambda item: float(item.get("overall_score", 0)),
        reverse=True,
    )
    product = design.get("product", {})
    reference_ids = list(
        dict.fromkeys(
            str(ref)
            for item in design.get("cultural_elements", [])
            for ref in item.get("reference_visual_ids", [])
            if ref
        )
    )
    valid_visual_ids = {str(item.get("visual_id", "")) for item in visual.get("references", [])}
    reference_ids = [item for item in reference_ids if item in valid_visual_ids]
    if not reference_ids:
        reference_ids = [item for item in list(valid_visual_ids)[:1] if item]
    active_concepts = concept_ids or ["concept-a", "concept-b", "concept-c"]
    return {
        "version": 1,
        "mode": "guided",
        "cultureRecordIds": preferred_culture or [item for item in list(culture_ids)[:4] if item],
        "marketPlatforms": list(MARKET_PLATFORMS),
        "marketProductForms": [
            str(item.get("product_form", ""))
            for item in hotness.get("ranking", [])[:5]
            if item.get("product_form")
        ],
        "opportunityIds": [
            str(item.get("opportunity_id", "")) for item in ranked[:3] if item.get("opportunity_id")
        ],
        "scoreWeights": dict(DEFAULT_SCORE_WEIGHTS),
        "culturalRiskPenalty": 0.20,
        "designIntent": {
            "targetAudience": str(product.get("target_audience", "18-30岁年轻消费者")),
            "preferredProductForms": [str(product.get("product_type", "文创产品"))],
            "priceBand": "待用户与渠道共同确认",
            "useScenarios": [str(item) for item in product.get("use_scenarios", [])[:8]],
            "materialPriorities": ["可追溯", "可拆解", "首样可验证"],
        },
        "visualDirection": {
            "referenceIds": reference_ids,
            "styleKeywords": [str(item) for item in product.get("visual_style", [])[:8]],
            "imageSize": "1024x1024",
            "notes": "仅提取结构、节奏与材料关系，不复用 reference_only 像素。",
        },
        "conceptCompareIds": active_concepts[:3],
        "activeConceptId": active_concepts[0] if active_concepts else "",
        "posterTheme": "editorial",
        "posterSections": list(POSTER_SECTIONS),
        "notes": "",
        "updatedAt": _now(),
    }


def _validate_decision_profile(
    candidate: Any,
    nodes: list[dict[str, Any]],
    workspace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    concept_ids = [str(node["id"]) for node in nodes if node["type"] == "ConceptNode"]
    defaults = _default_decision_profile(concept_ids, workspace)
    if candidate is None:
        candidate = {}
    if not isinstance(candidate, dict):
        raise TypeError("metadata.decision_profile 必须是对象。")
    merged = copy.deepcopy(defaults)
    merged.update(candidate)
    merged["scoreWeights"] = {
        **defaults["scoreWeights"],
        **(
            candidate.get("scoreWeights", {})
            if isinstance(candidate.get("scoreWeights"), dict)
            else {}
        ),
    }
    merged["designIntent"] = {
        **defaults["designIntent"],
        **(
            candidate.get("designIntent", {})
            if isinstance(candidate.get("designIntent"), dict)
            else {}
        ),
    }
    merged["visualDirection"] = {
        **defaults["visualDirection"],
        **(
            candidate.get("visualDirection", {})
            if isinstance(candidate.get("visualDirection"), dict)
            else {}
        ),
    }

    mode = str(merged.get("mode", "guided"))
    if mode not in DECISION_MODES:
        raise ValueError("decision_profile.mode 只允许 guided 或 manual。")

    culture_ids = {
        str(item.get("culture_id", "")) for item in _load_json(CULTURE_PATH).get("records", [])
    }
    market_path = _workspace_hotness_path(workspace) if workspace else HOTNESS_PATH
    strategy_path = workspace_strategy_path(workspace) if workspace else STRATEGY_PATH
    market_forms = {
        str(item.get("product_form", "")) for item in _load_json(market_path).get("ranking", [])
    }
    strategy_items = _load_json(strategy_path).get("opportunity_signals", [])
    opportunity_ids = {
        str(item.get("opportunity_id", ""))
        for item in strategy_items
        if item.get("verification", {}).get("status") != "rejected"
    }
    visual_ids = {
        str(item.get("visual_id", ""))
        for item in _load_json(VISUAL_REFERENCES_PATH).get("references", [])
    }

    def allowed_list(
        field: str,
        allowed: set[str],
        max_items: int,
        *,
        required: bool = True,
    ) -> list[str]:
        values = _clean_string_list(
            merged.get(field, []),
            f"decision_profile.{field}",
            max_items=max_items,
        )
        invalid = [item for item in values if item not in allowed]
        if invalid:
            raise ValueError(f"decision_profile.{field} 包含未知编号：{', '.join(invalid)}")
        if required and not values:
            raise ValueError(f"decision_profile.{field} 至少选择 1 项。")
        return values

    culture_record_ids = allowed_list("cultureRecordIds", culture_ids, 22)
    market_platforms = allowed_list("marketPlatforms", set(MARKET_PLATFORMS), len(MARKET_PLATFORMS))
    market_product_forms = allowed_list("marketProductForms", market_forms, 10)
    selected_opportunities = allowed_list("opportunityIds", opportunity_ids, 3)
    selected_concepts = allowed_list("conceptCompareIds", set(concept_ids), 12)
    active_concept_id = str(merged.get("activeConceptId", ""))
    if active_concept_id not in concept_ids:
        raise ValueError("decision_profile.activeConceptId 必须指向 ConceptNode。")

    weights = merged.get("scoreWeights", {})
    if not isinstance(weights, dict):
        raise TypeError("decision_profile.scoreWeights 必须是对象。")
    cleaned_weights: dict[str, float] = {}
    for field in SCORE_FIELDS:
        value = weights.get(field, DEFAULT_SCORE_WEIGHTS[field])
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            raise ValueError(f"decision_profile.scoreWeights.{field} 必须在 0 到 1 之间。")
        cleaned_weights[field] = float(value)
    total_weight = sum(cleaned_weights.values())
    if total_weight <= 0:
        raise ValueError("decision_profile.scoreWeights 至少有一个正权重。")
    cleaned_weights = {
        key: round(value / total_weight, 6) for key, value in cleaned_weights.items()
    }
    risk_penalty = merged.get("culturalRiskPenalty", 0.20)
    if not isinstance(risk_penalty, (int, float)) or not 0 <= float(risk_penalty) <= 1:
        raise ValueError("decision_profile.culturalRiskPenalty 必须在 0 到 1 之间。")

    intent = merged["designIntent"]
    if not isinstance(intent, dict):
        raise TypeError("decision_profile.designIntent 必须是对象。")
    target_audience = str(intent.get("targetAudience", "")).strip()[:500]
    price_band = str(intent.get("priceBand", "")).strip()[:240]
    preferred_forms = _clean_string_list(
        intent.get("preferredProductForms", []),
        "decision_profile.designIntent.preferredProductForms",
        max_items=8,
    )
    use_scenarios = _clean_string_list(
        intent.get("useScenarios", []),
        "decision_profile.designIntent.useScenarios",
        max_items=12,
        max_length=300,
    )
    material_priorities = _clean_string_list(
        intent.get("materialPriorities", []),
        "decision_profile.designIntent.materialPriorities",
        max_items=12,
        max_length=300,
    )

    direction = merged["visualDirection"]
    if not isinstance(direction, dict):
        raise TypeError("decision_profile.visualDirection 必须是对象。")
    reference_ids = _clean_string_list(
        direction.get("referenceIds", []),
        "decision_profile.visualDirection.referenceIds",
        max_items=8,
    )
    invalid_visual = [item for item in reference_ids if item not in visual_ids]
    if invalid_visual:
        raise ValueError(
            "decision_profile.visualDirection.referenceIds 包含未知编号："
            + ", ".join(invalid_visual)
        )
    style_keywords = _clean_string_list(
        direction.get("styleKeywords", []),
        "decision_profile.visualDirection.styleKeywords",
        max_items=16,
        max_length=160,
    )
    image_size = str(direction.get("imageSize", "1024x1024"))
    if image_size not in VISUAL_SIZES:
        raise ValueError("decision_profile.visualDirection.imageSize 不受支持。")

    poster_theme = str(merged.get("posterTheme", "editorial"))
    if poster_theme not in POSTER_THEMES:
        raise ValueError("decision_profile.posterTheme 不受支持。")
    poster_sections = allowed_list("posterSections", set(POSTER_SECTIONS), len(POSTER_SECTIONS))
    version = merged.get("version", 1)
    if not isinstance(version, int) or version < 1:
        version = 1

    return {
        "version": version,
        "mode": mode,
        "cultureRecordIds": culture_record_ids,
        "marketPlatforms": market_platforms,
        "marketProductForms": market_product_forms,
        "opportunityIds": selected_opportunities,
        "scoreWeights": cleaned_weights,
        "culturalRiskPenalty": round(float(risk_penalty), 4),
        "designIntent": {
            "targetAudience": target_audience,
            "preferredProductForms": preferred_forms,
            "priceBand": price_band,
            "useScenarios": use_scenarios,
            "materialPriorities": material_priorities,
        },
        "visualDirection": {
            "referenceIds": reference_ids,
            "styleKeywords": style_keywords,
            "imageSize": image_size,
            "notes": str(direction.get("notes", "")).strip()[:2000],
        },
        "conceptCompareIds": selected_concepts,
        "activeConceptId": active_concept_id,
        "posterTheme": poster_theme,
        "posterSections": poster_sections,
        "notes": str(merged.get("notes", "")).strip()[:4000],
        "updatedAt": str(merged.get("updatedAt", _now())),
    }


def default_workspace() -> dict[str, Any]:
    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(HOTNESS_PATH)
    strategy = _load_json(STRATEGY_PATH)
    design = _load_json(DESIGN_PATH)
    manifest = _load_json(MANIFEST_PATH)
    adapter_status = ImageGenerationAdapter().status()
    concept_b_asset = _bundled_concept_asset("concept-b-v1.png")
    concept_c_asset = _bundled_concept_asset("concept-c-v1.png")
    records = culture.get("records", [])
    sources = culture.get("sources", [])
    ranking = hotness.get("ranking", [])
    opportunities = strategy.get("opportunity_signals", [])
    top_opportunities = sorted(
        opportunities,
        key=lambda item: float(item.get("overall_score", 0)),
        reverse=True,
    )[:3]
    product = design.get("product", {})
    manufacturing = design.get("manufacturing", {})
    poster_request = design.get("poster_request", {})
    brief = _default_brief(design)
    timestamp = _now()
    concept_title = product.get("product_name", "针格模块")
    image_prompt = poster_request.get("image_prompt", "")
    concepts = [
        {
            "id": "concept-a",
            "label": "A",
            "title": concept_title,
            "summary": product.get("concept_statement", ""),
            "status": "success",
            "imageUrl": "/assets/official/product-hero.png",
            "direction": "深靛框体 × 原创数纱网格 × 可替换织物面板",
            "prompt": image_prompt,
            "version": 1,
            "active": True,
        },
        {
            "id": "concept-b",
            "label": "B",
            "title": "轻量礼赠版",
            "summary": "保留可替换结构，探索更轻的礼赠包装和低对比线色。",
            "status": "success" if concept_b_asset else "idle",
            "imageUrl": concept_b_asset["imageUrl"] if concept_b_asset else "",
            "direction": "暖灰框体 × 低对比针格 × 旅行礼赠",
            "prompt": image_prompt
            + "\nVariant B: warm gray frame, restrained low-contrast threads, travel gift positioning.",
            "version": concept_b_asset["version"] if concept_b_asset else 0,
            "active": False,
            **({"generation": concept_b_asset["generation"]} if concept_b_asset else {}),
        },
        {
            "id": "concept-c",
            "label": "C",
            "title": "系列收藏版",
            "summary": "以编号与面板收藏系统扩展支系学习，但不混用地域纹样。",
            "status": "success" if concept_c_asset else "idle",
            "imageUrl": concept_c_asset["imageUrl"] if concept_c_asset else "",
            "direction": "系列编号 × 面板档案 × 学习收藏",
            "prompt": image_prompt
            + "\nVariant C: numbered collectible system, archival presentation, modular inserts.",
            "version": concept_c_asset["version"] if concept_c_asset else 0,
            "active": False,
            **({"generation": concept_c_asset["generation"]} if concept_c_asset else {}),
        },
    ]
    nodes = [
        _node(
            "culture",
            "CultureGraphNode",
            -520,
            -235,
            {
                "label": "文化图谱",
                "eyebrow": "CULTURE DNA",
                "title": "贵州苗绣文化图谱",
                "summary": "从地域、工艺、纹样语义与禁忌边界提取可验证的文化设计输入。",
                "status": "success",
                "stats": [
                    {"label": "文化记录", "value": len(records)},
                    {"label": "登记来源", "value": len(sources)},
                ],
                "sourceRefs": ["C001", "C002", "C003", "C029"],
                "outputs": {
                    "topic": (
                        culture.get("scope", {}).get("topic", "贵州苗绣")
                        if isinstance(culture.get("scope"), dict)
                        else str(culture.get("scope") or "贵州苗绣")
                    ),
                    "keyCrafts": records[0].get("crafts", [])[:6] if records else [],
                    "boundaries": records[0].get("cultural_taboos", [])[:3] if records else [],
                },
                "history": [{"at": timestamp, "event": "载入策展式文化图谱"}],
            },
        ),
        _node(
            "market",
            "MarketRadarNode",
            -520,
            195,
            {
                "label": "市场雷达",
                "eyebrow": "MARKET RADAR",
                "title": "四平台形态热度",
                "summary": "基于已保存的真实平台历史快照比较产品形态，不把缓存标成实时趋势。",
                "status": "cached",
                "stats": [
                    {"label": "历史样本", "value": hotness.get("total_sample_size", 0)},
                    {"label": "平台", "value": len(hotness.get("platforms", []))},
                ],
                "platforms": manifest.get("market_platforms", {}),
                "topForms": [
                    {
                        "name": item.get("product_form", ""),
                        "score": item.get("cross_platform_hot_score", 0),
                        "sampleSize": item.get("sample_size", 0),
                    }
                    for item in ranking[:5]
                ],
                "sourceRefs": [
                    item.get("source_ref", "")
                    for item in ranking[0].get("representative_posts", [])[:4]
                    if item.get("source_ref")
                ]
                if ranking
                else [],
                "history": [{"at": timestamp, "event": "载入四平台历史证据快照"}],
            },
        ),
        _node(
            "strategy",
            "StrategyNode",
            -85,
            -15,
            {
                "label": "机会策略",
                "eyebrow": "OPPORTUNITY",
                "title": "文化 × 市场机会排序",
                "summary": "综合文化适配、市场拉力、原创空间、视觉潜力与风险惩罚。",
                "status": "success",
                "stats": [
                    {"label": "候选机会", "value": len(opportunities)},
                    {"label": "进入设计", "value": len(top_opportunities)},
                ],
                "opportunities": [
                    {
                        "id": item.get("opportunity_id", ""),
                        "title": (
                            f"{item.get('culture_element', '')} × {item.get('trend_element', '')}"
                        ),
                        "score": item.get("overall_score", 0),
                        "verification": item.get("verification", {}).get("status", ""),
                    }
                    for item in top_opportunities
                ],
                "sourceRefs": list(
                    dict.fromkeys(
                        ref for item in top_opportunities for ref in item.get("evidence_refs", [])
                    )
                )[:12],
                "history": [{"at": timestamp, "event": "完成证据锁定与二次核验"}],
            },
        ),
        _node(
            "brief",
            "DesignBriefNode",
            345,
            -15,
            {
                "label": "设计任务书",
                "eyebrow": "DESIGN BRIEF",
                "title": brief["title"],
                "summary": brief["objective"],
                "status": "success",
                "version": 1,
                "brief": brief,
                "sourceRefs": design.get("evidence_refs", [])[:16],
                "history": [{"at": timestamp, "event": "建立可编辑任务书 v1"}],
            },
        ),
        _node(
            "visual",
            "VisualGenerationNode",
            790,
            -15,
            {
                "label": "视觉生成",
                "eyebrow": "VISUAL GENERATION",
                "title": "概念方向 A / B / C",
                "summary": (
                    "图像服务已就绪，可生成三个可追溯方向。"
                    if adapter_status["configured"]
                    else (
                        "三套概念方向已具备可展示视觉；重新生成仍需配置独立图像服务。"
                        if concept_b_asset and concept_c_asset
                        else "已保留当前项目概念图；新图像服务尚未配置。"
                    )
                ),
                "status": "success" if adapter_status["configured"] else "warning",
                "provider": adapter_status,
                "size": "1024x1024",
                "prompts": [item["prompt"] for item in concepts],
                "sourceRefs": design.get("evidence_refs", [])[:12],
                "history": [
                    {
                        "at": timestamp,
                        "event": adapter_status["detail"],
                    }
                ],
            },
        ),
        *[
            _node(
                item["id"],
                "ConceptNode",
                1240,
                y,
                {
                    "label": f"概念 {item['label']}",
                    "eyebrow": f"CONCEPT {item['label']}",
                    **{key: value for key, value in item.items() if key != "id"},
                    "sourceRefs": design.get("evidence_refs", [])[:10],
                    "history": [
                        {
                            "at": timestamp,
                            "event": (
                                "载入现有项目概念视觉" if item["imageUrl"] else "建立待生成方向"
                            ),
                        }
                    ],
                },
            )
            for item, y in zip(concepts, (-350, -15, 320), strict=True)
        ],
        _node(
            "poster",
            "PosterBoardNode",
            1700,
            -15,
            {
                "label": "概念海报",
                "eyebrow": "POSTER BOARD",
                "title": poster_request.get("exact_copy", {}).get("title", "针格模块"),
                "summary": poster_request.get("exact_copy", {}).get("subtitle", ""),
                "status": "cached",
                "imageUrl": "/assets/official/design-poster.png",
                "poster": {
                    "title": poster_request.get("exact_copy", {}).get("title", "针格模块"),
                    "subtitle": poster_request.get("exact_copy", {}).get("subtitle", ""),
                    "sections": list(POSTER_SECTIONS),
                    "hiddenSections": [],
                    "cultureElement": (
                        design.get("cultural_elements", [{}])[0].get("name", "原创数纱网格")
                    ),
                    "cultureRule": (
                        design.get("cultural_elements", [{}])[0].get("transformation_rule", "")
                    ),
                    "materials": [
                        f"{item.get('component', '')}｜{item.get('material', '')}"
                        for item in manufacturing.get("bill_of_materials", [])[:5]
                    ],
                    "process": manufacturing.get("assembly_steps", [])[:6],
                    "boundary": brief["factoryBoundary"],
                },
                "sourceRefs": design.get("evidence_refs", [])[:16],
                "history": [{"at": timestamp, "event": "载入可编辑固定版式"}],
            },
        ),
    ]
    edges = [
        _edge("culture-strategy", "culture", "strategy", "文化证据"),
        _edge("market-strategy", "market", "strategy", "市场证据"),
        _edge("strategy-brief", "strategy", "brief", "机会输入"),
        _edge("brief-visual", "brief", "visual", "设计约束"),
        _edge("visual-concept-a", "visual", "concept-a", "方向 A"),
        _edge("visual-concept-b", "visual", "concept-b", "方向 B"),
        _edge("visual-concept-c", "visual", "concept-c", "方向 C"),
        _edge("concept-a-poster", "concept-a", "poster", "当前采用"),
        _edge("concept-b-poster", "concept-b", "poster", "候选"),
        _edge("concept-c-poster", "concept-c", "poster", "候选"),
    ]
    workspace = {
        "schema_version": "1.1",
        "workspace_id": DEFAULT_WORKSPACE_ID,
        "name": "贵州苗绣 · 文创机会工作台",
        "created_at": timestamp,
        "updated_at": timestamp,
        "viewport": {"x": 20, "y": 210, "zoom": 0.82},
        "selected_node_id": "brief",
        "metadata": {
            "topic": "贵州苗绣",
            "region": "贵州",
            "target_market": "18-30岁年轻消费者",
            "source_run_id": manifest.get("run_id", ""),
            "selected_concept_id": "concept-a",
            "brief_version": 1,
            "decision_profile": _default_decision_profile(
                [item["id"] for item in nodes if item["type"] == "ConceptNode"]
            ),
            "node_types": list(NODE_TYPES),
            "product_stage": "concept_visual_and_prototype_brief",
            "stop_before": "production_release_and_factory_order",
        },
        "nodes": nodes,
        "edges": edges,
    }
    return _apply_decision_profile_to_workspace(workspace, mark_downstream=False)


def _validate_workspace(candidate: dict[str, Any], workspace_id: str) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise TypeError("workspace must be a JSON object")
    payload = copy.deepcopy(candidate)
    payload["workspace_id"] = workspace_id
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 80:
        raise ValueError("工作区名称必须为 1 到 80 个字符。")
    payload["name"] = name
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    viewport = payload.get("viewport")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise TypeError("workspace 必须包含 nodes 与 edges 数组。")
    if not isinstance(viewport, dict):
        raise TypeError("workspace 必须包含 viewport 对象。")
    if len(nodes) > 200 or len(edges) > 500:
        raise ValueError("工作区超过 200 个节点或 500 条连线的安全上限。")

    node_ids: set[str] = set()
    observed_types: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise TypeError("每个节点必须是对象。")
        node_id = str(node.get("id", ""))
        node_type = str(node.get("type", ""))
        if not node_id or node_id in node_ids:
            raise ValueError("节点 id 不能为空或重复。")
        if node_type not in NODE_TYPES:
            raise ValueError(f"不支持的节点类型：{node_type}")
        data = node.get("data")
        position = node.get("position")
        if not isinstance(data, dict) or not isinstance(position, dict):
            raise TypeError("节点必须包含 data 与 position。")
        if data.get("status", "idle") not in NODE_STATUSES:
            raise ValueError(f"不支持的节点状态：{data.get('status')}")
        if not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y")):
            raise ValueError("节点 position.x / position.y 必须为数字。")
        node_ids.add(node_id)
        observed_types.add(node_type)
    missing_types = set(NODE_TYPES) - observed_types
    if missing_types:
        raise ValueError(f"工作区缺少必要节点类型：{', '.join(sorted(missing_types))}")

    edge_ids: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise TypeError("每条连线必须是对象。")
        edge_id = str(edge.get("id", ""))
        if not edge_id or edge_id in edge_ids:
            raise ValueError("连线 id 不能为空或重复。")
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            raise ValueError(f"连线 {edge_id} 指向不存在的节点。")
        edge_ids.add(edge_id)

    zoom = viewport.get("zoom", 1)
    if not isinstance(zoom, (int, float)) or not 0.05 <= float(zoom) <= 4:
        raise ValueError("viewport.zoom 必须在 0.05 到 4 之间。")
    metadata = payload.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        raise TypeError("metadata 必须是对象。")
    selected_concept = str(metadata.get("selected_concept_id", ""))
    concept_ids = {node["id"] for node in nodes if node["type"] == "ConceptNode"}
    if selected_concept and selected_concept not in concept_ids:
        raise ValueError("selected_concept_id 必须指向 ConceptNode。")
    profile_candidate = metadata.get("decision_profile")
    if profile_candidate is None:
        profile_candidate = {"activeConceptId": selected_concept or next(iter(concept_ids), "")}
    profile = _validate_decision_profile(profile_candidate, nodes, payload)
    if selected_concept and profile["activeConceptId"] != selected_concept:
        raise ValueError("decision_profile.activeConceptId 必须与 selected_concept_id 一致。")
    metadata["decision_profile"] = profile
    payload["schema_version"] = "1.1"
    payload.setdefault("created_at", _now())
    payload.setdefault("updated_at", payload["created_at"])
    return _apply_decision_profile_to_workspace(payload, mark_downstream=False)


def ensure_default_workspace() -> dict[str, Any]:
    path = _workspace_path(DEFAULT_WORKSPACE_ID)
    if not path.exists():
        bundled_path = BUNDLED_WORKSPACES_DIR / f"{DEFAULT_WORKSPACE_ID}.json"
        if bundled_path != path and bundled_path.is_file():
            payload = _validate_workspace(_load_json(bundled_path), DEFAULT_WORKSPACE_ID)
        else:
            payload = default_workspace()
        _atomic_json(path, payload)
        return payload
    return _validate_workspace(_load_json(path), DEFAULT_WORKSPACE_ID)


def load_workbench_workspace(workspace_id: str = DEFAULT_WORKSPACE_ID) -> dict[str, Any]:
    if workspace_id == DEFAULT_WORKSPACE_ID:
        return ensure_default_workspace()
    path = _workspace_path(workspace_id)
    if not path.exists():
        raise FileNotFoundError(f"工作区不存在：{workspace_id}")
    return _validate_workspace(_load_json(path), workspace_id)


def save_workbench_workspace(workspace_id: str, candidate: dict[str, Any]) -> dict[str, Any]:
    path = _workspace_path(workspace_id)
    existing = _load_json(path) if path.exists() else {}
    payload = _validate_workspace(candidate, workspace_id)
    payload["created_at"] = existing.get("created_at", payload.get("created_at", _now()))
    payload["updated_at"] = _now()
    _atomic_json(path, payload)
    return payload


def list_workbench_workspaces() -> list[dict[str, Any]]:
    ensure_default_workspace()
    result: list[dict[str, Any]] = []
    for path in sorted(WORKSPACES_DIR.glob("*.json")):
        try:
            payload = _load_json(path)
            result.append(
                {
                    "workspace_id": payload.get("workspace_id", path.stem),
                    "name": payload.get("name", path.stem),
                    "updated_at": payload.get("updated_at", ""),
                    "topic": payload.get("metadata", {}).get("topic", ""),
                }
            )
        except (OSError, ValueError, TypeError):
            continue
    return sorted(result, key=lambda item: item["updated_at"], reverse=True)


def create_workbench_workspace(candidate: dict[str, Any]) -> dict[str, Any]:
    name = str(candidate.get("name", "新工作区")).strip() or "新工作区"
    workspace_id = f"workspace-{uuid.uuid4().hex[:8]}"
    base = default_workspace()
    base["workspace_id"] = workspace_id
    base["name"] = name[:80]
    base["created_at"] = _now()
    base["updated_at"] = base["created_at"]
    return save_workbench_workspace(workspace_id, base)


def _reconcile_promoted_decisions(
    workspace: dict[str, Any],
    *,
    event_time: str,
) -> dict[str, Any] | None:
    """Keep valid human choices and explicitly replace only vanished research IDs."""

    metadata = workspace.setdefault("metadata", {})
    profile = metadata.get("decision_profile")
    if not isinstance(profile, dict):
        return None
    strategy = _load_json(workspace_strategy_path(workspace))
    hotness = _load_json(_workspace_hotness_path(workspace))
    opportunity_rows = [
        item
        for item in strategy.get("opportunity_signals", [])
        if item.get("verification", {}).get("status") != "rejected"
    ]
    ranked_ids = [
        str(item.get("opportunity_id", ""))
        for item in sorted(
            opportunity_rows,
            key=lambda item: float(item.get("overall_score", 0)),
            reverse=True,
        )
        if item.get("opportunity_id")
    ]
    valid_opportunity_ids = set(ranked_ids)
    old_opportunities = [str(item) for item in profile.get("opportunityIds", [])]
    kept_opportunities = [item for item in old_opportunities if item in valid_opportunity_ids]
    target_opportunity_count = max(1, min(3, len(old_opportunities) or 3))
    new_opportunities = list(kept_opportunities)
    for item in ranked_ids:
        if item not in new_opportunities:
            new_opportunities.append(item)
        if len(new_opportunities) >= target_opportunity_count:
            break

    ranked_forms = [
        str(item.get("product_form", ""))
        for item in hotness.get("ranking", [])
        if item.get("product_form")
    ]
    valid_forms = set(ranked_forms)
    old_forms = [str(item) for item in profile.get("marketProductForms", [])]
    new_forms = [item for item in old_forms if item in valid_forms]
    target_form_count = max(1, min(10, len(old_forms) or 5))
    for item in ranked_forms:
        if item not in new_forms:
            new_forms.append(item)
        if len(new_forms) >= target_form_count:
            break

    if not new_opportunities or not new_forms:
        raise ValueError("新研究结果缺少可选择的机会或产品形态，不能晋级。")
    if new_opportunities == old_opportunities and new_forms == old_forms:
        return None

    profile["opportunityIds"] = new_opportunities
    profile["marketProductForms"] = new_forms
    profile["version"] = int(profile.get("version", 0)) + 1
    profile["updatedAt"] = event_time
    audit = {
        "at": event_time,
        "reason": "新研究结果晋级后，保留仍有效的人工选择并补齐已失效编号。",
        "previousOpportunityIds": old_opportunities,
        "currentOpportunityIds": new_opportunities,
        "previousProductForms": old_forms,
        "currentProductForms": new_forms,
    }
    metadata["decision_reconciliation"] = audit
    return audit


def promote_research_run(
    workspace_id: str,
    run_dir: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Promote only a fully verified isolated research run into one workspace."""

    workspace = load_workbench_workspace(workspace_id)
    run_root = run_dir.resolve()
    manifest_run_id = str(manifest.get("run_id", ""))
    if not _RUN_ID.fullmatch(manifest_run_id):
        raise ValueError("研究运行编号无效，不能晋级。")

    component_modes = {
        str(item.get("component", "")): str(item.get("mode", ""))
        for item in manifest.get("components", [])
        if item.get("component") in {"culture_knowledge", "market_research", "strategist"}
    }
    platform_modes = {
        code: str(manifest.get("market_platforms", {}).get(code, {}).get("status", ""))
        for code in MARKET_PLATFORMS
    }
    if set(component_modes.values()) != {"live"} or any(
        mode != "live" for mode in platform_modes.values()
    ):
        raise ValueError("只有文化、市场、策划及四平台全部 live 的运行可以晋级。")

    destination = RESEARCH_DIR / workspace_id / manifest_run_id
    outputs = manifest.get("outputs", {})
    sources: dict[str, Path] = {
        "pre_design_strategy.json": _manifest_artifact_path(outputs.get("strategy_json")),
        "visual_reference_pack.json": _manifest_artifact_path(
            outputs.get("visual_reference_json")
        ),
        "designer_handoff.json": _manifest_artifact_path(outputs.get("designer_handoff_json")),
        "run_manifest.json": _manifest_artifact_path(outputs.get("manifest")),
        "product_form_hotness.json": _manifest_artifact_path(
            outputs.get("product_form_hotness")
        ),
        "market_evidence.json": _manifest_artifact_path(
            manifest.get("market_source", {}).get("derived_path")
        ),
    }
    missing: list[str] = []
    for name, source in sources.items():
        try:
            resolved = source.resolve(strict=True)
        except (FileNotFoundError, OSError):
            missing.append(name)
            continue
        if not resolved.is_relative_to(run_root):
            raise ValueError(f"研究产物 {name} 不在隔离运行目录内。")
    if missing:
        raise FileNotFoundError("研究运行缺少产物：" + "、".join(missing))

    destination.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        shutil.copy2(source.resolve(), destination / name)

    metadata = workspace.setdefault("metadata", {})
    metadata.update(
        {
            "source_run_id": manifest_run_id,
            "research_run_id": manifest_run_id,
            "research_verified_at": str(manifest.get("finished_at", _now())),
            "research_component_modes": component_modes,
            "research_platform_modes": platform_modes,
        }
    )
    reconciliation = _reconcile_promoted_decisions(
        workspace,
        event_time=str(manifest.get("finished_at", _now())),
    )
    workspace = _apply_decision_profile_to_workspace(
        workspace,
        mark_downstream=True,
    )
    for node in workspace["nodes"]:
        if node["type"] not in {
            "CultureGraphNode",
            "MarketRadarNode",
            "StrategyNode",
        }:
            continue
        node["data"]["status"] = "success"
        node["data"].setdefault("history", []).insert(
            0,
            {
                "at": str(manifest.get("finished_at", _now())),
                "event": (
                    f"实时研究 {manifest_run_id} 已核验并回写；失效的人工编号已在审计记录中替换"
                    if reconciliation
                    else f"实时研究 {manifest_run_id} 已核验并回写"
                ),
            },
        )
    return save_workbench_workspace(workspace_id, workspace)


def _descendants(workspace: dict[str, Any], source_id: str) -> set[str]:
    adjacency: dict[str, list[str]] = {}
    for edge in workspace.get("edges", []):
        adjacency.setdefault(str(edge.get("source", "")), []).append(str(edge.get("target", "")))
    visited: set[str] = set()
    queue = deque(adjacency.get(source_id, []))
    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        queue.extend(adjacency.get(node_id, []))
    return visited


def manual_opportunity_score(
    opportunity: dict[str, Any],
    weights: dict[str, float],
    cultural_risk_penalty: float,
) -> float:
    total_weight = sum(float(weights.get(field, 0)) for field in SCORE_FIELDS)
    if total_weight <= 0:
        raise ValueError("人工评分权重之和必须大于 0。")
    weighted_positive = (
        sum(
            float(opportunity.get(field, 0)) * float(weights.get(field, 0))
            for field in SCORE_FIELDS
        )
        / total_weight
    )
    score = weighted_positive - cultural_risk_penalty * float(opportunity.get("cultural_risk", 0))
    verification = opportunity.get("verification", {}).get("status", "")
    if verification == "rejected":
        return 0.0
    if verification == "warning":
        score -= 5
    return round(max(0, min(100, score)), 1)


def _decision_output(
    profile: dict[str, Any],
    workspace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace = workspace or {}
    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace))
    strategy = _load_json(workspace_strategy_path(workspace))
    culture_map = {str(item.get("culture_id", "")): item for item in culture.get("records", [])}
    selected_culture = [
        {
            "id": item_id,
            "name": culture_map[item_id].get("culture_name", item_id),
            "category": culture_map[item_id].get("category", ""),
        }
        for item_id in profile["cultureRecordIds"]
        if item_id in culture_map
    ]
    selected_forms = set(profile["marketProductForms"])
    form_rows = [
        item for item in hotness.get("ranking", []) if item.get("product_form") in selected_forms
    ]
    platform_sizes = hotness.get("platform_sample_sizes", {})
    ranked_opportunities = []
    for item in strategy.get("opportunity_signals", []):
        ranked_opportunities.append(
            {
                "id": item.get("opportunity_id", ""),
                "title": (f"{item.get('culture_element', '')} × {item.get('trend_element', '')}"),
                "manualScore": manual_opportunity_score(
                    item,
                    profile["scoreWeights"],
                    profile["culturalRiskPenalty"],
                ),
                "systemScore": item.get("overall_score", 0),
                "verification": item.get("verification", {}).get("status", ""),
                "selected": item.get("opportunity_id") in profile["opportunityIds"],
            }
        )
    ranked_opportunities.sort(
        key=lambda item: (float(item["manualScore"]), float(item["systemScore"])),
        reverse=True,
    )
    return {
        "profileVersion": profile["version"],
        "mode": profile["mode"],
        "selectedCulture": selected_culture,
        "marketScope": {
            "platforms": profile["marketPlatforms"],
            "productForms": profile["marketProductForms"],
            "selectedPlatformSamples": sum(
                int(platform_sizes.get(item, 0)) for item in profile["marketPlatforms"]
            ),
            "selectedFormSamples": sum(int(item.get("sample_size", 0)) for item in form_rows),
        },
        "manualRanking": ranked_opportunities,
        "selectedOpportunityIds": profile["opportunityIds"],
        "designIntent": profile["designIntent"],
        "visualDirection": profile["visualDirection"],
        "conceptCompareIds": profile["conceptCompareIds"],
        "activeConceptId": profile["activeConceptId"],
        "posterTheme": profile["posterTheme"],
        "posterSections": profile["posterSections"],
    }


def _apply_decision_profile_to_workspace(
    workspace: dict[str, Any],
    *,
    mark_downstream: bool,
) -> dict[str, Any]:
    metadata = workspace.setdefault("metadata", {})
    profile = _validate_decision_profile(
        metadata.get("decision_profile"), workspace["nodes"], workspace
    )
    metadata["decision_profile"] = profile
    metadata["selected_concept_id"] = profile["activeConceptId"]
    output = _decision_output(profile, workspace)
    metadata["decision_output"] = output

    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace))
    strategy = _load_json(workspace_strategy_path(workspace))
    culture_map = {str(item.get("culture_id", "")): item for item in culture.get("records", [])}
    selected_culture_records = [
        culture_map[item] for item in profile["cultureRecordIds"] if item in culture_map
    ]
    selected_culture_refs = list(
        dict.fromkeys(
            str(ref)
            for item in selected_culture_records
            for ref in item.get("source_refs", [])
            if ref
        )
    )
    form_map = {str(item.get("product_form", "")): item for item in hotness.get("ranking", [])}
    selected_form_rows = [
        form_map[item] for item in profile["marketProductForms"] if item in form_map
    ]
    market_refs = list(
        dict.fromkeys(
            str(post.get("source_ref", ""))
            for item in selected_form_rows
            for post in item.get("representative_posts", [])
            if post.get("source_ref")
        )
    )
    strategy_map = {
        str(item.get("opportunity_id", "")): item
        for item in strategy.get("opportunity_signals", [])
    }
    manual_map = {item["id"]: item for item in output["manualRanking"]}
    selected_opportunities = [
        strategy_map[item] for item in profile["opportunityIds"] if item in strategy_map
    ]
    selected_opportunity_rows = sorted(
        (
            {
                "id": item.get("opportunity_id", ""),
                "title": (f"{item.get('culture_element', '')} × {item.get('trend_element', '')}"),
                "score": manual_map.get(item.get("opportunity_id", ""), {}).get("manualScore", 0),
                "systemScore": item.get("overall_score", 0),
                "verification": item.get("verification", {}).get("status", ""),
            }
            for item in selected_opportunities
        ),
        key=lambda item: float(item["score"]),
        reverse=True,
    )
    strategy_refs = list(
        dict.fromkeys(
            str(ref)
            for item in selected_opportunities
            for ref in item.get("evidence_refs", [])
            if ref
        )
    )
    profile_version = profile["version"]
    event_time = profile["updatedAt"]

    for node in workspace["nodes"]:
        data = node["data"]
        data["decisionVersion"] = profile_version
        data["decisionMode"] = profile["mode"]
        if node["type"] == "CultureGraphNode":
            data["selectedRecordIds"] = profile["cultureRecordIds"]
            data["sourceRefs"] = selected_culture_refs
            data["stats"] = [
                {"label": "人工选用", "value": len(selected_culture_records)},
                {"label": "图谱总记录", "value": len(culture_map)},
            ]
            data["outputs"] = {
                **data.get("outputs", {}),
                "selectedRecordIds": profile["cultureRecordIds"],
            }
        elif node["type"] == "MarketRadarNode":
            data["selectedPlatforms"] = profile["marketPlatforms"]
            data["selectedProductForms"] = profile["marketProductForms"]
            data["sourceRefs"] = market_refs
            data["topForms"] = [
                {
                    "name": item.get("product_form", ""),
                    "score": item.get("cross_platform_hot_score", 0),
                    "sampleSize": item.get("sample_size", 0),
                }
                for item in selected_form_rows[:5]
            ]
            data["stats"] = [
                {"label": "选用平台", "value": len(profile["marketPlatforms"])},
                {
                    "label": "形态样本",
                    "value": output["marketScope"]["selectedFormSamples"],
                },
            ]
        elif node["type"] == "StrategyNode":
            data["opportunities"] = selected_opportunity_rows
            data["manualRanking"] = output["manualRanking"]
            data["scoreWeights"] = profile["scoreWeights"]
            data["culturalRiskPenalty"] = profile["culturalRiskPenalty"]
            data["sourceRefs"] = strategy_refs
            data["stats"] = [
                {"label": "人工候选", "value": len(selected_opportunity_rows)},
                {"label": "权重版本", "value": f"v{profile_version}"},
            ]
            data["status"] = "success"
        elif node["type"] == "DesignBriefNode":
            data["decisionInputs"] = profile["designIntent"]
            if mark_downstream and isinstance(data.get("brief"), dict):
                brief = data["brief"]
                intent = profile["designIntent"]
                if intent["targetAudience"]:
                    brief["audience"] = intent["targetAudience"]
                if intent["preferredProductForms"]:
                    brief["productType"] = " / ".join(intent["preferredProductForms"])
                if intent["useScenarios"]:
                    brief["scenarios"] = intent["useScenarios"]
                decision_constraints = [
                    *([f"目标价格带：{intent['priceBand']}"] if intent["priceBand"] else []),
                    *[f"材料优先：{item}" for item in intent["materialPriorities"]],
                ]
                brief["constraints"] = list(
                    dict.fromkeys([*brief.get("constraints", []), *decision_constraints])
                )[:30]
                data["version"] = int(data.get("version", 1)) + 1
                metadata["brief_version"] = data["version"]
        elif node["type"] == "VisualGenerationNode":
            direction = profile["visualDirection"]
            data["selectedReferenceIds"] = direction["referenceIds"]
            data["styleKeywords"] = direction["styleKeywords"]
            data["size"] = direction["imageSize"]
            data["visualNotes"] = direction["notes"]
        elif node["type"] == "ConceptNode":
            data["inComparison"] = node["id"] in profile["conceptCompareIds"]
            data["active"] = node["id"] == profile["activeConceptId"]
            direction = profile["visualDirection"]
            data["decisionPromptSuffix"] = "\n".join(
                item
                for item in (
                    "Manual art direction: " + ", ".join(direction["styleKeywords"])
                    if direction["styleKeywords"]
                    else "",
                    direction["notes"],
                )
                if item
            )
        elif node["type"] == "PosterBoardNode":
            data["posterTheme"] = profile["posterTheme"]
            poster = data.get("poster")
            if isinstance(poster, dict):
                poster["hiddenSections"] = [
                    item for item in POSTER_SECTIONS if item not in profile["posterSections"]
                ]

        if mark_downstream and node["type"] in {
            "DesignBriefNode",
            "VisualGenerationNode",
            "ConceptNode",
            "PosterBoardNode",
        }:
            data["status"] = "stale"
            data.setdefault("history", []).insert(
                0,
                {
                    "at": event_time,
                    "event": f"人工决策配置 v{profile_version} 已更新；等待确认或重跑",
                },
            )

    return workspace


def update_decision_profile(
    workspace_id: str,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    current = workspace.get("metadata", {}).get("decision_profile", {})
    cleaned = _validate_decision_profile(candidate, workspace["nodes"], workspace)
    cleaned["version"] = int(current.get("version", 0)) + 1
    cleaned["updatedAt"] = _now()
    workspace["metadata"]["decision_profile"] = cleaned
    workspace = _apply_decision_profile_to_workspace(
        workspace,
        mark_downstream=True,
    )
    return save_workbench_workspace(workspace_id, workspace)


def decision_catalog(workspace: dict[str, Any]) -> dict[str, Any]:
    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace))
    strategy = _load_json(workspace_strategy_path(workspace))
    manifest = _load_json(_workspace_manifest_path(workspace))
    visual = _load_json(VISUAL_REFERENCES_PATH)
    recommended = _validate_decision_profile(
        _default_decision_profile(
            [node["id"] for node in workspace["nodes"] if node["type"] == "ConceptNode"],
            workspace,
        ),
        workspace["nodes"],
        workspace,
    )
    return {
        "cultureRecords": [
            {
                "id": item.get("culture_id", ""),
                "name": item.get("culture_name", ""),
                "category": item.get("category", ""),
                "region": item.get("region", [])[:4],
                "crafts": item.get("crafts", [])[:5],
                "patterns": item.get("patterns", [])[:6],
                "boundaries": item.get("cultural_taboos", [])[:3],
                "sourceRefs": item.get("source_refs", [])[:8],
            }
            for item in culture.get("records", [])
        ],
        "marketPlatforms": [
            {
                "id": platform,
                "status": manifest.get("market_platforms", {})
                .get(platform, {})
                .get("status", "unavailable"),
                "sampleSize": int(hotness.get("platform_sample_sizes", {}).get(platform, 0)),
            }
            for platform in MARKET_PLATFORMS
        ],
        "productForms": [
            {
                "id": item.get("product_form", ""),
                "rank": item.get("rank", 0),
                "score": item.get("cross_platform_hot_score", 0),
                "sampleSize": item.get("sample_size", 0),
                "coverage": item.get("platform_coverage", 0),
            }
            for item in hotness.get("ranking", [])[:10]
        ],
        "opportunities": [
            {
                "id": item.get("opportunity_id", ""),
                "cultureElement": item.get("culture_element", ""),
                "trendElement": item.get("trend_element", ""),
                "systemScore": item.get("overall_score", 0),
                "verification": item.get("verification", {}).get("status", ""),
                "culturalRisk": item.get("cultural_risk", 0),
                "scores": {field: item.get(field, 0) for field in SCORE_FIELDS},
                "evidenceRefs": item.get("evidence_refs", []),
            }
            for item in strategy.get("opportunity_signals", [])
            if item.get("verification", {}).get("status") != "rejected"
        ],
        "visualReferences": [
            {
                "id": item.get("visual_id", ""),
                "title": item.get("title", ""),
                "region": item.get("region", ""),
                "subjectType": item.get("subject_type", ""),
                "rightsStatus": item.get("rights_status", "reference_only"),
            }
            for item in visual.get("references", [])
        ],
        "concepts": [
            {
                "id": node["id"],
                "label": node["data"].get("label", node["id"]),
                "title": node["data"].get("title", ""),
                "imageUrl": node["data"].get("imageUrl", ""),
            }
            for node in workspace["nodes"]
            if node["type"] == "ConceptNode"
        ],
        "scoreFields": list(SCORE_FIELDS),
        "visualSizes": list(VISUAL_SIZES),
        "posterThemes": list(POSTER_THEMES),
        "posterSections": list(POSTER_SECTIONS),
        "recommendedProfile": recommended,
    }


def update_design_brief(workspace_id: str, brief: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(brief, dict):
        raise TypeError("brief must be a JSON object")
    workspace = load_workbench_workspace(workspace_id)
    brief_node = next(
        (node for node in workspace["nodes"] if node["type"] == "DesignBriefNode"),
        None,
    )
    if brief_node is None:
        raise ValueError("工作区中没有 DesignBriefNode。")
    allowed_strings = ("title", "objective", "audience", "productType", "factoryBoundary")
    cleaned: dict[str, Any] = {}
    for key in allowed_strings:
        value = str(brief.get(key, "")).strip()
        if len(value) > 4000:
            raise ValueError(f"brief.{key} 超过 4000 字符。")
        cleaned[key] = value
    for key in ("scenarios", "style", "constraints"):
        values = brief.get(key, [])
        if not isinstance(values, list) or len(values) > 30:
            raise ValueError(f"brief.{key} 必须为不超过 30 项的数组。")
        cleaned[key] = [str(item).strip()[:500] for item in values if str(item).strip()]

    version = int(brief_node["data"].get("version", 0)) + 1
    brief_node["data"].update(
        {
            "brief": cleaned,
            "title": cleaned["title"],
            "summary": cleaned["objective"],
            "version": version,
            "status": "success",
        }
    )
    brief_node["data"].setdefault("history", []).insert(
        0, {"at": _now(), "event": f"保存任务书 v{version}；下游已标记 stale"}
    )
    descendants = _descendants(workspace, brief_node["id"])
    for node in workspace["nodes"]:
        if node["id"] in descendants:
            node["data"]["status"] = "stale"
            node["data"].setdefault("history", []).insert(
                0, {"at": _now(), "event": f"因任务书 v{version} 更新而待重跑"}
            )
    workspace["metadata"]["brief_version"] = version
    return save_workbench_workspace(workspace_id, workspace)


def set_active_concept(workspace_id: str, concept_id: str) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    concepts = [node for node in workspace["nodes"] if node["type"] == "ConceptNode"]
    if concept_id not in {node["id"] for node in concepts}:
        raise ValueError("指定概念不存在。")
    for node in concepts:
        node["data"]["active"] = node["id"] == concept_id
    workspace["metadata"]["selected_concept_id"] = concept_id
    workspace["metadata"]["decision_profile"]["activeConceptId"] = concept_id
    workspace["metadata"]["decision_profile"]["updatedAt"] = _now()
    poster = next(
        (node for node in workspace["nodes"] if node["type"] == "PosterBoardNode"),
        None,
    )
    if poster:
        poster["data"]["status"] = "stale"
        poster["data"].setdefault("history", []).insert(
            0, {"at": _now(), "event": f"切换为 {concept_id}，海报待刷新"}
        )
    return save_workbench_workspace(workspace_id, workspace)


def duplicate_concept(workspace_id: str, concept_id: str) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    source = next(
        (
            node
            for node in workspace["nodes"]
            if node["type"] == "ConceptNode" and node["id"] == concept_id
        ),
        None,
    )
    if source is None:
        raise ValueError("指定概念不存在。")
    concept_count = sum(node["type"] == "ConceptNode" for node in workspace["nodes"])
    if concept_count >= 12:
        raise ValueError("单个工作区最多保留 12 个概念方向。")
    clone = copy.deepcopy(source)
    clone_id = f"concept-{uuid.uuid4().hex[:8]}"
    clone["id"] = clone_id
    clone["position"] = {
        "x": float(source["position"]["x"]) + 70,
        "y": float(source["position"]["y"]) + 70,
    }
    clone["data"]["label"] = f"概念 {chr(65 + concept_count)}"
    clone["data"]["eyebrow"] = f"CONCEPT {chr(65 + concept_count)}"
    clone["data"]["title"] = f"{source['data'].get('title', '概念')} · 复制"
    clone["data"]["active"] = False
    clone["data"]["status"] = "cached" if clone["data"].get("imageUrl") else "idle"
    clone["data"]["history"] = [{"at": _now(), "event": f"从 {concept_id} 复制，等待独立迭代"}]
    workspace["nodes"].append(clone)
    workspace["edges"].extend(
        [
            _edge(
                f"visual-{clone_id}",
                "visual",
                clone_id,
                f"方向 {chr(65 + concept_count)}",
            ),
            _edge(f"{clone_id}-poster", clone_id, "poster", "候选"),
        ]
    )
    workspace["selected_node_id"] = clone_id
    return save_workbench_workspace(workspace_id, workspace)


def regenerate_concept(workspace_id: str, concept_id: str) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    concept = next(
        (
            node
            for node in workspace["nodes"]
            if node["type"] == "ConceptNode" and node["id"] == concept_id
        ),
        None,
    )
    if concept is None:
        raise ValueError("指定概念不存在。")
    adapter = ImageGenerationAdapter()
    provider = adapter.status()
    if not provider["configured"]:
        concept["data"]["status"] = "warning"
        concept["data"].setdefault("history", []).insert(
            0, {"at": _now(), "event": provider["detail"]}
        )
        return save_workbench_workspace(workspace_id, workspace)
    version = int(concept["data"].get("version", 0)) + 1
    filename = f"{concept_id}-v{version}.png"
    prompt = str(concept["data"].get("prompt", ""))
    prompt_suffix = str(concept["data"].get("decisionPromptSuffix", "")).strip()
    if prompt_suffix:
        prompt = f"{prompt}\n{prompt_suffix}"
    image_size = workspace["metadata"]["decision_profile"]["visualDirection"]["imageSize"]
    try:
        result = adapter.generate(
            prompt,
            GENERATED_DIR / workspace_id / filename,
            size=image_size,
        )
    except Exception as exc:
        concept["data"]["status"] = "error"
        concept["data"].setdefault("history", []).insert(
            0, {"at": _now(), "event": "单概念重生成失败；请检查图像服务"}
        )
        save_workbench_workspace(workspace_id, workspace)
        raise RuntimeError("概念重生成失败，请检查 provider、模型、配额与接口兼容性。") from exc
    concept["data"].update(
        {
            "imageUrl": f"/assets/workbench/{workspace_id}/{filename}",
            "status": "success",
            "version": version,
            "generation": result,
        }
    )
    concept["data"].setdefault("history", []).insert(
        0, {"at": _now(), "event": f"独立重生成 {filename}"}
    )
    poster = next(
        (node for node in workspace["nodes"] if node["type"] == "PosterBoardNode"),
        None,
    )
    if poster and concept["data"].get("active"):
        poster["data"]["status"] = "stale"
    return save_workbench_workspace(workspace_id, workspace)


def generate_more_concept(workspace_id: str, concept_id: str) -> dict[str, Any]:
    workspace = duplicate_concept(workspace_id, concept_id)
    clone_id = str(workspace["selected_node_id"])
    clone = next(node for node in workspace["nodes"] if node["id"] == clone_id)
    clone["data"].update(
        {
            "title": str(clone["data"].get("title", "概念")).replace(" · 复制", " · 新方向"),
            "imageUrl": "",
            "version": 0,
            "status": "idle",
        }
    )
    clone["data"]["history"] = [{"at": _now(), "event": f"从 {concept_id} 建立新生成方向"}]
    save_workbench_workspace(workspace_id, workspace)
    if ImageGenerationAdapter().status()["configured"]:
        return regenerate_concept(workspace_id, clone_id)
    clone["data"]["status"] = "warning"
    clone["data"]["history"].insert(
        0, {"at": _now(), "event": "图像服务未配置；新方向已建立但未生成图片"}
    )
    return save_workbench_workspace(workspace_id, workspace)


def _validate_brief_node(node: dict[str, Any]) -> None:
    brief = node.get("data", {}).get("brief")
    if not isinstance(brief, dict):
        raise ValueError("设计任务书不存在，不能运行。")  # noqa: TRY004 - API value error
    required = ("title", "objective", "audience", "productType", "factoryBoundary")
    missing = [key for key in required if not str(brief.get(key, "")).strip()]
    if missing:
        raise ValueError("设计任务书缺少字段：" + "、".join(missing))


def _concept_hero_path(workspace_id: str, image_url: str) -> Path | None:
    prefix = f"/assets/workbench/{workspace_id}/"
    if not image_url.startswith(prefix):
        return None
    filename = image_url.removeprefix(prefix)
    if not filename or Path(filename).name != filename:
        return None
    candidates = (
        GENERATED_DIR / workspace_id / filename,
        BUNDLED_GENERATED_DIR / workspace_id / filename,
    )
    return next((path for path in candidates if path.is_file()), None)


def _render_workspace_poster(
    workspace: dict[str, Any],
    node: dict[str, Any],
) -> None:
    package = DesignPackage.model_validate(_load_json(_workspace_design_path(workspace)))
    poster = node.get("data", {}).get("poster", {})
    if isinstance(poster, dict):
        title = str(poster.get("title", "")).strip()
        subtitle = str(poster.get("subtitle", "")).strip()
        if title:
            package.poster_request.exact_copy["title"] = title
        if subtitle:
            package.poster_request.exact_copy["subtitle"] = subtitle
    active = next(
        (
            item
            for item in workspace["nodes"]
            if item["type"] == "ConceptNode" and item["data"].get("active")
        ),
        None,
    )
    hero_path = _concept_hero_path(
        workspace["workspace_id"],
        str(active.get("data", {}).get("imageUrl", "")) if active else "",
    )
    version = int(node["data"].get("version", 0)) + 1
    filename = f"poster-v{version}.png"
    output_path = GENERATED_DIR / workspace["workspace_id"] / filename
    render_manifest, render_status = render_design_poster(
        package,
        output_path,
        hero_path,
        generated_now=True,
    )
    _atomic_json(
        output_path.with_suffix(".manifest.json"),
        render_manifest.model_dump(mode="json"),
    )
    node["data"].update(
        {
            "imageUrl": f"/assets/workbench/{workspace['workspace_id']}/{filename}",
            "status": "success",
            "version": version,
            "generation": {
                "engine": render_status.engine,
                "mode": render_status.mode,
                "generatedAt": _now(),
            },
        }
    )


def run_workbench_node(workspace_id: str, node_id: str) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    node = next((item for item in workspace["nodes"] if item["id"] == node_id), None)
    if node is None:
        raise ValueError("指定节点不存在。")
    node["data"]["status"] = "running"
    if node["type"] in {"CultureGraphNode", "MarketRadarNode", "StrategyNode"}:
        node["data"]["status"] = "error"
        node["data"].setdefault("history", []).insert(
            0,
            {
                "at": _now(),
                "event": "已阻止用旧文件冒充新运行；请启动严格实时研究任务",
            },
        )
        save_workbench_workspace(workspace_id, workspace)
        raise RuntimeError(
            "研究节点必须通过“实时运行”执行知识检索、四平台采集与模型策划；"
            "系统不会把读取旧文件标成新运行成功。"
        )
    if node["type"] == "DesignBriefNode":
        try:
            _validate_brief_node(node)
        except Exception:
            node["data"]["status"] = "error"
            save_workbench_workspace(workspace_id, workspace)
            raise
        node["data"]["status"] = "success"
        node["data"].setdefault("history", []).insert(
            0,
            {"at": _now(), "event": "任务书服务端契约校验通过；未伪造生成调用"},
        )
        return save_workbench_workspace(workspace_id, workspace)
    if node["type"] == "ConceptNode":
        return regenerate_concept(workspace_id, node_id)
    if node["type"] == "PosterBoardNode":
        try:
            _render_workspace_poster(workspace, node)
        except Exception as exc:
            node["data"]["status"] = "error"
            node["data"].setdefault("history", []).insert(
                0, {"at": _now(), "event": "海报渲染失败；没有复用旧图冒充新版本"}
            )
            save_workbench_workspace(workspace_id, workspace)
            raise RuntimeError("海报渲染失败，请检查设计包和概念资产。") from exc
    elif node["type"] == "VisualGenerationNode":
        adapter = ImageGenerationAdapter()
        provider = adapter.status()
        node["data"]["provider"] = provider
        if not provider["configured"]:
            node["data"]["status"] = "warning"
            node["data"].setdefault("history", []).insert(
                0, {"at": _now(), "event": provider["detail"]}
            )
            return save_workbench_workspace(workspace_id, workspace)
        try:
            concept_nodes = [
                item
                for item in workspace["nodes"]
                if item["type"] == "ConceptNode" and item["data"].get("inComparison", True)
            ]
            for concept in concept_nodes:
                prompt = str(concept["data"].get("prompt", ""))
                prompt_suffix = str(concept["data"].get("decisionPromptSuffix", "")).strip()
                if prompt_suffix:
                    prompt = f"{prompt}\n{prompt_suffix}"
                filename = f"{concept['id']}-v{int(concept['data'].get('version', 0)) + 1}.png"
                output_path = GENERATED_DIR / workspace_id / filename
                result = adapter.generate(
                    prompt,
                    output_path,
                    size=str(node["data"].get("size", "1024x1024")),
                )
                concept["data"].update(
                    {
                        "imageUrl": f"/assets/workbench/{workspace_id}/{filename}",
                        "status": "success",
                        "version": int(concept["data"].get("version", 0)) + 1,
                        "generation": result,
                    }
                )
                concept["data"].setdefault("history", []).insert(
                    0, {"at": _now(), "event": f"生成 {filename}"}
                )
            node["data"]["status"] = "success"
        except Exception as exc:
            node["data"]["status"] = "error"
            node["data"].setdefault("history", []).insert(
                0, {"at": _now(), "event": "图像生成调用失败；请检查模型、配额与接口兼容性"}
            )
            save_workbench_workspace(workspace_id, workspace)
            raise RuntimeError(
                "图像生成服务调用失败，请检查 provider、模型、配额与接口兼容性。"
            ) from exc
    node["data"].setdefault("history", []).insert(
        0, {"at": _now(), "event": "节点产生并保存了新的可核验结果"}
    )
    return save_workbench_workspace(workspace_id, workspace)


def knowledge_center(workspace: dict[str, Any] | None = None) -> dict[str, Any]:
    workspace = workspace or {}
    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace))
    manifest = _load_json(_workspace_manifest_path(workspace))
    records = []
    for item in culture.get("records", []):
        records.append(
            {
                "id": item.get("culture_id", ""),
                "name": item.get("culture_name", ""),
                "category": item.get("category", ""),
                "region": item.get("region", [])[:4],
                "crafts": item.get("crafts", [])[:6],
                "patterns": item.get("patterns", [])[:6],
                "boundaries": item.get("cultural_taboos", [])[:2],
                "sourceRefs": item.get("source_refs", [])[:8],
            }
        )
    return {
        "culture": {
            "recordCount": len(records),
            "sourceCount": len(culture.get("sources", [])),
            "records": records,
        },
        "market": {
            "status": manifest.get("market_source", {}).get("status", "unavailable"),
            "sampleSize": hotness.get("total_sample_size", 0),
            "platforms": manifest.get("market_platforms", {}),
            "ranking": [
                {
                    "rank": item.get("rank", 0),
                    "name": item.get("product_form", ""),
                    "score": item.get("cross_platform_hot_score", 0),
                    "coverage": item.get("platform_coverage", 0),
                    "sampleSize": item.get("sample_size", 0),
                }
                for item in hotness.get("ranking", [])[:10]
            ],
        },
    }


def _citation_catalog(
    workspace: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    workspace = workspace or {}
    catalog: dict[str, dict[str, Any]] = {}

    def add_source(item: dict[str, Any], kind: str) -> None:
        source_id = str(item.get("source_id", "")).strip()
        if not source_id:
            return
        catalog[source_id] = {
            "id": source_id,
            "kind": kind,
            "title": item.get("source_title", source_id),
            "publisher": item.get("publisher", ""),
            "sourceType": item.get("source_type", ""),
            "url": item.get("source_url", ""),
            "publishedAt": item.get("published_at", ""),
            "retrievedAt": item.get("retrieved_at", ""),
            "supports": item.get("supports", []),
            "rightsStatus": "public_source",
        }

    culture = _load_json(CULTURE_PATH)
    for item in culture.get("sources", []):
        add_source(item, "culture")

    market = _load_json(MARKET_VERIFIED_PATH)
    for item in market.get("sources", []):
        add_source(item, "market")

    visual = _load_json(VISUAL_REFERENCES_PATH)
    for item in visual.get("references", []):
        visual_id = str(item.get("visual_id", "")).strip()
        if not visual_id:
            continue
        catalog[visual_id] = {
            "id": visual_id,
            "kind": "visual_reference",
            "title": item.get("title", visual_id),
            "publisher": "馆藏公开页面",
            "sourceType": item.get("subject_type", "视觉研究参考"),
            "url": item.get("source_url", ""),
            "publishedAt": "",
            "retrievedAt": culture.get("updated_at", ""),
            "supports": item.get("design_relevance", []),
            "rightsStatus": item.get("rights_status", "reference_only"),
            "rightsNote": item.get("rights_note", ""),
        }

    promoted_evidence = _research_artifact_path(
        workspace,
        "market_evidence.json",
        Path("__missing_market_evidence__"),
    )
    evidence_path: Path | None = promoted_evidence if promoted_evidence.is_file() else None
    if evidence_path is None:
        evidence_candidates: list[tuple[int, str, Path]] = []
        for path in (ROOT_DIR / "data" / "market" / "derived").glob("market_evidence_*.json"):
            try:
                payload = _load_json(path)
            except (OSError, ValueError):
                continue
            records = [
                item
                for item in payload.get("records", [])
                if item.get("platform") in MARKET_PLATFORMS
                and item.get("evidence_type") == "social_signal"
            ]
            evidence_candidates.append((len(records), str(payload.get("generated_at", "")), path))
        if evidence_candidates:
            evidence_path = max(
                evidence_candidates,
                key=lambda item: (item[0], item[1]),
            )[2]
    if evidence_path is not None:
        evidence = _load_json(evidence_path)
        for item in evidence.get("records", []):
            source_id = str(item.get("source_ref", "")).strip()
            if not source_id or source_id in catalog:
                continue
            platform = str(item.get("platform", "")).upper()
            title = str(item.get("title", "")).strip()
            if not title:
                title = str(item.get("content", "")).strip().replace("\n", " ")[:88]
            catalog[source_id] = {
                "id": source_id,
                "kind": "platform_record",
                "title": title or f"{platform} 市场记录",
                "publisher": platform,
                "sourceType": "用户授权的平台历史快照",
                "url": item.get("url", ""),
                "publishedAt": item.get("published_at", ""),
                "retrievedAt": item.get("retrieved_at", ""),
                "supports": [
                    value
                    for value in (
                        item.get("product_form", ""),
                        item.get("search_keyword", ""),
                        f"平台内热度 {item.get('platform_hot_score', 0)}",
                    )
                    if value
                ],
                "rightsStatus": "evidence_link_only",
            }
    return catalog


def _market_post_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourceRef": item.get("source_ref", ""),
        "platform": item.get("platform", ""),
        "title": item.get("title", "") or str(item.get("content", "")).replace("\n", " ")[:100],
        "publishedAt": item.get("published_at", ""),
        "retrievedAt": item.get("retrieved_at", ""),
        "url": item.get("url", ""),
        "productForm": item.get("product_form", ""),
        "searchKeyword": item.get("search_keyword", ""),
        "engagement": {
            "likes": item.get("likes", 0),
            "favorites": item.get("favorites", 0),
            "comments": item.get("comments", 0),
            "shares": item.get("shares", 0),
            "views": item.get("views", 0),
        },
        "platformHotScore": item.get("platform_hot_score", 0),
        "viralScore": item.get("viral_score", 0),
        "qualityScore": item.get("evidence_quality_score", 0),
        "qualityReasons": item.get("evidence_quality_reasons", []),
    }


def node_detail(
    workspace_id: str,
    node_id: str,
) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    node = next((item for item in workspace["nodes"] if item["id"] == node_id), None)
    if node is None:
        raise FileNotFoundError(f"节点不存在：{node_id}")

    upstream_ids = {
        str(edge.get("source", ""))
        for edge in workspace.get("edges", [])
        if edge.get("target") == node_id
    }
    downstream_ids = {
        str(edge.get("target", ""))
        for edge in workspace.get("edges", [])
        if edge.get("source") == node_id
    }
    related_nodes = [
        {
            "id": item["id"],
            "type": item["type"],
            "title": item["data"].get("title", ""),
            "status": item["data"].get("status", "idle"),
            "relation": ("upstream" if item["id"] in upstream_ids else "downstream"),
        }
        for item in workspace["nodes"]
        if item["id"] in upstream_ids or item["id"] in downstream_ids
    ]

    culture = _load_json(CULTURE_PATH)
    hotness = _load_json(_workspace_hotness_path(workspace))
    strategy = _load_json(workspace_strategy_path(workspace))
    design = _load_json(_workspace_design_path(workspace))
    manifest = _load_json(_workspace_manifest_path(workspace))
    visual = _load_json(VISUAL_REFERENCES_PATH)
    design_visual_refs = list(
        dict.fromkeys(
            str(ref)
            for item in design.get("cultural_elements", [])
            for ref in item.get("reference_visual_ids", [])
            if ref
        )
    )
    content: dict[str, Any]
    citation_refs = list(node.get("data", {}).get("sourceRefs", []))

    if node["type"] == "CultureGraphNode":
        records = culture.get("records", [])
        citation_refs = list(
            dict.fromkeys(ref for item in records for ref in item.get("source_refs", []))
        )
        content = {
            "records": records,
            "visualReferences": visual.get("references", []),
            "scope": culture.get("scope", {}),
            "methodology": culture.get("methodology", {}),
        }
    elif node["type"] == "MarketRadarNode":
        ranking_with_posts = hotness.get("ranking", [])[:10]
        posts = [
            _market_post_summary(post)
            for item in ranking_with_posts
            for post in item.get("representative_posts", [])[:4]
        ]
        ranking = [
            {key: value for key, value in item.items() if key != "representative_posts"}
            for item in ranking_with_posts
        ]
        citation_refs = list(
            dict.fromkeys(
                [post["sourceRef"] for post in posts if post.get("sourceRef")]
                + [
                    item.get("source_id", "")
                    for item in _load_json(MARKET_VERIFIED_PATH).get("sources", [])
                ]
            )
        )
        content = {
            "status": manifest.get("market_source", {}).get("status", "unavailable"),
            "platforms": manifest.get("market_platforms", {}),
            "sampleSize": hotness.get("total_sample_size", 0),
            "platformSampleSizes": hotness.get("platform_sample_sizes", {}),
            "ranking": ranking,
            "representativePosts": posts,
            "methodology": hotness.get("methodology", {}),
            "generatedAt": hotness.get("generated_at", ""),
        }
    elif node["type"] == "StrategyNode":
        opportunities = strategy.get("opportunity_signals", [])
        citation_refs = list(
            dict.fromkeys(ref for item in opportunities for ref in item.get("evidence_refs", []))
        )
        content = {
            "opportunities": opportunities,
            "scoring": strategy.get("metadata", {}).get("opportunity_scoring", {}),
            "evidenceSummary": strategy.get("evidence_summary", {}),
            "recommendedCategories": strategy.get("recommended_product_categories", []),
            "designKeywords": strategy.get("design_keywords", []),
            "culturalConstraints": strategy.get("cultural_constraints", []),
        }
    elif node["type"] == "DesignBriefNode":
        content = {
            "brief": node["data"].get("brief", {}),
            "selection": design.get("selection", {}),
            "product": design.get("product", {}),
            "reviewGates": design.get("cultural_review_gates", []),
            "engineeringGates": design.get("engineering_review_gates", []),
        }
    elif node["type"] == "VisualGenerationNode":
        citation_refs = list(dict.fromkeys(citation_refs + design_visual_refs))
        content = {
            "provider": ImageGenerationAdapter().status(),
            "prompts": node["data"].get("prompts", []),
            "concepts": [item for item in workspace["nodes"] if item["type"] == "ConceptNode"],
            "posterRequest": design.get("poster_request", {}),
        }

    elif node["type"] == "ConceptNode":
        citation_refs = list(dict.fromkeys(citation_refs + design_visual_refs))
        content = {
            "concept": node,
            "product": design.get("product", {}),
            "culturalElements": design.get("cultural_elements", []),
            "manufacturing": design.get("manufacturing", {}),
            "validation": design.get("validation", {}),
        }
    else:
        citation_refs = list(dict.fromkeys(citation_refs + design_visual_refs))
        active_concept = next(
            (
                item
                for item in workspace["nodes"]
                if item["type"] == "ConceptNode" and item["data"].get("active")
            ),
            None,
        )
        content = {
            "poster": node["data"].get("poster", {}),
            "activeConcept": active_concept,
            "product": design.get("product", {}),
            "culturalElements": design.get("cultural_elements", []),
            "manufacturing": design.get("manufacturing", {}),
            "posterRequest": design.get("poster_request", {}),
        }

    content["decisionProfile"] = workspace.get("metadata", {}).get("decision_profile", {})
    content["decisionOutput"] = workspace.get("metadata", {}).get("decision_output", {})

    catalog = _citation_catalog(workspace)
    citations = [catalog[ref] for ref in citation_refs if ref in catalog]
    missing_refs = [ref for ref in citation_refs if ref and ref not in catalog]
    return {
        "workspace": {
            "id": workspace["workspace_id"],
            "name": workspace["name"],
            "updatedAt": workspace["updated_at"],
            "topic": workspace.get("metadata", {}).get("topic", ""),
            "sourceRunId": workspace.get("metadata", {}).get("source_run_id", ""),
        },
        "node": node,
        "relatedNodes": related_nodes,
        "content": content,
        "citations": citations,
        "citationAudit": {
            "requested": len(citation_refs),
            "resolved": len(citations),
            "missing": missing_refs,
        },
        "boundary": workspace.get("metadata", {}).get("stop_before", ""),
    }


def workbench_bootstrap(workspace_id: str = DEFAULT_WORKSPACE_ID) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    return {
        "workspace": workspace,
        "workspaces": list_workbench_workspaces(),
        "knowledge": knowledge_center(workspace),
        "decisionCatalog": decision_catalog(workspace),
        "imageProvider": ImageGenerationAdapter().status(),
        "nodeTypes": list(NODE_TYPES),
        "statuses": list(NODE_STATUSES),
    }


def workbench_design_package(workspace_id: str) -> dict[str, Any]:
    workspace = load_workbench_workspace(workspace_id)
    path = _workspace_design_path(workspace)
    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace["name"],
        "source_run_id": workspace.get("metadata", {}).get("source_run_id", ""),
        "research_verified_at": workspace.get("metadata", {}).get("research_verified_at", ""),
        "artifact": path.name,
        "design": _load_json(path),
    }
