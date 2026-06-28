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
runtime:
  target_fps: 60
  max_jitter_ms: 4

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

## `runtime`

```yaml
runtime:
  target_fps: 60
```

`target_fps` controls the scheduler cadence. It must be a positive integer.

## `logging`

```yaml
logging:
  enabled: true
  folder: logs
  file_prefix: my_profile
```

If `file_prefix` is omitted, the runner derives the log prefix from the selected config/profile filename.

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
