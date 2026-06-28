# Phase 7 - Observation / Perception Foundation

Phase 7 adds basic screenshot capture so the project can observe RetroArch or the desktop in a controlled, diagnostic way.

## Scope

Included:

- `mss` screenshot dependency.
- `src/perception/` package.
- `MssScreenshotBackend` for PNG capture.
- JSON sidecar metadata for every captured frame.
- `scripts/capture_sample_frame.py` CLI.
- Monitor listing.
- Config-driven monitor and region capture.
- Validation of `perception.screenshot` settings.
- Git ignore rules for diagnostic PNG/JSONL output.

Not included:

- OCR
- Template matching
- Image recognition
- Conditional wait-until-screen logic
- Autonomous decisions
- Route correction
- Save-state orchestration

## Install

```powershell
python -m pip install -r requirements.txt
```

## List monitors

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
```

Monitor `0` is usually the full virtual desktop. Monitor `1` is usually the primary monitor.

## Capture sample frame

```powershell
python ".\scripts\capture_sample_frame.py"
```

or:

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

## Capture a specific region

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test --left 0 --top 0 --width 1280 --height 720
```

## Output

By default captures go to:

```text
logs/screenshots/
```

Each capture creates:

```text
sample_frame-YYYYMMDD-HHMMSS.png
sample_frame-YYYYMMDD-HHMMSS.json
```

The JSON sidecar records monitor/region/size/config metadata and explicitly marks that the output contains no OCR or decision logic.

## Config

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

Example region:

```yaml
region:
  left: 0
  top: 0
  width: 1280
  height: 720
```

## Validation

```powershell
python ".\scripts\validate_config.py" retroarch_menu_test
python ".\scripts\validate_all_profiles.py"
```

## Why no OCR yet?

The screenshot layer must be stable first. Once captures are reliable, the next phase can add lightweight observation utilities such as image dimensions, region crops, and later template matching/OCR.
