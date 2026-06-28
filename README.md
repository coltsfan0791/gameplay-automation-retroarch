# Gameplay Automation - RetroArch

This folder contains a staged automation framework for controlling RetroArch externally.

## Architecture

- `src/core/interfaces.py`: shared contracts for input adapters and perception adapters.
- `src/core/scheduler.py`: deterministic frame-timed control loop.
- `src/input/vgamepad_backend.py`: Windows virtual gamepad backend using `vgamepad`.
- `src/scenarios/scripted_playback.py`: predefined input sequence replay runner.
- `config/default.yaml`: timing, backend, and mapping defaults.
- `logs/`: runtime JSONL traces for validation and replay comparison.

## Design goals

- Keep platform-specific code isolated behind adapter interfaces.
- Use a monotonic scheduler for repeatable timing.
- Log all dispatched actions with timestamps for drift analysis.

## Quick start

1. Install dependencies:

```powershell
pip install vgamepad
```

2. Run scripted playback:

```powershell
python "g:/VSC projects/gameplay-automation-retroarch/src/scenarios/scripted_playback.py"
```

3. Inspect logs in `g:/VSC projects/gameplay-automation-retroarch/logs/`.
