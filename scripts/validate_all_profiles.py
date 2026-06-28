from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scenarios.scripted_playback import (  # noqa: E402
    _build_sequence,
    _discover_profiles,
    _load_config,
    _profile_display_name,
    _summarize_events,
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
        except Exception as exc:  # noqa: BLE001 - CLI validator should report all profile failures.
            failures.append(f"{display}: {exc}")
            print(f"FAIL: {display}")
            print(f"  {exc}")
            continue

        print(f"OK: {display}")
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
