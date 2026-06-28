from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from perception.screenshot_backend import ScreenshotRegion


@dataclass(frozen=True)
class ScreenshotConfig:
    enabled: bool
    backend: str
    monitor_index: int
    output_folder: Path
    file_prefix: str
    region: ScreenshotRegion | None


def resolve_screenshot_config(
    config: dict[str, Any],
    *,
    project_root: Path,
    monitor_index_override: int | None = None,
    output_folder_override: str | None = None,
    file_prefix_override: str | None = None,
    region_override: ScreenshotRegion | None = None,
) -> ScreenshotConfig:
    screenshot = _screenshot_section(config)

    enabled = screenshot.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("perception.screenshot.enabled must be a boolean")

    backend = str(screenshot.get("backend", "mss")).strip().lower()
    if backend != "mss":
        raise ValueError("Only perception.screenshot.backend: mss is supported in Phase 7")

    monitor_index = monitor_index_override if monitor_index_override is not None else screenshot.get("monitor_index", 1)
    if not isinstance(monitor_index, int):
        raise ValueError("perception.screenshot.monitor_index must be an integer")
    if monitor_index < 0:
        raise ValueError("perception.screenshot.monitor_index must be zero or greater")

    raw_folder = output_folder_override or screenshot.get("output_folder", "logs/screenshots")
    output_folder = _resolve_output_folder(project_root, raw_folder)

    file_prefix = str(file_prefix_override or screenshot.get("file_prefix", "sample_frame")).strip()
    if not file_prefix:
        raise ValueError("perception.screenshot.file_prefix must not be empty")

    region = region_override if region_override is not None else _resolve_config_region(screenshot)

    return ScreenshotConfig(
        enabled=enabled,
        backend=backend,
        monitor_index=monitor_index,
        output_folder=output_folder,
        file_prefix=file_prefix,
        region=region,
    )


def make_region(raw: dict[str, Any]) -> ScreenshotRegion:
    required = ("left", "top", "width", "height")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Screenshot region missing required keys: {missing}")

    values = {key: raw[key] for key in required}
    for key, value in values.items():
        if not isinstance(value, int):
            raise ValueError(f"Screenshot region '{key}' must be an integer")

    if values["width"] <= 0 or values["height"] <= 0:
        raise ValueError("Screenshot region width and height must be positive")

    return ScreenshotRegion(
        left=values["left"],
        top=values["top"],
        width=values["width"],
        height=values["height"],
    )


def _screenshot_section(config: dict[str, Any]) -> dict[str, Any]:
    perception = config.get("perception", {})
    if perception is None:
        perception = {}
    if not isinstance(perception, dict):
        raise ValueError("perception must be a mapping when provided")

    screenshot = perception.get("screenshot", {})
    if screenshot is None:
        screenshot = {}
    if not isinstance(screenshot, dict):
        raise ValueError("perception.screenshot must be a mapping when provided")

    return screenshot


def _resolve_config_region(screenshot: dict[str, Any]) -> ScreenshotRegion | None:
    raw_region = screenshot.get("region")
    if raw_region is None:
        return None
    if not isinstance(raw_region, dict):
        raise ValueError("perception.screenshot.region must be a mapping or null")
    return make_region(raw_region)


def _resolve_output_folder(project_root: Path, raw_folder: Any) -> Path:
    path = Path(str(raw_folder)).expanduser()
    if path.is_absolute():
        return path
    return project_root / path
