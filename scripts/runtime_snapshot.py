from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile, ZipInfo

ROOT_DIR = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "manifest.json"
ARCHIVE_PREFIX = "runtime/"
MAX_FILE_COUNT = 100_000
MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
RESTORE_CONFIRMATION = "RESTORE_QIANCRAFT_RUNTIME"
EXCLUDED_RUNTIME_PREFIXES = ("browser-profile",)


def runtime_root(configured: Path | None = None) -> Path:
    if configured is not None:
        return configured.expanduser().resolve()
    explicit = os.environ.get("QIANCRAFT_RUNTIME_ROOT", "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    configured_dirs = [
        os.environ.get("QIANCRAFT_WORKBENCH_DIR", "").strip(),
        os.environ.get("QIANCRAFT_TOOL_WORKSPACE_DIR", "").strip(),
    ]
    parents = {
        Path(value).expanduser().resolve().parent for value in configured_dirs if value
    }
    if len(parents) == 1:
        return parents.pop()
    return (ROOT_DIR / "data" / "runtime").resolve()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _archive_files(root: Path) -> list[Path]:
    files: list[Path] = []
    if not root.exists():
        return files
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"运行态根目录必须是普通目录：{root}")
    for candidate in sorted(root.rglob("*")):
        relative = candidate.relative_to(root)
        if relative.parts and relative.parts[0] in EXCLUDED_RUNTIME_PREFIXES:
            continue
        if candidate.is_symlink():
            raise ValueError(f"运行态快照拒绝符号链接：{candidate}")
        if candidate.is_file() and not candidate.name.endswith(".tmp"):
            files.append(candidate)
    return files


def create_backup(root: Path, output: Path) -> dict[str, Any]:
    root = root.expanduser().resolve()
    output = output.expanduser().resolve()
    if output == root or root in output.parents:
        raise ValueError("备份文件必须位于运行态目录之外。")
    files = _archive_files(root)
    if len(files) > MAX_FILE_COUNT:
        raise ValueError(f"运行态文件数超过安全上限：{len(files)}")
    total_bytes = sum(path.stat().st_size for path in files)
    if total_bytes > MAX_UNCOMPRESSED_BYTES:
        raise ValueError(f"运行态体积超过安全上限：{total_bytes} bytes")

    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]
    manifest: dict[str, Any] = {
        "schemaVersion": "1.0",
        "createdAt": datetime.now(UTC).isoformat(),
        "sourceName": root.name,
        "fileCount": len(entries),
        "totalBytes": total_bytes,
        "excludedPaths": [f"{prefix}/" for prefix in EXCLUDED_RUNTIME_PREFIXES],
        "containsBrowserAuthorization": False,
        "files": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{uuid4().hex[:8]}.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path, entry in zip(files, entries, strict=True):
                archive.write(path, f"{ARCHIVE_PREFIX}{entry['path']}")
            archive.writestr(
                MANIFEST_NAME,
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            )
        verify_backup(temporary)
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return manifest


def _safe_member(info: ZipInfo) -> PurePosixPath:
    member = PurePosixPath(info.filename)
    if member.is_absolute() or ".." in member.parts:
        raise ValueError(f"快照包含不安全路径：{info.filename}")
    mode = info.external_attr >> 16
    if mode and stat.S_ISLNK(mode):
        raise ValueError(f"快照包含符号链接：{info.filename}")
    return member


def verify_backup(archive_path: Path) -> dict[str, Any]:
    archive_path = archive_path.expanduser().resolve()
    try:
        with ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > MAX_FILE_COUNT + 1:
                raise ValueError("快照文件数量超过安全上限。")
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise ValueError("快照包含重复文件名。")
            if sum(info.file_size for info in infos) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("快照解压体积超过安全上限。")
            info_by_name = {info.filename: info for info in infos}
            if MANIFEST_NAME not in info_by_name:
                raise ValueError("快照缺少 manifest.json。")
            for info in infos:
                _safe_member(info)
            manifest = json.loads(archive.read(MANIFEST_NAME))
            if manifest.get("schemaVersion") != "1.0":
                raise ValueError("不支持的快照版本。")
            rows = manifest.get("files")
            if not isinstance(rows, list):
                raise TypeError("快照清单格式无效。")
            for row in rows:
                relative = PurePosixPath(str(row["path"]))
                if (
                    relative.parts
                    and relative.parts[0] in EXCLUDED_RUNTIME_PREFIXES
                ):
                    raise ValueError("运行态快照不得包含平台浏览器授权资料。")
            expected_names = {f"{ARCHIVE_PREFIX}{row['path']}" for row in rows}
            actual_names = set(info_by_name) - {MANIFEST_NAME}
            if expected_names != actual_names:
                raise ValueError("快照文件与清单不一致。")
            verified_bytes = 0
            for row in rows:
                member_name = f"{ARCHIVE_PREFIX}{row['path']}"
                info = info_by_name[member_name]
                if info.is_dir() or info.file_size != int(row["size"]):
                    raise ValueError(f"快照文件尺寸不一致：{row['path']}")
                digest = hashlib.sha256()
                with archive.open(info, "r") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != row["sha256"]:
                    raise ValueError(f"快照文件摘要不一致：{row['path']}")
                verified_bytes += info.file_size
            if manifest.get("fileCount") != len(rows):
                raise ValueError("快照文件计数不一致。")
            if manifest.get("totalBytes") != verified_bytes:
                raise ValueError("快照总字节数不一致。")
            return manifest
    except (BadZipFile, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"无法校验运行态快照：{exc}") from exc


def restore_backup(archive_path: Path, root: Path) -> tuple[dict[str, Any], Path | None]:
    manifest = verify_backup(archive_path)
    archive_path = archive_path.expanduser().resolve()
    root = root.expanduser().resolve()
    root.parent.mkdir(parents=True, exist_ok=True)
    staging = root.parent / f".{root.name}.restore-{uuid4().hex[:8]}"
    rollback: Path | None = None
    staging.mkdir(parents=False)
    try:
        with ZipFile(archive_path, "r") as archive:
            for row in manifest["files"]:
                relative = PurePosixPath(row["path"])
                destination = staging.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with (
                    archive.open(f"{ARCHIVE_PREFIX}{row['path']}", "r") as source,
                    destination.open("wb") as target,
                ):
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        target.write(chunk)
        if root.exists():
            rollback = root.parent / (
                f"{root.name}.pre-restore-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
            )
            if rollback.exists():
                raise FileExistsError(f"回滚目录已存在：{rollback}")
            root.replace(rollback)
        try:
            staging.replace(root)
        except Exception:
            if rollback is not None and not root.exists():
                rollback.replace(root)
            raise
    finally:
        if staging.exists():
            for candidate in sorted(staging.rglob("*"), reverse=True):
                if candidate.is_file():
                    candidate.unlink()
                elif candidate.is_dir():
                    candidate.rmdir()
            staging.rmdir()
    return manifest, rollback


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="备份、校验或恢复 QianCraft 运行态")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup = subparsers.add_parser("backup", help="创建带 SHA-256 清单的 ZIP 快照")
    backup.add_argument("--runtime-root", type=Path)
    backup.add_argument("--output", type=Path, required=True)

    verify = subparsers.add_parser("verify", help="校验快照路径、尺寸与 SHA-256")
    verify.add_argument("archive", type=Path)

    restore = subparsers.add_parser("restore", help="原子恢复并保留恢复前回滚目录")
    restore.add_argument("archive", type=Path)
    restore.add_argument("--runtime-root", type=Path)
    restore.add_argument("--confirm-service-stopped", action="store_true")
    restore.add_argument("--confirm", default="")
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    if args.command == "backup":
        manifest = create_backup(runtime_root(args.runtime_root), args.output)
        result = {"ok": True, "archive": str(args.output.resolve()), **manifest}
    elif args.command == "verify":
        manifest = verify_backup(args.archive)
        result = {"ok": True, "archive": str(args.archive.resolve()), **manifest}
    else:
        if not args.confirm_service_stopped or args.confirm != RESTORE_CONFIRMATION:
            raise SystemExit(
                "恢复前必须停止 Tool API，并同时传入 --confirm-service-stopped "
                f"--confirm {RESTORE_CONFIRMATION}"
            )
        manifest, rollback = restore_backup(args.archive, runtime_root(args.runtime_root))
        result = {
            "ok": True,
            "archive": str(args.archive.resolve()),
            "rollbackPath": str(rollback) if rollback else "",
            **manifest,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
