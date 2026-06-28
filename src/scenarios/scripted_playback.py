from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc

# Enable direct script execution from the scenarios folder.
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.interfaces import ActionEvent
from core.scheduler import FrameScheduler
from input.vgamepad_backend import VGamepadBackend


FALLBACK_SEQUENCE: tuple[ActionEvent, ...] = (
    ActionEvent("a", hold_seconds=0.08),
    ActionEvent("right", hold_seconds=0.10),
    ActionEvent("b", hold_seconds=0.08),
    ActionEvent("left", hold_seconds=0.10),
    ActionEvent("y", hold_seconds=0.08),
)


def _load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping")

    return data


def _build_sequence(config: dict[str, Any]) -> list[ActionEvent]:
    playback = config.get("playback")
    if playback is None:
        print("No 'playback' section found. Using fallback demo sequence.")
        return list(FALLBACK_SEQUENCE)

    if not isinstance(playback, dict):
        raise ValueError("Invalid 'playback' section: expected a mapping")

    raw_sequence = playback.get("sequence")
    if raw_sequence is None or raw_sequence == []:
        print("No 'playback.sequence' found. Using fallback demo sequence.")
        return list(FALLBACK_SEQUENCE)

    if not isinstance(raw_sequence, list):
        raise ValueError("'playback.sequence' must be a list")

    events: list[ActionEvent] = []
    for index, step in enumerate(raw_sequence, start=1):
        if not isinstance(step, dict):
            raise ValueError(f"Sequence step #{index} must be a mapping")

        action = step.get("action")
        if not isinstance(action, str) or not action.strip():
            raise ValueError(f"Sequence step #{index} has invalid 'action'")

        hold = step.get("hold_seconds", 0.05)
        if not isinstance(hold, (int, float)):
            raise ValueError(f"Sequence step #{index} has invalid 'hold_seconds'")
        if hold < 0:
            raise ValueError(f"Sequence step #{index} has negative 'hold_seconds'")

        events.append(ActionEvent(action=action.strip(), hold_seconds=float(hold)))

    return events


def _resolve_log_path(project_root: Path, config: dict[str, Any]) -> Path | None:
    logging_cfg = config.get("logging")
    if not isinstance(logging_cfg, dict):
        return project_root / "logs" / _build_log_name("playback")

    if not logging_cfg.get("enabled", True):
        return None

    folder = logging_cfg.get("folder", "logs")
    prefix = logging_cfg.get("file_prefix", "playback")
    return project_root / str(folder) / _build_log_name(str(prefix))


def _build_log_name(prefix: str) -> str:
    safe_prefix = prefix.strip() or "playback"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{safe_prefix}-{stamp}.jsonl"


def _resolve_target_fps(config: dict[str, Any]) -> int:
    runtime = config.get("runtime")
    if not isinstance(runtime, dict):
        return 60

    target_fps = runtime.get("target_fps", 60)
    if not isinstance(target_fps, int) or target_fps <= 0:
        raise ValueError("'runtime.target_fps' must be a positive integer")

    return target_fps


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / "config" / "default.yaml"
    config = _load_config(config_path)
    events = _build_sequence(config)
    log_path = _resolve_log_path(project_root, config)

    backend = VGamepadBackend()
    scheduler = FrameScheduler(
        backend=backend,
        target_fps=_resolve_target_fps(config),
        log_file=log_path,
    )
    scheduler.run(events)

    if log_path is None:
        print(f"Playback complete. Events dispatched: {len(events)}. Logging disabled by config.")
    else:
        print(f"Playback complete. Events dispatched: {len(events)}. Log: {log_path}")


if __name__ == "__main__":
    main()
