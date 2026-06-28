from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from perception.config import resolve_screenshot_config  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    _build_sequence,
    _discover_profiles,
    _load_config,
    _profile_display_name,
    _profile_metadata,
    _resolve_safety_settings,
    _summarize_events,
)


def _default_safety_args() -> argparse.Namespace:
    return argparse.Namespace(
        countdown_seconds=None,
        no_countdown=False,
        max_runtime_seconds=None,
        stop_key=None,
        no_stop_key=False,
        require_enter=False,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate default config plus profile YAML files without sending input."
    )
    parser.add_argument(
        "--profiles",
        default="profiles",
        help="Profiles directory to scan (relative to repo root or absolute). Default: profiles",
    )
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Default config path to validate before profile files. Default: config/default.yaml",
    )
    return parser


def _resolve_path(project_root: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return project_root / path


def _discover_profiles_in_dir(profiles_dir: Path) -> list[Path]:
    if not profiles_dir.exists():
        return []

    profiles: list[Path] = []
    for suffix in (".yaml", ".yml"):
        profiles.extend(profiles_dir.rglob(f"*{suffix}"))

    return sorted(path for path in profiles if path.is_file())


def main() -> None:
    args = _build_arg_parser().parse_args()

    config_path = _resolve_path(PROJECT_ROOT, args.config)
    profiles_dir = _resolve_path(PROJECT_ROOT, args.profiles)
    profile_targets = _discover_profiles_in_dir(profiles_dir)
    targets = [config_path, *profile_targets]

    if not targets:
        raise SystemExit("No configs or profiles found.")

    failures: list[str] = []
    for target in targets:
        display = _profile_display_name(PROJECT_ROOT, target)
        try:
            config = _load_config(target)
            events = _build_sequence(config)
            metadata = _profile_metadata(config, target)
            safety = _resolve_safety_settings(config, _default_safety_args())
            screenshot = resolve_screenshot_config(config, project_root=PROJECT_ROOT)
        except Exception as exc:  # noqa: BLE001 - CLI validator should report all profile failures.
            failures.append(f"{display}: {exc}")
            print(f"FAIL: {display}")
            print(f"  {exc}")
            continue

        print(f"OK: {display}")
        print(f"  Profile: {metadata['name']} | Risk: {metadata['risk_level']}")
        if metadata["description"]:
            print(f"  Description: {metadata['description']}")
        print(f"  Safety: countdown={safety['countdown_seconds']}s max_runtime={safety['max_runtime_seconds']}s stop_key={safety['stop_key']}")
        print(
            "  Screenshot: "
            f"enabled={screenshot.enabled} backend={screenshot.backend} monitor_index={screenshot.monitor_index} "
            f"output_folder={screenshot.output_folder} file_prefix={screenshot.file_prefix} region={screenshot.region}"
        )
        for line in _summarize_events(events).splitlines():
            print(f"  {line}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(f"\nValidated {len(targets)} config/profile file(s).")


if __name__ == "__main__":
    main()
