from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QianCraft local API and web workbench together."
    )
    parser.add_argument("--api-port", type=int, default=8787)
    parser.add_argument("--web-port", type=int, default=3000)
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    pnpm = shutil.which("pnpm")
    if not pnpm:
        raise RuntimeError("pnpm is required to run the QianCraft web workbench")

    api = subprocess.Popen(
        [
            sys.executable,
            str(ROOT_DIR / "scripts" / "run_tool.py"),
            "--host",
            "127.0.0.1",
            "--port",
            str(args.api_port),
        ],
        cwd=ROOT_DIR,
    )
    web = subprocess.Popen(
        [
            pnpm,
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.web_port),
        ],
        cwd=ROOT_DIR / "web",
    )
    print(f"QianCraft workbench: http://localhost:{args.web_port}/")
    try:
        while api.poll() is None and web.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (web, api):
            if process.poll() is None:
                process.terminate()
        for process in (web, api):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    if api.returncode not in (None, 0, -15):
        return int(api.returncode)
    if web.returncode not in (None, 0, -15):
        return int(web.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
