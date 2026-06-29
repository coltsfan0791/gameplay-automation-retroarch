from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.regions import (resolve_regions,  # noqa: E402
                                validate_regions_against_monitor)
from perception.screenshot_backend import MssScreenshotBackend  # noqa: E402
from scenarios.scripted_playback import (_load_config,  # noqa: E402
                                         _profile_display_name,
                                         _resolve_config_path)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List named screen regions defined in a config or profile."
    )
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Check region coordinates against the detected monitor bounds.",
    )
    parser.add_argument(
        "--monitor-index",
        type=int,
        default=1,
        help="Monitor index to validate against (default: 1).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    regions = resolve_regions(config)

    if not regions:
        print(f"No named regions defined in {_profile_display_name(PROJECT_ROOT, config_path)}.")
        print("Add a 'regions:' section to your config/profile YAML.")
        return

    print(f"Named regions in {_profile_display_name(PROJECT_ROOT, config_path)}:")
    print(f"  Total: {len(regions)}\n")

    for name in sorted(regions):
        region = regions[name]
        print(f"  {name}:")
        print(f"    left:   {region.left}")
        print(f"    top:    {region.top}")
        print(f"    width:  {region.width}")
        print(f"    height: {region.height}")
        print(f"    box:    {region.box}")
        print()

    if args.validate:
        print("Validating regions against monitor bounds...")
        backend = MssScreenshotBackend()
        monitors = backend.list_monitors()
        if args.monitor_index < 0 or args.monitor_index >= len(monitors):
            print(f"  Error: monitor index {args.monitor_index} out of range (0..{len(monitors) - 1}).")
            sys.exit(1)
        monitor = monitors[args.monitor_index]
        warnings = validate_regions_against_monitor(regions, monitor)
        if warnings:
            print(f"  Found {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"    - {warning}")
        else:
            print("  All regions fit within the monitor bounds.")


if __name__ == "__main__":
    main()
