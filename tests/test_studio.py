from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from PIL import Image

from app.studio import StudioEngine, StudioScheduler, StudioStore, _local_date

ROOT = Path(__file__).resolve().parents[1]
CULTURE = ROOT / "data" / "culture" / "knowledge_graph.json"
FORMS = ROOT / "data" / "market" / "derived" / "product_form_hotness.json"


@pytest.fixture
def studio(tmp_path: Path) -> tuple[StudioStore, StudioEngine]:
    store = StudioStore(tmp_path / "studio")
    return store, StudioEngine(store, CULTURE, FORMS)


def test_libraries_report_actual_records_sources_and_market_samples(studio) -> None:
    _store, engine = studio
    culture = engine.culture_library()
    forms = engine.form_library()

    assert culture["recordCount"] == len(culture["records"]) == 22
    assert culture["sourceCount"] == 32
    assert all(item["sourceRefs"] for item in culture["records"])
    assert all(not item["missingSourceRefs"] for item in culture["records"])
    assert culture["records"][0]["evidenceScoreBreakdown"]["formula"]
    assert forms["recordCount"] == len(forms["records"]) == 10
    assert forms["sampleSize"] == 378
    assert all(item["sampleSize"] > 0 for item in forms["records"])
    assert all(item["executable"] for item in forms["records"])
    assert all(item["evidenceReady"] for item in forms["records"])
    assert "60%" in forms["methodology"]["cross_platform_hot_score"]


def test_daily_run_selects_three_distinct_real_combinations_and_renders_assets(studio) -> None:
    store, engine = studio
    result = engine.generate_daily(trigger="test")

    assert result["generatedCount"] == 3
    assert len({item["cultureItems"][0]["id"] for item in result["designs"]}) == 3
    assert len({item["productForms"][0]["id"] for item in result["designs"]}) == 3
    assert store.designs_for_date(_local_date()) == result["designs"]
    for design in result["designs"]:
        assert design["scores"]["formula"]
        assert design["provenance"]["cultureSourceRefs"]
        assert design["provenance"]["marketSourceRefs"]
        assert design["provenance"]["imageGenerationUsed"] is False
        assert design["production"]["massProductionReady"] is False
        path = store.assets_dir / design["designId"] / design["asset"]["filename"]
        assert path.is_file()
        with Image.open(path) as image:
            assert image.size == (1440, 960)


def test_daily_run_reuses_today_unless_manual_rerun_is_explicit(studio) -> None:
    store, engine = studio
    first = engine.generate_daily(trigger="schedule")
    repeated = engine.generate_daily(trigger="schedule")
    rerun = engine.generate_daily(trigger="manual", force=True)

    assert repeated["reused"] is True
    assert repeated["batchId"] == first["batchId"]
    assert rerun["reused"] is False
    assert rerun["batchId"] != first["batchId"]
    assert len(store.designs_for_date(_local_date())) == 3
    all_today = store.designs_for_date(_local_date(), active_only=False)
    assert sum(bool(item["superseded"]) for item in all_today) == 3


def test_manual_combination_and_edit_regenerate_from_actual_library_ids(studio) -> None:
    store, engine = studio
    design = engine.generate_manual(
        {
            "cultureIds": ["GZ-MIAO-HUAXI", "GZ-MIAO-BATIK"],
            "productFormIds": ["冰箱贴", "包挂"],
            "title": "双材质旅行模块",
            "palette": "indigo",
        }
    )
    revised = engine.revise_design(
        design["designId"],
        {
            "cultureIds": ["GZ-MIAO-HUAXI"],
            "productFormIds": ["徽章"],
            "title": "花溪针脚层叠徽章",
            "concept": "只保留数纱结构与针脚秩序，重新生成层叠徽章概念。",
            "palette": "vermilion",
        },
    )

    assert design["origin"] == "manual"
    assert revised["version"] == 2
    assert revised["cultureItems"][0]["id"] == "GZ-MIAO-HUAXI"
    assert revised["productForms"][0]["id"] == "徽章"
    assert revised["title"] == "花溪针脚层叠徽章"
    assert revised["asset"]["sha256"] != design["asset"]["sha256"]
    assert revised["revisionHistory"][-1]["version"] == 1
    assert revised["revisionHistory"][-1]["cultureNames"] == [
        "花溪苗绣",
        "苗族蜡染技艺",
    ]
    assert revised["revisionHistory"][-1]["productFormNames"] == ["冰箱贴", "包挂"]
    assert revised["revisionHistory"][-1]["imageUrl"].endswith("/v1.png")
    assert (store.assets_dir / design["designId"] / "v1.png").is_file()
    assert (store.assets_dir / design["designId"] / "v2.png").is_file()


def test_no_executable_form_means_no_daily_fake_result(tmp_path: Path) -> None:
    payload = json.loads(FORMS.read_text(encoding="utf-8"))
    for item in payload["ranking"]:
        item["sample_size"] = 0
    forms = tmp_path / "forms.json"
    forms.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    engine = StudioEngine(StudioStore(tmp_path / "runtime"), CULTURE, forms)

    with pytest.raises(RuntimeError, match="没有同时通过"):
        engine.generate_daily()


def test_scheduler_catches_up_today_and_keeps_a_fresh_heartbeat(studio) -> None:
    store, engine = studio
    scheduler = StudioScheduler(store, engine, tick_seconds=0.05)
    scheduler.start()
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = scheduler.status()
            if (
                len(store.designs_for_date(_local_date())) == 3
                and status["daily"]["status"] == "healthy"
            ):
                break
            time.sleep(0.03)
        assert len(store.designs_for_date(_local_date())) == 3
        assert scheduler.health()["ok"] is True
        assert scheduler.status()["daily"]["status"] == "healthy"
    finally:
        scheduler.stop()
