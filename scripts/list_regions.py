from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.regions import format_region, load_regions, regions_payload  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    _load_config,
    _profile_display_name,
    _resolve_config_path,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List named screen regions for a config/profile.")
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    regions = load_regions(config)

    if args.json:
        print(json.dumps({
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "region_count": len(regions),
            "regions": regions_payload(regions),
        }, indent=2))
        return

    print(f"Regions for {_profile_display_name(PROJECT_ROOT, config_path)}:")
    if not regions:
        print("- none")
        return

    for region in sorted(regions.values(), key=lambda item: item.name):
        print(f"- {format_region(region)}")


if __name__ == "__main__":
    main()
