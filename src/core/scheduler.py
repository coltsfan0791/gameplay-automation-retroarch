from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from core.interfaces import ActionEvent, InputBackend


class FrameScheduler:
    """Runs action playback on a fixed frame cadence using a monotonic clock."""

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
            self._backend.press(event.action)
            self._backend.flush()
            time.sleep(max(event.hold_seconds, 0.0))
            self._backend.release(event.action)
            self._backend.flush()
            elapsed = time.perf_counter() - started

            self._write_log(event, elapsed)
            next_tick += self._frame_interval

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
