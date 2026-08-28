from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import replace
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.adapters.media_crawler_adapter import (
    MARKET_PLATFORMS,
    PLATFORM_LABELS,
    MediaCrawlerAdapter,
)
from app.config import load_settings


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "逐平台验证 MediaCrawler 登录、关键词搜索、真实结果与保存；"
            "默认不打开浏览器，--authorize 才允许人工登录。"
        )
    )
    parser.add_argument(
        "--platform",
        choices=["all", *MARKET_PLATFORMS],
        default="all",
        help="建议首次授权逐个平台运行；all 用于已登录 CDP 浏览器的总复核。",
    )
    parser.add_argument("--method", choices=["cdp", "qrcode", "cookie"], default="cdp")
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--topic", default="非遗")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--keyword-limit", type=int, default=1)
    parser.add_argument("--max-results", type=int, default=10)
    return parser.parse_args()


async def _main() -> int:
    args = _arguments()
    platforms = (
        MARKET_PLATFORMS if args.platform == "all" else (str(args.platform),)
    )
    keyword_limit = 6 if args.formal else max(1, min(6, args.keyword_limit))
    max_results = 20 if args.formal else max(10, min(20, args.max_results))
    record_limit = 150 if args.formal else 20
    base = load_settings()
    settings = replace(
        base,
        live_mode=True,
        demo_mode=True,
        mediacrawler_live_enabled=True,
        mediacrawler_platform=platforms[0],
        mediacrawler_platforms=platforms,
        mediacrawler_login_method=args.method,
        mediacrawler_interactive_login=args.authorize,
        mediacrawler_cdp_connect_existing=(
            base.mediacrawler_cdp_connect_existing
            if not args.authorize
            else False
        ),
        mediacrawler_timeout_seconds=max(60, args.timeout),
        mediacrawler_keyword_limit=keyword_limit,
        mediacrawler_max_results=max_results,
        mediacrawler_platform_record_limit=record_limit,
    )
    trend, _ = await MediaCrawlerAdapter(settings).research(args.topic)
    statuses = trend.retrieval["market_platforms"]

    print("QianCraft Market Intelligence Probe")
    print()
    live_count = 0
    for platform in platforms:
        source = statuses[platform]
        minimum = 50 if args.formal else 5
        live = source["status"] == "live" and source["sample_size"] >= minimum
        live_count += int(live)
        login_label = "LOGIN OK" if source["login_ok"] else "LOGIN WAIT"
        search_label = "SEARCH OK" if source["search_ok"] else "SEARCH NO"
        label = f"{platform.upper():<5}"
        print(
            f"{label}  {login_label:<10}  {search_label:<10}  "
            f"{source['sample_size']:>3} RESULTS  [{source['status']}]"
        )
        if not live:
            print(f"       {PLATFORM_LABELS[platform]}：{source['detail']}")
            if source["status"] == "live":
                print(f"       样本不足：本模式至少需要 {minimum} 条。")
    print()
    print(f"{live_count} / {len(platforms)} platforms live")
    print(f"hotness: {trend.retrieval['product_form_hotness_path']}")
    return 0 if live_count == len(platforms) else 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(asyncio.run(_main()))
