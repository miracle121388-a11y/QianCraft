from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_nginx_keeps_health_public_and_protects_application_routes() -> None:
    config = (ROOT_DIR / "deploy" / "nginx.conf.template").read_text(encoding="utf-8")

    assert 'auth_basic "QianCraft Workbench";' in config
    assert "location = /healthz" in config
    assert config.count("auth_basic off;") == 1
    assert "proxy_pass http://127.0.0.1:8787/api/health;" in config


def test_nginx_applies_production_security_and_abuse_controls() -> None:
    config = (ROOT_DIR / "deploy" / "nginx.conf.template").read_text(encoding="utf-8")

    assert "server_tokens off;" in config
    assert "limit_req_zone $binary_remote_addr" in config
    assert "limit_req zone=qiancraft_api" in config
    assert "Strict-Transport-Security" in config
    assert "Content-Security-Policy" in config
    assert "Permissions-Policy" in config
    assert "object-src 'none'" in config
    assert "frame-ancestors 'self'" in config


def test_nginx_protects_the_loopback_only_browser_gateway() -> None:
    config = (ROOT_DIR / "deploy" / "nginx.conf.template").read_text(encoding="utf-8")

    assert "location /browser-auth/" in config
    assert "proxy_pass http://127.0.0.1:6080/;" in config
    assert "proxy_read_timeout 3600s;" in config
    assert config.count("auth_basic off;") == 1


def test_startup_never_persists_plaintext_web_password() -> None:
    script = (ROOT_DIR / "deploy" / "start-zeabur.sh").read_text(encoding="utf-8")

    assert "openssl passwd -6 -stdin" in script
    assert "chmod 0600 /app/runtime/auth/.htpasswd" in script
    assert "unset password_hash QIANCRAFT_WEB_PASSWORD" in script


def test_runtime_image_includes_snapshot_tool_and_explicit_runtime_root() -> None:
    dockerfile = (ROOT_DIR / "Dockerfile").read_text(encoding="utf-8")
    startup = (ROOT_DIR / "deploy" / "start-zeabur.sh").read_text(encoding="utf-8")
    probe = (ROOT_DIR / "scripts" / "probe_market_platforms.py").read_text(encoding="utf-8")

    assert "QIANCRAFT_RUNTIME_ROOT=/app/data/runtime" in dockerfile
    assert "COPY scripts/runtime_snapshot.py ./scripts/runtime_snapshot.py" in dockerfile
    assert "COPY scripts/probe_market_platforms.py ./scripts/probe_market_platforms.py" in dockerfile
    assert "COPY .env.example" not in dockerfile
    assert "gosu" in dockerfile
    assert "gosu www-data python -m app.tool_api" in startup
    assert "gosu www-data ./node_modules/.bin/vinext start" in startup
    assert "managed_cdp_connected" in probe
    assert "_cdp_port_open(base.mediacrawler_cdp_port)" in probe


def test_runtime_image_contains_all_research_runtimes_and_managed_browser() -> None:
    dockerfile = (ROOT_DIR / "Dockerfile").read_text(encoding="utf-8")
    startup = (ROOT_DIR / "deploy" / "start-zeabur.sh").read_text(encoding="utf-8")

    assert "COPY local_culture/LightRAG-main/" in dockerfile
    assert "COPY researcher_agent/gpt-researcher-main/" in dockerfile
    assert "COPY market-intel_agent/MediaCrawler-main/" in dockerfile
    assert "MEDIACRAWLER_PYTHON=/opt/mediacrawler-venv/bin/python" in dockerfile
    assert "MEDIACRAWLER_LIVE_ENABLED=true" in dockerfile
    for package in ("chromium", "novnc", "websockify", "x11vnc", "xvfb"):
        assert package in dockerfile
    assert "--remote-debugging-address=127.0.0.1" in startup
    assert "127.0.0.1:6080" in startup
    assert "127.0.0.1:5900" in startup
    assert "QIANCRAFT_BROWSER_PROFILE_DIR" in startup
    assert '"$QIANCRAFT_BROWSER_PROFILE_DIR/SingletonLock"' in startup
    assert "-nopw" in startup
    assert '"$MEDIACRAWLER_PYTHON" -c' in startup
    assert "from tools.cdp_browser import CDPBrowserManager" in startup
    assert "from tools.cdp_browser import CDPBrowserManager; import main" in dockerfile


def test_docker_context_excludes_local_quality_and_runtime_artifacts() -> None:
    dockerignore = (ROOT_DIR / ".dockerignore").read_text(encoding="utf-8")

    for path in (
        ".github",
        "qiancraft.egg-info",
        "web/.playwright-cli",
        "web/.playwright-report",
        "web/.playwright-results",
        "web/output",
        "web/tests",
    ):
        assert path in dockerignore.splitlines()
    assert "!scripts/runtime_snapshot.py" in dockerignore
    assert "!scripts/probe_market_platforms.py" in dockerignore
    assert "local_culture" not in dockerignore.splitlines()
    assert "market-intel_agent" not in dockerignore.splitlines()
    assert "researcher_agent" not in dockerignore.splitlines()
