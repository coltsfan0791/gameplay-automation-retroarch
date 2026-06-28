# Phase 6 - Safety and Reliability

Phase 6 adds safety controls before moving into computer vision, screenshots, OCR, or autonomous decision-making.

## Why this phase matters

Before a bot can react to the screen, it needs hard guardrails:

- Stop quickly.
- Avoid runaway loops.
- Give the user time to focus the emulator window.
- Release buttons even when playback fails.
- Log failures clearly.
- Validate profile safety metadata before playback.

## Included

### Scheduler safety

- Guarded waits and holds.
- `max_runtime_seconds` hard stop.
- Optional stop callback.
- `Ctrl+C` converted into a safe stop.
- Best-effort release of pressed buttons during failures.
- Error and stopped rows in JSONL logs.

### Runner safety

- Preflight summary before playback.
- Profile name, description, and risk level display.
- Countdown before input starts.
- Optional Enter confirmation.
- Optional Windows console stop key, default `q`.
- CLI overrides for countdown/runtime/stop behavior.

### Profile safety metadata

Profiles can now declare:

```yaml
profile:
  name: RetroArch menu test
  description: Opens a menu, wiggles through entries, and backs out.
  risk_level: low

safety:
  countdown_seconds: 3
  max_runtime_seconds: 30
  enable_console_stop: true
  stop_key: q
  require_enter: false
```

### Validation safety

Both validators now check profile metadata and safety settings:

```powershell
python ".\scripts\validate_config.py" retroarch_menu_test --show-events
python ".\scripts\validate_all_profiles.py"
```

## CLI examples

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --no-countdown
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --countdown-seconds 5
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --max-runtime-seconds 10
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --require-enter
```

## Emergency stop behavior

- `Ctrl+C` is always available from the terminal.
- On Windows, the optional console stop key works when the terminal has focus.
- Default stop key is `q`.
- The scheduler releases buttons it pressed before stopping.

## JSONL status values

Logs now use:

```text
ok
stopped
error
```

Stopped/error rows may include:

```text
error_type
error
```

## Not included yet

- Computer vision
- OCR
- Screenshot capture
- Conditional waits
- Save-state orchestration
- Route recovery
- State-machine profiles

Those come after safety is stable.
