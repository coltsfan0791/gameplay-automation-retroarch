# Quickstart

This is the shortest safe path to run the project on Windows.

## 1) Open project root

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
```

## 2) Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3) Validate configuration

```powershell
python ".\scripts\validate_config.py" --config config/default.yaml
python ".\scripts\validate_all_profiles.py" --profiles profiles
```

## 4) Inspect profiles and dry-run first

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
```

## 5) Capture one diagnostic frame

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

## 6) Run live playback only after dry-run

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

## Safety reminders

- Keep RetroArch window focused during playback.
- `Ctrl+C` is the emergency stop.
- Optional terminal stop key defaults to `q` when enabled.
- Use short, reversible profiles first.
