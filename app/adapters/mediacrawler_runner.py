from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote


def _platform_argument(arguments: list[str]) -> str:
    for index, argument in enumerate(arguments):
        if argument == "--platform" and index + 1 < len(arguments):
            return arguments[index + 1].strip().lower()
        if argument.startswith("--platform="):
            return argument.partition("=")[2].strip().lower()
    return ""


def _install_managed_navigation_override(page_type: type[Any] | None = None) -> None:
    """Let managed-platform homepages proceed once their DOM is ready."""

    if page_type is None:
        from playwright.async_api import Page

        page_type = Page
    original_goto = page_type.goto

    managed_homepages = {
        "https://www.xiaohongshu.com",
        "https://www.rednote.com",
        "https://www.douyin.com",
        "https://www.bilibili.com",
        "https://www.weibo.com",
        "https://weibo.com",
        "https://m.weibo.cn",
    }

    async def goto_dom_ready(self: Any, url: str, **kwargs: Any) -> Any:
        if url.rstrip("/") in managed_homepages:
            kwargs.setdefault("wait_until", "domcontentloaded")
            kwargs.setdefault("timeout", 60_000)
        return await original_goto(self, url, **kwargs)

    page_type.goto = goto_dom_ready


def _install_douyin_managed_cdp_search(client_type: type[Any] | None = None) -> None:
    """Use the authorized browser's current search request instead of stale API params."""

    if client_type is None:
        from media_platform.douyin.client import DouYinClient

        client_type = DouYinClient

    async def browser_session_is_authorized(
        self: Any, browser_context: Any
    ) -> bool:
        del self, browser_context
        # The protected CDP session is authorized explicitly by the user. Actual
        # authorization is still proven by a non-empty browser search response;
        # the adapter never marks this platform live based on this method alone.
        return True

    async def search_via_authorized_page(
        self: Any,
        keyword: str,
        offset: int = 0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del kwargs
        # The browser UI returns ten records per submitted keyword. One page for
        # each of six formal keywords is sufficient for the >=50-record gate and
        # avoids unsupported direct pagination parameters.
        if offset > 0:
            return {"status_code": 0, "data": []}

        page = self.playwright_page
        if page is None:
            raise RuntimeError("Douyin managed CDP search has no browser page")
        # Douyin pre-fills the keyword encoded in the route. Submitting that
        # unchanged value is currently a no-op, so open a neutral query first
        # and then submit the requested keyword through the visible button.
        seed_keyword = "文化创意" if keyword != "文化创意" else "文创"
        search_url = (
            f"https://www.douyin.com/search/{quote(seed_keyword, safe='')}?type=general"
        )
        await page.goto(search_url, wait_until="domcontentloaded", timeout=60_000)
        field = page.locator('input[placeholder="搜索你感兴趣的内容"]')
        await field.wait_for(state="visible", timeout=60_000)
        # The field can become visible before Douyin finishes hydrating its
        # event handlers. A conservative interval also avoids issuing the six
        # formal searches as a burst against the user's authorized session.
        await page.wait_for_timeout(15_000)
        captcha = page.locator("#captcha_container")
        if await captcha.count() and await captcha.is_visible():
            raise RuntimeError("Douyin requires visible user verification")
        await field.fill(keyword)
        search_button = field.locator("xpath=../..").get_by_role(
            "button", name="搜索"
        )
        await search_button.wait_for(state="visible", timeout=60_000)
        async with page.expect_response(
            lambda response: "/aweme/v1/web/general/search/" in response.url,
            timeout=60_000,
        ) as response_info:
            await search_button.click()
        response = await response_info.value
        if response.status != 200:
            raise RuntimeError(f"Douyin browser search returned HTTP {response.status}")
        payload = await response.json()
        if not isinstance(payload, dict):
            raise TypeError("Douyin browser search returned a non-object payload")
        return payload

    client_type.pong = browser_session_is_authorized
    client_type.search_info_by_keyword = search_via_authorized_page


def _install_managed_browser_reuse(manager_type: type[Any] | None = None) -> None:
    """Close pages created by one crawl without terminating the shared browser."""

    if manager_type is None:
        from tools.cdp_browser import CDPBrowserManager

        manager_type = CDPBrowserManager
    original_launch = manager_type.launch_and_connect

    async def launch_and_track(self: Any, *args: Any, **kwargs: Any) -> Any:
        context = await original_launch(self, *args, **kwargs)
        self._qiancraft_existing_page_ids = {id(page) for page in context.pages}
        return context

    async def keep_managed_browser(self: Any, force: bool = False) -> None:
        del force
        context = self.browser_context
        existing_page_ids = getattr(self, "_qiancraft_existing_page_ids", set())
        if context is not None:
            for page in tuple(context.pages):
                if id(page) in existing_page_ids:
                    continue
                try:
                    await page.close()
                except Exception:  # noqa: BLE001, S110 - best-effort cleanup
                    pass
        self.browser_context = None
        self.browser = None

    manager_type.launch_and_connect = launch_and_track
    manager_type.cleanup = keep_managed_browser


def run() -> None:
    """Launch upstream MediaCrawler with an explicit user-authorized login path."""

    source_root = Path(os.environ.pop("QIANCRAFT_MEDIACRAWLER_ROOT", "")).resolve()
    cookie = os.environ.pop("QIANCRAFT_MEDIACRAWLER_COOKIE", "")
    login_method = os.environ.pop("QIANCRAFT_MEDIACRAWLER_LOGIN_METHOD", "cdp")
    cdp_port = int(os.environ.pop("QIANCRAFT_MEDIACRAWLER_CDP_PORT", "9222"))
    cdp_connect_existing = os.environ.pop(
        "QIANCRAFT_MEDIACRAWLER_CDP_CONNECT_EXISTING", "true"
    ).lower() in {"1", "true", "yes"}
    headless = os.environ.pop("QIANCRAFT_MEDIACRAWLER_HEADLESS", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    if not source_root.joinpath("main.py").exists():
        raise FileNotFoundError(f"MediaCrawler source not found: {source_root}")
    if login_method == "cookie" and not cookie:
        raise RuntimeError("QianCraft MediaCrawler cookie path received no authorized cookie")
    sys.path.insert(0, str(source_root))

    import config  # type: ignore

    if cookie:
        config.COOKIES = cookie
    config.ENABLE_CDP_MODE = login_method == "cdp"
    config.CDP_DEBUG_PORT = cdp_port
    config.CDP_CONNECT_EXISTING = cdp_connect_existing
    config.HEADLESS = headless
    config.CDP_HEADLESS = headless
    config.AUTO_CLOSE_BROWSER = not cdp_connect_existing
    platform = _platform_argument(sys.argv[1:])
    if login_method == "cdp" and cdp_connect_existing:
        _install_managed_navigation_override()
        if platform == "dy":
            _install_douyin_managed_cdp_search()
        _install_managed_browser_reuse()
    from main import async_cleanup, main  # type: ignore
    from tools.app_runner import run as run_upstream  # type: ignore

    run_upstream(main, async_cleanup, cleanup_timeout_seconds=15.0)


if __name__ == "__main__":
    run()
