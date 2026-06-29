from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.image_diagnostics import ImageDiagnostics  # noqa: E402
from perception.regions import get_region, resolve_regions  # noqa: E402
from scenarios.scripted_playback import _load_config  # noqa: E402
from scenarios.scripted_playback import (_profile_display_name,
                                         _resolve_config_path)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a named screen region using existing image diagnostics. "
            "Captures the region and computes statistics."
        )
    )
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument(
        "--region",
        "-r",
        required=True,
        help="Name of the region to analyze (must be defined in the config's 'regions:' section).",
    )
    parser.add_argument(
        "--image",
        help=(
            "Path to an already-captured region image. If omitted, a fresh "
            "capture is made and analyzed."
        ),
    )
    parser.add_argument(
        "--output-folder",
        help="Override the output folder for analysis reports (default: logs/screenshots).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the analysis report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    regions = resolve_regions(config)

    if not regions:
        raise SystemExit(
            f"No 'regions:' section in {_profile_display_name(PROJECT_ROOT, config_path)}. "
            "Define regions in your config/profile YAML first."
        )

    region = get_region(regions, args.region)
    diagnostics = ImageDiagnostics()

    output_dir = Path(args.output_folder).expanduser() if args.output_folder else PROJECT_ROOT / "logs" / "screenshots"

    if args.image:
        image_path = Path(args.image).expanduser()
        if not image_path.exists():
            raise SystemExit(f"Image not found: {image_path}")
        payload = diagnostics.stats(image_path)
        report = {
            "operation": "analyze_region",
            "source": "existing_image",
            "image_path": str(image_path),
            "region": {
                "name": region.name,
                "left": region.left,
                "top": region.top,
                "width": region.width,
                "height": region.height,
            },
            "stats": {
                "width": payload.width,
                "height": payload.height,
                "mode": payload.mode,
                "file_size_bytes": payload.file_size_bytes,
                "channel_means": payload.channel_means,
                "channel_extrema": payload.channel_extrema,
            },
        }
    else:
        # Capture fresh, then analyze
        from perception.regions import capture_region as _capture
        from perception.screenshot_backend import MssScreenshotBackend

        backend = MssScreenshotBackend()
        capture_result = _capture(
            regions=regions,
            region_name=args.region,
            backend=backend,
            output_dir=output_dir,
            metadata={
                "config_path": _profile_display_name(PROJECT_ROOT, config_path),
                "script": "scripts/analyze_region.py",
            },
        )
        image_path = Path(capture_result["path"])
        payload = diagnostics.stats(image_path)
        report = {
            "operation": "analyze_region",
            "source": "fresh_capture",
            "image_path": str(image_path),
            "capture_metadata": {
                "metadata_path": capture_result["metadata_path"],
                "timestamp_utc": capture_result["timestamp_utc"],
            },
            "region": {
                "name": region.name,
                "left": region.left,
                "top": region.top,
                "width": region.width,
                "height": region.height,
            },
            "stats": {
                "width": payload.width,
                "height": payload.height,
                "mode": payload.mode,
                "file_size_bytes": payload.file_size_bytes,
                "channel_means": payload.channel_means,
                "channel_extrema": payload.channel_extrema,
            },
        }

    if args.json:
        import json

        print(json.dumps(report, indent=2))
    else:
        print(f"Region: {region.name}")
        print(f"  Coordinate: left={region.left}, top={region.top}, "
              f"width={region.width}, height={region.height}")
        print(f"Image: {report['image_path']}")
        print(f"Size: {payload.width}x{payload.height}")
        print(f"Mode: {payload.mode}")
        print(f"File size: {payload.file_size_bytes} bytes")
        print("Channel means (R,G,B):", ", ".join(f"{m:.3f}" for m in payload.channel_means))
        print("Channel extrema (R,G,B):", payload.channel_extrema)


if __name__ == "__main__":
    main()
