from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import load_settings, portable_artifact_path
from app.designer import DesignAgent, render_design_package_markdown, render_design_poster
from app.schemas import RunManifest


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume DesignerHandoff JSON and render a QianCraft concept poster."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/outputs/designer_handoff.json"),
        help="DesignerHandoff JSON path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/outputs"),
        help="Directory for design outputs.",
    )
    parser.add_argument(
        "--hero-image",
        type=Path,
        help="Optional generated product visual; exact poster text remains locally composed.",
    )
    parser.add_argument(
        "--update-run-manifest",
        action="store_true",
        help="Update design/poster component status in output-dir/run_manifest.json.",
    )
    return parser.parse_args()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> int:
    args = _arguments()
    settings = load_settings()
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    package, design_status = DesignAgent(settings).create_from_file(input_path)
    package_path = output_dir / "design_specification.json"
    markdown_path = output_dir / "design_specification.md"
    request_path = output_dir / "poster_render_request.json"
    poster_path = output_dir / "design_poster.png"
    render_manifest_path = output_dir / "design_render_manifest.json"

    _write(
        package_path,
        json.dumps(package.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    _write(markdown_path, render_design_package_markdown(package))
    _write(
        request_path,
        json.dumps(package.poster_request.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
    )
    render_manifest, render_status = render_design_poster(
        package,
        poster_path,
        args.hero_image.resolve() if args.hero_image else None,
    )
    _write(
        render_manifest_path,
        json.dumps(render_manifest.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
    )
    if args.update_run_manifest:
        main_manifest_path = output_dir / "run_manifest.json"
        manifest = RunManifest.model_validate_json(
            main_manifest_path.read_text(encoding="utf-8")
        )
        replacements = {
            "design_agent": design_status,
            "poster_renderer": render_status,
        }
        existing = {status.component for status in manifest.components}
        manifest.components = [
            replacements.get(status.component, status) for status in manifest.components
        ]
        manifest.components.extend(
            replacements[name] for name in replacements if name not in existing
        )
        manifest.finished_at = datetime.now(UTC)
        manifest.outputs.update(
            {
                "design_specification_json": portable_artifact_path(
                    package_path, settings.root_dir
                ),
                "design_specification_markdown": portable_artifact_path(
                    markdown_path, settings.root_dir
                ),
                "poster_render_request": portable_artifact_path(
                    request_path, settings.root_dir
                ),
                "design_poster": portable_artifact_path(poster_path, settings.root_dir),
                "design_render_manifest": portable_artifact_path(
                    render_manifest_path, settings.root_dir
                ),
            }
        )
        _write(
            main_manifest_path,
            json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        )

    print(f"[{design_status.mode.upper()}] {design_status.detail}")
    print(f"[{render_status.mode.upper()}] {render_status.detail}")
    print(f"Design Specification: {package_path}")
    print(f"Poster Render Request: {request_path}")
    print(f"Design Poster: {poster_path}")
    print(f"Render Manifest: {render_manifest_path}")
    if args.update_run_manifest:
        print(f"Updated Run Manifest: {output_dir / 'run_manifest.json'}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
