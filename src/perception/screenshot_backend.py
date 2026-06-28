from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScreenshotRegion:
    """Screen rectangle to capture.

    Coordinates use desktop pixels. For multi-monitor setups, `left` and `top`
    can be negative depending on monitor layout.
    """

    left: int
    top: int
    width: int
    height: int

    def to_mss_monitor(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True)
class ScreenshotResult:
    path: Path
    metadata_path: Path
    width: int
    height: int
    monitor: dict[str, int]
    region: ScreenshotRegion | None
    timestamp_utc: str


class MssScreenshotBackend:
    """Screenshot backend using the cross-platform `mss` package.

    Phase 7 only captures and saves diagnostic frames. It does not perform OCR,
    image recognition, template matching, or gameplay decisions.
    """

    def __init__(self) -> None:
        try:
            import mss
            import mss.tools
        except ImportError as exc:
            raise RuntimeError(
                "mss is required for screenshots. Install with: python -m pip install -r requirements.txt"
            ) from exc

        self._mss = mss
        self._tools = mss.tools

    def list_monitors(self) -> list[dict[str, int]]:
        with self._mss.mss() as sct:
            return [dict(monitor) for monitor in sct.monitors]

    def capture_png(
        self,
        *,
        output_dir: Path,
        file_prefix: str = "sample_frame",
        monitor_index: int = 1,
        region: ScreenshotRegion | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ScreenshotResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        safe_prefix = _safe_file_prefix(file_prefix)
        image_path = output_dir / f"{safe_prefix}-{timestamp}.png"
        metadata_path = output_dir / f"{safe_prefix}-{timestamp}.json"
        timestamp_utc = datetime.now(timezone.utc).isoformat()

        with self._mss.mss() as sct:
            monitor = _resolve_monitor(sct.monitors, monitor_index, region)
            shot = sct.grab(monitor)
            self._tools.to_png(shot.rgb, shot.size, output=str(image_path))

        result = ScreenshotResult(
            path=image_path,
            metadata_path=metadata_path,
            width=int(monitor["width"]),
            height=int(monitor["height"]),
            monitor=dict(monitor),
            region=region,
            timestamp_utc=timestamp_utc,
        )
        _write_metadata(result, metadata or {})
        return result


def _resolve_monitor(
    monitors: list[dict[str, int]],
    monitor_index: int,
    region: ScreenshotRegion | None,
) -> dict[str, int]:
    if region is not None:
        return region.to_mss_monitor()

    if monitor_index < 0 or monitor_index >= len(monitors):
        raise ValueError(
            f"Invalid monitor index {monitor_index}. Available monitor indexes: 0..{len(monitors) - 1}"
        )

    return dict(monitors[monitor_index])


def _safe_file_prefix(prefix: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in prefix.strip())
    return cleaned or "sample_frame"


def _write_metadata(result: ScreenshotResult, extra_metadata: dict[str, Any]) -> None:
    payload: dict[str, Any] = {
        "timestamp_utc": result.timestamp_utc,
        "image_path": str(result.path),
        "width": result.width,
        "height": result.height,
        "monitor": result.monitor,
        "region": asdict(result.region) if result.region is not None else None,
        "phase": "phase7_perception_foundation",
        "contains_ocr": False,
        "contains_decision_logic": False,
    }
    payload.update(extra_metadata)

    with result.metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
