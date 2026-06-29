from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.config import resolve_screenshot_config  # noqa: E402
from perception.regions import capture_region, resolve_regions  # noqa: E402
from perception.screenshot_backend import MssScreenshotBackend  # noqa: E402
from perception.screenshot_backend import ScreenshotRegion
from scenarios.scripted_playback import _load_config  # noqa: E402
from scenarios.scripted_playback import (_profile_display_name,
                                         _resolve_config_path)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture a named screen region to PNG with JSON metadata sidecar."
    )
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument(
        "--region",
        "-r",
        help=(
            "Name of the region to capture (must be defined in the config's 'regions:' section). "
            "Optional if --left/--top/--width/--height are provided."
        ),
    )
    parser.add_argument(
        "--file-prefix",
        help="Override the file prefix for this capture (default: region name or 'cli_capture').",
    )
    parser.add_argument(
        "--output-folder",
        help="Override the perception.screenshot.output_folder.",
    )
    parser.add_argument(
        "--monitor-index",
        type=int,
        help="Override the monitor index for the screenshot backend.",
    )
    # Legacy coordinate overrides — bypass named regions
    parser.add_argument("--left", type=int, help="Override: region left coordinate.")
    parser.add_argument("--top", type=int, help="Override: region top coordinate.")
    parser.add_argument("--width", type=int, help="Override: region width.")
    parser.add_argument("--height", type=int, help="Override: region height.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    backend = MssScreenshotBackend()

    # Check for legacy coordinate overrides
    cli_coords = [args.left, args.top, args.width, args.height]
    if any(c is not None for c in cli_coords):
        if not all(c is not None for c in cli_coords):
            raise SystemExit("Coordinate overrides require --left, --top, --width, and --height together.")
        from perception.config import make_region

        region_override = make_region({
            "left": args.left,
            "top": args.top,
            "width": args.width,
            "height": args.height,
        })
        # When using CLI coords we bypass named regions
        screenshot_config = resolve_screenshot_config(
            config,
            project_root=PROJECT_ROOT,
            monitor_index_override=args.monitor_index,
            output_folder_override=args.output_folder,
            file_prefix_override=args.file_prefix,
            region_override=region_override,
        )
        result = backend.capture_png(
            output_dir=screenshot_config.output_folder,
            file_prefix=screenshot_config.file_prefix,
            monitor_index=screenshot_config.monitor_index,
            region=screenshot_config.region,
            metadata={
                "config_path": _profile_display_name(PROJECT_ROOT, config_path),
                "script": "scripts/capture_region.py",
                "cli_override": True,
            },
        )
        print(f"Captured (CLI coords): {result.path}")
        print(f"Metadata: {result.metadata_path}")
        print(f"Size: {result.width}x{result.height}")
        return

    # Must have --region for named region capture
    if not args.region:
        raise SystemExit(
            "Provide --region REGION for a named region capture, "
            "or use --left/--top/--width/--height for CLI coordinate capture."
        )

    # Named region capture
    regions = resolve_regions(config)
    if not regions:
        raise SystemExit(
            f"No 'regions:' section in {_profile_display_name(PROJECT_ROOT, config_path)}. "
            "Define regions in your config/profile YAML, or use --left/--top/--width/--height."
        )

    # Resolve output folder
    screenshot_config = resolve_screenshot_config(
        config,
        project_root=PROJECT_ROOT,
        monitor_index_override=args.monitor_index,
        output_folder_override=args.output_folder,
    )

    result = capture_region(
        regions=regions,
        region_name=args.region,
        backend=backend,
        output_dir=screenshot_config.output_folder,
        file_prefix=args.file_prefix,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/capture_region.py",
            "monitor_index": screenshot_config.monitor_index,
        },
    )

    print(f"Captured region '{result['name']}': {result['path']}")
    print(f"Metadata: {result['metadata_path']}")
    print(f"Size: {result['width']}x{result['height']}")
    print(f"Region: {result['region']}")


if __name__ == "__main__":
    main()
