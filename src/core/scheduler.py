from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional

from core.interfaces import ActionEvent, InputBackend


_WAIT_ACTIONS = {"wait", "pause", "sleep"}


class PlaybackStopped(RuntimeError):
    """Raised when playback is intentionally stopped by a safety guard."""


class FrameScheduler:
    """Runs action playback on a fixed frame cadence using a monotonic clock.

    Supported macro conveniences:

    - Wait events use action names: wait, pause, or sleep.
    - Chord events join actions with '+', for example: lb+rb or a+b.

    Phase 6 safety guards:

    - Guarded sleeps that can stop during long holds/waits.
    - Optional max runtime limit.
    - Optional stop callback for console hotkeys or future UI signals.
    - Error/stopped status logging.
    - Pressed-button cleanup on failures and Ctrl+C.
    """

    def __init__(
        self,
        backend: InputBackend,
        target_fps: int = 60,
        log_file: Optional[Path] = None,
        max_runtime_seconds: float | None = None,
        stop_requested: Callable[[], bool] | None = None,
        guard_check_interval: float = 0.02,
    ) -> None:
        if target_fps <= 0:
            raise ValueError("target_fps must be positive")
        if max_runtime_seconds is not None and max_runtime_seconds <= 0:
            raise ValueError("max_runtime_seconds must be positive when provided")
        if guard_check_interval <= 0:
            raise ValueError("guard_check_interval must be positive")

        self._backend = backend
        self._frame_interval = 1.0 / target_fps
        self._log_file = log_file
        self._max_runtime_seconds = max_runtime_seconds
        self._stop_requested = stop_requested
        self._guard_check_interval = guard_check_interval

    def run(self, events: Iterable[ActionEvent]) -> None:
        playback_started = time.monotonic()
        next_tick = playback_started

        try:
            for event in events:
                self._check_guards(playback_started)

                now = time.monotonic()
                if now < next_tick:
                    self._sleep_with_guards(next_tick - now, playback_started)

                started = time.perf_counter()
                actions = self._split_actions(event.action)

                try:
                    if self._is_wait(actions):
                        self._sleep_with_guards(max(event.hold_seconds, 0.0), playback_started)
                    else:
                        self._dispatch_actions(actions, event.hold_seconds, playback_started)
                except Exception as exc:
                    elapsed = time.perf_counter() - started
                    self._write_log(
                        event,
                        elapsed,
                        status="stopped" if isinstance(exc, PlaybackStopped) else "error",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    )
                    raise

                elapsed = time.perf_counter() - started
                self._write_log(event, elapsed, status="ok")
                next_tick += self._frame_interval
        except KeyboardInterrupt as exc:
            self._write_log(
                ActionEvent(action="keyboard_interrupt", hold_seconds=0.0),
                0.0,
                status="stopped",
                error_type="KeyboardInterrupt",
                error="Playback interrupted by Ctrl+C",
            )
            raise PlaybackStopped("Playback interrupted by Ctrl+C") from exc
        finally:
            self._backend.flush()

    def _dispatch_actions(
        self,
        actions: list[str],
        hold_seconds: float,
        playback_started: float,
    ) -> None:
        pressed: list[str] = []
        try:
            for action in actions:
                self._check_guards(playback_started)
                self._backend.press(action)
                pressed.append(action)

            self._backend.flush()
            self._sleep_with_guards(max(hold_seconds, 0.0), playback_started)
        finally:
            for action in reversed(pressed):
                try:
                    self._backend.release(action)
                except Exception:
                    # Best-effort cleanup: keep trying to release the rest, then flush.
                    pass
            if pressed:
                self._backend.flush()

    def _sleep_with_guards(self, duration: float, playback_started: float) -> None:
        if duration <= 0:
            self._check_guards(playback_started)
            return

        end_at = time.monotonic() + duration
        while True:
            self._check_guards(playback_started)
            remaining = end_at - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(remaining, self._guard_check_interval))

    def _check_guards(self, playback_started: float) -> None:
        if self._max_runtime_seconds is not None:
            elapsed = time.monotonic() - playback_started
            if elapsed > self._max_runtime_seconds:
                raise PlaybackStopped(
                    f"Max runtime exceeded: {elapsed:.2f}s > {self._max_runtime_seconds:.2f}s"
                )

        if self._stop_requested is not None and self._stop_requested():
            raise PlaybackStopped("Stop requested")

    def _split_actions(self, action: str) -> list[str]:
        actions = [part.strip() for part in str(action).split("+") if part.strip()]
        if not actions:
            raise ValueError("Action event must contain at least one action")
        return actions

    def _is_wait(self, actions: list[str]) -> bool:
        return len(actions) == 1 and actions[0].lower() in _WAIT_ACTIONS

    def _write_log(
        self,
        event: ActionEvent,
        elapsed_seconds: float,
        *,
        status: str,
        error_type: str | None = None,
        error: str | None = None,
    ) -> None:
        if self._log_file is None:
            return
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": asdict(event),
            "dispatch_seconds": elapsed_seconds,
            "backend": type(self._backend).__name__,
            "status": status,
        }
        if error_type is not None:
            payload["error_type"] = error_type
        if error is not None:
            payload["error"] = error

        with self._log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload))
            handle.write("\n")
