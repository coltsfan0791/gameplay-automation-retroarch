# Phase 4 - Macro Quality-of-Life

Phase 4 improves authoring YAML macros without adding computer vision or perception yet.

## Included

- Named macros under `playback.macros`.
- `playback.run` to choose which macro to execute.
- Backward compatibility with direct `playback.sequence` from Phase 2.
- `wait_seconds` steps for pauses between inputs.
- `repeat` blocks for repeated mini-sequences.
- `chord` blocks for pressing multiple actions together.
- Config validation helper that expands macros without sending controller input.

## Not included yet

- Computer vision
- OCR
- Screenshot capture
- Conditional waits such as wait-until-menu-appears
- Save-state orchestration
- ROM/game automation profiles
- Variable trigger strength or analog magnitude from YAML

## Supported YAML shapes

### Direct action

```yaml
- action: a
  hold_seconds: 0.08
```

### Wait

```yaml
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

```yaml
- chord:
    - lb
    - rb
  hold_seconds: 0.10
```

### Named macro

```yaml
playback:
  run: menu_wiggle_demo
  macros:
    menu_wiggle_demo:
      - action: start
        hold_seconds: 0.08
```

## Validate without pressing buttons

```powershell
python ".\scripts\validate_config.py"
```

## Run macro playback

```powershell
python "G:\VSC projects\gameplay-automation-retroarch\src\scenarios\scripted_playback.py"
```
