# Stage 3 - Controller Expansion

Stage 3 expands the virtual Xbox 360 controller backend while keeping the same Stage 2 YAML macro runner.

## Scope

Included:

- Start/Menu
- Back/Select/View
- LB/RB and L1/R1 aliases
- Left/right stick click aliases
- LT/RT trigger press/release actions
- Left/right analog stick directional actions
- Better unsupported-action error messages
- `supported_actions()` helper for debugging

Not included yet:

- Computer vision
- OCR
- Screenshot perception
- Conditional wait-until-screen logic
- Multi-button chord support
- Variable analog strength per YAML step

Those belong in later phases.

## Files changed

```text
src/input/vgamepad_backend.py
config/default.yaml
```

The Stage 2 `scripted_playback.py` can stay as-is after applying the Phase 2 final patch.

## Recommended git flow

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
git checkout main
git pull
git checkout stage3-controller-expansion
```

Run:

```powershell
python "G:\VSC projects\gameplay-automation-retroarch\src\scenarios\scripted_playback.py"
```

## Supported action names

Face buttons:

```text
a, b, x, y
```

D-pad:

```text
up, down, left, right
```

System:

```text
start, menu, back, select, view
```

Shoulders:

```text
lb, l1, left_shoulder, rb, r1, right_shoulder
```

Stick clicks:

```text
ls, l3, left_thumb, left_stick_click, rs, r3, right_thumb, right_stick_click
```

Triggers:

```text
lt, l2, left_trigger, rt, r2, right_trigger
```

Analog stick directions:

```text
left_stick_up, left_stick_down, left_stick_left, left_stick_right
ls_up, ls_down, ls_left, ls_right
right_stick_up, right_stick_down, right_stick_left, right_stick_right
rs_up, rs_down, rs_left, rs_right
```
