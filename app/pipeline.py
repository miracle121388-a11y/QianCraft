from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.adapters.lightrag_adapter import LightRAGAdapter
from app.adapters.media_crawler_adapter import MediaCrawlerAdapter
from app.config import Settings
from app.designer import DesignAgent, render_design_package_markdown, render_design_poster
from app.schemas import (
    BenchmarkCase,
    DemoRequest,
    DesignerHandoff,
    MarketPlatformStatus,
    MarketSourceStatus,
    PreDesignStrategy,
    RunManifest,
    VisualReferencePack,
)
from app.strategist.strategist import Strategist


async def run_pipeline(
    request: DemoRequest,
    settings: Settings,
    design_hero_path: Path | None = None,
) -> tuple[PreDesignStrategy, RunManifest]:
    started_at = datetime.now(UTC)
    run_id = f"{started_at.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"

    culture_adapter = LightRAGAdapter(settings)
    culture_task = culture_adapter.query(request.topic)
    market_task = MediaCrawlerAdapter(settings).research(request.topic)
    (culture_dna, culture_status), (trend_dna, market_status) = await asyncio.gather(
        culture_task, market_task
    )
    benchmarks = _load_benchmarks(settings.benchmark_path)
    visual_pack = culture_adapter.build_visual_reference_pack(request.topic)
    strategy, strategist_status = await Strategist(settings, culture_adapter).create_strategy(
        request, culture_dna, trend_dna, benchmarks, visual_pack
    )

    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.demo_cache_dir.mkdir(parents=True, exist_ok=True)
    json_path = settings.outputs_dir / "pre_design_strategy.json"
    markdown_path = settings.outputs_dir / "pre_design_strategy.md"
    visual_json_path = settings.outputs_dir / "visual_reference_pack.json"
    visual_markdown_path = settings.outputs_dir / "visual_reference_pack.md"
    handoff_json_path = settings.outputs_dir / "designer_handoff.json"
    handoff_markdown_path = settings.outputs_dir / "designer_handoff.md"
    design_json_path = settings.outputs_dir / "design_specification.json"
    design_markdown_path = settings.outputs_dir / "design_specification.md"
    poster_request_path = settings.outputs_dir / "poster_render_request.json"
    design_poster_path = settings.outputs_dir / "design_poster.png"
    design_render_manifest_path = settings.outputs_dir / "design_render_manifest.json"
    manifest_path = settings.outputs_dir / "run_manifest.json"
    strategy_payload = strategy.model_dump(mode="json")
    _atomic_write(json_path, json.dumps(strategy_payload, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(
        markdown_path,
        render_strategy_markdown(
            strategy, [culture_status, market_status, strategist_status]
        ),
    )
    _atomic_write(
        visual_json_path,
        json.dumps(visual_pack.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    _atomic_write(visual_markdown_path, render_visual_reference_pack_markdown(visual_pack))
    _atomic_write(
        handoff_json_path,
        json.dumps(
            strategy.handoff_to_designer.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    _atomic_write(
        handoff_markdown_path,
        render_designer_handoff_markdown(strategy.handoff_to_designer),
    )
    design_package, design_status = DesignAgent(settings).create_from_file(handoff_json_path)
    _atomic_write(
        design_json_path,
        json.dumps(design_package.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    _atomic_write(design_markdown_path, render_design_package_markdown(design_package))
    _atomic_write(
        poster_request_path,
        json.dumps(
            design_package.poster_request.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    render_manifest, poster_status = render_design_poster(
        design_package,
        design_poster_path,
        design_hero_path,
    )
    _atomic_write(
        design_render_manifest_path,
        json.dumps(render_manifest.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
    )
    _atomic_write(
        settings.demo_cache_dir / "pre_design_strategy.json",
        json.dumps(strategy_payload, ensure_ascii=False, indent=2) + "\n",
    )

    finished_at = datetime.now(UTC)
    manifest = RunManifest(
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        request=request,
        components=[
            culture_status,
            market_status,
            strategist_status,
            design_status,
            poster_status,
        ],
        market_source=MarketSourceStatus.model_validate(
            trend_dna.retrieval["market_source"]
        ),
        market_platforms={
            platform: MarketPlatformStatus.model_validate(source)
            for platform, source in trend_dna.retrieval["market_platforms"].items()
        },
        outputs={
            "strategy_json": str(json_path.resolve()),
            "strategy_markdown": str(markdown_path.resolve()),
            "visual_reference_json": str(visual_json_path.resolve()),
            "visual_reference_markdown": str(visual_markdown_path.resolve()),
            "designer_handoff_json": str(handoff_json_path.resolve()),
            "designer_handoff_markdown": str(handoff_markdown_path.resolve()),
            "product_form_hotness": trend_dna.retrieval[
                "product_form_hotness_path"
            ],
            "design_specification_json": str(design_json_path.resolve()),
            "design_specification_markdown": str(design_markdown_path.resolve()),
            "poster_render_request": str(poster_request_path.resolve()),
            "design_poster": str(design_poster_path.resolve()),
            "design_render_manifest": str(design_render_manifest_path.resolve()),
            "manifest": str(manifest_path.resolve()),
        },
        source_snapshot_date=_source_snapshot_date(strategy),
    )
    _atomic_write(
        manifest_path,
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    return strategy, manifest


def _load_benchmarks(path: Path) -> list[BenchmarkCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [BenchmarkCase.model_validate(item) for item in payload.get("cases", [])]


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _source_snapshot_date(strategy: PreDesignStrategy) -> str:
    dates = [
        source.retrieved_at
        for source in [*strategy.culture_dna.source_refs, *strategy.trend_dna.source_refs]
        if source.retrieved_at
    ]
    return max(dates, default=datetime.now(UTC).date().isoformat())


def render_strategy_markdown(strategy: PreDesignStrategy, statuses: list[Any]) -> str:
    project = strategy.project
    culture = strategy.culture_dna
    trend = strategy.trend_dna
    lines = [
        "# QianCraft 前设计策略｜贵州苗绣",
        "",
        "> 本文件止于设计前策略：给出证据、机会关系和待验证问题，不给最终造型、尺寸、SKU或视觉终稿。",
        "",
        "## 1. 项目范围",
        "",
        f"- 主题：{project.get('topic', '')}",
        f"- 地域：{project.get('region', '')}",
        f"- 目标市场：{project.get('target_market', '')}",
        f"- 目标：{project.get('goal', '')}",
        "",
        "## 2. 运行状态与证据口径",
        "",
    ]
    for status in statuses:
        lines.append(
            f"- {status.component}：`{status.mode}`｜{status.engine}｜{status.detail}"
        )
    lines.extend(
        [
            "",
            "没有来源披露的点赞、收藏、评论和分享一律为 0；策划推断不冒充平台全量统计。",
            "",
            "## 3. Culture DNA",
            "",
            f"- 核心名称：{culture.culture_name}",
            f"- 地域：{'、'.join(culture.region)}",
            f"- 核心故事：{'；'.join(culture.core_stories[:8])}",
            f"- 核心价值：{'、'.join(culture.core_values[:12])}",
            "",
            "## 4. Visual DNA",
            "",
            f"- 图形/纹样：{'、'.join(culture.visual_dna.get('graphics', [])[:20])}",
            f"- 色彩：{'、'.join(culture.colors)}",
            f"- 材料：{'、'.join(culture.materials)}",
            f"- 工艺：{'、'.join(culture.crafts[:20])}",
            f"- 构图与触感：{'；'.join(culture.visual_features)}",
            "",
            "## 5. Semantic DNA",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in culture.semantic_dna)
    lines.extend(["", "## 6. Cultural Boundaries", "", "### 必须保留", ""])
    lines.extend(f"- {item}" for item in culture.cultural_boundary.get("must_keep", []))
    lines.extend(["", "### 可现代化", ""])
    lines.extend(f"- {item}" for item in culture.cultural_boundary.get("can_modernize", []))
    lines.extend(["", "### 避免", ""])
    lines.extend(f"- {item}" for item in culture.cultural_boundary.get("avoid", []))
    lines.extend(
        [
            "",
            "## 7. Trend DNA",
            "",
            f"- 时间窗：{trend.time_window}",
            f"- 样本：{trend.sample_size} 条；平台/来源类型：{'、'.join(trend.platforms)}",
            f"- 热门品类：{'、'.join(trend.hot_categories)}",
            (
                "- Top 10 产品形态："
                + (
                    "、".join(
                        f"#{item.rank} {item.product_form}({item.cross_platform_hot_score})"
                        for item in trend.hot_product_forms
                    )
                    or "尚无真实四平台样本，未生成排名"
                )
            ),
            (
                "- Top 5 优先形态："
                + ("、".join(trend.priority_product_forms) or "尚未生成")
            ),
            f"- 上升方向：{'；'.join(trend.rising_categories)}",
            f"- 情绪价值：{'、'.join(trend.emotional_values)}",
            f"- 白空间：{'；'.join(trend.white_space_opportunities)}",
            "",
            "## 8. Benchmark Cases",
            "",
            "| 案例 | 形态 | 可迁移启发 | 证据 |",
            "|---|---|---|---|",
        ]
    )
    for case in strategy.benchmark_cases:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(case.brand_or_institution),
                    _cell(case.product_category),
                    _cell("；".join(case.transferable_lessons)),
                    _cell("、".join(case.source_refs)),
                ]
            )
            + " |"
        )
    lines.extend(["", "## 9. Opportunity Signals", ""])
    for index, signal in enumerate(strategy.opportunity_signals, 1):
        lines.extend(
            [
                f"### {index}. {signal.culture_element} × {signal.trend_element}",
                "",
                f"- 关系：{signal.match_reason}",
                f"- 可探索品类：{'、'.join(signal.potential_product_categories)}",
                f"- 关键词：{'、'.join(signal.design_keywords)}",
                f"- 文化约束：{'；'.join(signal.cultural_constraints)}",
                f"- 证据：{'、'.join(signal.evidence_refs)}｜置信度：{signal.confidence_score}/100",
                (
                    f"- 评分：{signal.overall_score}/100（文化契合{signal.culture_fit}、"
                    f"市场拉力{signal.market_pull}、新颖度{signal.novelty}、视觉潜力"
                    f"{signal.visual_potential}、社交传播{signal.social_shareability}、"
                    f"产品可行性{signal.product_feasibility}、文化风险{signal.cultural_risk}）"
                ),
                (
                    f"- 二次核验：`{signal.verification.status}`｜"
                    f"{signal.verification.retrieval_mode}｜"
                    f"查询：{'、'.join(signal.verification.queries)}"
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## 10. 推荐方向与设计关键词",
            "",
            f"- 推荐品类：{'；'.join(strategy.recommended_product_categories)}",
            f"- 设计关键词：{'、'.join(strategy.design_keywords)}",
            "",
            "这些是待验证的方向，不是产品定案。下一阶段应先比较用户价值、社区意愿、材料可行性和收益机制。",
            "",
            "## 11. Designer Handoff 与下一步验证",
            "",
            f"- 交接状态：{'可进入概念设计' if strategy.handoff_to_designer.ready else '尚未就绪'}",
            "- 机器唯一事实源：`designer_handoff.json`；Markdown 由同一对象自动渲染。",
            "- 仅交接通过文化门槛的 Top 3：",
        ]
    )
    lines.extend(
        f"  - #{item.rank} {item.title}｜{item.overall_score}/100｜{item.verification.status}"
        for item in strategy.handoff_to_designer.priority_opportunities
    )
    lines.extend(
        [
            "- 待验证问题：",
        ]
    )
    lines.extend(
        f"  - {item}" for item in strategy.evidence_summary.get("unknowns_to_validate", [])
    )
    lines.extend(["", "### 来源索引", ""])
    all_sources = {source.source_id: source for source in culture.source_refs}
    all_sources.update({source.source_id: source for source in trend.source_refs})
    for source_id in sorted(all_sources):
        source = all_sources[source_id]
        label = source.source_title or source_id
        if source.source_url:
            lines.append(f"- [{source_id}] [{label}]({source.source_url}) — {source.publisher}")
        else:
            lines.append(f"- [{source_id}] {label} — {source.publisher}")
    return "\n".join(lines).rstrip() + "\n"


def render_visual_reference_pack_markdown(pack: VisualReferencePack) -> str:
    lines = [
        f"# QianCraft Visual Reference Pack｜{pack.topic}",
        "",
        "> 全部 reference_only 图像只用于文化与视觉研究；页面可访问不代表可复制或可商用。",
        "",
        "## 视觉参考",
        "",
    ]
    for item in pack.references:
        lines.extend(
            [
                f"### {item.visual_id}｜{item.title}",
                "",
                f"- 地域：{item.region}",
                f"- 工艺：{item.craft}",
                f"- 对象：{item.subject_type}",
                f"- 文化语境：{item.cultural_context}",
                f"- 来源：[{item.source_ref}] [{item.source_url}]({item.source_url})",
                f"- 图片直链（参考）：[{item.image_url}]({item.image_url})",
                f"- 权利状态：`{item.rights_status}`｜{item.rights_note}",
                f"- 可研究关系：{'、'.join(item.design_relevance)}",
                f"- 不可直接复制：{'；'.join(item.not_to_copy)}",
                "",
            ]
        )
    lines.extend(["## Pattern Primitives", ""])
    for primitive in pack.pattern_primitives:
        lines.extend(
            [
                f"### {primitive.primitive_id}｜{primitive.name}",
                "",
                f"- 来自：{'、'.join(primitive.derived_from)}",
                f"- 结构：{'、'.join(primitive.geometry)}",
                f"- 转译方向：{'；'.join(primitive.transformation_guidance)}",
                f"- 文化边界：{'；'.join(primitive.cultural_boundary)}",
                f"- 证据：{'、'.join(primitive.evidence_refs)}",
                "",
            ]
        )
    lines.extend(["## Color Palettes（无伪造 HEX）", ""])
    for palette in pack.color_palettes:
        lines.extend(
            [
                f"### {palette.palette_id}｜{palette.name}",
                "",
                f"- 颜色关系：{'、'.join(palette.colors)}",
                f"- 来源依据：{palette.source_basis}",
                f"- 证据：{'、'.join(palette.evidence_refs)}",
                f"- 说明：{'；'.join(palette.notes)}",
                "",
            ]
        )
    lines.extend(["## 方法与权利边界", ""])
    lines.extend(f"- {note}" for note in pack.methodology_notes)
    return "\n".join(lines).rstrip() + "\n"


def render_designer_handoff_markdown(handoff: DesignerHandoff) -> str:
    lines = [
        "# QianCraft Designer Handoff",
        "",
        "> 本文件由 `designer_handoff.json` 的同一 Pydantic 对象自动渲染；JSON 是机器唯一事实源。",
        "",
        "## Design Mission",
        "",
        f"- 目标：{handoff.design_mission.get('objective', '')}",
        f"- 用户：{handoff.design_mission.get('audience', '')}",
        f"- 成功标准：{'；'.join(handoff.design_mission.get('success_criteria', []))}",
        "",
        "## Creative Brief",
        "",
        handoff.creative_brief,
        "",
        "## Priority Opportunities（仅 Top 3）",
        "",
    ]
    for item in handoff.priority_opportunities:
        score = item.score_breakdown
        lines.extend(
            [
                f"### #{item.rank} {item.title}",
                "",
                f"- ID：`{item.opportunity_id}`",
                f"- 综合分：{item.overall_score}/100",
                (
                    "- 分项："
                    f"文化{score.get('culture_fit', 0)} / 市场{score.get('market_pull', 0)} / "
                    f"新颖{score.get('novelty', 0)} / 视觉{score.get('visual_potential', 0)} / "
                    f"传播{score.get('social_shareability', 0)} / "
                    f"可行{score.get('product_feasibility', 0)} / "
                    f"风险{score.get('cultural_risk', 0)}"
                ),
                f"- 二次核验：`{item.verification.status}`｜{item.verification.retrieval_mode}",
                f"- 为什么现在：{item.why_now}",
                f"- 可探索品类：{'、'.join(item.potential_product_categories)}",
                f"- 关键词：{'、'.join(item.design_keywords)}",
                f"- 文化约束：{'；'.join(item.cultural_constraints)}",
                f"- 证据：{'、'.join(item.evidence_refs)}",
                "",
            ]
        )
    lines.extend(["## Visual Reference Pack", ""])
    lines.append(
        f"- {len(handoff.visual_reference_pack.references)} 条参考、"
        f"{len(handoff.visual_reference_pack.pattern_primitives)} 个结构原语、"
        f"{len(handoff.visual_reference_pack.color_palettes)} 组文字色彩关系。"
    )
    lines.extend(["", "## Hard Constraints", ""])
    lines.extend(f"- {item}" for item in handoff.hard_constraints)
    lines.extend(["", "## Soft Direction", ""])
    lines.extend(f"- {item}" for item in handoff.soft_direction)
    lines.extend(["", "## Output Requirements", ""])
    lines.extend(
        f"- {item}" for item in handoff.output_requirements.get("deliverables", [])
    )
    lines.extend(["", "### 禁止", ""])
    lines.extend(f"- {item}" for item in handoff.output_requirements.get("prohibited", []))
    lines.extend(["", "## Evidence Refs", ""])
    lines.append("、".join(handoff.evidence_refs))
    return "\n".join(lines).rstrip() + "\n"


def _cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
