from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.adapters.mediacrawler_runner import (
    _install_douyin_managed_cdp_search,
    _install_managed_browser_reuse,
    _install_managed_navigation_override,
    _platform_argument,
)


def test_platform_argument_supports_both_cli_forms() -> None:
    assert _platform_argument(["--platform", "DY"]) == "dy"
    assert _platform_argument(["--platform=wb"]) == "wb"
    assert _platform_argument(["--keywords", "非遗文创"]) == ""


def test_managed_homepage_navigation_waits_for_dom_only() -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    class FakePage:
        async def goto(self, url: str, **kwargs: Any) -> str:
            calls.append((url, kwargs))
            return "ok"

    _install_managed_navigation_override(FakePage)
    page = FakePage()

    assert asyncio.run(page.goto("https://www.douyin.com")) == "ok"
    assert calls[-1] == (
        "https://www.douyin.com",
        {"wait_until": "domcontentloaded", "timeout": 60_000},
    )

    asyncio.run(page.goto("https://www.xiaohongshu.com"))
    assert calls[-1] == (
        "https://www.xiaohongshu.com",
        {"wait_until": "domcontentloaded", "timeout": 60_000},
    )

    asyncio.run(page.goto("https://www.xiaohongshu.com/explore", timeout=12_000))
    assert calls[-1] == (
        "https://www.xiaohongshu.com/explore",
        {"timeout": 12_000},
    )


def test_douyin_managed_cdp_search_uses_browser_response() -> None:
    calls: list[tuple[str, Any]] = []
    payload = {"status_code": 0, "data": [{"aweme_info": {"aweme_id": "1"}}]}

    class FakeResponse:
        status = 200
        url = "https://www.douyin.com/aweme/v1/web/general/search/stream/"

        async def json(self) -> dict[str, Any]:
            return payload

    class FakeResponseInfo:
        @property
        async def value(self) -> FakeResponse:
            return FakeResponse()

    class FakeResponseContext:
        async def __aenter__(self) -> FakeResponseInfo:
            calls.append(("expect_enter", None))
            return FakeResponseInfo()

        async def __aexit__(self, *args: object) -> None:
            calls.append(("expect_exit", None))

    class FakeField:
        async def wait_for(self, **kwargs: Any) -> None:
            calls.append(("wait_for", kwargs))

        async def fill(self, value: str) -> None:
            calls.append(("fill", value))

        def locator(self, selector: str) -> FakeSearchContainer:
            calls.append(("field_locator", selector))
            return FakeSearchContainer()

    class FakeSearchButton:
        async def wait_for(self, **kwargs: Any) -> None:
            calls.append(("button_wait_for", kwargs))

        async def click(self) -> None:
            calls.append(("button_click", None))

    class FakeSearchContainer:
        def get_by_role(self, role: str, **kwargs: Any) -> FakeSearchButton:
            calls.append(("get_by_role", (role, kwargs)))
            return FakeSearchButton()

    class FakeCaptcha:
        visible = False

        async def count(self) -> int:
            return 1

        async def is_visible(self) -> bool:
            return self.visible

    class FakePage:
        async def goto(self, url: str, **kwargs: Any) -> None:
            calls.append(("goto", (url, kwargs)))

        async def wait_for_timeout(self, timeout: int) -> None:
            calls.append(("wait_for_timeout", timeout))

        def locator(self, selector: str) -> FakeField:
            calls.append(("locator", selector))
            if selector == "#captcha_container":
                return FakeCaptcha()  # type: ignore[return-value]
            return FakeField()

        def expect_response(self, predicate: Any, **kwargs: Any) -> FakeResponseContext:
            assert predicate(FakeResponse()) is True
            calls.append(("expect_response", kwargs))
            return FakeResponseContext()

    class FakeClient:
        def __init__(self) -> None:
            self.playwright_page = FakePage()

    _install_douyin_managed_cdp_search(FakeClient)
    client = FakeClient()

    assert asyncio.run(client.pong(object())) is True
    assert (
        asyncio.run(client.search_info_by_keyword("苗绣 文创", offset=0))
        == payload
    )
    assert calls[0] == (
        "goto",
        (
            "https://www.douyin.com/search/%E6%96%87%E5%8C%96%E5%88%9B%E6%84%8F?type=general",
            {"wait_until": "domcontentloaded", "timeout": 60_000},
        ),
    )
    assert ("wait_for_timeout", 15_000) in calls
    assert ("button_click", None) in calls
    assert asyncio.run(client.search_info_by_keyword("苗绣文创", offset=10)) == {
        "status_code": 0,
        "data": [],
    }
    FakeCaptcha.visible = True
    with pytest.raises(RuntimeError, match="visible user verification"):
        asyncio.run(client.search_info_by_keyword("苗绣文创", offset=0))


def test_managed_browser_cleanup_closes_only_pages_created_by_crawl() -> None:
    class FakePage:
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    class FakeContext:
        def __init__(self, pages: list[FakePage]) -> None:
            self.pages = pages

    existing = FakePage()
    created = FakePage()
    context = FakeContext([existing])

    class FakeManager:
        def __init__(self) -> None:
            self.browser_context: FakeContext | None = None
            self.browser: object | None = object()

        async def launch_and_connect(self) -> FakeContext:
            self.browser_context = context
            return context

    _install_managed_browser_reuse(FakeManager)
    manager = FakeManager()
    asyncio.run(manager.launch_and_connect())
    context.pages.append(created)
    asyncio.run(manager.cleanup())

    assert existing.closed is False
    assert created.closed is True
    assert manager.browser_context is None
    assert manager.browser is None
