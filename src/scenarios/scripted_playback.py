from __future__ import annotations

import argparse
import sys
from collections import Counter
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

DEFAULT_CONFIG_RELATIVE = Path("config") / "default.yaml"
PROFILES_DIR_NAME = "profiles"
PROFILE_SUFFIXES = (".yaml", ".yml")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping")

    return data


def _discover_profiles(project_root: Path) -> list[Path]:
    profiles_dir = project_root / PROFILES_DIR_NAME
    if not profiles_dir.exists():
        return []

    profiles: list[Path] = []
    for suffix in PROFILE_SUFFIXES:
        profiles.extend(profiles_dir.rglob(f"*{suffix}"))

    return sorted(path for path in profiles if path.is_file())


def _resolve_config_path(
    project_root: Path,
    *,
    config: str | None = None,
    profile: str | None = None,
) -> Path:
    if config and profile:
        raise ValueError("Use either --config or --profile, not both")

    if config:
        return _resolve_path(project_root, config)

    if profile:
        return _resolve_profile_path(project_root, profile)

    return project_root / DEFAULT_CONFIG_RELATIVE


def _resolve_path(project_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def _resolve_profile_path(project_root: Path, profile: str) -> Path:
    requested = Path(profile).expanduser()

    candidates: list[Path] = []
    if requested.is_absolute():
        candidates.append(requested)
    else:
        candidates.append(project_root / requested)
        candidates.append(project_root / PROFILES_DIR_NAME / requested)

        if requested.suffix == "":
            for suffix in PROFILE_SUFFIXES:
                candidates.append(project_root / requested.with_suffix(suffix))
                candidates.append(project_root / PROFILES_DIR_NAME / requested.with_suffix(suffix))

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    known_profiles = _discover_profiles(project_root)
    available = ", ".join(_profile_display_name(project_root, path) for path in known_profiles) or "<none>"
    raise FileNotFoundError(
        f"Profile not found: {profile}. Available profiles: {available}"
    )


def _profile_display_name(project_root: Path, path: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


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


def _resolve_log_path(project_root: Path, config: dict[str, Any], config_path: Path) -> Path | None:
    logging_cfg = config.get("logging")
    if not isinstance(logging_cfg, dict):
        return project_root / "logs" / _build_log_name(_log_prefix_from_config_path(config_path))

    if not logging_cfg.get("enabled", True):
        return None

    folder = logging_cfg.get("folder", "logs")
    prefix = logging_cfg.get("file_prefix")
    if prefix is None:
        prefix = _log_prefix_from_config_path(config_path)
    return project_root / str(folder) / _build_log_name(str(prefix))


def _log_prefix_from_config_path(config_path: Path) -> str:
    return config_path.stem.replace(" ", "_") or "playback"


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


def _summarize_events(events: list[ActionEvent]) -> str:
    action_counts = Counter(event.action for event in events)
    total_hold = sum(event.hold_seconds for event in events)
    lines = [
        f"Expanded events: {len(events)}",
        f"Total hold/wait seconds: {total_hold:.3f}",
        "Actions:",
    ]
    for action, count in sorted(action_counts.items()):
        lines.append(f"- {action}: {count}")
    return "\n".join(lines)


def _print_events(events: list[ActionEvent]) -> None:
    for index, event in enumerate(events, start=1):
        print(f"{index:03d}. {event.action} hold={event.hold_seconds:.3f}s")


def _list_profiles(project_root: Path) -> None:
    profiles = _discover_profiles(project_root)
    if not profiles:
        print("No profiles found.")
        return

    print("Available profiles:")
    for profile in profiles:
        print(f"- {_profile_display_name(project_root, profile)}")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run or inspect YAML-driven RetroArch controller playback profiles."
    )
    parser.add_argument(
        "--profile",
        "-p",
        help="Profile name or path. Examples: retroarch_menu_test, profiles/gba_basic_movement.yaml",
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Explicit config YAML path. Cannot be combined with --profile.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available YAML profiles and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and expand the selected config without sending controller input.",
    )
    parser.add_argument(
        "--show-events",
        action="store_true",
        help="Print every expanded event. Useful with --dry-run.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    project_root = _project_root()
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.list_profiles:
        _list_profiles(project_root)
        return

    config_path = _resolve_config_path(
        project_root,
        config=args.config,
        profile=args.profile,
    )
    config = _load_config(config_path)
    events = _build_sequence(config)

    print(f"Using config: {_profile_display_name(project_root, config_path)}")

    if args.dry_run:
        print(_summarize_events(events))
        if args.show_events:
            _print_events(events)
        return

    log_path = _resolve_log_path(project_root, config, config_path)
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
