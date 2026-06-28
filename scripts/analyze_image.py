from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.image_diagnostics import (  # noqa: E402
    ImageDiagnostics,
    dataclass_payload,
    image_region_from_values,
    save_json,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run read-only diagnostics on captured images: stats, crop, and compare."
    )
    parser.add_argument("--image", help="Image path for stats or crop.")
    parser.add_argument("--baseline", help="Baseline image path for comparison.")
    parser.add_argument("--candidate", help="Candidate image path for comparison.")
    parser.add_argument("--crop-output", help="Output path for cropped image.")
    parser.add_argument("--left", type=int, help="Crop left coordinate.")
    parser.add_argument("--top", type=int, help="Crop top coordinate.")
    parser.add_argument("--width", type=int, help="Crop width.")
    parser.add_argument("--height", type=int, help="Crop height.")
    parser.add_argument("--json-output", help="Optional JSON report output path.")
    return parser


def _resolve_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _print_payload(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


def _save_optional(payload: dict, raw_output: str | None) -> None:
    if not raw_output:
        return
    output_path = _resolve_path(raw_output)
    save_json(payload, output_path)
    print(f"JSON report: {output_path}")


def _region_from_args(args: argparse.Namespace):
    values = [args.left, args.top, args.width, args.height]
    if any(value is not None for value in values) and not all(value is not None for value in values):
        raise ValueError("Crop requires --left, --top, --width, and --height together")
    if all(value is not None for value in values):
        return image_region_from_values(args.left, args.top, args.width, args.height)
    return None


def main(argv: list[str] | None = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    diagnostics = ImageDiagnostics()
    region = _region_from_args(args)

    if args.baseline or args.candidate:
        if not args.baseline or not args.candidate:
            raise SystemExit("Comparison requires --baseline and --candidate together")
        comparison = diagnostics.compare(_resolve_path(args.baseline), _resolve_path(args.candidate))
        payload = {
            "operation": "compare",
            "comparison": dataclass_payload(comparison),
        }
        _print_payload(payload)
        _save_optional(payload, args.json_output)
        return

    if not args.image:
        raise SystemExit("Provide --image for stats/crop, or --baseline and --candidate for comparison")

    image_path = _resolve_path(args.image)

    if args.crop_output:
        if region is None:
            raise SystemExit("Crop requires --left, --top, --width, --height, and --crop-output")
        crop_stats = diagnostics.crop(image_path, _resolve_path(args.crop_output), region)
        payload = {
            "operation": "crop",
            "source_image": str(image_path),
            "region": dataclass_payload(region),
            "output_stats": dataclass_payload(crop_stats),
        }
        _print_payload(payload)
        _save_optional(payload, args.json_output)
        return

    stats = diagnostics.stats(image_path)
    payload = {
        "operation": "stats",
        "stats": dataclass_payload(stats),
    }
    _print_payload(payload)
    _save_optional(payload, args.json_output)


if __name__ == "__main__":
    main()
