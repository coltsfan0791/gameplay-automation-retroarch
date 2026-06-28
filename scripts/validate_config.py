from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.config import resolve_screenshot_config  # noqa: E402
from perception.regions import format_region, load_regions  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    _build_sequence,
    _load_config,
    _print_events,
    _profile_display_name,
    _profile_metadata,
    _resolve_config_path,
    _resolve_safety_settings,
    _summarize_events,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a RetroArch automation YAML config/profile without sending input."
    )
    parser.add_argument(
        "profile_or_config",
        nargs="?",
        help="Optional profile name/path or config path. Defaults to config/default.yaml.",
    )
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config path.")
    parser.add_argument("--show-events", action="store_true", help="Print every expanded event.")
    return parser


def _default_safety_args() -> argparse.Namespace:
    return argparse.Namespace(
        countdown_seconds=None,
        no_countdown=False,
        max_runtime_seconds=None,
        stop_key=None,
        no_stop_key=False,
        require_enter=False,
    )


def _print_regions(regions) -> None:
    if not regions:
        print("Regions: none")
        return
    print(f"Regions: {len(regions)}")
    for region in sorted(regions.values(), key=lambda item: item.name):
        print(f"- {format_region(region)}")


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    profile = args.profile
    config = args.config
    if args.profile_or_config:
        candidate = Path(args.profile_or_config)
        if candidate.suffix.lower() in {".yaml", ".yml"} or any(part in {"config", "profiles"} for part in candidate.parts):
            config = args.profile_or_config
        else:
            profile = args.profile_or_config

    config_path = _resolve_config_path(PROJECT_ROOT, config=config, profile=profile)
    config_data = _load_config(config_path)
    events = _build_sequence(config_data)
    metadata = _profile_metadata(config_data, config_path)
    safety = _resolve_safety_settings(config_data, _default_safety_args())
    screenshot = resolve_screenshot_config(config_data, project_root=PROJECT_ROOT)
    regions = load_regions(config_data)

    print(f"Config OK: {_profile_display_name(PROJECT_ROOT, config_path)}")
    print(f"Profile: {metadata['name']} | Risk: {metadata['risk_level']}")
    if metadata["description"]:
        print(f"Description: {metadata['description']}")
    print(f"Safety: countdown={safety['countdown_seconds']}s max_runtime={safety['max_runtime_seconds']}s stop_key={safety['stop_key']}")
    print(
        "Screenshot: "
        f"enabled={screenshot.enabled} backend={screenshot.backend} monitor_index={screenshot.monitor_index} "
        f"output_folder={screenshot.output_folder} file_prefix={screenshot.file_prefix} region={screenshot.region}"
    )
    _print_regions(regions)
    print(_summarize_events(events))
    if args.show_events:
        _print_events(events)


if __name__ == "__main__":
    main()
