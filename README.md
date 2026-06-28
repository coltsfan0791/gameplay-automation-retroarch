# Gameplay Automation - RetroArch

This folder contains a staged automation framework for controlling RetroArch externally.

## Architecture

- `src/core/interfaces.py`: shared contracts for input adapters and perception adapters.
- `src/core/scheduler.py`: deterministic frame-timed control loop with safety guards.
- `src/input/vgamepad_backend.py`: Windows virtual gamepad backend using `vgamepad`.
- `src/scenarios/scripted_playback.py`: YAML-driven input sequence/profile replay runner.
- `config/default.yaml`: default timing, macro, safety, and logging config.
- `profiles/`: reusable playback profile YAML files.
- `logs/`: runtime JSONL traces for validation and replay comparison.

## Design goals

- Keep platform-specific code isolated behind adapter interfaces.
- Use a monotonic scheduler for repeatable timing.
- Log all dispatched actions with timestamps for drift analysis.
- Keep macro authoring in YAML instead of editing Python for every route.
- Keep profiles code-only: no ROMs, BIOS files, save states, screenshots, or private logs.
- Prefer safe, testable, reversible steps before adding perception or autonomy.

## Quick start

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. List available profiles:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
```

3. Dry-run a profile without pressing controller buttons:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
```

4. Run a profile with normal safety prompts/countdown:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

5. Inspect logs in `logs/`.

## Default config mode

Running without arguments still uses `config/default.yaml`:

```powershell
python ".\src\scenarios\scripted_playback.py"
```

You can also point directly to a config file:

```powershell
python ".\src\scenarios\scripted_playback.py" --config config/default.yaml
```

## Phase 2: config-driven playback

The legacy playback sequence format still works:

```yaml
playback:
  sequence:
    - action: a
      hold_seconds: 0.08
    - action: right
      hold_seconds: 0.10
```

The runner also reads `runtime.target_fps` and logging settings from the same file.

## Phase 3: expanded controller actions

The `vgamepad` backend supports face buttons, D-pad, Start/Menu, Back/Select/View, shoulders, triggers, stick clicks, and basic analog stick direction aliases.

Use this helper to list supported action names:

```powershell
python ".\scripts\list_supported_actions.py"
```

## Phase 4: macro quality-of-life

Phase 4 adds richer YAML macro authoring while preserving the old `playback.sequence` style.

### Named macro

```yaml
playback:
  run: menu_wiggle_demo
  macros:
    menu_wiggle_demo:
      - action: start
        hold_seconds: 0.08
      - wait_seconds: 0.25
```

### Repeat

```yaml
- repeat: 3
  sequence:
    - action: down
      hold_seconds: 0.08
    - wait_seconds: 0.08
```

### Chord

A chord presses multiple actions together, holds them, then releases them in reverse order.

```yaml
- chord:
    - lb
    - rb
  hold_seconds: 0.10
```

Internally, the scheduler logs that chord as `lb+rb`.

### Wait

```yaml
- wait_seconds: 0.50
```

Internally, the scheduler logs that wait as action `wait`.

## Phase 5: profiles and examples

Phase 5 turns one config file into a small profile library.

### Run by profile name

```powershell
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement
```

### Run by profile path

```powershell
python ".\src\scenarios\scripted_playback.py" --profile profiles\gba_basic_movement.yaml
```

### Dry-run before pressing anything

```powershell
python ".\src\scenarios\scripted_playback.py" --profile pokemon_menu_nav --dry-run --show-events
```

### Validate one profile

```powershell
python ".\scripts\validate_config.py" pokemon_menu_nav --show-events
```

### Validate every profile

```powershell
python ".\scripts\validate_all_profiles.py"
```

## Phase 6: safety and reliability

Phase 6 adds runtime safety controls before any computer vision or autonomous logic.

### Safety config

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

### Safety CLI overrides

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --no-countdown
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --countdown-seconds 5
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --max-runtime-seconds 10
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --require-enter
```

### Emergency stop

- `Ctrl+C` is the universal emergency stop.
- On Windows, the optional console stop key defaults to `q` while the terminal is focused.
- The scheduler releases any buttons it pressed before stopping.
- Log rows now include `status: ok`, `status: stopped`, or `status: error`.

## Included profiles

```text
profiles/generic_controller_test.yaml
profiles/retroarch_menu_test.yaml
profiles/gba_basic_movement.yaml
profiles/pokemon_menu_nav.yaml
profiles/analog_stick_trigger_test.yaml
```

## Safety / repo hygiene

Do not commit ROMs, BIOS files, save states, copyrighted game files, screenshots, or private logs. Keep the repository code-only.
