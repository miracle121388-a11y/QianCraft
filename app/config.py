from __future__ import annotations

import os
import re
from dataclasses import dataclass, replace
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
MARKET_PLATFORM_CODES = ("xhs", "dy", "bili", "wb")


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_path(value: str, default: str) -> Path:
    raw = value.strip() if value else default
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (ROOT_DIR / path).resolve()


def _resolve_executable_path(value: str, default: str) -> Path:
    """Normalize an executable path without dereferencing virtualenv symlinks."""

    raw = value.strip() if value else default
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT_DIR / path
    return Path(os.path.abspath(path))


def portable_artifact_path(path: Path, root_dir: Path = ROOT_DIR) -> str:
    """Keep project artifacts relocatable while preserving external absolute paths."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(root_dir.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _normalize_deepseek_model(value: str) -> str:
    aliases = {
        "deepseek_v4_flash": "deepseek-v4-flash",
        "deepseek_v4_pro": "deepseek-v4-pro",
    }
    return aliases.get(value.strip(), value.strip())


def _market_platforms(value: str) -> tuple[str, ...]:
    requested = [item.strip().lower() for item in value.split(",") if item.strip()]
    ordered = tuple(code for code in MARKET_PLATFORM_CODES if code in requested)
    return ordered or MARKET_PLATFORM_CODES


def _read_api_txt(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8-sig").strip()
    match = re.search(r"\b(sk-[A-Za-z0-9_-]{20,})\b", text)
    return match.group(1) if match else ""


@dataclass(frozen=True, slots=True)
class Settings:
    root_dir: Path
    live_mode: bool
    demo_mode: bool
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_timeout_seconds: float
    llm_max_tokens: int
    embedding_model: str
    image_provider: str
    image_api_key: str
    image_base_url: str
    image_model: str
    image_timeout_seconds: float
    gpt_researcher_path: Path
    mediacrawler_path: Path
    mediacrawler_python: Path
    lightrag_path: Path
    lightrag_storage_dir: Path
    lightrag_base_url: str
    mediacrawler_live_enabled: bool
    mediacrawler_platform: str
    mediacrawler_platforms: tuple[str, ...]
    mediacrawler_cookie: str
    mediacrawler_cookies: dict[str, str]
    mediacrawler_login_method: str
    mediacrawler_interactive_login: bool
    mediacrawler_cdp_port: int
    mediacrawler_cdp_connect_existing: bool
    mediacrawler_headless: bool
    mediacrawler_keyword_limit: int
    mediacrawler_max_results: int
    mediacrawler_platform_record_limit: int
    mediacrawler_timeout_seconds: int
    culture_graph_path: Path
    visual_references_path: Path
    market_signals_path: Path
    market_raw_dir: Path
    market_derived_dir: Path
    benchmark_path: Path
    demo_cache_dir: Path
    outputs_dir: Path
    design_assets_dir: Path

    @property
    def has_llm_key(self) -> bool:
        return bool(self.llm_api_key)

    @property
    def has_image_provider(self) -> bool:
        return bool(
            self.image_provider
            and self.image_api_key
            and self.image_base_url
            and self.image_model
        )

    def with_mode(self, mode: str) -> Settings:
        if mode == "demo":
            return replace(self, live_mode=False, demo_mode=True)
        if mode == "auto":
            return replace(self, live_mode=True, demo_mode=True)
        if mode == "live":
            return replace(self, live_mode=True, demo_mode=False)
        return self


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env", override=False)
    values = {**dotenv_values(ROOT_DIR / ".env.example"), **dotenv_values(ROOT_DIR / ".env")}

    def env(name: str, default: str = "") -> str:
        value = os.getenv(name)
        if value is not None:
            return value
        stored = values.get(name)
        return str(stored) if stored is not None else default

    allow_file_key = _as_bool(env("ALLOW_API_TXT_FALLBACK", "true"), True)
    api_key = env("LLM_API_KEY")
    if not api_key and allow_file_key:
        api_key = _read_api_txt(ROOT_DIR / "api.txt")

    return Settings(
        root_dir=ROOT_DIR,
        live_mode=_as_bool(env("LIVE_MODE", "false")),
        demo_mode=_as_bool(env("DEMO_MODE", "true"), True),
        llm_api_key=api_key,
        llm_base_url=env("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        llm_model=_normalize_deepseek_model(env("LLM_MODEL", "deepseek-v4-flash")),
        llm_timeout_seconds=float(env("LLM_TIMEOUT_SECONDS", "180")),
        llm_max_tokens=int(env("LLM_MAX_TOKENS", "10000")),
        embedding_model=env("EMBEDDING_MODEL", "local-hash-384"),
        image_provider=env("IMAGE_PROVIDER").strip().lower(),
        image_api_key=env("IMAGE_API_KEY"),
        image_base_url=env("IMAGE_BASE_URL").rstrip("/"),
        image_model=env("IMAGE_MODEL"),
        image_timeout_seconds=float(env("IMAGE_TIMEOUT_SECONDS", "180")),
        gpt_researcher_path=_resolve_path(
            env("GPT_RESEARCHER_PATH"), "researcher_agent/gpt-researcher-main"
        ),
        mediacrawler_path=_resolve_path(
            env("MEDIACRAWLER_PATH"), "market-intel_agent/MediaCrawler-main"
        ),
        mediacrawler_python=_resolve_executable_path(
            env("MEDIACRAWLER_PYTHON"),
            (
                "market-intel_agent/MediaCrawler-main/.venv-qiancraft/Scripts/python.exe"
                if os.name == "nt"
                else "market-intel_agent/MediaCrawler-main/.venv-qiancraft/bin/python"
            ),
        ),
        lightrag_path=_resolve_path(env("LIGHTRAG_PATH"), "local_culture/LightRAG-main"),
        lightrag_storage_dir=_resolve_path(
            env("LIGHTRAG_STORAGE_DIR"), "data/culture/lightrag_storage"
        ),
        lightrag_base_url=env("LIGHTRAG_BASE_URL"),
        mediacrawler_live_enabled=_as_bool(env("MEDIACRAWLER_LIVE_ENABLED", "false")),
        mediacrawler_platform=env("MEDIACRAWLER_PLATFORM", "xhs").strip().lower(),
        mediacrawler_platforms=_market_platforms(
            env("MEDIACRAWLER_PLATFORMS", ",".join(MARKET_PLATFORM_CODES))
        ),
        mediacrawler_cookie=env("MEDIACRAWLER_COOKIE"),
        mediacrawler_cookies={
            code: env(
                f"MEDIACRAWLER_{code.upper()}_COOKIE",
                env("MEDIACRAWLER_COOKIE") if code == "xhs" else "",
            )
            for code in MARKET_PLATFORM_CODES
        },
        mediacrawler_login_method=env("MEDIACRAWLER_LOGIN_METHOD", "cdp").strip().lower(),
        mediacrawler_interactive_login=_as_bool(
            env("MEDIACRAWLER_INTERACTIVE_LOGIN", "false")
        ),
        mediacrawler_cdp_port=max(1024, min(int(env("MEDIACRAWLER_CDP_PORT", "9222")), 65535)),
        mediacrawler_cdp_connect_existing=_as_bool(
            env("MEDIACRAWLER_CDP_CONNECT_EXISTING", "true"), True
        ),
        mediacrawler_headless=_as_bool(env("MEDIACRAWLER_HEADLESS", "false")),
        mediacrawler_keyword_limit=max(
            1, min(int(env("MEDIACRAWLER_KEYWORD_LIMIT", "6")), 23)
        ),
        mediacrawler_max_results=max(
            10, min(int(env("MEDIACRAWLER_MAX_RESULTS", "20")), 25)
        ),
        mediacrawler_platform_record_limit=max(
            5, min(int(env("MEDIACRAWLER_PLATFORM_RECORD_LIMIT", "150")), 150)
        ),
        mediacrawler_timeout_seconds=max(30, int(env("MEDIACRAWLER_TIMEOUT_SECONDS", "180"))),
        culture_graph_path=ROOT_DIR / "data" / "culture" / "knowledge_graph.json",
        visual_references_path=ROOT_DIR / "data" / "culture" / "visual_references.json",
        market_signals_path=ROOT_DIR / "data" / "market" / "verified_signals.json",
        market_raw_dir=ROOT_DIR / "data" / "market" / "raw",
        market_derived_dir=ROOT_DIR / "data" / "market" / "derived",
        benchmark_path=ROOT_DIR / "data" / "benchmark" / "cases.json",
        demo_cache_dir=ROOT_DIR / "data" / "demo_cache",
        outputs_dir=ROOT_DIR / "data" / "outputs",
        design_assets_dir=ROOT_DIR / "data" / "design" / "assets",
    )
