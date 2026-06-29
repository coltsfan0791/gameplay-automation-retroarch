# Named Screen Regions (Phase 9)

This document describes the named screen region system introduced in Phase 9.

Named regions let you define rectangular areas of the screen once in your config/profile YAML and refer to them by name in commands. This replaces one-off `--left --top --width --height` coordinates with a reusable, documented region library.

## Purpose

- Stop hardcoding pixel coordinates in command lines.
- Make region definitions visible, documented, and shareable between profiles.
- Validate region coordinates against actual monitor bounds before capture.
- Keep the capture path purely diagnostic — no OCR, template matching, or decisions.

## Defining regions

Regions are defined under the top-level `regions:` key in any config or profile YAML file.

```yaml
regions:
  full_screen:
    left: 0
    top: 0
    width: 1366
    height: 768
  menu_area:
    left: 200
    top: 100
    width: 966
    height: 568
  dialog_box:
    left: 100
    top: 520
    width: 1160
    height: 180
```

Every region requires:

| Key    | Type | Description |
|--------|------|-------------|
| left   | int  | X offset from the left edge of the monitor (desktop pixels). |
| top    | int  | Y offset from the top edge of the monitor. |
| width  | int  | Width of the region in pixels (must be positive). |
| height | int  | Height of the region in pixels (must be positive). |

Region names must be unique within a file and non-empty.

## Calibrating coordinates

To find the right coordinates for your layout:

1. Capture a full-screen diagnostic frame:
   ```powershell
   python ".\scripts\capture_sample_frame.py"
   ```

2. Open the captured PNG in an image editor that shows pixel coordinates (Paint, GIMP, etc.).

3. Note the `left`, `top`, `width`, and `height` values for each area you care about.

4. Add them to your config or profile under a `regions:` section.

5. Validate that they fit your monitor:
   ```powershell
   python ".\scripts\list_regions.py" --profile retroarch_menu_test --validate
   ```

## Listing regions

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
```

Output:
```
Named regions in profiles/retroarch_menu_test.yaml:
  Total: 2

  full_screen:
    left:   0
    top:    0
    width:  1366
    height: 768
    box:    (0, 0, 1366, 768)

  menu_area:
    left:   200
    top:    100
    width:  966
    height: 568
    box:    (200, 100, 1166, 668)
```

Validate bounds against the actual monitor:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test --validate --monitor-index 1
```

## Capturing a region by name

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region menu_area
```

Creates:

```
logs/screenshots/menu_area-20260629-140000.png
logs/screenshots/menu_area-20260629-140000.json
```

The JSON sidecar includes the region name, coordinates, monitor index, timestamp, and the config path.

## Capturing with CLI coordinates (legacy fallback)

The old `--left --top --width --height` overrides still work for ad-hoc captures and bypass named regions entirely:

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --left 200 --top 100 --width 966 --height 568
```

## Analyzing a region

You can analyze a named region two ways:

### Fresh capture + analyze

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen
```

Output:
```
Region: full_screen
  Coordinate: left=0, top=0, width=1366, height=768
Image: logs/screenshots/full_screen-20260629-140100.png
Size: 1366x768
Mode: RGB
File size: 1048576 bytes
Channel means (R,G,B): 0.345, 0.456, 0.567
Channel extrema (R,G,B): [(0, 255), (0, 255), (0, 255)]
```

### Analyze an already-captured image

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region menu_area --image "logs/screenshots/menu_area-20260629-140000.png"
```

### JSON output

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen --json
```

## Where regions are used

Regions are defined in:

- `config/default.yaml` (shared defaults)
- `profiles/_template.yaml` (commented-out example)
- `profiles/retroarch_menu_test.yaml` (active example)

They are consumed by:

- `scripts/list_regions.py`
- `scripts/capture_region.py`
- `scripts/analyze_region.py`

## What regions do NOT do

- Regions cannot trigger controller input.
- Regions cannot run OCR or template matching.
- Regions cannot make decisions.
- Regions cannot chain or cascade.
- Regions are purely coordinate labels for diagnostic capture and analysis.

## Acceptance checklist

- [ ] Regions validate shape and positive dimensions.
- [ ] Regions can be listed by name.
- [ ] Regions can be captured by name, producing PNG + JSON sidecar.
- [ ] Region crops fit within monitor bounds (validated on request).
- [ ] Existing `--left --top --width --height` CLI overrides still work.
- [ ] Region analysis works with both fresh capture and existing images.
- [ ] Documentation explains calibration and safety boundaries.

## Future phases

- **Phase 10**: region catalogs — multiple named region sets for different emulator layouts or games.
- **Phase 11**: diagnostic overlays — draw region boxes and labels onto saved screenshots.
- **Phase 12**: baseline snapshots — compare current region crops against approved baselines.
- **Phase 13**: threshold checks — numeric pass/fail on region metrics.
