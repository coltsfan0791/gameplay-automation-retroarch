# Profile Schema

Profiles are YAML files loaded by `src/scenarios/scripted_playback.py`.

A profile may be passed by name:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement
```

or by path:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile profiles\gba_basic_movement.yaml
```

## Top-level shape

```yaml
profile:
  name: My profile
  description: Short explanation of what this macro does.
  risk_level: low

runtime:
  target_fps: 60
  max_jitter_ms: 4

safety:
  countdown_seconds: 3
  max_runtime_seconds: 30
  enable_console_stop: true
  stop_key: q
  require_enter: false

logging:
  enabled: true
  folder: logs
  file_prefix: my_profile

playback:
  run: my_macro
  macros:
    my_macro:
      - action: a
        hold_seconds: 0.08
```

## `profile`

```yaml
profile:
  name: GBA basic movement
  description: Moves a GBA-style character and taps A/B.
  risk_level: low
```

`risk_level` must be one of:

```text
low, medium, high
```

Risk level is informational for now. Use it honestly so dangerous/longer profiles are easy to recognize before playback.

## `runtime`

```yaml
runtime:
  target_fps: 60
```

`target_fps` controls the scheduler cadence. It must be a positive integer.

## `safety`

```yaml
safety:
  countdown_seconds: 3
  max_runtime_seconds: 30
  enable_console_stop: true
  stop_key: q
  require_enter: false
```

Fields:

- `countdown_seconds`: delay before playback starts so you can focus RetroArch.
- `max_runtime_seconds`: hard stop guard for runaway profiles.
- `enable_console_stop`: enables the optional Windows terminal stop key.
- `stop_key`: single-character terminal stop key. Default is `q`.
- `require_enter`: requires Enter before countdown/playback begins.

`Ctrl+C` is always the universal emergency stop.

## `logging`

```yaml
logging:
  enabled: true
  folder: logs
  file_prefix: my_profile
```

If `file_prefix` is omitted, the runner derives the log prefix from the selected config/profile filename.

Log rows use status values:

```text
ok
stopped
error
```

Stopped/error rows also include `error_type` and `error`.

## `playback.run`

```yaml
playback:
  run: main_route
```

Selects a named macro from `playback.macros`.

## `playback.macros`

```yaml
playback:
  macros:
    main_route:
      - action: start
        hold_seconds: 0.08
```

Macros are reusable named sequences. A macro can call another macro with `use_macro`.

## Direct action step

```yaml
- action: a
  hold_seconds: 0.08
```

`hold_seconds` is optional and defaults to `0.05`.

## Wait step

```yaml
- wait_seconds: 0.25
```

The scheduler logs waits as action `wait`.

## Repeat step

```yaml
- repeat: 3
  sequence:
    - action: down
      hold_seconds: 0.08
    - wait_seconds: 0.08
```

`repeat` must be an integer from 1 to 10,000.

## Chord step

```yaml
- chord:
    - lb
    - rb
  hold_seconds: 0.10
```

The scheduler presses all chord actions, flushes, holds, then releases them in reverse order. Chords are logged as plus-joined action strings such as `lb+rb`.

## Macro call step

```yaml
- use_macro: open_menu
```

Alias also supported:

```yaml
- macro: open_menu
```

Recursive macro calls are rejected.

## Legacy direct sequence

Phase 2 style remains supported:

```yaml
playback:
  sequence:
    - action: a
      hold_seconds: 0.08
```

If `playback.run` is present, it takes priority over `playback.sequence`.

## Validate

Validate one profile:

```powershell
python ".\scripts\validate_config.py" gba_basic_movement --show-events
```

Validate all profiles:

```powershell
python ".\scripts\validate_all_profiles.py"
```

## Run with safety overrides

```powershell
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement --no-countdown
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement --max-runtime-seconds 10
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement --require-enter
```
