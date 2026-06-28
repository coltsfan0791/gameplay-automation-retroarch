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


def main() -> None:
    targets = [PROJECT_ROOT / "config" / "default.yaml", *_discover_profiles(PROJECT_ROOT)]
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
