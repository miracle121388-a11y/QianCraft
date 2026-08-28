from __future__ import annotations

import pytest

from app.config import MARKET_PLATFORM_CODES, load_settings
from app.designer import DesignAgent
from app.tool_api import HANDOFF_PATH, ROOT_DIR, audit_summary, opportunities


def test_truth_audit_uses_real_repository_files() -> None:
    summary = audit_summary()

    assert summary["truth_audit"]["culture"]["actual"] == 22
    assert summary["truth_audit"]["market"]["actual"] == 378
    raw_dir = ROOT_DIR / "data" / "market" / "raw"
    raw_file_count = sum(
        (raw_dir / f"{code}.jsonl").is_file() for code in MARKET_PLATFORM_CODES
    )
    assert summary["truth_audit"]["market"]["raw_file_count"] == raw_file_count
    assert summary["truth_audit"]["market"]["raw_files_present"] is (
        raw_file_count > 0
    )
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
