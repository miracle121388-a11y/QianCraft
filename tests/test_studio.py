from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest
from PIL import Image

from app.adapters.image_generation_adapter import ImageGenerationProviderError
from app.studio import StudioEngine, StudioScheduler, StudioStore, _local_date

ROOT = Path(__file__).resolve().parents[1]
CULTURE = ROOT / "data" / "culture" / "knowledge_graph.json"
FORMS = ROOT / "data" / "market" / "derived" / "product_form_hotness.json"


class FakeImageAdapter:
    def __init__(
        self,
        *,
        configured: bool = True,
        fail_on_call: int = 0,
        arrearage_on_reference: bool = False,
        timeout_on_reference: bool = False,
    ) -> None:
        self.configured = configured
        self.fail_on_call = fail_on_call
        self.arrearage_on_reference = arrearage_on_reference
        self.timeout_on_reference = timeout_on_reference
        self.calls: list[dict[str, object]] = []

    def status(self) -> dict[str, object]:
        return {
            "provider": "test-image-provider" if self.configured else "unconfigured",
            "model": "test-image-model-v1" if self.configured else "",
            "base_url_configured": self.configured,
            "credential_configured": self.configured,
            "configured": self.configured,
            "supports_image_to_image": self.configured,
            "detail": "测试生图模型已配置。" if self.configured else "未配置测试生图模型。",
        }

    def generate(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str = "1024x1024",
        reference_image_path: Path | None = None,
    ) -> dict[str, object]:
        if not self.configured:
            raise ValueError("未配置测试生图模型。")
        self.calls.append(
            {
                "prompt": prompt,
                "output": output_path,
                "reference": reference_image_path,
            }
        )
        if self.fail_on_call and len(self.calls) == self.fail_on_call:
            raise RuntimeError("模拟模型调用失败")
        if self.arrearage_on_reference and reference_image_path is not None:
            raise ImageGenerationProviderError(
                400,
                "Arrearage",
                "图像服务账户余额不足或账务状态异常，请在服务商控制台恢复账户状态。",
            )
        if self.timeout_on_reference and reference_image_path is not None:
            raise ImageGenerationProviderError(
                504,
                "UpstreamTimeout",
                "图像生成服务在配置的等待时间内未返回结果。",
            )
        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        image = Image.new("RGB", (1024, 1024), tuple(digest[:3]))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        image_bytes = output_path.read_bytes()
        reference_sha = (
            hashlib.sha256(reference_image_path.read_bytes()).hexdigest()
            if reference_image_path is not None
            else ""
        )
        return {
            "provider": "test-image-provider",
            "model": "test-image-model-v1",
            "generated_at": "2026-09-02T00:00:00+00:00",
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "reference_sha256": reference_sha,
            "mode": "image_to_image" if reference_image_path else "text_to_image",
        }


@pytest.fixture
def studio(tmp_path: Path) -> tuple[StudioStore, StudioEngine]:
    store = StudioStore(tmp_path / "studio")
    return store, StudioEngine(store, CULTURE, FORMS, FakeImageAdapter())


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


def test_daily_run_selects_three_distinct_real_combinations_and_generates_both_assets(studio) -> None:
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
        assert design["provenance"]["imageGenerationUsed"] is True
        assert design["provenance"]["imageModel"] == "test-image-model-v1"
        assert design["production"]["massProductionReady"] is False
        assert design["production"]["visualStatus"] == "generated_model"
        path = store.assets_dir / design["designId"] / design["asset"]["filename"]
        production_path = (
            store.assets_dir
            / design["designId"]
            / design["production"]["asset"]["filename"]
        )
        assert path.is_file()
        assert production_path.is_file()
        with Image.open(path) as image:
            assert image.size == (1024, 1024)
        with Image.open(production_path) as image:
            assert image.size == (1024, 1024)
        assert design["asset"]["generation"]["mode"] == "text_to_image"
        assert design["production"]["asset"]["generation"]["mode"] == "image_to_image"
        assert design["production"]["asset"]["generation"]["inputAssetSha256"] == design["asset"]["sha256"]
        assert "不得复制" in design["asset"]["generation"]["prompt"]


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


def test_legacy_local_daily_result_is_not_reused_as_a_model_result(studio) -> None:
    store, engine = studio
    store.save_designs(
        [
            {
                "designId": "QCD-AAAAAAAAAAAA",
                "batchId": "DAY-LEGACY",
                "dailyDate": _local_date(),
                "dailyRank": 1,
                "origin": "daily",
                "superseded": False,
                "provenance": {"imageGenerationUsed": False},
                "asset": {"imageUrl": "/assets/studio/QCD-AAAAAAAAAAAA/v1.png"},
                "production": {"massProductionReady": False},
            }
        ]
    )

    result = engine.generate_daily(trigger="schedule")

    assert result["reused"] is False
    assert result["generatedCount"] == 3
    legacy = next(
        item for item in store.load_designs() if item["designId"] == "QCD-AAAAAAAAAAAA"
    )
    assert legacy["superseded"] is True


def test_daily_model_metadata_without_files_is_not_reused(studio) -> None:
    store, engine = studio
    store.save_designs(
        [
            {
                "designId": "QCD-BBBBBBBBBBBB",
                "batchId": "DAY-INCOMPLETE",
                "dailyDate": _local_date(),
                "dailyRank": 1,
                "origin": "daily",
                "superseded": False,
                "provenance": {"imageGenerationUsed": True},
                "asset": {
                    "filename": "v1-design.png",
                    "imageUrl": "/assets/studio/QCD-BBBBBBBBBBBB/v1-design.png",
                    "generation": {"model": "missing-file-model"},
                },
                "production": {
                    "massProductionReady": False,
                    "asset": {
                        "filename": "v1-production.png",
                        "imageUrl": (
                            "/assets/studio/QCD-BBBBBBBBBBBB/v1-production.png"
                        ),
                        "generation": {"model": "missing-file-model"},
                    },
                },
            }
        ]
    )

    result = engine.generate_daily(trigger="schedule")

    assert result["reused"] is False
    assert result["generatedCount"] == 3
    incomplete = next(
        item for item in store.load_designs() if item["designId"] == "QCD-BBBBBBBBBBBB"
    )
    assert incomplete["superseded"] is True


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
    assert revised["production"]["asset"]["sha256"] != design["production"]["asset"]["sha256"]
    assert revised["revisionHistory"][-1]["version"] == 1
    assert revised["revisionHistory"][-1]["cultureNames"] == [
        "花溪苗绣",
        "苗族蜡染技艺",
    ]
    assert revised["revisionHistory"][-1]["productFormNames"] == ["冰箱贴", "包挂"]
    assert revised["revisionHistory"][-1]["imageUrl"].endswith("/v1-design.png")
    assert revised["revisionHistory"][-1]["productionImageUrl"].endswith(
        "/v1-production.png"
    )
    assert (store.assets_dir / design["designId"] / "v1-design.png").is_file()
    assert (store.assets_dir / design["designId"] / "v1-production.png").is_file()
    assert (store.assets_dir / design["designId"] / "v2-design.png").is_file()
    assert (store.assets_dir / design["designId"] / "v2-production.png").is_file()


def test_no_executable_form_means_no_daily_fake_result(tmp_path: Path) -> None:
    payload = json.loads(FORMS.read_text(encoding="utf-8"))
    for item in payload["ranking"]:
        item["sample_size"] = 0
    forms = tmp_path / "forms.json"
    forms.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    engine = StudioEngine(
        StudioStore(tmp_path / "runtime"),
        CULTURE,
        forms,
        FakeImageAdapter(),
    )

    with pytest.raises(RuntimeError, match="没有同时通过"):
        engine.generate_daily()


def test_missing_or_failed_image_model_never_persists_a_placeholder(tmp_path: Path) -> None:
    missing_store = StudioStore(tmp_path / "missing")
    missing_engine = StudioEngine(
        missing_store,
        CULTURE,
        FORMS,
        FakeImageAdapter(configured=False),
    )
    with pytest.raises(RuntimeError, match="不会生成本地占位图"):
        missing_engine.generate_manual(
            {"cultureIds": ["GZ-MIAO-HUAXI"], "productFormIds": ["冰箱贴"]}
        )
    assert missing_store.load_designs() == []
    assert list(missing_store.assets_dir.rglob("*.png")) == []

    failed_store = StudioStore(tmp_path / "failed")
    failed_engine = StudioEngine(
        failed_store,
        CULTURE,
        FORMS,
        FakeImageAdapter(fail_on_call=2),
    )
    with pytest.raises(RuntimeError, match="没有使用本地占位图") as caught:
        failed_engine.generate_manual(
            {"cultureIds": ["GZ-MIAO-HUAXI"], "productFormIds": ["冰箱贴"]}
        )
    assert "上游原因：模拟模型调用失败" in str(caught.value)
    assert failed_store.load_designs() == []
    assert list(failed_store.assets_dir.rglob("*.png")) == []


def test_billing_blocked_image_to_image_uses_a_second_real_model_call(
    tmp_path: Path,
) -> None:
    store = StudioStore(tmp_path / "runtime")
    adapter = FakeImageAdapter(arrearage_on_reference=True)
    engine = StudioEngine(store, CULTURE, FORMS, adapter)

    design = engine.generate_manual(
        {"cultureIds": ["GZ-MIAO-HUAXI"], "productFormIds": ["冰箱贴"]}
    )

    production = design["production"]["asset"]
    assert len(adapter.calls) == 3
    assert adapter.calls[1]["reference"] is not None
    assert adapter.calls[2]["reference"] is None
    assert production["generation"]["mode"] == "text_to_image"
    assert production["generation"]["inputAssetSha256"] == ""
    assert production["generation"]["referenceAttempt"] == {
        "attempted": True,
        "status": "blocked",
        "code": "Arrearage",
        "detail": (
            "图像生成服务拒绝请求（HTTP 400，Arrearage）："
            "图像服务账户余额不足或账务状态异常，请在服务商控制台恢复账户状态。"
        ),
    }
    assert (store.assets_dir / design["designId"] / "v1-design.png").is_file()
    assert (store.assets_dir / design["designId"] / "v1-production.png").is_file()


def test_timed_out_image_to_image_uses_a_second_real_model_call(
    tmp_path: Path,
) -> None:
    store = StudioStore(tmp_path / "runtime")
    adapter = FakeImageAdapter(timeout_on_reference=True)
    engine = StudioEngine(store, CULTURE, FORMS, adapter)

    design = engine.generate_manual(
        {"cultureIds": ["GZ-MIAO-HUAXI"], "productFormIds": ["冰箱贴"]}
    )

    production = design["production"]["asset"]
    assert len(adapter.calls) == 3
    assert adapter.calls[1]["reference"] is not None
    assert adapter.calls[2]["reference"] is None
    assert production["generation"]["mode"] == "text_to_image"
    assert production["generation"]["inputAssetSha256"] == ""
    assert production["generation"]["referenceAttempt"] == {
        "attempted": True,
        "status": "blocked",
        "code": "UpstreamTimeout",
        "detail": (
            "图像生成服务拒绝请求（HTTP 504，UpstreamTimeout）："
            "图像生成服务在配置的等待时间内未返回结果。"
        ),
    }
    assert (store.assets_dir / design["designId"] / "v1-design.png").is_file()
    assert (store.assets_dir / design["designId"] / "v1-production.png").is_file()


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
