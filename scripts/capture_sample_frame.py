from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

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


def _screenshot_config(config: dict[str, Any]) -> dict[str, Any]:
    perception = config.get("perception", {})
    if perception is None:
        perception = {}
    if not isinstance(perception, dict):
        raise ValueError("'perception' section must be a mapping when provided")

    screenshot = perception.get("screenshot", {})
    if screenshot is None:
        screenshot = {}
    if not isinstance(screenshot, dict):
        raise ValueError("'perception.screenshot' section must be a mapping when provided")

    return screenshot


def _resolve_region(screenshot: dict[str, Any], args: argparse.Namespace) -> ScreenshotRegion | None:
    cli_region_values = [args.left, args.top, args.width, args.height]
    if any(value is not None for value in cli_region_values):
        if not all(value is not None for value in cli_region_values):
            raise ValueError("Region CLI overrides require --left, --top, --width, and --height together")
        return _make_region({
            "left": args.left,
            "top": args.top,
            "width": args.width,
            "height": args.height,
        })

    region = screenshot.get("region")
    if region is None:
        return None
    if not isinstance(region, dict):
        raise ValueError("'perception.screenshot.region' must be a mapping or null")
    return _make_region(region)


def _make_region(raw: dict[str, Any]) -> ScreenshotRegion:
    required = ("left", "top", "width", "height")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Screenshot region missing required keys: {missing}")

    values = {key: raw[key] for key in required}
    for key, value in values.items():
        if not isinstance(value, int):
            raise ValueError(f"Screenshot region '{key}' must be an integer")

    if values["width"] <= 0 or values["height"] <= 0:
        raise ValueError("Screenshot region width and height must be positive")

    return ScreenshotRegion(
        left=values["left"],
        top=values["top"],
        width=values["width"],
        height=values["height"],
    )


def _resolve_output_dir(screenshot: dict[str, Any], args: argparse.Namespace) -> Path:
    raw_folder = args.output_folder or screenshot.get("output_folder", "logs/screenshots")
    path = Path(str(raw_folder)).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _resolve_file_prefix(screenshot: dict[str, Any], args: argparse.Namespace) -> str:
    return str(args.file_prefix or screenshot.get("file_prefix", "sample_frame"))


def _resolve_monitor_index(screenshot: dict[str, Any], args: argparse.Namespace) -> int:
    value = args.monitor_index if args.monitor_index is not None else screenshot.get("monitor_index", 1)
    if not isinstance(value, int):
        raise ValueError("monitor_index must be an integer")
    return value


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
    screenshot = _screenshot_config(config)

    region = _resolve_region(screenshot, args)
    output_dir = _resolve_output_dir(screenshot, args)
    file_prefix = _resolve_file_prefix(screenshot, args)
    monitor_index = _resolve_monitor_index(screenshot, args)

    result = backend.capture_png(
        output_dir=output_dir,
        file_prefix=file_prefix,
        monitor_index=monitor_index,
        region=region,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/capture_sample_frame.py",
        },
    )

    print(f"Captured: {result.path}")
    print(f"Metadata: {result.metadata_path}")
    print(f"Size: {result.width}x{result.height}")
    if result.region is None:
        print(f"Monitor: index {monitor_index} -> {result.monitor}")
    else:
        print(f"Region: {result.region}")


if __name__ == "__main__":
    main()
