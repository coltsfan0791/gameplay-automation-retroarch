# Image Diagnostics

Phase 8 adds read-only diagnostics for captured screenshots.

These tools do not perform OCR, template matching, object detection, or decision-making.

## Install

```powershell
python -m pip install -r requirements.txt
```

## Capture a screenshot first

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

## Image stats

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
```

The stats report includes:

```text
width
height
mode
file_size_bytes
channel_means
channel_extrema
```

## Crop

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png" --crop-output "logs\screenshots\crop.png" --left 0 --top 0 --width 320 --height 240
```

Crop coordinates are image pixels, not controller coordinates.

## Compare two images

```powershell
python ".\scripts\analyze_image.py" --baseline "logs\screenshots\before.png" --candidate "logs\screenshots\after.png"
```

Optional JSON report:

```powershell
python ".\scripts\analyze_image.py" --baseline "logs\screenshots\before.png" --candidate "logs\screenshots\after.png" --json-output "logs\screenshots\comparison.json"
```

Comparison fields:

```text
same_size
baseline_size
candidate_size
diff_bbox
mean_abs_diff
max_abs_diff
changed_pixels
changed_percent
```

If the images are different sizes, pixel comparison is skipped and `same_size` is false.

## Before/after profile snapshots

```powershell
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

The command does this:

1. Capture a before screenshot.
2. Run the selected profile through the normal scheduler and safety layer.
3. Capture an after screenshot.
4. Compare the before/after screenshots.
5. Save a JSON report under the configured screenshot output folder.

## Safety boundary

Image diagnostics are measurement only.

They do not decide which buttons to press.
They do not wait for menus.
They do not read text.
They do not identify game objects.
They do not modify saves or emulator state.

## Local output

By default outputs go under:

```text
logs/screenshots/
```

This folder is ignored by Git.
