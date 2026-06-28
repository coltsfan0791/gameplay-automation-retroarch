from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ImageRegion:
    left: int
    top: int
    width: int
    height: int

    @property
    def box(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.left + self.width, self.top + self.height)


@dataclass(frozen=True)
class ImageStats:
    path: Path
    width: int
    height: int
    mode: str
    file_size_bytes: int
    channel_means: list[float]
    channel_extrema: list[tuple[int, int]]


@dataclass(frozen=True)
class ImageComparison:
    baseline_path: Path
    candidate_path: Path
    same_size: bool
    baseline_size: tuple[int, int]
    candidate_size: tuple[int, int]
    diff_bbox: tuple[int, int, int, int] | None
    mean_abs_diff: float | None
    max_abs_diff: int | None
    changed_pixels: int | None
    changed_percent: float | None


class ImageDiagnostics:
    """Read-only image diagnostics for captured frames.

    Phase 8 intentionally does not perform OCR, template matching, or gameplay
    decisions. These helpers only summarize, crop, and compare saved images.
    """

    def __init__(self) -> None:
        try:
            from PIL import Image, ImageChops, ImageStat
        except ImportError as exc:
            raise RuntimeError(
                "Pillow is required for image diagnostics. Install with: python -m pip install -r requirements.txt"
            ) from exc

        self._Image = Image
        self._ImageChops = ImageChops
        self._ImageStat = ImageStat

    def stats(self, image_path: Path) -> ImageStats:
        image_path = image_path.expanduser()
        with self._Image.open(image_path) as image:
            stat = self._ImageStat.Stat(image.convert("RGB"))
            return ImageStats(
                path=image_path,
                width=image.width,
                height=image.height,
                mode=image.mode,
                file_size_bytes=image_path.stat().st_size,
                channel_means=[round(value, 3) for value in stat.mean],
                channel_extrema=[tuple(pair) for pair in stat.extrema],
            )

    def crop(self, image_path: Path, output_path: Path, region: ImageRegion) -> ImageStats:
        image_path = image_path.expanduser()
        output_path = output_path.expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self._Image.open(image_path) as image:
            _validate_region(region, image.width, image.height)
            cropped = image.crop(region.box)
            cropped.save(output_path)

        return self.stats(output_path)

    def compare(self, baseline_path: Path, candidate_path: Path) -> ImageComparison:
        baseline_path = baseline_path.expanduser()
        candidate_path = candidate_path.expanduser()

        with self._Image.open(baseline_path) as baseline_raw, self._Image.open(candidate_path) as candidate_raw:
            baseline_size = baseline_raw.size
            candidate_size = candidate_raw.size
            same_size = baseline_size == candidate_size
            if not same_size:
                return ImageComparison(
                    baseline_path=baseline_path,
                    candidate_path=candidate_path,
                    same_size=False,
                    baseline_size=baseline_size,
                    candidate_size=candidate_size,
                    diff_bbox=None,
                    mean_abs_diff=None,
                    max_abs_diff=None,
                    changed_pixels=None,
                    changed_percent=None,
                )

            baseline = baseline_raw.convert("RGB")
            candidate = candidate_raw.convert("RGB")
            diff = self._ImageChops.difference(baseline, candidate)
            diff_bbox = diff.getbbox()
            stat = self._ImageStat.Stat(diff)
            channel_means = stat.mean
            mean_abs_diff = sum(channel_means) / len(channel_means)
            channel_extrema = stat.extrema
            max_abs_diff = max(max_value for _, max_value in channel_extrema)

            changed_pixels = _count_changed_pixels(diff)
            total_pixels = baseline.width * baseline.height
            changed_percent = (changed_pixels / total_pixels) * 100 if total_pixels else 0.0

            return ImageComparison(
                baseline_path=baseline_path,
                candidate_path=candidate_path,
                same_size=True,
                baseline_size=baseline_size,
                candidate_size=candidate_size,
                diff_bbox=diff_bbox,
                mean_abs_diff=round(mean_abs_diff, 6),
                max_abs_diff=int(max_abs_diff),
                changed_pixels=changed_pixels,
                changed_percent=round(changed_percent, 6),
            )


def save_json(payload: dict[str, Any], output_path: Path) -> None:
    output_path = output_path.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "phase8_image_diagnostics",
        "contains_ocr": False,
        "contains_decision_logic": False,
        **payload,
    }
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=_json_default)
        handle.write("\n")


def image_region_from_values(left: int, top: int, width: int, height: int) -> ImageRegion:
    if width <= 0 or height <= 0:
        raise ValueError("Region width and height must be positive")
    return ImageRegion(left=left, top=top, width=width, height=height)


def dataclass_payload(value: Any) -> dict[str, Any]:
    payload = asdict(value)
    return _convert_paths(payload)


def _validate_region(region: ImageRegion, image_width: int, image_height: int) -> None:
    left, top, right, bottom = region.box
    if left < 0 or top < 0:
        raise ValueError("Crop region left/top must be zero or greater")
    if right > image_width or bottom > image_height:
        raise ValueError(
            f"Crop region {region} exceeds image bounds {image_width}x{image_height}"
        )


def _count_changed_pixels(diff_image: Any) -> int:
    # Count any RGB pixel where at least one channel changed.
    changed = 0
    for red, green, blue in diff_image.getdata():
        if red or green or blue:
            changed += 1
    return changed


def _convert_paths(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _convert_paths(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_convert_paths(inner) for inner in value]
    if isinstance(value, tuple):
        return [_convert_paths(inner) for inner in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
