from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import load_settings
from app.pipeline import run_pipeline
from app.schemas import DemoRequest


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 QianCraft 贵州文化前策划流水线")
    parser.add_argument("--mode", choices=["auto", "demo", "live"], default="auto")
    parser.add_argument("--topic", default="贵州苗绣")
    parser.add_argument("--region", default="贵州")
    parser.add_argument("--target-market", default="18-30岁年轻消费者")
    parser.add_argument("--goal", default="寻找具有爆款潜力的文创产品机会")
    parser.add_argument(
        "--design-hero",
        type=Path,
        help="可选的生成式产品主视觉；精确文字与技术信息仍由本地海报排版器合成。",
    )
    return parser.parse_args()


async def _main() -> int:
    args = _arguments()
    settings = load_settings().with_mode(args.mode)
    request = DemoRequest(
        topic=args.topic,
        region=args.region,
        target_market=args.target_market,
        goal=args.goal,
    )
    strategy, manifest = await run_pipeline(
        request,
        settings,
        args.design_hero.resolve() if args.design_hero else None,
    )
    print(f"QianCraft 完成：{len(strategy.opportunity_signals)} 条机会信号")
    for status in manifest.components:
        print(f"[{status.mode.upper()}] {status.component}: {status.engine}")
        print(f"  {status.detail}")
    print(f"JSON: {manifest.outputs['strategy_json']}")
    print(f"Markdown: {manifest.outputs['strategy_markdown']}")
    print(f"Visual Reference Pack: {manifest.outputs['visual_reference_json']}")
    print(f"Designer Handoff: {manifest.outputs['designer_handoff_json']}")
    print(f"Product Form Hotness: {manifest.outputs['product_form_hotness']}")
    print(f"Design Specification: {manifest.outputs['design_specification_json']}")
    print(f"Design Poster: {manifest.outputs['design_poster']}")
    print(f"Design Render Manifest: {manifest.outputs['design_render_manifest']}")
    print(f"Manifest: {manifest.outputs['manifest']}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(asyncio.run(_main()))
