from __future__ import annotations

import copy
from dataclasses import replace

import pytest

from app import workbench
from app.adapters.image_generation_adapter import ImageGenerationAdapter
from app.config import load_settings


@pytest.fixture
def isolated_workspaces(tmp_path, monkeypatch):
    monkeypatch.setattr(workbench, "WORKSPACES_DIR", tmp_path / "workspaces")
    monkeypatch.setattr(workbench, "GENERATED_DIR", tmp_path / "generated")
    monkeypatch.setattr(
        workbench,
        "BUNDLED_WORKSPACES_DIR",
        tmp_path / "bundled-workspaces",
    )
    monkeypatch.setattr(
        workbench,
        "BUNDLED_GENERATED_DIR",
        tmp_path / "bundled-generated",
    )
    return tmp_path


def test_default_workspace_covers_exactly_seven_supported_node_types(
    isolated_workspaces,
) -> None:
    payload = workbench.ensure_default_workspace()

    assert len(payload["nodes"]) == 9
    assert {node["type"] for node in payload["nodes"]} == set(workbench.NODE_TYPES)
    assert payload["metadata"]["selected_concept_id"] == "concept-a"
    assert payload["metadata"]["stop_before"] == "production_release_and_factory_order"
    assert payload["schema_version"] == "1.1"
    assert payload["metadata"]["decision_profile"]["mode"] == "guided"
    assert payload["metadata"]["decision_profile"]["cultureRecordIds"]


def test_default_workspace_loads_bundled_concept_assets(isolated_workspaces) -> None:
    asset_dir = workbench.GENERATED_DIR / workbench.DEFAULT_WORKSPACE_ID
    asset_dir.mkdir(parents=True)
    (asset_dir / "concept-b-v1.png").write_bytes(b"concept-b")
    (asset_dir / "concept-c-v1.png").write_bytes(b"concept-c")

    payload = workbench.default_workspace()
    concepts = {
        node["id"]: node["data"]
        for node in payload["nodes"]
        if node["type"] == "ConceptNode"
    }

    assert concepts["concept-b"]["status"] == "success"
    assert concepts["concept-c"]["status"] == "success"
    assert concepts["concept-b"]["imageUrl"].endswith("concept-b-v1.png")
    assert concepts["concept-c"]["generation"]["sha256"]


def test_workspace_round_trip_persists_viewport_nodes_and_edges(
    isolated_workspaces,
) -> None:
    payload = workbench.ensure_default_workspace()
    payload["viewport"] = {"x": 123.0, "y": 456.0, "zoom": 0.72}
    payload["nodes"][0]["position"] = {"x": -222.0, "y": 91.0}

    saved = workbench.save_workbench_workspace(payload["workspace_id"], payload)
    loaded = workbench.load_workbench_workspace(payload["workspace_id"])

    assert saved["viewport"] == loaded["viewport"]
    assert loaded["nodes"][0]["position"] == {"x": -222.0, "y": 91.0}
    assert len(loaded["edges"]) == 10


def test_brief_version_marks_only_downstream_nodes_stale(isolated_workspaces) -> None:
    payload = workbench.ensure_default_workspace()
    brief_node = next(node for node in payload["nodes"] if node["id"] == "brief")
    brief = copy.deepcopy(brief_node["data"]["brief"])
    brief["objective"] = "测试新的设计目标"

    updated = workbench.update_design_brief(payload["workspace_id"], brief)
    status = {node["id"]: node["data"]["status"] for node in updated["nodes"]}

    assert updated["metadata"]["brief_version"] == 2
    assert status["strategy"] == "success"
    assert status["brief"] == "success"
    assert status["visual"] == "stale"
    assert status["concept-a"] == "stale"
    assert status["poster"] == "stale"


def test_invalid_edge_is_rejected_before_workspace_write(isolated_workspaces) -> None:
    payload = workbench.ensure_default_workspace()
    payload["edges"].append(
        {"id": "broken", "source": "brief", "target": "missing-node"}
    )

    with pytest.raises(ValueError, match="不存在的节点"):
        workbench.save_workbench_workspace(payload["workspace_id"], payload)


def test_switching_concept_marks_poster_stale(isolated_workspaces) -> None:
    payload = workbench.ensure_default_workspace()

    updated = workbench.set_active_concept(payload["workspace_id"], "concept-b")
    concepts = {
        node["id"]: node["data"]["active"]
        for node in updated["nodes"]
        if node["type"] == "ConceptNode"
    }
    poster = next(node for node in updated["nodes"] if node["id"] == "poster")

    assert concepts == {"concept-a": False, "concept-b": True, "concept-c": False}
    assert poster["data"]["status"] == "stale"


def test_image_adapter_fails_explicitly_when_provider_is_missing(tmp_path) -> None:
    settings = replace(
        load_settings(),
        image_provider="",
        image_api_key="",
        image_base_url="",
        image_model="",
    )
    adapter = ImageGenerationAdapter(settings)

    assert adapter.status()["configured"] is False
    with pytest.raises(ValueError, match="IMAGE_PROVIDER"):
        adapter.generate("original product concept", tmp_path / "concept.png")


def test_concept_can_be_duplicated_as_an_independent_branch(
    isolated_workspaces,
) -> None:
    payload = workbench.ensure_default_workspace()

    updated = workbench.duplicate_concept(payload["workspace_id"], "concept-a")
    clone = next(node for node in updated["nodes"] if node["id"] == updated["selected_node_id"])

    assert clone["type"] == "ConceptNode"
    assert clone["data"]["active"] is False
    assert clone["data"]["title"].endswith("· 复制")
    assert len(updated["nodes"]) == 10
    assert len(updated["edges"]) == 12


def test_single_concept_regeneration_reports_missing_provider_without_fake_image(
    isolated_workspaces,
    monkeypatch,
) -> None:
    payload = workbench.ensure_default_workspace()
    monkeypatch.setattr(
        ImageGenerationAdapter,
        "status",
        lambda self: {
            "provider": "unconfigured",
            "model": "",
            "base_url_configured": False,
            "credential_configured": False,
            "configured": False,
            "detail": "未配置 IMAGE_PROVIDER。",
        },
    )

    updated = workbench.regenerate_concept(payload["workspace_id"], "concept-b")
    concept = next(node for node in updated["nodes"] if node["id"] == "concept-b")

    assert concept["data"]["status"] == "warning"
    assert concept["data"]["imageUrl"] == ""


def test_generate_more_creates_empty_direction_when_provider_is_missing(
    isolated_workspaces,
    monkeypatch,
) -> None:
    payload = workbench.ensure_default_workspace()
    monkeypatch.setattr(
        ImageGenerationAdapter,
        "status",
        lambda self: {
            "provider": "unconfigured",
            "model": "",
            "base_url_configured": False,
            "credential_configured": False,
            "configured": False,
            "detail": "未配置 IMAGE_PROVIDER。",
        },
    )

    updated = workbench.generate_more_concept(payload["workspace_id"], "concept-a")
    created = next(node for node in updated["nodes"] if node["id"] == updated["selected_node_id"])

    assert created["data"]["title"].endswith("· 新方向")
    assert created["data"]["imageUrl"] == ""
    assert created["data"]["version"] == 0
    assert created["data"]["status"] == "warning"


def test_node_detail_resolves_professional_citations(isolated_workspaces) -> None:
    workbench.ensure_default_workspace()

    culture = workbench.node_detail(workbench.DEFAULT_WORKSPACE_ID, "culture")
    market = workbench.node_detail(workbench.DEFAULT_WORKSPACE_ID, "market")
    strategy = workbench.node_detail(workbench.DEFAULT_WORKSPACE_ID, "strategy")
    visual = workbench.node_detail(workbench.DEFAULT_WORKSPACE_ID, "visual")

    assert len(culture["content"]["records"]) == 22
    assert culture["citationAudit"]["resolved"] >= 28
    assert all(item["url"].startswith("http") for item in culture["citations"])
    assert market["content"]["sampleSize"] == 378
    assert market["content"]["representativePosts"]
    assert all(item["sourceRef"] for item in market["content"]["representativePosts"])
    assert len(strategy["content"]["opportunities"]) == 8
    assert strategy["citationAudit"]["missing"] == []
    assert next(item for item in strategy["citations"] if item["id"] == "M007")[
        "kind"
    ] == "market"
    assert any(item["id"] == "V001" for item in visual["citations"])


def test_manual_opportunity_score_uses_normalized_weights_and_risk_penalty() -> None:
    opportunity = {
        "culture_fit": 90,
        "market_pull": 20,
        "novelty": 20,
        "visual_potential": 20,
        "social_shareability": 20,
        "product_feasibility": 20,
        "cultural_risk": 50,
        "verification": {"status": "verified"},
    }
    weights = {field: 0.0 for field in workbench.SCORE_FIELDS}
    weights["culture_fit"] = 1.0

    assert workbench.manual_opportunity_score(opportunity, weights, 0.20) == 80.0


def test_decision_profile_updates_all_workflow_stages(isolated_workspaces) -> None:
    workspace = workbench.ensure_default_workspace()
    profile = copy.deepcopy(workspace["metadata"]["decision_profile"])
    profile.update(
        {
            "mode": "manual",
            "cultureRecordIds": ["GZ-MIAO-HUAXI"],
            "marketPlatforms": ["xhs", "bili"],
            "marketProductForms": ["冰箱贴", "徽章"],
            "opportunityIds": ["OPP-003", "OPP-007"],
            "scoreWeights": {
                "culture_fit": 0.35,
                "market_pull": 0.10,
                "novelty": 0.10,
                "visual_potential": 0.15,
                "social_shareability": 0.10,
                "product_feasibility": 0.20,
            },
            "designIntent": {
                "targetAudience": "城市通勤与博物馆商店用户",
                "preferredProductForms": ["围巾", "包挂"],
                "priceBand": "199–399 元概念验证",
                "useScenarios": ["通勤", "礼赠"],
                "materialPriorities": ["天然纤维", "可追溯"],
            },
            "visualDirection": {
                "referenceIds": ["V001", "V009"],
                "styleKeywords": ["编辑感", "低饱和"],
                "imageSize": "1024x1536",
                "notes": "只提取数纱节奏，不复制馆藏像素。",
            },
            "conceptCompareIds": ["concept-b", "concept-c"],
            "activeConceptId": "concept-b",
            "posterTheme": "workshop",
            "posterSections": ["hero", "culture", "bom"],
        }
    )

    updated = workbench.update_decision_profile(workspace["workspace_id"], profile)
    nodes = {node["id"]: node for node in updated["nodes"]}
    decision = updated["metadata"]["decision_profile"]

    assert decision["version"] == 2
    assert decision["mode"] == "manual"
    assert nodes["culture"]["data"]["selectedRecordIds"] == ["GZ-MIAO-HUAXI"]
    assert nodes["market"]["data"]["selectedPlatforms"] == ["xhs", "bili"]
    assert {item["id"] for item in nodes["strategy"]["data"]["opportunities"]} == {
        "OPP-003",
        "OPP-007",
    }
    assert nodes["brief"]["data"]["brief"]["audience"] == "城市通勤与博物馆商店用户"
    assert nodes["brief"]["data"]["brief"]["productType"] == "围巾 / 包挂"
    assert nodes["visual"]["data"]["selectedReferenceIds"] == ["V001", "V009"]
    assert nodes["visual"]["data"]["size"] == "1024x1536"
    assert nodes["concept-a"]["data"]["inComparison"] is False
    assert nodes["concept-b"]["data"]["active"] is True
    assert nodes["poster"]["data"]["posterTheme"] == "workshop"
    assert nodes["poster"]["data"]["poster"]["hiddenSections"] == [
        "breakdown",
        "process",
    ]
    assert all(
        nodes[node_id]["data"]["status"] == "stale"
        for node_id in ("brief", "visual", "concept-a", "concept-b", "poster")
    )


def test_decision_profile_rejects_unknown_evidence_selection(
    isolated_workspaces,
) -> None:
    workspace = workbench.ensure_default_workspace()
    profile = copy.deepcopy(workspace["metadata"]["decision_profile"])
    profile["cultureRecordIds"] = ["NOT-A-CULTURE-RECORD"]

    with pytest.raises(ValueError, match="未知编号"):
        workbench.update_decision_profile(workspace["workspace_id"], profile)


def test_bootstrap_exposes_complete_human_decision_catalog(
    isolated_workspaces,
) -> None:
    payload = workbench.workbench_bootstrap()
    catalog = payload["decisionCatalog"]

    assert len(catalog["cultureRecords"]) == 22
    assert {item["id"] for item in catalog["marketPlatforms"]} == {
        "xhs",
        "dy",
        "bili",
        "wb",
    }
    assert len(catalog["opportunities"]) == 8
    assert len(catalog["visualReferences"]) == 12
    assert len(catalog["concepts"]) == 3
    assert catalog["recommendedProfile"]["mode"] == "guided"
