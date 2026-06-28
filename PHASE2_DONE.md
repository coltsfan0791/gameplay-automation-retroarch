# Phase 2 Complete - YAML Macro Playback

Phase 2 turns the original hardcoded RetroArch playback script into a config-driven macro runner.

## What Phase 2 does

- Loads `config/default.yaml` with `yaml.safe_load`.
- Reads `runtime.target_fps` from config.
- Reads `logging.enabled`, `logging.folder`, and `logging.file_prefix` from config.
- Converts `playback.sequence` into `ActionEvent` objects.
- Falls back to the original demo sequence when `playback.sequence` is missing or empty.
- Fails clearly when malformed sequence entries are provided.
- Keeps direct script execution working from the scenarios folder.

## Files involved

```text
requirements.txt
config/default.yaml
src/scenarios/scripted_playback.py
```

## Verify

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
python -m pip install -r requirements.txt
python "G:\VSC projects\gameplay-automation-retroarch\src\scenarios\scripted_playback.py"
Get-ChildItem ".\logs" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```
