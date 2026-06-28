# Perception Foundation

Phase 7 adds screenshot capture only. It does not add OCR, image recognition, template matching, conditional waits, or autonomous decisions.

## Commands

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

List monitors:

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
```

Capture with default config:

```powershell
python ".\scripts\capture_sample_frame.py"
```

Capture with a profile:

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

Capture with an explicit region:

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test --left 0 --top 0 --width 1280 --height 720
```

## Monitor indexes

The `mss` backend reports monitors like this:

```text
0: virtual desktop
1: primary monitor, usually
2+: additional monitors
```

Use `--list-monitors` to confirm your own layout.

## Screenshot config

```yaml
perception:
  screenshot:
    enabled: true
    backend: mss
    monitor_index: 1
    output_folder: logs/screenshots
    file_prefix: sample_frame
    region: null
```

## Region config

```yaml
region:
  left: 0
  top: 0
  width: 1280
  height: 720
```

Coordinates use desktop pixels. On multi-monitor layouts, `left` or `top` may be negative depending on how Windows arranges the displays.

## Output files

A capture writes both:

```text
*.png
*.json
```

The JSON sidecar includes:

```text
timestamp_utc
image_path
width
height
monitor
region
phase
contains_ocr
contains_decision_logic
config_path
script
backend
```

## Git hygiene

Diagnostic screenshots and logs stay local and are ignored by Git.

Do not commit screenshots unless you have checked that they contain no private information and no copyrighted game content that should not be published.
