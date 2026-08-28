from __future__ import annotations

import argparse
import asyncio
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.adapters.gpt_researcher_adapter import GPTResearcherAdapter
from app.config import load_settings


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 QianCraft 运行环境")
    parser.add_argument(
        "--install-api",
        action="store_true",
        help="从被忽略的 api.txt 将 DeepSeek 配置写入被忽略的 .env",
    )
    parser.add_argument("--probe-api", action="store_true", help="查询可用模型并确认目标模型")
    parser.add_argument(
        "--probe-mediacrawler",
        action="store_true",
        help="只导入 MediaCrawler 并列出适配平台，不登录、不启动浏览器、不抓取",
    )
    return parser.parse_args()


def _api_key_from_file(path: Path) -> str:
    if not path.exists():
        return ""
    match = re.search(r"\b(sk-[A-Za-z0-9_-]{20,})\b", path.read_text(encoding="utf-8-sig"))
    return match.group(1) if match else ""


def _update_dotenv(path: Path, updates: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    remaining = dict(updates)
    output: list[str] = []
    for line in lines:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
        if match and match.group(1) in remaining:
            name = match.group(1)
            output.append(f"{name}={remaining.pop(name)}")
        else:
            output.append(line)
    if output and output[-1].strip():
        output.append("")
    output.extend(f"{name}={value}" for name, value in remaining.items())
    path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8", newline="\n")


async def _probe() -> bool:
    settings = load_settings()
    models = await GPTResearcherAdapter(settings).probe()
    target_available = settings.llm_model in models
    print(f"DeepSeek API: reachable; models={len(models)}")
    print(f"Target model {settings.llm_model}: {'available' if target_available else 'not listed'}")
    return target_available


def _print_environment() -> None:
    settings = load_settings()
    print(f"Python: {sys.version.split()[0]}")
    for module in ("pydantic", "httpx", "json_repair", "numpy"):
        print(f"Python package {module}: {'ok' if importlib.util.find_spec(module) else 'missing'}")
    for name, root, marker in (
        ("LightRAG", settings.lightrag_path, "lightrag"),
        ("GPT Researcher", settings.gpt_researcher_path, "gpt_researcher"),
        ("MediaCrawler", settings.mediacrawler_path, "main.py"),
    ):
        print(f"Upstream {name}: {'ok' if (root / marker).exists() else 'missing'}")
    print(
        "MediaCrawler isolated runtime: "
        f"{'ok' if settings.mediacrawler_python.exists() else 'missing'}"
    )
    print(f"LLM key: {'configured' if settings.has_llm_key else 'missing'} (value hidden)")


def _probe_mediacrawler() -> bool:
    settings = load_settings()
    if not settings.mediacrawler_python.exists():
        print("MediaCrawler probe: isolated Python missing", file=sys.stderr)
        return False
    command = [
        str(settings.mediacrawler_python),
        "-c",
        (
            "import main; print('platforms=' + "
            "','.join(sorted(main.CrawlerFactory.CRAWLERS)))"
        ),
    ]
    try:
        result = subprocess.run(
            command,
            cwd=settings.mediacrawler_path,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"MediaCrawler probe failed: {type(exc).__name__}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(f"MediaCrawler probe failed: exit={result.returncode}", file=sys.stderr)
        return False
    summary = next((line for line in result.stdout.splitlines() if line.startswith("platforms=")), "")
    print(f"MediaCrawler import: ok; {summary}")
    return bool(summary)


async def _main() -> int:
    args = _arguments()
    if args.install_api:
        key = _api_key_from_file(ROOT_DIR / "api.txt")
        if not key:
            print("api.txt 中未找到合法的 sk- 密钥。", file=sys.stderr)
            return 2
        _update_dotenv(
            ROOT_DIR / ".env",
            {
                "LIVE_MODE": "true",
                "DEMO_MODE": "true",
                "LLM_API_KEY": key,
                "LLM_BASE_URL": "https://api.deepseek.com",
                "LLM_MODEL": "deepseek-v4-flash",
                "ALLOW_API_TXT_FALLBACK": "false",
            },
        )
        print("DeepSeek 配置已写入被 .gitignore 排除的 .env；密钥未回显。")
    _print_environment()
    ok = True
    if args.probe_mediacrawler:
        ok = _probe_mediacrawler() and ok
    if args.probe_api:
        try:
            ok = await _probe() and ok
        except Exception as exc:  # noqa: BLE001 - CLI boundary must mask arbitrary client errors
            message = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", str(exc))
            print(f"DeepSeek API probe failed: {type(exc).__name__}: {message}", file=sys.stderr)
            return 4
    return 0 if ok else 3


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(asyncio.run(_main()))
