from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from perception.image_diagnostics import ImageDiagnostics, save_json
from perception.screenshot_backend import (MssScreenshotBackend,
                                           ScreenshotRegion)


@dataclass(frozen=True)
class NamedRegion:
    """A named rectangular region on the screen."""

    name: str
    left: int
    top: int
    width: int
    height: int

    def to_screenshot_region(self) -> ScreenshotRegion:
        return ScreenshotRegion(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
        )

    def to_image_region(self) -> "ImageRegion":
        from perception.image_diagnostics import ImageRegion

        return ImageRegion(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
        )

    @property
    def box(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.left + self.width, self.top + self.height)

    def __repr__(self) -> str:
        return (
            f"NamedRegion(name={self.name!r}, "
            f"left={self.left}, top={self.top}, "
            f"width={self.width}, height={self.height})"
        )


# ---------------------------------------------------------------------------
# Region resolution from config
# ---------------------------------------------------------------------------


def resolve_regions(config: dict[str, Any]) -> dict[str, NamedRegion]:
    """Load and validate all named regions from the config's ``regions`` section.

    Returns a dict mapping region name to ``NamedRegion``.  Validates that
    every region has positive width/height.
    """
    raw = config.get("regions", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("'regions' must be a mapping when provided")

    regions: dict[str, NamedRegion] = {}
    for name, rect in raw.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Region name must be a non-empty string")
        if not isinstance(rect, dict):
            raise ValueError(f"Region '{name}' must be a mapping with left/top/width/height")

        left = rect.get("left")
        top = rect.get("top")
        width = rect.get("width")
        height = rect.get("height")

        missing = [k for k in ("left", "top", "width", "height") if k not in rect]
        if missing:
            raise ValueError(f"Region '{name}' missing required keys: {missing}")

        for key, val in [("left", left), ("top", top), ("width", width), ("height", height)]:
            if not isinstance(val, int):
                raise ValueError(f"Region '{name}.{key}' must be an integer")

        if width <= 0 or height <= 0:
            raise ValueError(f"Region '{name}' width and height must be positive, got {width}x{height}")

        clean_name = name.strip()
        if clean_name in regions:
            raise ValueError(f"Duplicate region name: {clean_name}")

        regions[clean_name] = NamedRegion(
            name=clean_name,
            left=left,
            top=top,
            width=width,
            height=height,
        )

    return regions


def get_region(regions: dict[str, NamedRegion], name: str) -> NamedRegion:
    """Look up a named region and raise a clear error if missing."""
    region = regions.get(name)
    if region is None:
        available = ", ".join(sorted(regions)) if regions else "<none>"
        raise ValueError(f"Unknown region '{name}'. Available regions: {available}")
    return region


# ---------------------------------------------------------------------------
# Monitor-bound validation
# ---------------------------------------------------------------------------


def validate_regions_against_monitor(
    regions: dict[str, NamedRegion],
    monitor: dict[str, int],
) -> list[str]:
    """Check that every named region fits inside *monitor*.

    Returns a list of warning messages (empty if all regions fit).
    """
    mon_width = monitor.get("width", 0)
    mon_height = monitor.get("height", 0)
    mon_left = monitor.get("left", 0)
    mon_top = monitor.get("top", 0)

    warnings: list[str] = []
    for region in regions.values():
        right = region.left + region.width
        bottom = region.top + region.height
        if region.left < mon_left:
            warnings.append(
                f"Region '{region.name}' left ({region.left}) is left of monitor left ({mon_left})"
            )
        if region.top < mon_top:
            warnings.append(
                f"Region '{region.name}' top ({region.top}) is above monitor top ({mon_top})"
            )
        if right > mon_left + mon_width:
            warnings.append(
                f"Region '{region.name}' right edge ({right}) exceeds monitor right "
                f"({mon_left + mon_width})"
            )
        if bottom > mon_top + mon_height:
            warnings.append(
                f"Region '{region.name}' bottom edge ({bottom}) exceeds monitor bottom "
                f"({mon_top + mon_height})"
            )
    return warnings


# ---------------------------------------------------------------------------
# Capture wrapper
# ---------------------------------------------------------------------------


def capture_region(
    regions: dict[str, NamedRegion],
    region_name: str,
    backend: MssScreenshotBackend,
    output_dir: Path,
    *,
    file_prefix: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Capture a named region to PNG with JSON metadata sidecar.

    Returns a dict with keys: ``name``, ``path``, ``metadata_path``,
    ``width``, ``height``, ``region``, ``timestamp_utc``.
    """
    region = get_region(regions, region_name)
    safe_prefix = file_prefix or region_name
    extra = dict(metadata or {})
    extra["region_name"] = region_name

    result = backend.capture_png(
        output_dir=output_dir,
        file_prefix=safe_prefix,
        region=region.to_screenshot_region(),
        metadata=extra,
    )

    return {
        "name": region_name,
        "path": str(result.path),
        "metadata_path": str(result.metadata_path),
        "width": result.width,
        "height": result.height,
        "region": asdict(region),
        "timestamp_utc": result.timestamp_utc,
    }


def analyze_captured_region(
    image_path: Path,
    region: NamedRegion,
    diagnostics: ImageDiagnostics,
    *,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run image diagnostics on a previously captured region image.

    Returns a dict with stats suitable for JSON serialization.  If
    *output_dir* is provided, writes a JSON report there.
    """
    stats = diagnostics.stats(image_path)
    payload: dict[str, Any] = {
        "operation": "analyze_region",
        "image_path": str(image_path),
        "region": asdict(region),
        "stats": {
            "width": stats.width,
            "height": stats.height,
            "mode": stats.mode,
            "file_size_bytes": stats.file_size_bytes,
            "channel_means": stats.channel_means,
            "channel_extrema": stats.channel_extrema,
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "contains_ocr": False,
        "contains_decision_logic": False,
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        report_path = output_dir / f"region_analysis_{region.name}_{stamp}.json"
        save_json(payload, report_path)
        payload["report_path"] = str(report_path)

    return payload
