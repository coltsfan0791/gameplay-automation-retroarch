# Gameplay Automation - RetroArch

This folder contains a staged automation framework for controlling RetroArch externally.

## Architecture

- `src/core/interfaces.py`: shared contracts for input adapters and perception adapters.
- `src/core/scheduler.py`: deterministic frame-timed control loop.
- `src/input/vgamepad_backend.py`: Windows virtual gamepad backend using `vgamepad`.
- `src/scenarios/scripted_playback.py`: YAML-driven input sequence replay runner.
- `config/default.yaml`: timing, backend, macro, and logging defaults.
- `logs/`: runtime JSONL traces for validation and replay comparison.

## Design goals

- Keep platform-specific code isolated behind adapter interfaces.
- Use a monotonic scheduler for repeatable timing.
- Log all dispatched actions with timestamps for drift analysis.
- Keep macro authoring in YAML instead of editing Python for every route.

## Quick start

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Validate the YAML config without sending controller input:

```powershell
python ".\scripts\validate_config.py"
```

3. Run scripted playback:

```powershell
python "g:/VSC projects/gameplay-automation-retroarch/src/scenarios/scripted_playback.py"
```

4. Inspect logs in `g:/VSC projects/gameplay-automation-retroarch/logs/`.

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

## Safety / repo hygiene

Do not commit ROMs, BIOS files, save states, copyrighted game files, or private logs. Keep the repository code-only.
