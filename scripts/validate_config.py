from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scenarios.scripted_playback import (  # noqa: E402
    _build_sequence,
    _load_config,
    _profile_display_name,
    _resolve_config_path,
    _summarize_events,
    _print_events,
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

    print(f"Config OK: {_profile_display_name(PROJECT_ROOT, config_path)}")
    print(_summarize_events(events))
    if args.show_events:
        _print_events(events)


if __name__ == "__main__":
    main()
