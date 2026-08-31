from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import socket
import threading
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
from http.client import HTTPConnection, HTTPSConnection
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import (
    HTTPHandler,
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)
from uuid import uuid4

USER_AGENT = "QianCraftEvidenceMonitor/0.9 (+local evidence research tool)"
LANE_IDS = ("culture_watch", "market_refresh")
TERMINAL_RESEARCH_STATUSES = {"live_verified", "failed_no_fallback", "error"}
SCHEDULER_HEARTBEAT_MAX_AGE_SECONDS = 45
CULTURE_DISCOVERY_KEYWORDS = (
    "贵州",
    "非遗",
    "非物质文化遗产",
    "传统技艺",
    "传统美术",
    "传统音乐",
    "民俗",
    "苗族",
    "侗族",
    "水族",
    "布依族",
    "仡佬族",
    "刺绣",
    "博物馆",
)
GENERIC_NAV_LABELS = {
    "首页",
    "贵州文化",
    "国家级非物质文化遗产代表性项目名录",
    "国家级非物质文化遗产代表性项目代表性传承人",
    "国家级非物质文化遗产生产性保护示范基地",
    "联合国教科文组织非物质文化遗产名录、名册",
    "中国列入联合国教科文组织非物质文化遗产名录、名册项目",
    "中国非物质文化遗产网 · 中国非物质文化遗产数字博物馆",
}


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def _parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _safe_detail(value: object, limit: int = 1200) -> str:
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(value))
    text = re.sub(r"(?i)(cookie|password|token)=([^\s;&]+)", r"\1=<redacted>", text)
    return text[:limit]


def _load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, ValueError):
        return fallback
    return payload if isinstance(payload, dict) else fallback


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex[:8]}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def _normalize_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("候选来源必须是公开的 http 或 https 地址。")
    if parsed.username or parsed.password:
        raise ValueError("来源地址不能包含用户名或密码。")
    host = parsed.hostname or ""
    if (
        host in {"localhost", "localhost.localdomain"}
        or host.endswith((".local", ".localhost", ".internal"))
    ):
        raise ValueError("来源地址不能指向本机或私有服务。")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("来源地址不能指向本机或私有服务。")
    normalized_path = parsed.path or "/"
    return urlunparse(
        (parsed.scheme.lower(), parsed.netloc.lower(), normalized_path, "", parsed.query, "")
    )


def _public_address_infos(host: str, port: int) -> list[tuple[Any, ...]]:
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"来源地址无法解析：{host}") from exc
    addresses = {item[4][0].split("%", maxsplit=1)[0] for item in answers if item[4]}
    if not addresses or any(not ipaddress.ip_address(item).is_global for item in addresses):
        raise ValueError("来源地址解析到本机、私有或保留网络，已拒绝访问。")
    return answers


def _assert_public_network_url(value: str) -> str:
    normalized = _normalize_url(value)
    parsed = urlparse(normalized)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    _public_address_infos(host, port)
    return normalized


def _create_public_connection(
    address: tuple[str, int],
    timeout: float | object = socket._GLOBAL_DEFAULT_TIMEOUT,
    source_address: tuple[str, int] | None = None,
) -> socket.socket:
    """Resolve, validate and connect to the exact public address set in one step."""

    host, port = address
    last_error: OSError | None = None
    for family, socktype, proto, _canonname, sockaddr in _public_address_infos(host, port):
        connection: socket.socket | None = None
        try:
            connection = socket.socket(family, socktype, proto)
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                connection.settimeout(timeout)
            if source_address:
                connection.bind(source_address)
            connection.connect(sockaddr)
            return connection
        except OSError as exc:
            last_error = exc
            if connection is not None:
                connection.close()
    if last_error is not None:
        raise last_error
    raise OSError("来源地址没有可连接的公网地址。")


class _PublicHTTPConnection(HTTPConnection):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._create_connection = _create_public_connection


class _PublicHTTPSConnection(HTTPSConnection):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._create_connection = _create_public_connection


class _PublicHTTPHandler(HTTPHandler):
    def http_open(self, req: Request) -> Any:
        return self.do_open(_PublicHTTPConnection, req)


class _PublicHTTPSHandler(HTTPSHandler):
    def https_open(self, req: Request) -> Any:
        return self.do_open(_PublicHTTPSConnection, req, context=self._context)


class _PublicRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        _assert_public_network_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    status: int
    body: bytes
    headers: Mapping[str, str]


Fetcher = Callable[[str, Mapping[str, str]], FetchResult]


def fetch_public_page(url: str, conditional_headers: Mapping[str, str]) -> FetchResult:
    url = _assert_public_network_url(url)
    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.8,*/*;q=0.3",
        **conditional_headers,
    }
    request = Request(url, headers=request_headers)
    try:
        with build_opener(
            ProxyHandler({}),
            _PublicHTTPHandler(),
            _PublicHTTPSHandler(),
            _PublicRedirectHandler(),
        ).open(request, timeout=12) as response:
            body = response.read(524_289)
            if len(body) > 524_288:
                body = body[:524_288]
            return FetchResult(
                url=response.geturl(),
                status=int(response.status),
                body=body,
                headers={key.lower(): value for key, value in response.headers.items()},
            )
    except HTTPError as exc:
        if exc.code == 304:
            return FetchResult(
                url=url,
                status=304,
                body=b"",
                headers={key.lower(): value for key, value in exc.headers.items()},
            )
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except (TimeoutError, URLError, OSError) as exc:
        raise RuntimeError(_safe_detail(exc, 240)) from exc


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._in_title = False
        self._current_href = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "a" and attributes.get("href"):
            self._current_href = str(attributes["href"])
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._current_href:
            label = " ".join("".join(self._current_text).split())
            self.links.append((self._current_href, label))
            self._current_href = ""
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._current_href:
            self._current_text.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


class CollectionStore:
    """Persistent control-plane state for the two evidence collection lanes."""

    def __init__(self, runtime_dir: Path) -> None:
        self.runtime_dir = runtime_dir.resolve()
        self.config_path = self.runtime_dir / "schedule.json"
        self.state_path = self.runtime_dir / "state.json"
        self.events_path = self.runtime_dir / "events.json"
        self.candidates_path = self.runtime_dir / "culture_candidates.json"
        self.source_state_path = self.runtime_dir / "culture_source_state.json"
        self._lock = threading.RLock()

    def default_config(self) -> dict[str, Any]:
        return {
            "schemaVersion": "1.0",
            "enabled": _bool_env("QIANCRAFT_CONTINUOUS_COLLECTION", True),
            "workspaceId": "guizhou-miao-demo",
            "updatedAt": _iso(),
            "lanes": {
                "culture_watch": {
                    "enabled": True,
                    "intervalMinutes": _int_env(
                        "QIANCRAFT_CULTURE_WATCH_MINUTES", 360, 30, 10_080
                    ),
                    "label": "文化来源巡检",
                },
                "market_refresh": {
                    "enabled": True,
                    "intervalMinutes": _int_env(
                        "QIANCRAFT_MARKET_REFRESH_MINUTES", 240, 30, 10_080
                    ),
                    "label": "四平台增量采集",
                },
            },
        }

    def load_config(self) -> dict[str, Any]:
        with self._lock:
            fallback = self.default_config()
            payload = _load_json(self.config_path, fallback)
            try:
                return self._validated_config(payload, fallback)
            except (TypeError, ValueError):
                return fallback

    def save_config(self, candidate: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            current = self.load_config()
            merged = {
                **current,
                **{key: candidate[key] for key in ("enabled", "workspaceId") if key in candidate},
                "lanes": {
                    lane: {
                        **current["lanes"][lane],
                        **(
                            candidate.get("lanes", {}).get(lane, {})
                            if isinstance(candidate.get("lanes"), dict)
                            else {}
                        ),
                    }
                    for lane in LANE_IDS
                },
                "updatedAt": _iso(),
            }
            validated = self._validated_config(merged, current)
            _atomic_json(self.config_path, validated)
            return validated

    @staticmethod
    def _validated_config(
        payload: dict[str, Any], fallback: dict[str, Any]
    ) -> dict[str, Any]:
        workspace_id = str(payload.get("workspaceId", fallback["workspaceId"]))
        if not re.fullmatch(r"[A-Za-z0-9-]{1,64}", workspace_id):
            raise ValueError("工作区编号无效。")
        raw_lanes = payload.get("lanes", {})
        if not isinstance(raw_lanes, dict):
            raise TypeError("lanes 必须是对象。")
        lanes: dict[str, Any] = {}
        for lane in LANE_IDS:
            raw = raw_lanes.get(lane, fallback["lanes"][lane])
            if not isinstance(raw, dict):
                raise TypeError(f"{lane} 配置无效。")
            interval = int(
                raw.get("intervalMinutes", fallback["lanes"][lane]["intervalMinutes"])
            )
            if not 30 <= interval <= 10_080:
                raise ValueError("采集间隔必须在 30 分钟到 7 天之间。")
            lanes[lane] = {
                "enabled": bool(raw.get("enabled", True)),
                "intervalMinutes": interval,
                "label": fallback["lanes"][lane]["label"],
            }
        return {
            "schemaVersion": "1.0",
            "enabled": bool(payload.get("enabled", fallback["enabled"])),
            "workspaceId": workspace_id,
            "updatedAt": str(payload.get("updatedAt", _iso())),
            "lanes": lanes,
        }

    def default_state(self) -> dict[str, Any]:
        now = _now()
        return {
            "schemaVersion": "1.0",
            "scheduler": {
                "status": "starting",
                "instanceId": "",
                "startedAt": "",
                "heartbeatAt": "",
            },
            "lanes": {
                "culture_watch": self._lane_state(now + timedelta(minutes=2)),
                "market_refresh": self._lane_state(now + timedelta(minutes=5)),
            },
        }

    @staticmethod
    def _lane_state(next_run: datetime) -> dict[str, Any]:
        return {
            "status": "scheduled",
            "lastAttemptAt": "",
            "lastSuccessAt": "",
            "nextRunAt": _iso(next_run),
            "detail": "等待下一次调度。",
            "consecutiveFailures": 0,
            "runCount": 0,
            "jobId": "",
            "metrics": {},
        }

    def load_state(self) -> dict[str, Any]:
        with self._lock:
            fallback = self.default_state()
            payload = _load_json(self.state_path, fallback)
            if not isinstance(payload.get("lanes"), dict):
                return fallback
            for lane in LANE_IDS:
                payload["lanes"].setdefault(lane, fallback["lanes"][lane])
            payload.setdefault("scheduler", fallback["scheduler"])
            return payload

    def save_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            _atomic_json(self.state_path, payload)
            return payload

    def add_event(
        self,
        *,
        lane: str,
        status: str,
        detail: str,
        event: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            payload = _load_json(self.events_path, {"events": []})
            events = payload.get("events", [])
            if not isinstance(events, list):
                events = []
            item = {
                "id": f"EVT-{uuid4().hex[:12].upper()}",
                "at": _iso(),
                "lane": lane,
                "event": event,
                "status": status,
                "detail": _safe_detail(detail),
                "metadata": dict(metadata or {}),
            }
            events.insert(0, item)
            _atomic_json(self.events_path, {"events": events[:500]})
            return item

    def list_events(self, limit: int = 60) -> list[dict[str, Any]]:
        with self._lock:
            payload = _load_json(self.events_path, {"events": []})
            events = payload.get("events", [])
            return events[: max(1, min(limit, 200))] if isinstance(events, list) else []

    def list_candidates(
        self, *, status: str = "", limit: int = 80
    ) -> list[dict[str, Any]]:
        with self._lock:
            payload = _load_json(self.candidates_path, {"candidates": []})
            rows = payload.get("candidates", [])
            if not isinstance(rows, list):
                return []
            filtered = [item for item in rows if not status or item.get("status") == status]
            return filtered[: max(1, min(limit, 200))]

    def upsert_candidates(self, candidates: list[dict[str, Any]]) -> int:
        if not candidates:
            return 0
        with self._lock:
            existing = self.list_candidates(limit=200)
            by_url = {str(item.get("url", "")): item for item in existing}
            inserted = 0
            for candidate in candidates:
                url = _normalize_url(str(candidate.get("url", "")))
                current = by_url.get(url)
                if current:
                    current["lastSeenAt"] = _iso()
                    current["discoveryCount"] = int(current.get("discoveryCount", 1)) + 1
                    if candidate.get("title") and not current.get("title"):
                        current["title"] = str(candidate["title"])[:240]
                    continue
                item = {
                    "id": f"CUL-{hashlib.sha1(url.encode('utf-8')).hexdigest()[:12].upper()}",
                    "url": url,
                    "title": str(candidate.get("title") or "待核对来源")[:240],
                    "publisher": str(candidate.get("publisher", ""))[:160],
                    "originSourceId": str(candidate.get("originSourceId", "manual"))[:80],
                    "reason": str(candidate.get("reason", "人工加入候选来源"))[:500],
                    "status": "pending_review",
                    "discoveredAt": _iso(),
                    "lastSeenAt": _iso(),
                    "discoveryCount": 1,
                    "reviewNote": "",
                    "reviewedAt": "",
                }
                existing.insert(0, item)
                by_url[url] = item
                inserted += 1
            _atomic_json(self.candidates_path, {"candidates": existing[:500]})
            return inserted

    def add_manual_candidate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        url = _normalize_url(str(candidate.get("url", "")))
        self.upsert_candidates(
            [
                {
                    "url": url,
                    "title": candidate.get("title") or "人工提交来源",
                    "publisher": candidate.get("publisher", ""),
                    "reason": candidate.get("reason", "人工加入候选来源"),
                    "originSourceId": "manual",
                }
            ]
        )
        return next(item for item in self.list_candidates(limit=500) if item["url"] == url)

    def review_candidate(
        self, candidate_id: str, *, status: str, note: str = ""
    ) -> dict[str, Any]:
        allowed = {"pending_review", "ready_to_structure", "rejected"}
        if status not in allowed:
            raise ValueError("候选状态必须是待核验、可结构化或已排除。")
        with self._lock:
            payload = _load_json(self.candidates_path, {"candidates": []})
            rows = payload.get("candidates", [])
            if not isinstance(rows, list):
                rows = []
            target = next((item for item in rows if item.get("id") == candidate_id), None)
            if target is None:
                raise FileNotFoundError(f"文化候选不存在：{candidate_id}")
            target.update(
                {
                    "status": status,
                    "reviewNote": str(note)[:800],
                    "reviewedAt": _iso(),
                }
            )
            _atomic_json(self.candidates_path, {"candidates": rows[:500]})
            return target

    def candidate_counts(self) -> dict[str, int]:
        counts = Counter(str(item.get("status", "unknown")) for item in self.list_candidates(limit=500))
        return dict(counts)


class CultureSourceWatcher:
    """Checks curated sources and discovers same-site candidates without auto-promoting facts."""

    def __init__(
        self,
        graph_path: Path,
        store: CollectionStore,
        *,
        fetcher: Fetcher = fetch_public_page,
        batch_size: int = 4,
    ) -> None:
        self.graph_path = graph_path.resolve()
        self.store = store
        self.fetcher = fetcher
        self.batch_size = max(1, min(batch_size, 12))

    def run(self) -> dict[str, Any]:
        graph = _load_json(self.graph_path, {"records": [], "sources": []})
        records = graph.get("records", []) if isinstance(graph.get("records"), list) else []
        sources = graph.get("sources", []) if isinstance(graph.get("sources"), list) else []
        if not sources:
            raise RuntimeError("文化图谱没有可巡检来源。")

        source_state = _load_json(
            self.store.source_state_path,
            {"cursor": 0, "sources": {}, "updatedAt": ""},
        )
        cursor = int(source_state.get("cursor", 0)) % len(sources)
        batch = [sources[(cursor + index) % len(sources)] for index in range(self.batch_size)]
        known_urls = {
            _normalize_url(str(item.get("source_url", "")))
            for item in sources
            if item.get("source_url")
        }
        source_rows = source_state.get("sources", {})
        if not isinstance(source_rows, dict):
            source_rows = {}

        metrics = {
            "verifiedRecords": len(records),
            "verifiedSources": len(sources),
            "probed": 0,
            "healthy": 0,
            "unchanged": 0,
            "changed": 0,
            "errors": 0,
            "newCandidates": 0,
        }
        discovered: list[dict[str, Any]] = []

        for source in batch:
            source_id = str(source.get("source_id", "unknown"))
            url = _normalize_url(str(source.get("source_url", "")))
            previous = source_rows.get(source_id, {})
            conditional = {}
            if previous.get("etag"):
                conditional["If-None-Match"] = str(previous["etag"])
            if previous.get("lastModified"):
                conditional["If-Modified-Since"] = str(previous["lastModified"])
            metrics["probed"] += 1
            try:
                response = self.fetcher(url, conditional)
                if response.status == 304:
                    metrics["healthy"] += 1
                    metrics["unchanged"] += 1
                    previous.update({"status": 304, "checkedAt": _iso(), "error": ""})
                    source_rows[source_id] = previous
                    continue
                digest = hashlib.sha256(response.body).hexdigest()
                changed = bool(previous.get("sha256") and previous.get("sha256") != digest)
                metrics["healthy"] += 1
                metrics["changed" if changed else "unchanged"] += 1
                collector = _LinkCollector()
                content_type = str(response.headers.get("content-type", ""))
                if "html" in content_type.lower() or response.body.lstrip().startswith(b"<"):
                    collector.feed(response.body.decode("utf-8", errors="ignore"))
                    discovered.extend(
                        self._candidate_links(
                            response.url,
                            collector.links,
                            known_urls,
                            source_id=source_id,
                            publisher=str(source.get("publisher", "")),
                        )
                    )
                source_rows[source_id] = {
                    "url": url,
                    "status": response.status,
                    "checkedAt": _iso(),
                    "changedAt": _iso() if changed else str(previous.get("changedAt", "")),
                    "sha256": digest,
                    "etag": str(response.headers.get("etag", "")),
                    "lastModified": str(response.headers.get("last-modified", "")),
                    "title": collector.title or str(source.get("source_title", "")),
                    "error": "",
                }
            except Exception as exc:  # noqa: BLE001 - source health is persisted, not raised
                metrics["errors"] += 1
                source_rows[source_id] = {
                    **(previous if isinstance(previous, dict) else {}),
                    "url": url,
                    "status": 0,
                    "checkedAt": _iso(),
                    "error": _safe_detail(exc, 300),
                }

        metrics["newCandidates"] = self.store.upsert_candidates(discovered)
        source_state.update(
            {
                "cursor": (cursor + len(batch)) % len(sources),
                "sources": source_rows,
                "updatedAt": _iso(),
                "lastMetrics": metrics,
            }
        )
        _atomic_json(self.store.source_state_path, source_state)
        return metrics

    @staticmethod
    def _candidate_links(
        page_url: str,
        links: list[tuple[str, str]],
        known_urls: set[str],
        *,
        source_id: str,
        publisher: str,
    ) -> list[dict[str, Any]]:
        page_host = urlparse(page_url).hostname
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for href, label in links:
            if not href or href.startswith(("mailto:", "javascript:", "tel:")):
                continue
            try:
                url = _normalize_url(urljoin(page_url, href))
            except ValueError:
                continue
            parsed = urlparse(url)
            if parsed.hostname != page_host or url in known_urls or url in seen:
                continue
            if re.search(
                r"\.(?:jpg|jpeg|png|gif|webp|svg|zip|rar|mp4|mp3|pdf)$",
                parsed.path,
                re.IGNORECASE,
            ):
                continue
            haystack = f"{label} {parsed.path} {parsed.query}"
            if not any(keyword in haystack for keyword in CULTURE_DISCOVERY_KEYWORDS):
                continue
            normalized_label = " ".join(label.split())
            article_like = bool(
                re.search(
                    r"(?:/20\d{2}(?:[-_/]|$)|(?:detail|details|article|content|news)|\.(?:html?|shtml)$)",
                    parsed.path,
                    re.IGNORECASE,
                )
            )
            if (
                not article_like
                or len(normalized_label) < 6
                or normalized_label in GENERIC_NAV_LABELS
                or normalized_label.endswith("杂志")
            ):
                continue
            seen.add(url)
            rows.append(
                {
                    "url": url,
                    "title": normalized_label or "同域文化资料候选",
                    "publisher": publisher,
                    "originSourceId": source_id,
                    "reason": f"由已核验来源 {source_id} 的同域相关链接发现；需人工核验后结构化。",
                }
            )
            if len(rows) >= 8:
                break
        return rows


class CollectionScheduler:
    """Single-process persistent scheduler for culture monitoring and market refresh."""

    def __init__(
        self,
        store: CollectionStore,
        watcher: CultureSourceWatcher,
        *,
        research_preflight: Callable[[], dict[str, Any]],
        research_start: Callable[[str], dict[str, Any]],
        research_status: Callable[[str], dict[str, Any]],
        tick_seconds: float = 15.0,
    ) -> None:
        self.store = store
        self.watcher = watcher
        self.research_preflight = research_preflight
        self.research_start = research_start
        self.research_status = research_status
        self.tick_seconds = max(0.2, tick_seconds)
        self.instance_id = f"collector-{uuid4().hex[:10]}"
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            state = self.store.load_state()
            for lane in LANE_IDS:
                lane_state = state["lanes"][lane]
                if lane_state.get("status") == "running":
                    lane_state.update(
                        {
                            "status": "interrupted",
                            "detail": "API 进程重启；旧运行不会被冒充为成功，已重新排队。",
                            "jobId": "",
                            "nextRunAt": _iso(_now() + timedelta(minutes=2)),
                        }
                    )
            state["scheduler"] = {
                "status": "running",
                "instanceId": self.instance_id,
                "startedAt": _iso(),
                "heartbeatAt": _iso(),
            }
            self.store.save_state(state)
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._loop,
                daemon=True,
                name="qiancraft-continuous-collection",
            )
            self._thread.start()
            self.store.add_event(
                lane="system",
                status="running",
                event="scheduler_started",
                detail="持续采集调度器已启动。",
                metadata={"instanceId": self.instance_id},
            )

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=min(5.0, self.tick_seconds + 0.5))
        state = self.store.load_state()
        state["scheduler"].update({"status": "stopped", "heartbeatAt": _iso()})
        self.store.save_state(state)

    def _loop(self) -> None:
        while not self._stop_event.wait(self.tick_seconds):
            try:
                self.tick()
            except Exception as exc:  # noqa: BLE001 - scheduler must survive one bad tick
                self.store.add_event(
                    lane="system",
                    status="error",
                    event="scheduler_tick_failed",
                    detail=_safe_detail(exc),
                )

    def tick(self) -> None:
        with self._lock:
            config = self.store.load_config()
            state = self.store.load_state()
            state["scheduler"].update(
                {
                    "status": "running" if config["enabled"] else "paused",
                    "instanceId": self.instance_id,
                    "heartbeatAt": _iso(),
                }
            )
            self._poll_market_job(state, config)
            for lane in LANE_IDS:
                lane_config = config["lanes"][lane]
                lane_state = state["lanes"][lane]
                if not config["enabled"] or not lane_config["enabled"]:
                    if lane_state.get("status") != "running":
                        lane_state.update(
                            {"status": "paused", "detail": "该采集通道已暂停。"}
                        )
                    continue
                if lane_state.get("status") == "running":
                    continue
                due = _parse_time(str(lane_state.get("nextRunAt", "")))
                if due is None or due <= _now():
                    if lane == "culture_watch":
                        self._start_culture_lane(state, config)
                    else:
                        self._start_market_lane(state, config)
            self.store.save_state(state)

    def _start_culture_lane(self, state: dict[str, Any], config: dict[str, Any]) -> None:
        lane = state["lanes"]["culture_watch"]
        lane.update(
            {
                "status": "running",
                "lastAttemptAt": _iso(),
                "detail": "正在巡检已核验来源并发现同域候选。",
                "jobId": "",
            }
        )
        self.store.save_state(state)
        worker = threading.Thread(
            target=self._culture_worker,
            args=(config["lanes"]["culture_watch"]["intervalMinutes"],),
            daemon=True,
            name="qiancraft-culture-watch",
        )
        worker.start()

    def _culture_worker(self, interval_minutes: int) -> None:
        try:
            metrics = self.watcher.run()
            success = (
                metrics["probed"] > 0
                and metrics["healthy"] == metrics["probed"]
                and metrics["errors"] == 0
            )
            detail = (
                f"巡检 {metrics['probed']} 个来源；{metrics['healthy']} 个成功、"
                f"{metrics['errors']} 个失败，"
                f"新增 {metrics['newCandidates']} 条待核验候选。"
            )
            with self._lock:
                state = self.store.load_state()
                lane = state["lanes"]["culture_watch"]
                failures = 0 if success else int(lane.get("consecutiveFailures", 0)) + 1
                lane.update(
                    {
                        "status": "healthy" if success else "degraded",
                        "lastSuccessAt": _iso() if success else lane.get("lastSuccessAt", ""),
                        "nextRunAt": _iso(_now() + timedelta(minutes=interval_minutes)),
                        "detail": detail,
                        "consecutiveFailures": failures,
                        "runCount": int(lane.get("runCount", 0)) + 1,
                        "metrics": metrics,
                    }
                )
                self.store.save_state(state)
            self.store.add_event(
                lane="culture_watch",
                status="healthy" if success else "degraded",
                event="culture_watch_completed",
                detail=detail,
                metadata=metrics,
            )
        except Exception as exc:  # noqa: BLE001 - lane failure is observable and retried
            self._fail_lane("culture_watch", exc, interval_minutes)

    def _start_market_lane(self, state: dict[str, Any], config: dict[str, Any]) -> None:
        lane = state["lanes"]["market_refresh"]
        lane["lastAttemptAt"] = _iso()
        preflight = self.research_preflight()
        if not preflight.get("research_ready"):
            failures = int(lane.get("consecutiveFailures", 0)) + 1
            retry_minutes = min(
                int(config["lanes"]["market_refresh"]["intervalMinutes"]),
                max(15, 15 * min(failures, 8)),
            )
            blockers = preflight.get("blockers", [])
            detail = "自动采集受阻：" + "；".join(str(item) for item in blockers[:4])
            lane.update(
                {
                    "status": "blocked",
                    "detail": detail,
                    "consecutiveFailures": failures,
                    "nextRunAt": _iso(_now() + timedelta(minutes=retry_minutes)),
                    "jobId": "",
                    "metrics": {"blockerCount": len(blockers)},
                }
            )
            self.store.add_event(
                lane="market_refresh",
                status="blocked",
                event="market_refresh_blocked",
                detail=detail,
                metadata={"retryMinutes": retry_minutes},
            )
            return
        try:
            job = self.research_start(str(config["workspaceId"]))
        except Exception as exc:  # noqa: BLE001 - contention/failure becomes visible state
            self._fail_lane(
                "market_refresh",
                exc,
                int(config["lanes"]["market_refresh"]["intervalMinutes"]),
                state=state,
            )
            return
        lane.update(
            {
                "status": "running",
                "detail": "严格知识检索与四平台增量采集已进入后台队列。",
                "jobId": str(job.get("job_id", "")),
                "metrics": {},
            }
        )
        self.store.add_event(
            lane="market_refresh",
            status="running",
            event="market_refresh_started",
            detail=lane["detail"],
            metadata={"jobId": lane["jobId"]},
        )

    def _poll_market_job(self, state: dict[str, Any], config: dict[str, Any]) -> None:
        lane = state["lanes"]["market_refresh"]
        job_id = str(lane.get("jobId", ""))
        if lane.get("status") != "running" or not job_id:
            return
        try:
            job = self.research_status(job_id)
        except Exception as exc:  # noqa: BLE001
            self._fail_lane(
                "market_refresh",
                exc,
                int(config["lanes"]["market_refresh"]["intervalMinutes"]),
                state=state,
            )
            return
        status = str(job.get("status", ""))
        if status not in TERMINAL_RESEARCH_STATUSES:
            lane["detail"] = str(job.get("detail", lane["detail"]))
            return
        interval = int(config["lanes"]["market_refresh"]["intervalMinutes"])
        success = status == "live_verified"
        failures = 0 if success else int(lane.get("consecutiveFailures", 0)) + 1
        retry_minutes = interval if success else min(interval, max(30, 30 * min(failures, 8)))
        lane.update(
            {
                "status": "healthy" if success else "degraded",
                "lastSuccessAt": _iso() if success else lane.get("lastSuccessAt", ""),
                "nextRunAt": _iso(_now() + timedelta(minutes=retry_minutes)),
                "detail": str(job.get("detail", "采集任务已结束。")),
                "consecutiveFailures": failures,
                "runCount": int(lane.get("runCount", 0)) + 1,
                "jobId": "",
                "metrics": {
                    "componentModes": job.get("component_modes", {}),
                    "platformModes": job.get("platform_modes", {}),
                },
            }
        )
        self.store.add_event(
            lane="market_refresh",
            status=lane["status"],
            event="market_refresh_completed",
            detail=lane["detail"],
            metadata={"jobId": job_id, **lane["metrics"]},
        )

    def _fail_lane(
        self,
        lane_id: str,
        error: object,
        interval_minutes: int,
        *,
        state: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            current = state or self.store.load_state()
            lane = current["lanes"][lane_id]
            failures = int(lane.get("consecutiveFailures", 0)) + 1
            retry_minutes = min(interval_minutes, max(15, 15 * min(failures, 8)))
            detail = f"运行失败：{_safe_detail(error, 500)}"
            lane.update(
                {
                    "status": "failed",
                    "detail": detail,
                    "consecutiveFailures": failures,
                    "nextRunAt": _iso(_now() + timedelta(minutes=retry_minutes)),
                    "jobId": "",
                }
            )
            self.store.save_state(current)
        self.store.add_event(
            lane=lane_id,
            status="failed",
            event="lane_failed",
            detail=detail,
            metadata={"retryMinutes": retry_minutes},
        )

    def run_now(self, lane_id: str) -> dict[str, Any]:
        requested = LANE_IDS if lane_id == "all" else (lane_id,)
        if any(item not in LANE_IDS for item in requested):
            raise ValueError("采集通道必须是 culture_watch、market_refresh 或 all。")
        config = self.store.load_config()
        if not config["enabled"]:
            raise RuntimeError("持续采集总开关已暂停；请先恢复调度。")
        with self._lock:
            state = self.store.load_state()
            for lane in requested:
                if not config["lanes"][lane]["enabled"]:
                    raise RuntimeError(f"采集通道已暂停：{lane}")
                if state["lanes"][lane].get("status") == "running":
                    continue
                state["lanes"][lane].update(
                    {
                        "status": "scheduled",
                        "nextRunAt": _iso(_now() - timedelta(seconds=1)),
                        "detail": "已请求立即运行。",
                    }
                )
            self.store.save_state(state)
        self.tick()
        return self.status()

    def configure(self, candidate: dict[str, Any]) -> dict[str, Any]:
        previous = self.store.load_config()
        config = self.store.save_config(candidate)
        with self._lock:
            state = self.store.load_state()
            for lane in LANE_IDS:
                enabled = config["enabled"] and config["lanes"][lane]["enabled"]
                was_enabled = previous["enabled"] and previous["lanes"][lane]["enabled"]
                if enabled and not was_enabled:
                    state["lanes"][lane].update(
                        {
                            "status": "scheduled",
                            "nextRunAt": _iso(_now() + timedelta(seconds=30)),
                            "detail": "通道已恢复，等待下一次调度。",
                        }
                    )
                elif not enabled and state["lanes"][lane].get("status") != "running":
                    state["lanes"][lane].update(
                        {"status": "paused", "detail": "该采集通道已暂停。"}
                    )
            self.store.save_state(state)
        self.store.add_event(
            lane="system",
            status="running" if config["enabled"] else "paused",
            event="schedule_updated",
            detail="持续采集计划已更新。",
            metadata={
                "enabled": config["enabled"],
                "cultureMinutes": config["lanes"]["culture_watch"]["intervalMinutes"],
                "marketMinutes": config["lanes"]["market_refresh"]["intervalMinutes"],
            },
        )
        return self.status()

    def status(self) -> dict[str, Any]:
        config = self.store.load_config()
        state = self.store.load_state()
        candidates = self.store.candidate_counts()
        source_state = _load_json(self.store.source_state_path, {})
        culture_graph = _load_json(
            self.watcher.graph_path,
            {"records": [], "sources": []},
        )
        preflight = self.research_preflight()
        scheduler = state["scheduler"]
        return {
            "schemaVersion": "1.0",
            "enabled": config["enabled"],
            "workspaceId": config["workspaceId"],
            "scheduler": {
                **scheduler,
                "threadAlive": bool(self._thread and self._thread.is_alive()),
            },
            "lanes": {
                lane: {
                    **state["lanes"][lane],
                    "enabled": config["lanes"][lane]["enabled"],
                    "intervalMinutes": config["lanes"][lane]["intervalMinutes"],
                    "label": config["lanes"][lane]["label"],
                }
                for lane in LANE_IDS
            },
            "culture": {
                "verifiedRecords": len(culture_graph.get("records", [])),
                "verifiedSources": len(culture_graph.get("sources", [])),
                "candidateCounts": candidates,
                "sourceStateUpdatedAt": source_state.get("updatedAt", ""),
                "lastMetrics": source_state.get("lastMetrics", {}),
                "promotionPolicy": (
                    "自动巡检只进入候选队列；人工核验、字段证据映射和文化边界检查完成后，"
                    "才能写入正式图谱。"
                ),
            },
            "market": {
                "preflight": preflight,
                "promotionPolicy": (
                    "只有文化、四平台和策划均为本轮 live 才晋级；失败轮只保留审计。"
                ),
            },
        }

    def health(self, *, now: datetime | None = None) -> dict[str, Any]:
        """Return a cheap liveness verdict suitable for container health checks."""
        config = self.store.load_config()
        state = self.store.load_state()
        scheduler = state.get("scheduler", {})
        heartbeat_at = str(scheduler.get("heartbeatAt", ""))
        heartbeat = _parse_time(heartbeat_at)
        current = now or _now()
        heartbeat_age_seconds = (
            max(0.0, (current - heartbeat).total_seconds()) if heartbeat else None
        )
        heartbeat_fresh = (
            heartbeat_age_seconds is not None
            and heartbeat_age_seconds <= SCHEDULER_HEARTBEAT_MAX_AGE_SECONDS
        )
        thread_alive = bool(self._thread and self._thread.is_alive())
        healthy = thread_alive and heartbeat_fresh
        return {
            "ok": healthy,
            "online": thread_alive,
            "heartbeatAt": heartbeat_at,
            "heartbeatFresh": heartbeat_fresh,
            "heartbeatAgeSeconds": (
                round(heartbeat_age_seconds, 3)
                if heartbeat_age_seconds is not None
                else None
            ),
            "maxHeartbeatAgeSeconds": SCHEDULER_HEARTBEAT_MAX_AGE_SECONDS,
            "enabled": config["enabled"],
            "status": "healthy" if healthy else "unhealthy",
        }
