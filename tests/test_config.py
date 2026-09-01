from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.config import (
    MARKET_PLATFORM_CODES,
    _market_platforms,
    _resolve_executable_path,
    load_settings,
)


def test_market_platform_default_preserves_historical_demo_scope() -> None:
    assert _market_platforms("") == MARKET_PLATFORM_CODES
    assert _market_platforms("wb,dy") == ("dy", "wb")


def test_executable_path_preserves_virtualenv_symlink(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "system-python"
    target.write_text("runtime", encoding="utf-8")
    interpreter = tmp_path / "venv" / "bin" / "python"
    interpreter.parent.mkdir(parents=True)
    try:
        interpreter.symlink_to(target)
    except (NotImplementedError, OSError):
        pytest.skip("当前文件系统不允许创建符号链接")

    configured = _resolve_executable_path(str(interpreter), "")
    monkeypatch.setenv("MEDIACRAWLER_PYTHON", str(interpreter))

    assert configured == Path(os.path.abspath(interpreter))
    assert configured != target.resolve()
    assert load_settings().mediacrawler_python == configured
