from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.config import make_region, resolve_screenshot_config  # noqa: E402
from perception.screenshot_backend import MssScreenshotBackend, ScreenshotRegion  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    _load_config,
    _profile_display_name,
    _resolve_config_path,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture a diagnostic screenshot frame without sending controller input."
    )
    parser.add_argument("--profile", "-p", help="Profile name or path to read perception config from.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument("--list-monitors", action="store_true", help="List detected monitors and exit.")
    parser.add_argument("--monitor-index", type=int, help="Override perception.screenshot.monitor_index.")
    parser.add_argument("--output-folder", help="Override perception.screenshot.output_folder.")
    parser.add_argument("--file-prefix", help="Override perception.screenshot.file_prefix.")
    parser.add_argument("--left", type=int, help="Capture region left coordinate.")
    parser.add_argument("--top", type=int, help="Capture region top coordinate.")
    parser.add_argument("--width", type=int, help="Capture region width.")
    parser.add_argument("--height", type=int, help="Capture region height.")
    return parser


def _cli_region(args: argparse.Namespace) -> ScreenshotRegion | None:
    cli_region_values = [args.left, args.top, args.width, args.height]
    if not any(value is not None for value in cli_region_values):
        return None
    if not all(value is not None for value in cli_region_values):
        raise ValueError("Region CLI overrides require --left, --top, --width, and --height together")
    return make_region({
        "left": args.left,
        "top": args.top,
        "width": args.width,
        "height": args.height,
    })


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    backend = MssScreenshotBackend()

    if args.list_monitors:
        print("Detected monitors:")
        for index, monitor in enumerate(backend.list_monitors()):
            label = "virtual desktop" if index == 0 else f"monitor {index}"
            print(f"- {index}: {label} {monitor}")
        return

    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    screenshot_config = resolve_screenshot_config(
        config,
        project_root=PROJECT_ROOT,
        monitor_index_override=args.monitor_index,
        output_folder_override=args.output_folder,
        file_prefix_override=args.file_prefix,
        region_override=_cli_region(args),
    )

    if not screenshot_config.enabled:
        raise RuntimeError("perception.screenshot.enabled is false for this config/profile")

    result = backend.capture_png(
        output_dir=screenshot_config.output_folder,
        file_prefix=screenshot_config.file_prefix,
        monitor_index=screenshot_config.monitor_index,
        region=screenshot_config.region,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/capture_sample_frame.py",
            "backend": screenshot_config.backend,
        },
    )

    print(f"Captured: {result.path}")
    print(f"Metadata: {result.metadata_path}")
    print(f"Size: {result.width}x{result.height}")
    if result.region is None:
        print(f"Monitor: index {screenshot_config.monitor_index} -> {result.monitor}")
    else:
        print(f"Region: {result.region}")


if __name__ == "__main__":
    main()
