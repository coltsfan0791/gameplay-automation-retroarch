from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

# Enable direct script execution from the scenarios folder.
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.interfaces import ActionEvent
from core.scheduler import FrameScheduler
from input.vgamepad_backend import VGamepadBackend


def _build_sequence() -> list[ActionEvent]:
    # Simple deterministic demo sequence for validation.
    return [
        ActionEvent("a", hold_seconds=0.08),
        ActionEvent("right", hold_seconds=0.10),
        ActionEvent("b", hold_seconds=0.08),
        ActionEvent("left", hold_seconds=0.10),
        ActionEvent("y", hold_seconds=0.08),
    ]


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    log_dir = project_root / "logs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"playback-{stamp}.jsonl"

    backend = VGamepadBackend()
    scheduler = FrameScheduler(backend=backend, target_fps=60, log_file=log_path)
    scheduler.run(_build_sequence())

    print(f"Playback complete. Log: {log_path}")


if __name__ == "__main__":
    main()

