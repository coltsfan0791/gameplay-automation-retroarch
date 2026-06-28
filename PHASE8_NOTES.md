# Phase 8 - Image Diagnostics

Phase 8 adds read-only image diagnostics on top of Phase 7 screenshot capture.

## Scope

Included:

- Pillow dependency.
- `src/perception/image_diagnostics.py`.
- Image statistics: size, mode, file size, channel means, and channel extrema.
- Cropping saved images to diagnostic regions.
- Comparing two same-sized screenshots.
- Before/after profile snapshot runner.
- JSON report output.

Not included:

- OCR
- Template matching
- Object detection
- Image-based decisions
- Conditional wait-until-screen logic
- Autonomous recovery
- Save-state orchestration

## Install

```powershell
python -m pip install -r requirements.txt
```

## Stats

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
```

## Crop

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png" --crop-output "logs\screenshots\crop.png" --left 0 --top 0 --width 320 --height 240
```

## Compare

```powershell
python ".\scripts\analyze_image.py" --baseline "logs\screenshots\before.png" --candidate "logs\screenshots\after.png" --json-output "logs\screenshots\comparison.json"
```

Comparison returns:

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

## Before/after profile snapshots

```powershell
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

This captures a before frame, runs the selected profile through the existing scheduler/safety layer, captures an after frame, then writes a comparison JSON report.

The report does not affect gameplay. It is diagnostic only.

## Why still no autonomy?

This phase teaches the project to measure what changed on screen. It does not yet teach the project what the screen means or what to do next.

The next safe step would be a small region catalog: named screen regions like `menu_area`, `player_area`, and `dialog_box`, plus tooling to crop those regions consistently.
