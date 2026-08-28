from __future__ import annotations

import os
import sys
from pathlib import Path


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
    from main import async_cleanup, main  # type: ignore
    from tools.app_runner import run as run_upstream  # type: ignore

    run_upstream(main, async_cleanup, cleanup_timeout_seconds=15.0)


if __name__ == "__main__":
    run()
