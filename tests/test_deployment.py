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


def test_startup_never_persists_plaintext_web_password() -> None:
    script = (ROOT_DIR / "deploy" / "start-zeabur.sh").read_text(encoding="utf-8")

    assert "openssl passwd -6 -stdin" in script
    assert "chmod 0600 /app/runtime/auth/.htpasswd" in script
    assert "unset password_hash QIANCRAFT_WEB_PASSWORD" in script


def test_runtime_image_includes_snapshot_tool_and_explicit_runtime_root() -> None:
    dockerfile = (ROOT_DIR / "Dockerfile").read_text(encoding="utf-8")
    startup = (ROOT_DIR / "deploy" / "start-zeabur.sh").read_text(encoding="utf-8")

    assert "QIANCRAFT_RUNTIME_ROOT=/app/data/runtime" in dockerfile
    assert "COPY scripts/runtime_snapshot.py ./scripts/runtime_snapshot.py" in dockerfile
    assert "gosu" in dockerfile
    assert "gosu www-data python -m app.tool_api" in startup
    assert "gosu www-data ./node_modules/.bin/vinext start" in startup
