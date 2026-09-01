from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from app import tool_api, workbench
from app.config import MARKET_PLATFORM_CODES, load_settings
from app.designer import DesignAgent
from app.tool_api import (
    HANDOFF_PATH,
    ROOT_DIR,
    _historical_market_snapshot,
    _strict_preflight,
    audit_summary,
    design_state,
    opportunities,
    start_research_job,
)


def test_truth_audit_uses_real_repository_files() -> None:
    summary = audit_summary()

    assert summary["truth_audit"]["culture"]["actual"] == 22
    assert summary["truth_audit"]["market"]["actual"] == 378
    raw_dir = ROOT_DIR / "data" / "market" / "raw"
    raw_file_count = sum((raw_dir / f"{code}.jsonl").is_file() for code in MARKET_PLATFORM_CODES)
    assert summary["truth_audit"]["market"]["raw_file_count"] == raw_file_count
    assert summary["truth_audit"]["market"]["raw_files_present"] is (raw_file_count > 0)
    assert summary["truth_audit"]["market"]["raw_files_complete"] is (
        raw_file_count == len(MARKET_PLATFORM_CODES)
    )
    assert summary["truth_audit"]["opportunities"] == {
        "actual": 8,
        "model_generated": 0,
        "rule_baseline": 8,
        "meaning": (
            "当前 8 条均来自代码中的证据规则基线，随后被真实评分与二次核验；"
            "不能标成模型从网上新生成的机会。"
        ),
    }


def test_historical_audit_prefers_complete_snapshot_over_newer_smoke_probe() -> None:
    _, _, counts = _historical_market_snapshot()

    assert sum(counts.values()) == 378
    assert counts == {"xhs": 115, "dy": 14, "bili": 101, "wb": 148}


def test_strict_research_requires_explicit_runtime_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tool_api, "_interactive_crawl_supported", lambda: True)
    passive = _strict_preflight(allow_interactive=False)
    explicit = _strict_preflight(allow_interactive=True)

    assert passive["research_ready"] is False
    assert any("实时市场采集开关" in item for item in passive["blockers"])
    assert explicit["interactive_launch"] is True
    assert next(item for item in explicit["checks"] if item["id"] == "crawler_switch")["ok"] is True
    with pytest.raises(ValueError, match="严格实时研究未就绪"):
        start_research_job({"workspace_id": "guizhou-miao-demo", "allow_interactive": False})


def test_strict_research_reserves_formal_platform_timeout() -> None:
    assert tool_api._strict_mediacrawler_timeout_seconds(180) == 600
    assert tool_api._strict_mediacrawler_timeout_seconds(900) == 900


def test_strict_research_requires_every_enabled_platform_and_no_extra() -> None:
    enabled = ("xhs", "bili", "wb")

    assert tool_api._enabled_platforms_are_live(
        {"xhs": "live", "bili": "live", "wb": "live"}, enabled
    )
    assert not tool_api._enabled_platforms_are_live(
        {"xhs": "live", "bili": "live"}, enabled
    )
    assert not tool_api._enabled_platforms_are_live(
        {"xhs": "live", "dy": "live", "bili": "live", "wb": "live"}, enabled
    )


def test_strict_preflight_marks_douyin_as_paused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = replace(
        load_settings(), mediacrawler_platforms=("xhs", "bili", "wb")
    )
    monkeypatch.setattr(tool_api, "load_settings", lambda: settings)

    preflight = _strict_preflight(allow_interactive=False)
    douyin = next(item for item in preflight["checks"] if item["id"] == "auth_dy")

    assert preflight["enabled_platforms"] == ["xhs", "bili", "wb"]
    assert preflight["disabled_platforms"] == ["dy"]
    assert douyin == {
        "id": "auth_dy",
        "label": "抖音授权入口",
        "ok": False,
        "enabled": False,
        "detail": "已暂停，不参与本轮采集或严格晋级。",
    }
    assert not any("抖音" in blocker for blocker in preflight["blockers"])


def test_strict_research_rejects_interactive_launch_without_display(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tool_api, "_interactive_crawl_supported", lambda: False)

    explicit = _strict_preflight(allow_interactive=True)

    assert explicit["interactive_launch"] is False
    assert explicit["interactive_supported"] is False
    assert any("没有可交互图形会话" in item for item in explicit["blockers"])


def test_strict_preflight_rejects_wrong_mediacrawler_interpreter(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "MediaCrawler"
    source_root.mkdir()
    (source_root / "main.py").write_text("# probe\n", encoding="utf-8")
    interpreter = tmp_path / "python"
    interpreter.touch()
    settings = replace(
        load_settings(),
        mediacrawler_path=source_root,
        mediacrawler_python=interpreter,
    )
    monkeypatch.setattr(tool_api, "load_settings", lambda: settings)
    monkeypatch.setattr(
        tool_api,
        "_mediacrawler_runtime_available",
        lambda executable, source: False,
    )

    preflight = _strict_preflight(allow_interactive=True)
    runtime = next(
        item for item in preflight["checks"] if item["id"] == "crawler_runtime"
    )

    assert runtime["ok"] is False
    assert "CDP 依赖不可用" in runtime["detail"]


def test_interactive_support_empty_override_uses_platform_detection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QIANCRAFT_INTERACTIVE_CRAWL_ALLOWED", "")
    monkeypatch.setattr(tool_api.sys, "platform", "darwin")

    assert tool_api._interactive_crawl_supported() is True

    monkeypatch.setenv("QIANCRAFT_INTERACTIVE_CRAWL_ALLOWED", "false")
    assert tool_api._interactive_crawl_supported() is False


def test_legacy_design_state_reports_actual_image_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = {
        "provider": "test-provider",
        "model": "test-model",
        "base_url_configured": True,
        "credential_configured": True,
        "configured": True,
        "detail": "图像生成适配器已就绪。",
    }
    monkeypatch.setattr(tool_api, "image_provider_status", lambda settings=None: provider)

    assert design_state()["image_generation"] == provider


def test_all_stored_opportunity_scores_are_reproducible() -> None:
    payload = opportunities()

    assert payload["count"] == 8
    assert all(item["score_audit"]["matches"] for item in payload["opportunities"])


def test_manual_primary_selection_is_real_and_unknown_generator_fails() -> None:
    agent = DesignAgent(load_settings())

    package, _ = agent.create_from_file(HANDOFF_PATH, primary_opportunity_id="OPP-002")
    assert package.selection.primary_opportunity_id == "OPP-002"
    assert "毛绒" in package.product.product_type

    with pytest.raises(ValueError, match="不会套用通用兜底模板"):
        agent.create_from_file(HANDOFF_PATH, primary_opportunity_id="OPP-004")


def test_auto_design_selects_an_executable_verified_opportunity(tmp_path) -> None:
    payload = json.loads(HANDOFF_PATH.read_text(encoding="utf-8"))
    unsupported = next(
        item for item in payload["priority_opportunities"] if item["opportunity_id"] == "OPP-004"
    )
    unsupported["overall_score"] = 100
    handoff = tmp_path / "designer_handoff.json"
    handoff.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    package, _ = DesignAgent(load_settings()).create_from_file(handoff)

    assert package.selection.primary_opportunity_id != "OPP-004"
    assert package.selection.primary_opportunity_id in {"OPP-002", "OPP-006"}


def test_workbench_design_run_consumes_current_decisions_and_writes_artifacts(
    tmp_path,
    monkeypatch,
) -> None:
    workspaces = tmp_path / "workspaces"
    generated = tmp_path / "generated"
    design_runs = tmp_path / "design-runs"
    monkeypatch.setattr(workbench, "WORKSPACES_DIR", workspaces)
    monkeypatch.setattr(workbench, "GENERATED_DIR", generated)
    monkeypatch.setattr(workbench, "DESIGN_RUNS_DIR", design_runs)
    monkeypatch.setattr(tool_api, "GENERATED_DIR", generated)
    monkeypatch.setattr(tool_api, "DESIGN_RUNS_DIR", design_runs)
    payload = workbench.ensure_default_workspace()

    updated = tool_api.generate_workbench_design(payload["workspace_id"])
    run_id = updated["metadata"]["design_run_id"]
    run_dir = design_runs / payload["workspace_id"] / run_id
    poster = next(node for node in updated["nodes"] if node["id"] == "poster")

    assert updated["metadata"]["design_primary_opportunity_id"] == "OPP-006"
    assert (run_dir / "designer_handoff_draft.json").is_file()
    assert (run_dir / "design_specification.json").is_file()
    assert (run_dir / "design_poster.png").is_file()
    assert poster["data"]["status"] == "success"
    assert run_id in poster["data"]["imageUrl"]
