from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.runtime_snapshot import create_backup, restore_backup, verify_backup


def _runtime(root: Path) -> None:
    (root / "workbench").mkdir(parents=True)
    (root / "tool_workspace" / "collection").mkdir(parents=True)
    (root / "workbench" / "workspace.json").write_text('{"version": 2}\n', encoding="utf-8")
    (root / "tool_workspace" / "collection" / "state.json").write_text(
        '{"status": "healthy"}\n', encoding="utf-8"
    )


def _duplicate_manifest_archive(path: Path) -> None:
    with ZipFile(path, "w") as handle:
        handle.writestr("manifest.json", '{"schemaVersion":"1.0","files":[]}')
        handle.writestr("manifest.json", '{"schemaVersion":"1.0","files":[]}')


def test_runtime_snapshot_round_trip_preserves_verified_files(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    archive = tmp_path / "backups" / "runtime.zip"
    _runtime(root)

    created = create_backup(root, archive)
    verified = verify_backup(archive)
    (root / "workbench" / "workspace.json").write_text('{"version": 3}\n', encoding="utf-8")
    restored, rollback = restore_backup(archive, root)

    assert created == verified == restored
    assert created["fileCount"] == 2
    assert (root / "workbench" / "workspace.json").read_text(encoding="utf-8") == (
        '{"version": 2}\n'
    )
    assert rollback is not None
    assert (rollback / "workbench" / "workspace.json").read_text(encoding="utf-8") == (
        '{"version": 3}\n'
    )


def test_runtime_snapshot_refuses_archive_inside_runtime(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _runtime(root)

    with pytest.raises(ValueError, match="运行态目录之外"):
        create_backup(root, root / "backup.zip")


def test_runtime_snapshot_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    with ZipFile(archive, "w") as handle:
        handle.writestr("../escape.txt", "unsafe")
        handle.writestr("manifest.json", '{"schemaVersion":"1.0","files":[]}')

    with pytest.raises(ValueError, match="不安全路径"):
        verify_backup(archive)

    duplicate = tmp_path / "duplicate.zip"
    with pytest.warns(UserWarning, match="Duplicate name"):
        _duplicate_manifest_archive(duplicate)

    with pytest.raises(ValueError, match="重复文件名"):
        verify_backup(duplicate)
