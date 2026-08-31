from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from pathlib import Path
from urllib.request import Request

import pytest

from app import collection as collection_module
from app import tool_api
from app.collection import (
    CollectionScheduler,
    CollectionStore,
    CultureSourceWatcher,
    FetchResult,
    _assert_public_network_url,
    _create_public_connection,
    _PublicRedirectHandler,
    fetch_public_page,
)


def _graph(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "records": [{"culture_id": "GZ-001", "culture_name": "测试文化"}],
                "sources": [
                    {
                        "source_id": "C001",
                        "source_url": "https://example.org/culture/source",
                        "source_title": "测试来源",
                        "publisher": "测试机构",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_culture_watcher_discovers_candidates_without_promoting_facts(tmp_path) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    store = CollectionStore(tmp_path / "runtime")

    def fetcher(url: str, headers: dict[str, str]) -> FetchResult:
        assert url == "https://example.org/culture/source"
        assert headers == {}
        return FetchResult(
            url=url,
            status=200,
            body=(
                b"<html><head><title>Source</title></head><body>"
                b'<a href="/culture/2026/guizhou-new.html">\xe8\xb4\xb5\xe5\xb7\x9e\xe9\x9d\x9e\xe9\x81\x97\xe6\x96\xb0\xe8\xb5\x84\xe6\x96\x99</a>'
                b"</body></html>"
            ),
            headers={"content-type": "text/html", "etag": '"v1"'},
        )

    metrics = CultureSourceWatcher(graph, store, fetcher=fetcher, batch_size=1).run()
    candidates = store.list_candidates()

    assert metrics == {
        "verifiedRecords": 1,
        "verifiedSources": 1,
        "probed": 1,
        "healthy": 1,
        "unchanged": 1,
        "changed": 0,
        "errors": 0,
        "newCandidates": 1,
    }
    assert len(candidates) == 1
    assert candidates[0]["status"] == "pending_review"
    assert candidates[0]["url"] == "https://example.org/culture/2026/guizhou-new.html"
    assert json.loads(graph.read_text(encoding="utf-8"))["records"] == [
        {"culture_id": "GZ-001", "culture_name": "测试文化"}
    ]


def test_culture_watcher_detects_source_change_and_keeps_review_state(tmp_path) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    store = CollectionStore(tmp_path / "runtime")
    bodies = [b"<html>first</html>", b"<html>second</html>"]

    def fetcher(url: str, headers: dict[str, str]) -> FetchResult:
        body = bodies.pop(0)
        return FetchResult(
            url=url,
            status=200,
            body=body,
            headers={"content-type": "text/html"},
        )

    watcher = CultureSourceWatcher(graph, store, fetcher=fetcher, batch_size=1)
    first = watcher.run()
    second = watcher.run()

    assert first["changed"] == 0
    assert second["changed"] == 1
    assert second["verifiedRecords"] == 1


def test_candidate_review_is_persistent_and_separate_from_verified_graph(tmp_path) -> None:
    store = CollectionStore(tmp_path / "runtime")
    candidate = store.add_manual_candidate(
        {
            "url": "https://example.org/culture/candidate",
            "title": "人工候选",
        }
    )

    reviewed = store.review_candidate(
        candidate["id"],
        status="ready_to_structure",
        note="已核对发布机构；仍需字段级证据映射。",
    )

    assert reviewed["status"] == "ready_to_structure"
    assert "字段级证据" in reviewed["reviewNote"]
    assert store.candidate_counts() == {"ready_to_structure": 1}


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://10.0.0.7/internal",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/admin",
        "http://service.internal/",
    ],
)
def test_manual_candidate_rejects_private_network_urls(tmp_path: Path, url: str) -> None:
    store = CollectionStore(tmp_path / "runtime")

    with pytest.raises(ValueError, match="本机或私有"):
        store.add_manual_candidate({"url": url, "title": "不安全来源"})


def test_public_fetch_rejects_hostname_resolving_to_private_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collection_module.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (collection_module.socket.AF_INET, collection_module.socket.SOCK_STREAM, 6, "", ("10.0.0.8", 443))
        ],
    )

    with pytest.raises(ValueError, match="私有或保留网络"):
        fetch_public_page("https://example.org/research", {})


def test_redirect_handler_revalidates_private_destination() -> None:
    handler = _PublicRedirectHandler()

    with pytest.raises(ValueError, match="本机或私有"):
        handler.redirect_request(
            Request("https://example.org/research"),
            None,
            302,
            "Found",
            {},
            "http://127.0.0.1/admin",
        )


def test_public_connection_revalidates_dns_and_refuses_rebound_private_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = [
        [(collection_module.socket.AF_INET, collection_module.socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
        [(collection_module.socket.AF_INET, collection_module.socket.SOCK_STREAM, 6, "", ("10.0.0.8", 443))],
    ]
    monkeypatch.setattr(
        collection_module.socket,
        "getaddrinfo",
        lambda *args, **kwargs: answers.pop(0),
    )

    assert _assert_public_network_url("https://example.org/research") == (
        "https://example.org/research"
    )
    with pytest.raises(ValueError, match="私有或保留网络"):
        _create_public_connection(("example.org", 443), timeout=1)


def test_scheduler_reports_blocked_market_lane_without_starting_fake_live_run(
    tmp_path,
) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    store = CollectionStore(tmp_path / "runtime")
    started: list[str] = []
    watcher = CultureSourceWatcher(
        graph,
        store,
        fetcher=lambda url, headers: FetchResult(url, 304, b"", {}),
        batch_size=1,
    )
    scheduler = CollectionScheduler(
        store,
        watcher,
        research_preflight=lambda: {
            "research_ready": False,
            "blockers": ["实时市场采集开关：未启用"],
            "checks": [],
        },
        research_start=lambda workspace_id: started.append(workspace_id) or {},
        research_status=lambda job_id: {},
        tick_seconds=0.2,
    )

    runtime = scheduler.run_now("market_refresh")

    assert runtime["lanes"]["market_refresh"]["status"] == "blocked"
    assert "未启用" in runtime["lanes"]["market_refresh"]["detail"]
    assert started == []


def test_scheduler_health_rejects_dead_or_stale_heartbeat(
    tmp_path,
    monkeypatch,
) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    store = CollectionStore(tmp_path / "runtime")
    scheduler = CollectionScheduler(
        store,
        CultureSourceWatcher(
            graph,
            store,
            fetcher=lambda url, headers: FetchResult(url, 304, b"", {}),
            batch_size=1,
        ),
        research_preflight=lambda: {
            "research_ready": False,
            "blockers": [],
            "checks": [],
        },
        research_start=lambda workspace_id: {},
        research_status=lambda job_id: {},
        tick_seconds=60,
    )

    monkeypatch.setattr(tool_api, "COLLECTION_SERVICE", scheduler)
    assert scheduler.health()["ok"] is False
    dead_payload, dead_status = tool_api.collection_health_response()
    assert dead_status is HTTPStatus.SERVICE_UNAVAILABLE
    assert dead_payload["ok"] is False
    scheduler.start()
    try:
        now = datetime.now(UTC)
        assert scheduler.health(now=now)["ok"] is True
        live_payload, live_status = tool_api.collection_health_response()
        assert live_status is HTTPStatus.OK
        assert live_payload["collectionScheduler"]["online"] is True

        state = store.load_state()
        state["scheduler"]["heartbeatAt"] = (now - timedelta(seconds=46)).isoformat()
        store.save_state(state)
        stale = scheduler.health(now=now)
        assert stale["ok"] is False
        assert stale["online"] is True
        assert stale["heartbeatFresh"] is False
        assert stale["heartbeatAgeSeconds"] == 46.0
        stale_payload, stale_status = tool_api.collection_health_response()
        assert stale_status is HTTPStatus.SERVICE_UNAVAILABLE
        assert stale_payload["collectionScheduler"]["heartbeatFresh"] is False
    finally:
        scheduler.stop()


def test_scheduler_marks_partial_culture_probe_as_degraded(tmp_path) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    payload = json.loads(graph.read_text(encoding="utf-8"))
    payload["sources"].append(
        {
            "source_id": "C002",
            "source_url": "https://example.org/culture/second",
            "source_title": "第二测试来源",
            "publisher": "测试机构",
        }
    )
    graph.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    store = CollectionStore(tmp_path / "runtime")

    def fetcher(url: str, headers: dict[str, str]) -> FetchResult:
        del headers
        if url.endswith("/second"):
            raise OSError("source unavailable")
        return FetchResult(url, 304, b"", {})

    scheduler = CollectionScheduler(
        store,
        CultureSourceWatcher(graph, store, fetcher=fetcher, batch_size=2),
        research_preflight=lambda: {"research_ready": False, "blockers": [], "checks": []},
        research_start=lambda workspace_id: {},
        research_status=lambda job_id: {},
        tick_seconds=0.2,
    )

    scheduler._culture_worker(60)
    first = scheduler.status()["lanes"]["culture_watch"]
    scheduler._culture_worker(60)
    second = scheduler.status()["lanes"]["culture_watch"]

    assert first["status"] == "degraded"
    assert first["consecutiveFailures"] == 1
    assert first["lastSuccessAt"] == ""
    assert first["metrics"]["healthy"] == 1
    assert first["metrics"]["errors"] == 1
    assert second["consecutiveFailures"] == 2


def test_scheduler_promotes_only_a_live_verified_market_job(tmp_path) -> None:
    graph = tmp_path / "knowledge_graph.json"
    _graph(graph)
    store = CollectionStore(tmp_path / "runtime")
    jobs: dict[str, dict[str, object]] = {
        "job-1": {"job_id": "job-1", "status": "queued", "detail": "排队中"}
    }
    watcher = CultureSourceWatcher(
        graph,
        store,
        fetcher=lambda url, headers: FetchResult(url, 304, b"", {}),
        batch_size=1,
    )
    scheduler = CollectionScheduler(
        store,
        watcher,
        research_preflight=lambda: {
            "research_ready": True,
            "blockers": [],
            "checks": [],
        },
        research_start=lambda workspace_id: jobs["job-1"],
        research_status=lambda job_id: jobs[job_id],
        tick_seconds=0.2,
    )

    queued = scheduler.run_now("market_refresh")
    assert queued["lanes"]["market_refresh"]["status"] == "running"

    jobs["job-1"] = {
        "job_id": "job-1",
        "status": "live_verified",
        "detail": "四平台本轮均为 live。",
        "component_modes": {
            "culture_knowledge": "live",
            "market_research": "live",
            "strategist": "live",
        },
        "platform_modes": {"xhs": "live", "dy": "live", "bili": "live", "wb": "live"},
    }
    scheduler.tick()
    completed = scheduler.status()

    assert completed["lanes"]["market_refresh"]["status"] == "healthy"
    assert completed["lanes"]["market_refresh"]["consecutiveFailures"] == 0
    assert completed["lanes"]["market_refresh"]["metrics"]["platformModes"] == {
        "xhs": "live",
        "dy": "live",
        "bili": "live",
        "wb": "live",
    }
