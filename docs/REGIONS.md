# Named Screen Regions

Phase 9 adds named screen regions: reusable rectangles that can be listed, captured, and analyzed by name.

This phase is diagnostic only. It does not add OCR, template matching, object detection, conditional waits, image-driven actions, or autonomy.

## Why named regions exist

Before Phase 9, every crop or capture needed raw coordinates:

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame.png" --crop-output "logs\screenshots\crop.png" --left 0 --top 0 --width 320 --height 240
```

With named regions, profiles/configs can define reusable labels:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region top_left
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region menu_area
```

## Coordinate system

Region coordinates are pixels relative to the captured screenshot/monitor.

They are not:

- game-world coordinates
- controller input coordinates
- emulator memory addresses
- OCR text boxes

For saved-image analysis, `left` and `top` should usually be zero or greater.

On multi-monitor desktop capture, monitor positions can be offset by Windows, but named regions in this phase are intended to describe the captured image area.

## Schema

Regions live at the top level of a config/profile YAML file:

```yaml
regions:
  full_screen:
    left: 0
    top: 0
    width: 1366
    height: 768
    description: Full captured monitor area.
    tags:
      - screen

  top_left:
    left: 0
    top: 0
    width: 320
    height: 240
    description: Small top-left diagnostic region.
    tags:
      - diagnostic
```

Required fields:

```text
left: integer
top: integer
width: positive integer
height: positive integer
```

Optional fields:

```text
description: string
tags: list of strings
```

## List regions

Default config:

```powershell
python ".\scripts\list_regions.py"
```

Profile:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
```

JSON output:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test --json
```

## Capture a region

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region top_left
```

Example output:

```text
Captured region: top_left
Image: G:\...\logs\screenshots\retroarch_menu_test_top_left-YYYYMMDD-HHMMSS.png
Metadata: G:\...\logs\screenshots\retroarch_menu_test_top_left-YYYYMMDD-HHMMSS.json
Size: 320x240
```

The JSON sidecar includes the region name and coordinates:

```json
{
  "region_name": "top_left",
  "region": {
    "name": "top_left",
    "left": 0,
    "top": 0,
    "width": 320,
    "height": 240,
    "description": "Top-left diagnostic area.",
    "tags": ["diagnostic"]
  },
  "contains_ocr": false,
  "contains_decision_logic": false
}
```

## Analyze a region

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region top_left
```

Optional JSON report:

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region top_left --json-output "logs\screenshots\top_left_stats.json"
```

`analyze_region.py` does this:

1. Resolves the profile/config.
2. Resolves the named region.
3. Captures that region.
4. Runs read-only image stats on the capture.
5. Prints JSON and optionally writes a JSON report.

It does not press buttons and does not make decisions.

## Validation

Validate one config/profile:

```powershell
python ".\scripts\validate_config.py" retroarch_menu_test
```

Validate all profiles:

```powershell
python ".\scripts\validate_all_profiles.py"
```

Validation checks:

- `regions` is a mapping when provided.
- region names are non-empty strings.
- each region is a mapping.
- `left`, `top`, `width`, and `height` exist.
- `left`, `top`, `width`, and `height` are integers.
- `width` and `height` are positive.
- `description`, when provided, is a string.
- `tags`, when provided, is a list of non-empty strings.

## Missing region behavior

Bad region names fail clearly:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region does_not_exist
```

Expected style:

```text
Region 'does_not_exist' not found. Available regions: full_screen, menu_area, top_left
```

The tool should not silently fall back to full screen.

## Calibrating regions

1. Capture a full screenshot:

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

2. Open the PNG under `logs/screenshots/`.
3. Estimate or measure the pixel rectangle you want.
4. Add it to the profile's `regions:` block.
5. Validate:

```powershell
python ".\scripts\validate_config.py" retroarch_menu_test
```

6. Test capture:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region your_region_name
```

## Phase 9 boundary

Named regions are building blocks for later visual features.

They are not visual intelligence by themselves.

Not included in Phase 9:

- OCR
- template matching
- object detection
- conditional waits
- image-driven actions
- state machines
- route recovery
- autonomy

## Next phase

The next recommended phase is Phase 10: region catalogs per emulator/game layout.
