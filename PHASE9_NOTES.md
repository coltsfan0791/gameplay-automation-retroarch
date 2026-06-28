# Phase 9 - Named Screen Regions

Phase 9 adds reusable named screen regions for capture and analysis commands.

## Scope

Included:

- `src/perception/regions.py`
- `scripts/list_regions.py`
- `scripts/capture_region.py`
- `scripts/analyze_region.py`
- top-level `regions:` YAML schema
- region validation in `validate_config.py`
- region validation in `validate_all_profiles.py`
- default/template/profile region examples
- region docs

Not included:

- OCR
- template matching
- object detection
- conditional waits
- image-driven actions
- autonomy
- save-state recovery

## Region schema

```yaml
regions:
  top_left:
    left: 0
    top: 0
    width: 320
    height: 240
    description: Top-left diagnostic area.
    tags:
      - diagnostic
```

Required:

```text
left
top
width
height
```

Optional:

```text
description
tags
```

## Commands

List regions:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
python ".\scripts\list_regions.py" --profile retroarch_menu_test --json
```

Capture a region:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region top_left
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region menu_area
```

Analyze a region:

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region top_left
```

Negative test:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region does_not_exist
```

Expected behavior: fail clearly and show available region names.

## Validation

```powershell
python ".\scripts\validate_config.py" retroarch_menu_test
python ".\scripts\validate_all_profiles.py"
```

Validation checks region structure and prints a region summary.

## Output

Region captures write PNG and JSON sidecar files under the configured screenshot output folder, usually:

```text
logs/screenshots/
```

Expected capture filename pattern:

```text
sample_frame_top_left-YYYYMMDD-HHMMSS.png
sample_frame_top_left-YYYYMMDD-HHMMSS.json
```

## Safety boundary

This phase is diagnostic only.

The region tools do not press buttons.
They do not read text.
They do not match templates.
They do not wait for visual conditions.
They do not choose actions.

## Acceptance criteria

Phase 9 is complete when:

```text
validate_all_profiles.py passes
list_regions.py works
list_regions.py --json works
capture_region.py works
analyze_region.py works
bad region names fail clearly
old capture_sample_frame.py still works
old analyze_image.py still works
old capture_profile_snapshots.py still works
docs explain named regions
README points to Phase 9 commands
PR body has test commands
```

## Next recommended phase

Phase 10: region catalogs per emulator/game layout.
