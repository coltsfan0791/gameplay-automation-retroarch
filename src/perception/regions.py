from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from perception.image_diagnostics import ImageRegion
from perception.screenshot_backend import ScreenshotRegion


@dataclass(frozen=True)
class NamedRegion:
    """A reusable named screen rectangle.

    Coordinates are pixels relative to the captured screenshot/monitor, not game
    world coordinates and not controller input coordinates.
    """

    name: str
    left: int
    top: int
    width: int
    height: int
    description: str | None = None
    tags: tuple[str, ...] = ()

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def to_screenshot_region(self) -> ScreenshotRegion:
        return ScreenshotRegion(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
        )

    def to_image_region(self) -> ImageRegion:
        return ImageRegion(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
        )


def load_regions(config: dict[str, Any]) -> dict[str, NamedRegion]:
    """Parse the top-level `regions` config block.

    Missing or null regions produce an empty mapping. Phase 9 intentionally
    supports only a single top-level region dictionary; region sets/catalogs are
    left for a later phase.
    """

    raw_regions = config.get("regions", {})
    if raw_regions is None:
        return {}
    if not isinstance(raw_regions, dict):
        raise ValueError("regions must be a mapping when provided")

    regions: dict[str, NamedRegion] = {}
    for raw_name, raw_region in raw_regions.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ValueError("region names must be non-empty strings")
        name = raw_name.strip()
        regions[name] = _parse_region(name, raw_region)

    return regions


def resolve_region(config: dict[str, Any], name: str) -> NamedRegion:
    regions = load_regions(config)
    if name in regions:
        return regions[name]

    available = ", ".join(sorted(regions)) if regions else "none"
    raise ValueError(f"Region '{name}' not found. Available regions: {available}")


def region_payload(region: NamedRegion) -> dict[str, Any]:
    payload = asdict(region)
    payload["tags"] = list(region.tags)
    return payload


def regions_payload(regions: dict[str, NamedRegion]) -> list[dict[str, Any]]:
    return [region_payload(region) for region in sorted(regions.values(), key=lambda item: item.name)]


def validate_region_bounds(region: NamedRegion, *, width: int, height: int) -> None:
    """Validate a region against an image/capture size.

    This is intentionally opt-in because desktop/monitor coordinates can be
    negative on some multi-monitor layouts, while saved-image coordinates should
    usually be zero-based.
    """

    if region.left < 0 or region.top < 0:
        raise ValueError(f"Region '{region.name}' left/top must be zero or greater for image bounds validation")
    if region.right > width or region.bottom > height:
        raise ValueError(
            f"Region '{region.name}' ({region.width}x{region.height} at {region.left},{region.top}) "
            f"exceeds image bounds {width}x{height}"
        )


def format_region(region: NamedRegion) -> str:
    description = f" - {region.description}" if region.description else ""
    tags = f" tags={list(region.tags)}" if region.tags else ""
    return (
        f"{region.name}: left={region.left} top={region.top} "
        f"width={region.width} height={region.height}{tags}{description}"
    )


def _parse_region(name: str, raw_region: Any) -> NamedRegion:
    if not isinstance(raw_region, dict):
        raise ValueError(f"region '{name}' must be a mapping")

    left = _required_int(raw_region, name, "left")
    top = _required_int(raw_region, name, "top")
    width = _required_int(raw_region, name, "width")
    height = _required_int(raw_region, name, "height")

    if width <= 0 or height <= 0:
        raise ValueError(f"region '{name}' width and height must be positive integers")

    description = raw_region.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"region '{name}' description must be a string when provided")

    tags = _parse_tags(name, raw_region.get("tags", []))

    return NamedRegion(
        name=name,
        left=left,
        top=top,
        width=width,
        height=height,
        description=description,
        tags=tags,
    )


def _required_int(raw_region: dict[str, Any], region_name: str, key: str) -> int:
    if key not in raw_region:
        raise ValueError(f"region '{region_name}' missing required key '{key}'")
    value = raw_region[key]
    if not isinstance(value, int):
        raise ValueError(f"region '{region_name}' key '{key}' must be an integer")
    return value


def _parse_tags(region_name: str, raw_tags: Any) -> tuple[str, ...]:
    if raw_tags is None:
        return ()
    if not isinstance(raw_tags, list):
        raise ValueError(f"region '{region_name}' tags must be a list of strings when provided")

    tags: list[str] = []
    for tag in raw_tags:
        if not isinstance(tag, str) or not tag.strip():
            raise ValueError(f"region '{region_name}' tags must contain only non-empty strings")
        tags.append(tag.strip())
    return tuple(tags)


def resolve_output_path(project_root: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return project_root / path
