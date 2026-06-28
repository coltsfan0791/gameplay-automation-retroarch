from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.scheduler import FrameScheduler, PlaybackStopped  # noqa: E402
from input.vgamepad_backend import VGamepadBackend  # noqa: E402
from perception.config import make_region, resolve_screenshot_config  # noqa: E402
from perception.image_diagnostics import ImageDiagnostics, dataclass_payload, save_json  # noqa: E402
from perception.screenshot_backend import MssScreenshotBackend, ScreenshotRegion  # noqa: E402
from scenarios.scripted_playback import (  # noqa: E402
    ConsoleStopKey,
    _build_sequence,
    _countdown,
    _load_config,
    _profile_display_name,
    _profile_metadata,
    _resolve_config_path,
    _resolve_log_path,
    _resolve_safety_settings,
    _resolve_target_fps,
    _summarize_events,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture before/after screenshots around a profile run and compare them."
    )
    parser.add_argument("--profile", "-p", help="Profile name or path.")
    parser.add_argument("--config", "-c", help="Explicit config YAML path.")
    parser.add_argument("--delay-after", type=float, default=0.25, help="Seconds to wait after playback before after-capture.")
    parser.add_argument("--monitor-index", type=int, help="Override perception.screenshot.monitor_index.")
    parser.add_argument("--output-folder", help="Override perception.screenshot.output_folder.")
    parser.add_argument("--file-prefix", help="Override perception.screenshot.file_prefix.")
    parser.add_argument("--left", type=int, help="Capture region left coordinate.")
    parser.add_argument("--top", type=int, help="Capture region top coordinate.")
    parser.add_argument("--width", type=int, help="Capture region width.")
    parser.add_argument("--height", type=int, help="Capture region height.")
    parser.add_argument("--no-countdown", action="store_true", help="Start immediately instead of using configured countdown.")
    parser.add_argument("--countdown-seconds", type=float, help="Override configured countdown seconds.")
    parser.add_argument("--max-runtime-seconds", type=float, help="Override configured max runtime guard.")
    parser.add_argument("--stop-key", help="Single-character Windows console stop key. Ctrl+C always works.")
    parser.add_argument("--no-stop-key", action="store_true", help="Disable optional console stop key polling.")
    parser.add_argument("--require-enter", action="store_true", help="Require Enter before countdown/playback starts.")
    return parser


def _cli_region(args: argparse.Namespace) -> ScreenshotRegion | None:
    values = [args.left, args.top, args.width, args.height]
    if not any(value is not None for value in values):
        return None
    if not all(value is not None for value in values):
        raise ValueError("Region CLI overrides require --left, --top, --width, and --height together")
    return make_region({
        "left": args.left,
        "top": args.top,
        "width": args.width,
        "height": args.height,
    })


def _snapshot_prefix(base_prefix: str, suffix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{base_prefix}_{suffix}_{stamp}"


def main(argv: list[str] | None = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    if args.delay_after < 0:
        raise SystemExit("--delay-after must be zero or greater")

    config_path = _resolve_config_path(PROJECT_ROOT, config=args.config, profile=args.profile)
    config = _load_config(config_path)
    events = _build_sequence(config)
    metadata = _profile_metadata(config, config_path)
    safety = _resolve_safety_settings(config, args)
    stop_key = ConsoleStopKey(enabled=bool(safety["enable_console_stop"]), key=safety["stop_key"])

    screenshot_config = resolve_screenshot_config(
        config,
        project_root=PROJECT_ROOT,
        monitor_index_override=args.monitor_index,
        output_folder_override=args.output_folder,
        file_prefix_override=args.file_prefix,
        region_override=_cli_region(args),
    )
    if not screenshot_config.enabled:
        raise SystemExit("perception.screenshot.enabled is false for this config/profile")

    print(f"Using config: {_profile_display_name(PROJECT_ROOT, config_path)}")
    print(f"Profile: {metadata['name']} | Risk: {metadata['risk_level']}")
    if metadata["description"]:
        print(f"Description: {metadata['description']}")
    print(_summarize_events(events))
    print("Diagnostic mode: before/after screenshots only; no image-based decisions.")
    print(f"Emergency stop: Ctrl+C. Max runtime: {safety['max_runtime_seconds']}s")

    if safety["require_enter"]:
        input("Press Enter to start before/after diagnostic run, or Ctrl+C to abort...")

    _countdown(float(safety["countdown_seconds"] or 0))

    screenshot_backend = MssScreenshotBackend()
    image_diagnostics = ImageDiagnostics()

    before = screenshot_backend.capture_png(
        output_dir=screenshot_config.output_folder,
        file_prefix=_snapshot_prefix(screenshot_config.file_prefix, "before"),
        monitor_index=screenshot_config.monitor_index,
        region=screenshot_config.region,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/capture_profile_snapshots.py",
            "snapshot_role": "before",
        },
    )
    print(f"Before capture: {before.path}")

    log_path = _resolve_log_path(PROJECT_ROOT, config, config_path)
    backend = VGamepadBackend()
    scheduler = FrameScheduler(
        backend=backend,
        target_fps=_resolve_target_fps(config),
        log_file=log_path,
        max_runtime_seconds=safety["max_runtime_seconds"],
        stop_requested=stop_key,
    )

    playback_stopped = None
    try:
        scheduler.run(events)
    except PlaybackStopped as exc:
        playback_stopped = str(exc)
        print(f"Playback stopped safely: {exc}")

    if args.delay_after:
        time.sleep(args.delay_after)

    after = screenshot_backend.capture_png(
        output_dir=screenshot_config.output_folder,
        file_prefix=_snapshot_prefix(screenshot_config.file_prefix, "after"),
        monitor_index=screenshot_config.monitor_index,
        region=screenshot_config.region,
        metadata={
            "config_path": _profile_display_name(PROJECT_ROOT, config_path),
            "script": "scripts/capture_profile_snapshots.py",
            "snapshot_role": "after",
        },
    )
    print(f"After capture: {after.path}")

    comparison = image_diagnostics.compare(before.path, after.path)
    report_path = screenshot_config.output_folder / f"{screenshot_config.file_prefix}_before_after_report-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    report = {
        "operation": "capture_profile_snapshots",
        "config_path": _profile_display_name(PROJECT_ROOT, config_path),
        "profile": metadata,
        "playback_stopped": playback_stopped,
        "playback_log_path": str(log_path) if log_path is not None else None,
        "before": dataclass_payload(before),
        "after": dataclass_payload(after),
        "comparison": dataclass_payload(comparison),
    }
    save_json(report, report_path)

    print(f"Comparison report: {report_path}")
    print(f"Changed pixels: {comparison.changed_pixels}")
    print(f"Changed percent: {comparison.changed_percent}")
    print(f"Mean abs diff: {comparison.mean_abs_diff}")


if __name__ == "__main__":
    main()
