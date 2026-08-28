from __future__ import annotations

import json
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest
from PIL import Image

from app.adapters.lightrag_adapter import LightRAGAdapter
from app.adapters.media_crawler_adapter import (
    MARKET_PLATFORMS,
    UNIFIED_MARKET_KEYWORDS,
    XHS_MVP_KEYWORDS,
    MediaCrawlerAdapter,
)
from app.config import load_settings
from app.designer import DesignAgent
from app.pipeline import render_designer_handoff_markdown, run_pipeline
from app.schemas import (
    DemoRequest,
    DesignerHandoff,
    DesignPackage,
    DesignRenderManifest,
    MarketPost,
    TrendDNA,
)
from app.strategist.strategist import (
    _baseline_opportunities,
    _score_opportunities,
    _validated_opportunities,
)


def test_guizhou_graph_has_depth_and_traceability() -> None:
    settings = load_settings().with_mode("demo")
    payload = json.loads(settings.culture_graph_path.read_text(encoding="utf-8"))
    assert len(payload["records"]) >= 20
    assert len(payload["sources"]) >= 25
    source_ids = {source["source_id"] for source in payload["sources"]}
    for record in payload["records"]:
        assert record["culture_id"]
        assert record["source_refs"]
        assert set(record["source_refs"]) <= source_ids
        assert record["field_sources"]
        assert set(record["field_sources"]) <= set(record)
        assert all(
            set(field_refs) <= set(record["source_refs"])
            for field_refs in record["field_sources"].values()
        )


def test_miao_embroidery_retrieval_keeps_branch_differences() -> None:
    settings = load_settings().with_mode("demo")
    dna = LightRAGAdapter(settings).build_culture_dna("贵州苗绣")
    assert dna.retrieval["records_matched"] >= 4
    assert len(dna.branch_differences) >= 4
    assert {"C001", "C002", "C003"} <= {source.source_id for source in dna.source_refs}
    assert dna.cultural_boundary["must_keep"]


@pytest.mark.asyncio
async def test_market_fallback_is_honest(tmp_path) -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        market_raw_dir=tmp_path / "raw",
        market_derived_dir=tmp_path / "derived",
    )
    payload = json.loads(settings.market_signals_path.read_text(encoding="utf-8"))
    source_ids = {source["source_id"] for source in payload["sources"]}
    assert len(payload["sources"]) >= 12
    assert all(signal["source_ref"] in source_ids for signal in payload["signals"])
    assert all(
        signal.get("metrics_verified")
        or not any(
            signal.get(metric, 0) for metric in ("likes", "favorites", "comments", "shares")
        )
        for signal in payload["signals"]
    )
    trend, status = await MediaCrawlerAdapter(settings).research("贵州苗绣")
    assert status.mode == "cache"
    assert trend.sample_size == 0
    assert trend.platforms == list(MARKET_PLATFORMS)
    assert trend.hot_product_forms == []
    assert trend.priority_product_forms == []
    assert trend.retrieval["verified_baseline_count"] >= 12
    assert all(
        source["status"] == "unavailable"
        for source in trend.retrieval["market_platforms"].values()
    )
    assert all(
        post.metrics_verified or not any([post.likes, post.favorites, post.comments, post.shares])
        for post in trend.representative_cases
    )
    assert any("未登录" in note or "公开" in note for note in trend.methodology_notes)


def test_strategist_rejects_unknown_or_one_sided_evidence() -> None:
    baseline = _baseline_opportunities(DemoRequest())
    generated = {
        "opportunity_signals": [
            {
                **baseline[0].model_dump(),
                "culture_element": "不存在的生成建议",
                "evidence_refs": ["C004", "C999"],
            }
        ]
    }
    opportunities, accepted = _validated_opportunities(
        generated,
        {"C004", "M003"},
        baseline,
    )
    assert accepted == 0
    assert len(opportunities) == 8
    assert all(any(ref.startswith("C") for ref in item.evidence_refs) for item in opportunities)
    assert all(any(ref.startswith("M") for ref in item.evidence_refs) for item in opportunities)


@pytest.mark.asyncio
async def test_demo_pipeline_contract_and_outputs(tmp_path) -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        outputs_dir=tmp_path / "outputs",
        demo_cache_dir=tmp_path / "cache",
        market_raw_dir=tmp_path / "market" / "raw",
        market_derived_dir=tmp_path / "market" / "derived",
    )
    strategy, manifest = await run_pipeline(DemoRequest(), settings)
    assert len(strategy.opportunity_signals) >= 8
    allowed = set(strategy.metadata["allowed_evidence_refs"])
    assert all(set(signal.evidence_refs) <= allowed for signal in strategy.opportunity_signals)
    assert strategy.handoff_to_designer.ready
    assert strategy.metadata["final_design_generated"] is False
    component_modes = {status.component: status.mode for status in manifest.components}
    assert component_modes["culture_knowledge"] == "cache"
    assert component_modes["market_research"] == "cache"
    assert component_modes["strategist"] == "cache"
    assert component_modes["design_agent"] == "live"
    assert component_modes["poster_renderer"] == "cache"
    assert {status.component for status in manifest.components} >= {
        "design_agent",
        "poster_renderer",
    }
    for output in manifest.outputs.values():
        assert tmp_path in __import__("pathlib").Path(output).parents
    markdown = (tmp_path / "outputs" / "pre_design_strategy.md").read_text(encoding="utf-8")
    assert "## 9. Opportunity Signals" in markdown
    assert "## 11. Designer Handoff 与下一步验证" in markdown
    assert sum(line.startswith("## ") for line in markdown.splitlines()) == 11
    assert "不生成最终" not in markdown or "止于设计前策略" in markdown
    design_path = Path(manifest.outputs["design_specification_json"])
    design = DesignPackage.model_validate_json(design_path.read_text(encoding="utf-8"))
    handoff_path = Path(manifest.outputs["designer_handoff_json"])
    assert design.input_contract.source_sha256 == sha256(handoff_path.read_bytes()).hexdigest()
    assert design.selection.primary_opportunity_id in {
        item.opportunity_id for item in strategy.handoff_to_designer.priority_opportunities
    }
    assert design.selection.primary_verification != "rejected"
    assert len(design.manufacturing.bill_of_materials) >= 5
    assert design.manufacturing.readiness == "prototype_quote_and_sample_only"
    assert not design.validation.mass_production_ready
    assert not design.validation.reference_images_used_as_pixels
    poster_path = Path(manifest.outputs["design_poster"])
    with Image.open(poster_path) as poster:
        assert poster.size == (1800, 2400)
    render_manifest_path = Path(manifest.outputs["design_render_manifest"])
    render_manifest = DesignRenderManifest.model_validate_json(
        render_manifest_path.read_text(encoding="utf-8")
    )
    assert render_manifest.poster_sha256 == sha256(poster_path.read_bytes()).hexdigest()
    assert render_manifest.exact_text_compositor
    assert not render_manifest.reference_only_images_used
    assert len(manifest.outputs) == 13


def test_visual_reference_pack_has_required_coverage_and_rights() -> None:
    settings = load_settings().with_mode("demo")
    pack = LightRAGAdapter(settings).build_visual_reference_pack("贵州苗绣")
    assert len(pack.references) >= 10
    combined = " ".join(
        f"{item.title} {item.region} {item.craft} {item.cultural_context}"
        for item in pack.references
    )
    for keyword in (
        "花溪",
        "剑河",
        "松桃",
        "雷山",
        "蝴蝶",
        "鸟",
        "龙",
        "服装",
        "针法",
        "银",
        "锡",
    ):
        assert keyword in combined
    assert all(item.rights_status == "reference_only" for item in pack.references)
    assert all(item.source_url and item.image_url for item in pack.references)


def test_visual_palettes_do_not_invent_hex() -> None:
    settings = load_settings().with_mode("demo")
    pack = LightRAGAdapter(settings).build_visual_reference_pack("贵州苗绣")
    assert pack.pattern_primitives
    assert pack.color_palettes
    assert all(
        not color.startswith("#")
        for palette in pack.color_palettes
        for color in palette.colors
    )


def test_all_visual_source_refs_are_registered() -> None:
    settings = load_settings().with_mode("demo")
    graph = json.loads(settings.culture_graph_path.read_text(encoding="utf-8"))
    registered = {source["source_id"] for source in graph["sources"]}
    pack = LightRAGAdapter(settings).build_visual_reference_pack("贵州苗绣")
    assert set(pack.source_refs) <= registered
    assert {item.source_ref for item in pack.references} <= registered


def test_xhs_mvp_keyword_and_volume_guardrails() -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        mediacrawler_platform="xhs",
        mediacrawler_keyword_limit=6,
        mediacrawler_max_results=20,
    )
    keywords = MediaCrawlerAdapter(settings)._keywords("贵州苗绣")
    assert XHS_MVP_KEYWORDS is UNIFIED_MARKET_KEYWORDS
    assert len(UNIFIED_MARKET_KEYWORDS) == 23
    assert len(keywords) == 6
    assert {"非遗文创", "博物馆文创", "文创包挂", "文创冰箱贴"} <= set(
        keywords
    )
    assert 50 <= len(keywords) * settings.mediacrawler_max_results <= 150
    assert 200 <= len(MARKET_PLATFORMS) * len(keywords) * settings.mediacrawler_max_results <= 600


def test_four_platform_records_normalize_to_one_schema(tmp_path) -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        market_raw_dir=tmp_path / "raw",
        market_derived_dir=tmp_path / "derived",
    )
    adapter = MediaCrawlerAdapter(settings)
    raw_records = {
        "xhs": {
            "note_id": "x1",
            "title": "非遗冰箱贴",
            "desc": "旋转冰箱贴",
            "liked_count": "120",
            "collected_count": "80",
            "comment_count": "12",
            "share_count": "4",
            "time": "1750000000",
            "note_url": "https://www.xiaohongshu.com/explore/x1",
            "source_keyword": "文创冰箱贴",
        },
        "dy": {
            "aweme_id": "d1",
            "desc": "非遗文创包挂",
            "liked_count": "2.1万",
            "collected_count": "500",
            "comment_count": "300",
            "share_count": "200",
            "create_time": "1750000000",
            "aweme_url": "https://www.douyin.com/video/d1",
        },
        "bili": {
            "video_id": "b1",
            "title": "博物馆文创徽章测评",
            "desc": "徽章合集",
            "liked_count": "900",
            "video_favorite_count": "450",
            "video_comment": "60",
            "video_share_count": "30",
            "video_play_count": "12000",
            "create_time": "1750000000",
            "video_url": "https://www.bilibili.com/video/avb1",
        },
        "wb": {
            "note_id": "w1",
            "content": "新中式文创丝巾上新",
            "liked_count": "70",
            "comments_count": "9",
            "shared_count": "14",
            "create_time": "1750000000",
            "note_url": "https://m.weibo.cn/detail/w1",
        },
    }
    posts = [
        adapter._normalize_post(platform, raw_records[platform])
        for platform in MARKET_PLATFORMS
    ]
    assert [post.platform for post in posts] == list(MARKET_PLATFORMS)
    assert [post.product_form for post in posts] == ["冰箱贴", "包挂", "徽章", "丝巾"]
    assert posts[1].likes == 21_000
    assert posts[2].views == 12_000
    assert posts[3].favorites == posts[3].views == 0
    assert all(post.post_id and post.url and post.retrieved_at for post in posts)
    assert all(post.metrics_verified for post in posts)


def test_platform_and_cross_platform_hot_scores_are_bounded() -> None:
    posts: list[MarketPost] = []
    for platform_index, platform in enumerate(MARKET_PLATFORMS, 1):
        for form_index, product_form in enumerate(("包挂", "冰箱贴"), 1):
            posts.append(
                MarketPost(
                    platform=platform,
                    post_id=f"{platform}-{product_form}",
                    title=f"非遗{product_form}",
                    url=f"https://example.com/{platform}/{form_index}",
                    published_at="2026-08-01T00:00:00+00:00",
                    retrieved_at="2026-08-28T00:00:00+00:00",
                    likes=platform_index * form_index * 100,
                    favorites=platform_index * form_index * 30,
                    comments=platform_index * form_index * 10,
                    shares=platform_index * form_index * 5,
                    views=platform_index * form_index * 1000,
                    product_form=product_form,
                    product_category=product_form,
                    metrics_verified=True,
                    evidence_quality_score=90,
                )
            )
    MediaCrawlerAdapter._score_posts(posts)
    ranking = MediaCrawlerAdapter._product_form_hotness(posts)
    assert all(0 <= post.platform_hot_score <= 100 for post in posts)
    assert all(0 <= item.cross_platform_hot_score <= 100 for item in ranking)
    assert all(item.platform_coverage == 4 for item in ranking)
    assert {item.product_form for item in ranking} == {"包挂", "冰箱贴"}
    assert len([item.product_form for item in ranking[:5]]) <= 5


@pytest.mark.asyncio
async def test_market_evidence_types_and_scores_are_separated(tmp_path) -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        market_raw_dir=tmp_path / "raw",
        market_derived_dir=tmp_path / "derived",
    )
    trend, status = await MediaCrawlerAdapter(settings).research("贵州苗绣")
    assert status.mode == "cache"
    assert trend.retrieval["market_source"]["login_state"] == "missing"
    assert set(trend.retrieval["market_platforms"]) == set(MARKET_PLATFORMS)
    assert Path(trend.retrieval["market_source"]["derived_path"]).exists()
    assert Path(trend.retrieval["product_form_hotness_path"]).exists()
    allowed_types = {
        "social_signal",
        "institutional_signal",
        "media_signal",
        "product_signal",
    }
    assert all(post.evidence_type in allowed_types for post in trend.representative_cases)
    assert all(0 <= post.evidence_quality_score <= 100 for post in trend.representative_cases)
    assert all(post.real_engagement_score == 0 for post in trend.representative_cases)
    assert all(
        post.derived_viral_score == post.viral_score
        for post in trend.representative_cases
    )


def test_opportunity_weighted_score_is_explainable() -> None:
    opportunity = _baseline_opportunities(DemoRequest())[3]
    _score_opportunities([opportunity], TrendDNA())
    expected = round(
        0.20 * opportunity.culture_fit
        + 0.20 * opportunity.market_pull
        + 0.20 * opportunity.novelty
        + 0.15 * opportunity.visual_potential
        + 0.15 * opportunity.social_shareability
        + 0.10 * opportunity.product_feasibility
        - 0.20 * opportunity.cultural_risk,
        1,
    )
    assert opportunity.opportunity_id == "OPP-001"
    assert opportunity.overall_score == expected
    assert "20/20/20/15/15/10" in opportunity.reason


def test_secondary_verification_rejects_region_mismatch() -> None:
    settings = load_settings().with_mode("demo")
    adapter = LightRAGAdapter(settings)
    opportunity = _baseline_opportunities(DemoRequest())[2]
    opportunity.evidence_refs = ["C003", "M007"]
    verification, _ = adapter._verify_structured(opportunity)
    assert verification.status == "rejected"
    assert any("花溪" in conflict for conflict in verification.conflicts)


def test_negative_region_constraints_are_not_treated_as_origin_claims() -> None:
    settings = load_settings().with_mode("demo")
    adapter = LightRAGAdapter(settings)
    opportunity = _baseline_opportunities(DemoRequest())[2]
    opportunity.cultural_constraints.append("不得与剑河锡绣、松桃苗绣或雷山苗绣混用")
    verification, _ = adapter._verify_structured(opportunity)
    assert verification.status != "rejected"
    assert not any("剑河" in conflict or "松桃" in conflict for conflict in verification.conflicts)


def test_cross_branch_signature_is_rejected_even_with_valid_source_id() -> None:
    settings = load_settings().with_mode("demo")
    adapter = LightRAGAdapter(settings)
    opportunity = _baseline_opportunities(DemoRequest())[2]
    opportunity.culture_element = "花溪挑花的几何纹与迷宫式核心图案"
    verification, _ = adapter._verify_structured(opportunity)
    assert verification.status == "rejected"
    assert any("迷宫式核心" in conflict for conflict in verification.conflicts)


def test_designer_handoff_gate_rejects_rejected_item() -> None:
    settings = load_settings().with_mode("demo")
    payload = json.loads(
        (settings.outputs_dir / "designer_handoff.json").read_text(encoding="utf-8")
    )
    assert len(payload["priority_opportunities"]) == 3
    payload["priority_opportunities"][0]["verification"]["status"] = "rejected"
    with pytest.raises(ValueError, match="rejected opportunity"):
        DesignerHandoff.model_validate(payload)


def test_design_agent_holds_sensitive_motif_when_safe_option_exists(tmp_path) -> None:
    settings = load_settings().with_mode("demo")
    source = settings.outputs_dir / "designer_handoff.json"
    handoff = DesignerHandoff.model_validate_json(source.read_text(encoding="utf-8"))
    target = tmp_path / "designer_handoff.json"
    target.write_text(
        json.dumps(handoff.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    package, status = DesignAgent(settings).create_from_file(target)
    titles = {
        item.opportunity_id: item.title for item in handoff.priority_opportunities
    }
    selected_title = titles[package.selection.primary_opportunity_id]
    safe_verified_exists = any(
        item.verification.status == "verified"
        and not any(term in item.title for term in ("鸟纹", "蝶纹", "蝴蝶", "苗龙", "祖源"))
        for item in handoff.priority_opportunities
    )
    if safe_verified_exists:
        assert not any(
            term in selected_title for term in ("鸟纹", "蝶纹", "蝴蝶", "苗龙", "祖源")
        )
    assert status.mode == "live"
    assert not package.validation.reference_images_used_as_pixels
    if package.product.product_type == "可替换织物面板冰箱贴":
        assert set(package.cultural_elements[0].evidence_refs) <= {"C001", "C029"}


@pytest.mark.asyncio
async def test_designer_handoff_json_is_markdown_truth(tmp_path) -> None:
    settings = replace(
        load_settings().with_mode("demo"),
        outputs_dir=tmp_path / "outputs",
        demo_cache_dir=tmp_path / "cache",
        market_raw_dir=tmp_path / "market" / "raw",
        market_derived_dir=tmp_path / "market" / "derived",
    )
    strategy, manifest = await run_pipeline(DemoRequest(), settings)
    handoff_path = Path(manifest.outputs["designer_handoff_json"])
    markdown_path = Path(manifest.outputs["designer_handoff_markdown"])
    handoff = DesignerHandoff.model_validate_json(handoff_path.read_text(encoding="utf-8"))
    assert handoff == strategy.handoff_to_designer
    assert len(handoff.priority_opportunities) == 3
    assert all(
        item.verification.status != "rejected"
        for item in handoff.priority_opportunities
    )
    assert 150 <= len(handoff.creative_brief) <= 350
    assert markdown_path.read_text(encoding="utf-8") == render_designer_handoff_markdown(
        handoff
    )
    assert len(manifest.outputs) == 13
    assert set(manifest.market_platforms) == set(MARKET_PLATFORMS)
    assert Path(manifest.outputs["product_form_hotness"]).exists()
    assert Path(manifest.outputs["design_specification_json"]).exists()
    assert Path(manifest.outputs["design_poster"]).exists()
