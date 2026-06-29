# Phase 9 - Named Screen Regions

## What was added

Phase 9 introduces a named screen region system that lets users define reusable rectangular areas in their config/profile YAML and refer to them by name in commands.

### Files created

| File | Purpose |
|------|---------|
| `src/perception/regions.py` | Core module: `NamedRegion` dataclass, `resolve_regions()`, `get_region()`, `validate_regions_against_monitor()`, `capture_region()`, `analyze_captured_region()`. |
| `scripts/list_regions.py` | List region names and coordinates from a config/profile; optionally validate against monitor bounds. |
| `scripts/capture_region.py` | Capture a named region to PNG with JSON metadata sidecar; legacy coordinate overrides still work. |
| `scripts/analyze_region.py` | Capture (or use existing image) and run image diagnostics on a named region. |
| `docs/REGIONS.md` | Full documentation with calibration guide, examples, and safety boundaries. |
| `PHASE9_NOTES.md` | This file. |

### Files updated

| File | Change |
|------|--------|
| `config/default.yaml` | Added `regions:` section with `full_screen`, `menu_area`, `dialog_box` examples. |
| `profiles/_template.yaml` | Added commented-out `regions:` example. |
| `profiles/retroarch_menu_test.yaml` | Added `regions:` section with `full_screen` and `menu_area`. |

### What was NOT added

- OCR.
- Template matching.
- Decision logic.
- Autonomous input.
- Region catalogs (multiple sets per profile).
- Diagnostic overlays (drawn region boxes).

Those belong in Phases 10–12.

## How to test

### 1. Validate all profiles still work

```powershell
python ".\scripts\validate_all_profiles.py"
```

### 2. List regions from default config

```powershell
python ".\scripts\list_regions.py"
```

### 3. List regions from a profile

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
```

### 4. Validate region bounds against the monitor

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test --validate
```

### 5. Capture a named region

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region menu_area
```

Expected output:
```
Captured region 'menu_area': logs/screenshots/menu_area-YYYYMMDD-HHMMSS.png
Metadata: logs/screenshots/menu_area-YYYYMMDD-HHMMSS.json
Size: 966x568
Region: {'name': 'menu_area', 'left': 200, 'top': 100, 'width': 966, 'height': 568}
```

### 6. Capture with legacy CLI coordinates

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --left 200 --top 100 --width 966 --height 568
```

### 7. Analyze a region (fresh capture)

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen
```

### 8. Analyze a region from existing image

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen --image "logs\screenshots\full_screen-*.png"
```

### 9. JSON output

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen --json
```

## Acceptance criteria

- [x] Regions validate shape and positive dimensions.
- [x] Regions can be listed by name.
- [x] Regions validate bounds against monitor (optional).
- [x] Regions can be captured by name to PNG + JSON sidecar.
- [x] Existing `--left --top --width --height` CLI overrides still work.
- [x] Region analysis works with both fresh capture and existing images.
- [x] Documentation explains calibration and safety boundaries.
- [ ] All profiles validate without errors (run `validate_all_profiles.py`).
- [ ] Dry-run region scripts produce correct output.
