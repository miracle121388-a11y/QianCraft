from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.adapters.media_crawler_adapter import MediaCrawlerAdapter
from app.config import load_settings


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="以用户显式授权的二维码或 CDP 浏览器运行小红书 MVP 采集"
    )
    parser.add_argument("--method", choices=["qrcode", "cdp", "cookie"], default="cdp")
    parser.add_argument("--topic", default="贵州苗绣")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--keyword-limit", type=int, default=6)
    return parser.parse_args()


async def _main() -> int:
    args = _arguments()
    base = load_settings()
    settings = replace(
        base,
        live_mode=True,
        demo_mode=True,
        mediacrawler_live_enabled=True,
        mediacrawler_platform="xhs",
        mediacrawler_platforms=("xhs",),
        mediacrawler_login_method=args.method,
        mediacrawler_interactive_login=True,
        mediacrawler_cdp_connect_existing=args.method != "cdp",
        mediacrawler_timeout_seconds=max(60, args.timeout),
        mediacrawler_keyword_limit=max(5, min(22, args.keyword_limit)),
        mediacrawler_platform_record_limit=150,
    )
    trend, status = await MediaCrawlerAdapter(settings).research(args.topic)
    source = trend.retrieval["market_platforms"]["xhs"]
    print(json.dumps(source, ensure_ascii=False, indent=2))
    print(f"[{status.mode.upper()}] {status.detail}")
    if source["status"] != "live":
        print("未取得实时样本；缓存证据仍可运行，但请按上面的 login_state 检查授权。")
        return 2
    print(f"授权采集完成：{source['live_post_count']} 条；原始与派生路径已写入清单。")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(asyncio.run(_main()))
