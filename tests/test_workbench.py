from __future__ import annotations

import base64
import copy
import json
from dataclasses import replace

import httpx
import pytest

from app import workbench
from app.adapters import image_generation_adapter
from app.adapters.image_generation_adapter import (
    ImageGenerationAdapter,
    ImageGenerationProviderError,
)
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
    monkeypatch.setattr(workbench, "RESEARCH_DIR", tmp_path / "research")
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
        node["id"]: node["data"] for node in payload["nodes"] if node["type"] == "ConceptNode"
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


def test_research_promotion_requires_only_research_artifacts(
    isolated_workspaces,
) -> None:
    payload = workbench.ensure_default_workspace()
    run_dir = isolated_workspaces / "strict-research-run"
    output_dir = run_dir / "outputs"
    market_dir = run_dir / "market" / "derived"
    output_dir.mkdir(parents=True)
    market_dir.mkdir(parents=True)

    sources = {
        "strategy_json": (output_dir / "pre_design_strategy.json", workbench.STRATEGY_PATH),
        "visual_reference_json": (
            output_dir / "visual_reference_pack.json",
            workbench.VISUAL_REFERENCES_PATH,
        ),
        "designer_handoff_json": (
            output_dir / "designer_handoff.json",
            workbench.ROOT_DIR / "data" / "outputs" / "designer_handoff.json",
        ),
        "product_form_hotness": (
            market_dir / "product_form_hotness.json",
            workbench.HOTNESS_PATH,
        ),
    }
    for target, source in sources.values():
        target.write_bytes(source.read_bytes())
    evidence_path = market_dir / "market_evidence.json"
    evidence_path.write_text("{}", encoding="utf-8")
    manifest_path = output_dir / "run_manifest.json"
    run_id = "20260829T000000Z-research"
    enabled_platforms = ("xhs", "bili", "wb")
    manifest = {
        "run_id": run_id,
        "finished_at": "2026-08-29T00:00:00+00:00",
        "components": [
            {"component": component, "mode": "live"}
            for component in ("culture_knowledge", "market_research", "strategist")
        ],
        "market_platforms": {
            platform: {"status": "live"} for platform in enabled_platforms
        },
        "market_source": {
            "platforms": list(enabled_platforms),
            "derived_path": str(evidence_path),
        },
        "outputs": {key: str(target) for key, (target, _source) in sources.items()},
    }
    manifest["outputs"]["manifest"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    promoted = workbench.promote_research_run(payload["workspace_id"], run_dir, manifest)
    promoted_dir = workbench.RESEARCH_DIR / payload["workspace_id"] / run_id

    assert promoted["metadata"]["research_run_id"] == run_id
    assert promoted["metadata"]["research_platform_modes"] == {
        platform: "live" for platform in enabled_platforms
    }
    assert (promoted_dir / "pre_design_strategy.json").is_file()
    assert (promoted_dir / "run_manifest.json").is_file()
    assert not (promoted_dir / "design_specification.json").exists()
    statuses = {node["id"]: node["data"]["status"] for node in promoted["nodes"]}
    assert statuses["culture"] == "success"
    assert statuses["market"] == "success"
    assert statuses["strategy"] == "success"
    assert statuses["brief"] == "stale"


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
    payload["edges"].append({"id": "broken", "source": "brief", "target": "missing-node"})

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


def test_dashscope_native_adapter_uses_sync_multimodal_contract(
    tmp_path,
    monkeypatch,
) -> None:
    settings = replace(
        load_settings(),
        image_provider="dashscope-native",
        image_api_key="test-key",
        image_base_url="https://workspace.cn-beijing.maas.aliyuncs.com/api/v1",
        image_model="qwen-image-3.0-pro",
    )
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    requests: list[httpx.Request] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "output": {
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {
                                    "role": "assistant",
                                    "content": [{"image": "https://assets.example/result.png"}],
                                },
                            }
                        ]
                    },
                    "request_id": "request-test",
                },
            )
        return httpx.Response(200, content=image_bytes, headers={"Content-Type": "image/png"})

    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        return original_client(*args, transport=httpx.MockTransport(handle_request), **kwargs)

    monkeypatch.setattr(image_generation_adapter.httpx, "Client", client_factory)
    output_path = tmp_path / "qwen.png"

    result = ImageGenerationAdapter(settings).generate(
        "Mesh Gradient glassmorphism UI",
        output_path,
        size="1664x928",
    )

    payload = json.loads(requests[0].content)
    assert str(requests[0].url) == (
        "https://workspace.cn-beijing.maas.aliyuncs.com/api/v1/"
        "services/aigc/multimodal-generation/generation"
    )
    assert requests[0].headers["Authorization"] == "Bearer test-key"
    assert payload == {
        "model": "qwen-image-3.0-pro",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "Mesh Gradient glassmorphism UI"}],
                }
            ]
        },
        "parameters": {
            "n": 1,
            "prompt_extend": True,
            "size": "1664*928",
            "watermark": False,
        },
    }
    assert output_path.read_bytes() == image_bytes
    assert result["model"] == "qwen-image-3.0-pro"
    assert result["mode"] == "text_to_image"
    assert result["width"] == 1
    assert result["height"] == 1

    edited_path = tmp_path / "qwen-production.png"
    edited = ImageGenerationAdapter(settings).generate(
        "基于输入图生成生产沟通拆解图",
        edited_path,
        size="1024x1024",
        reference_image_path=output_path,
    )
    edit_payload = json.loads(requests[2].content)
    edit_content = edit_payload["input"]["messages"][0]["content"]
    assert edit_content[0]["image"].startswith("data:image/png;base64,")
    assert edit_content[1] == {"text": "基于输入图生成生产沟通拆解图"}
    assert edited["mode"] == "image_to_image"
    assert edited["reference_sha256"] == result["sha256"]


def test_image_adapter_exposes_safe_provider_billing_failure(
    tmp_path,
    monkeypatch,
) -> None:
    settings = replace(
        load_settings(),
        image_provider="dashscope-native",
        image_api_key="test-key-that-must-not-leak",
        image_base_url="https://dashscope.example/api/v1",
        image_model="qwen-image-3.0-pro",
    )

    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "code": "Arrearage",
                "message": "Access denied because the account is overdue.",
            },
        )

    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        return original_client(*args, transport=httpx.MockTransport(handle_request), **kwargs)

    monkeypatch.setattr(image_generation_adapter.httpx, "Client", client_factory)

    with pytest.raises(RuntimeError, match="账户余额不足") as caught:
        ImageGenerationAdapter(settings).generate("真实产品设计", tmp_path / "result.png")

    assert "Arrearage" in str(caught.value)
    assert "test-key-that-must-not-leak" not in str(caught.value)


def test_image_adapter_normalizes_provider_timeouts(tmp_path, monkeypatch) -> None:
    settings = replace(
        load_settings(),
        image_provider="dashscope-native",
        image_api_key="test-key-that-must-not-leak",
        image_base_url="https://dashscope.example/api/v1",
        image_model="qwen-image-3.0-pro",
    )

    def handle_request(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("provider did not answer", request=request)

    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        return original_client(*args, transport=httpx.MockTransport(handle_request), **kwargs)

    monkeypatch.setattr(image_generation_adapter.httpx, "Client", client_factory)

    with pytest.raises(ImageGenerationProviderError) as caught:
        ImageGenerationAdapter(settings).generate("真实产品设计", tmp_path / "result.png")

    assert caught.value.code == "UpstreamTimeout"
    assert caught.value.status_code == 504
    assert "等待时间内未返回" in str(caught.value)
    assert "test-key-that-must-not-leak" not in str(caught.value)


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


def test_research_node_cannot_refresh_old_file_as_new_success(
    isolated_workspaces,
) -> None:
    payload = workbench.ensure_default_workspace()

    with pytest.raises(RuntimeError, match="实时运行"):
        workbench.run_workbench_node(payload["workspace_id"], "culture")

    saved = workbench.load_workbench_workspace(payload["workspace_id"])
    culture = next(node for node in saved["nodes"] if node["id"] == "culture")
    assert culture["data"]["status"] == "error"
    assert "旧文件" in culture["data"]["history"][0]["event"]


def test_poster_run_writes_a_new_verifiable_png(isolated_workspaces) -> None:
    payload = workbench.ensure_default_workspace()

    updated = workbench.run_workbench_node(payload["workspace_id"], "poster")
    poster = next(node for node in updated["nodes"] if node["id"] == "poster")
    filename = str(poster["data"]["imageUrl"]).rsplit("/", 1)[-1]
    generated = workbench.GENERATED_DIR / payload["workspace_id"] / filename

    assert poster["data"]["status"] == "success"
    assert poster["data"]["version"] >= 1
    assert generated.is_file()
    assert generated.with_suffix(".manifest.json").is_file()


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
    assert next(item for item in strategy["citations"] if item["id"] == "M007")["kind"] == "market"
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
