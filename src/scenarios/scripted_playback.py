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

    macros = playback.get("macros", {})
    if macros is None:
        macros = {}
    if not isinstance(macros, dict):
        raise ValueError("'playback.macros' must be a mapping when provided")

    selected_macro = playback.get("run", playback.get("macro"))
    if selected_macro is not None:
        if not isinstance(selected_macro, str) or not selected_macro.strip():
            raise ValueError("'playback.run' must be a non-empty macro name")
        return _expand_macro(selected_macro.strip(), macros, stack=[])

    raw_sequence = playback.get("sequence")
    if raw_sequence is None or raw_sequence == []:
        print("No 'playback.sequence' found. Using fallback demo sequence.")
        return list(FALLBACK_SEQUENCE)

    return _expand_sequence(raw_sequence, macros, path="playback.sequence", stack=[])


def _expand_macro(
    name: str,
    macros: dict[str, Any],
    stack: list[str],
) -> list[ActionEvent]:
    if name in stack:
        chain = " -> ".join([*stack, name])
        raise ValueError(f"Recursive macro reference detected: {chain}")

    raw_sequence = macros.get(name)
    if raw_sequence is None:
        available = ", ".join(sorted(macros)) or "<none>"
        raise ValueError(f"Unknown macro '{name}'. Available macros: {available}")

    return _expand_sequence(
        raw_sequence,
        macros,
        path=f"playback.macros.{name}",
        stack=[*stack, name],
    )


def _expand_sequence(
    raw_sequence: Any,
    macros: dict[str, Any],
    path: str,
    stack: list[str],
) -> list[ActionEvent]:
    if not isinstance(raw_sequence, list):
        raise ValueError(f"'{path}' must be a list")

    events: list[ActionEvent] = []
    for index, step in enumerate(raw_sequence, start=1):
        events.extend(_expand_step(step, macros, f"{path}[{index}]", stack))

    return events


def _expand_step(
    step: Any,
    macros: dict[str, Any],
    path: str,
    stack: list[str],
) -> list[ActionEvent]:
    if not isinstance(step, dict):
        raise ValueError(f"{path} must be a mapping")

    if "repeat" in step:
        count = _resolve_repeat_count(step.get("repeat"), path)
        nested = step.get("sequence", step.get("steps"))
        if nested is None:
            raise ValueError(f"{path} repeat step requires 'sequence' or 'steps'")
        expanded_once = _expand_sequence(nested, macros, f"{path}.sequence", stack)
        return expanded_once * count

    macro_name = step.get("use_macro", step.get("macro"))
    if macro_name is not None:
        if not isinstance(macro_name, str) or not macro_name.strip():
            raise ValueError(f"{path}.use_macro must be a non-empty macro name")
        return _expand_macro(macro_name.strip(), macros, stack)

    if "wait_seconds" in step or "wait" in step:
        seconds = step.get("wait_seconds", step.get("wait"))
        return [ActionEvent(action="wait", hold_seconds=_resolve_duration(seconds, path, "wait_seconds"))]

    if "chord" in step:
        chord = step["chord"]
        if not isinstance(chord, list) or not chord:
            raise ValueError(f"{path}.chord must be a non-empty list of action names")
        actions = []
        for action_index, action in enumerate(chord, start=1):
            if not isinstance(action, str) or not action.strip():
                raise ValueError(f"{path}.chord[{action_index}] must be a non-empty string")
            actions.append(action.strip())
        hold = _resolve_hold(step, path)
        return [ActionEvent(action="+".join(actions), hold_seconds=hold)]

    action = step.get("action")
    if not isinstance(action, str) or not action.strip():
        raise ValueError(f"{path} has invalid 'action'")

    hold = _resolve_hold(step, path)
    return [ActionEvent(action=action.strip(), hold_seconds=hold)]


def _resolve_repeat_count(value: Any, path: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{path}.repeat must be an integer")
    if value < 1:
        raise ValueError(f"{path}.repeat must be at least 1")
    if value > 10_000:
        raise ValueError(f"{path}.repeat is too large; refusing to expand more than 10,000 repeats")
    return value


def _resolve_hold(step: dict[str, Any], path: str) -> float:
    value = step.get("hold_seconds", step.get("seconds", 0.05))
    return _resolve_duration(value, path, "hold_seconds")


def _resolve_duration(value: Any, path: str, field_name: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{path}.{field_name} must be a number")
    if value < 0:
        raise ValueError(f"{path}.{field_name} must be non-negative")
    return float(value)


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
