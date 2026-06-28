from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.config import resolve_screenshot_config  # noqa: E402
from perception.image_diagnostics import ImageDiagnostics, dataclass_payload, save_json  # noqa: E402
from perception.regions import region_payload, resolve_output_path, resolve_region  # noqa: E402
from perception.screenshot_backend import MssScreenshotBackend  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    _load_config,
    _profile_display_name,
    _resolve_config_path,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture and analyze a named screen region.")
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument("--region", required=True, help="Named region to capture and analyze.")
    parser.add_argument("--monitor-index", type=int, help="Override perception.screenshot.monitor_index.")
    parser.add_argument("--output-folder", help="Override perception.screenshot.output_folder.")
    parser.add_argument("--file-prefix", help="Override perception.screenshot.file_prefix.")
    parser.add_argument("--json-output", help="Optional JSON report output path.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    named_region = resolve_region(config, args.region)
    screenshot_config = resolve_screenshot_config(
        config,
        project_root=PROJECT_ROOT,
        monitor_index_override=args.monitor_index,
        output_folder_override=args.output_folder,
        file_prefix_override=args.file_prefix,
        region_override=named_region.to_screenshot_region(),
    )

    if not screenshot_config.enabled:
        raise SystemExit("perception.screenshot.enabled is false for this config/profile")

    screenshot_backend = MssScreenshotBackend()
    capture = screenshot_backend.capture_png(
        output_dir=screenshot_config.output_folder,
        file_prefix=f"{screenshot_config.file_prefix}_{named_region.name}",
        monitor_index=screenshot_config.monitor_index,
        region=screenshot_config.region,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/analyze_region.py",
            "region_name": named_region.name,
            "region": region_payload(named_region),
            "backend": screenshot_config.backend,
        },
    )

    diagnostics = ImageDiagnostics()
    stats = diagnostics.stats(capture.path)
    payload = {
        "operation": "analyze_region",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": _profile_display_name(PROJECT_ROOT, config_path),
        "region_name": named_region.name,
        "region": region_payload(named_region),
        "capture": dataclass_payload(capture),
        "stats": dataclass_payload(stats),
        "contains_ocr": False,
        "contains_decision_logic": False,
    }

    print(json.dumps(payload, indent=2))

    if args.json_output:
        output_path = resolve_output_path(PROJECT_ROOT, args.json_output)
        save_json(payload, output_path)
        print(f"JSON report: {output_path}")


if __name__ == "__main__":
    main()
