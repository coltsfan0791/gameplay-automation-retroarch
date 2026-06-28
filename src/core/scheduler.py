from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from core.interfaces import ActionEvent, InputBackend


_WAIT_ACTIONS = {"wait", "pause", "sleep"}


class FrameScheduler:
    """Runs action playback on a fixed frame cadence using a monotonic clock.

    Phase 4 keeps the public ActionEvent contract simple while adding two
    macro conveniences:

    - Wait events use action names: wait, pause, or sleep.
    - Chord events join actions with '+', for example: lb+rb or a+b.
    """

    def __init__(
        self,
        backend: InputBackend,
        target_fps: int = 60,
        log_file: Optional[Path] = None,
    ) -> None:
        if target_fps <= 0:
            raise ValueError("target_fps must be positive")
        self._backend = backend
        self._frame_interval = 1.0 / target_fps
        self._log_file = log_file

    def run(self, events: Iterable[ActionEvent]) -> None:
        next_tick = time.monotonic()
        for event in events:
            now = time.monotonic()
            if now < next_tick:
                time.sleep(next_tick - now)

            started = time.perf_counter()
            actions = self._split_actions(event.action)

            if self._is_wait(actions):
                time.sleep(max(event.hold_seconds, 0.0))
            else:
                self._dispatch_actions(actions, event.hold_seconds)

            elapsed = time.perf_counter() - started
            self._write_log(event, elapsed)
            next_tick += self._frame_interval

    def _dispatch_actions(self, actions: list[str], hold_seconds: float) -> None:
        pressed: list[str] = []
        try:
            for action in actions:
                self._backend.press(action)
                pressed.append(action)

            self._backend.flush()
            time.sleep(max(hold_seconds, 0.0))
        finally:
            for action in reversed(pressed):
                self._backend.release(action)
            if pressed:
                self._backend.flush()

    def _split_actions(self, action: str) -> list[str]:
        actions = [part.strip() for part in str(action).split("+") if part.strip()]
        if not actions:
            raise ValueError("Action event must contain at least one action")
        return actions

    def _is_wait(self, actions: list[str]) -> bool:
        return len(actions) == 1 and actions[0].lower() in _WAIT_ACTIONS

    def _write_log(self, event: ActionEvent, elapsed_seconds: float) -> None:
        if self._log_file is None:
            return
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": asdict(event),
            "dispatch_seconds": elapsed_seconds,
            "backend": type(self._backend).__name__,
            "status": "ok",
        }
        with self._log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload))
            handle.write("\n")
