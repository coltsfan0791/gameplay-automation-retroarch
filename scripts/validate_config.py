from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scenarios.scripted_playback import _build_sequence, _load_config


def main() -> None:
    config_path = PROJECT_ROOT / "config" / "default.yaml"
    config = _load_config(config_path)
    events = _build_sequence(config)

    action_counts = Counter(event.action for event in events)
    total_hold = sum(event.hold_seconds for event in events)

    print(f"Config OK: {config_path}")
    print(f"Expanded events: {len(events)}")
    print(f"Total hold/wait seconds: {total_hold:.3f}")
    print("Actions:")
    for action, count in sorted(action_counts.items()):
        print(f"- {action}: {count}")


if __name__ == "__main__":
    main()
