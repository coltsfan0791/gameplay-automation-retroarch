# Project Audit and Roadmap

This document audits the current state of the RetroArch gameplay automation project and lays out the remaining phases in a safe order.

The core rule is simple: build observation and reliability before autonomy. Do not let screenshots control input until the lower layers are stable, validated, logged, and reversible.

## Current status summary

| Phase | Status | Result |
|---|---:|---|
| Phase 1 | Complete | Repository scaffold and adapter-oriented architecture. |
| Phase 2 | Complete | YAML-driven scripted playback. |
| Phase 3 | Complete | Expanded virtual controller action support. |
| Phase 4 | Complete | Macro quality-of-life: named macros, waits, repeats, chords. |
| Phase 5 | Complete | Profile library, profile discovery, dry-run/show-events, all-profile validation. |
| Phase 6 | Complete | Safety/reliability layer: countdown, max runtime, safe stop, logging statuses. |
| Phase 7 | Complete | Screenshot/perception foundation using `mss`. |
| Phase 8 | Complete | Read-only image diagnostics using Pillow: stats, crop, compare, before/after reports. |

## Audit findings

### Strengths

1. The project has a clean separation between input, scheduling, scenarios, and perception.
2. Live playback is guarded by countdowns, max runtime, Ctrl+C handling, and best-effort button release.
3. Profile expansion is testable without pressing input through dry-run and validation commands.
4. Screenshot capture is isolated from decision logic.
5. Image diagnostics are read-only and cannot drive gameplay.
6. Logs and diagnostic screenshots are ignored by Git, keeping the repository code-focused.
7. Local testing has already verified validation, screenshot capture, image stats, cropping, and before/after comparison.

### Fixes applied during audit

- Simplified before/after snapshot filename prefixes.
  - Before: `sample_frame_before_YYYYMMDD-HHMMSS-YYYYMMDD-HHMMSS.png`
  - After: `sample_frame_before-YYYYMMDD-HHMMSS.png`

### Known local-only issue

The user has a stash named:

```text
stash@{0}: On main: local files before phase 8 pull
```

That stash contains local files that were blocking a fast-forward pull:

```text
.vscode/settings.json
Downloads/RetroArch bot creation.html
Downloads/RetroArch bot creation_files/inline-styles.css
README.md local edit
```

Recommendation: leave the stash alone unless those files are needed. Do not pop it blindly onto `main` because it may reintroduce README conflicts.

## Completed phases: detailed proofcheck

### Phase 1: scaffold

Purpose: create a repository layout that can grow without becoming a pile of one-off scripts.

Proofcheck:

- Core contracts live under `src/core/`.
- Input backend code is isolated under `src/input/`.
- Scenario/runner code is isolated under `src/scenarios/`.
- Perception code later landed under `src/perception/`, which fits the original architecture.

Optimization note: keep all future features behind modules and CLIs rather than stuffing everything into `scripted_playback.py`.

### Phase 2: YAML macro runner

Purpose: make playback data-driven.

Proofcheck:

- Config lives in YAML.
- The runner still supports the older direct `playback.sequence` format.
- Log paths are derived safely.

Optimization note: legacy support is useful, but new examples should prefer named macros.

### Phase 3: expanded virtual controller actions

Purpose: support a practical controller surface.

Proofcheck:

- Face buttons, D-pad, menu/back/select aliases, shoulders, triggers, stick clicks, and analog directional aliases are supported.
- Stage 3 action expansion was validated through profile dry-runs and later all-profile validation.

Optimization note: future action validation should compare expanded events against backend-supported actions before live playback.

### Phase 4: macro quality-of-life

Purpose: make route/profile authoring manageable.

Proofcheck:

- Named macros work.
- `use_macro` references work.
- Repeats expand correctly.
- Wait steps are explicit.
- Chords press together and release in reverse order.
- Recursive macro references are rejected.

Optimization note: add a future profile linter that warns about too many repeats, very long holds, or risky buttons.

### Phase 5: profiles and examples

Purpose: move from one config file to reusable profiles.

Proofcheck:

- `--list-profiles` works.
- `--profile` and `--config` are separate.
- `--dry-run` and `--show-events` make testing safe.
- `validate_all_profiles.py` validated every current profile locally.

Optimization note: add named screen regions next so profiles can define what parts of the screen matter without hardcoding coordinates into commands.

### Phase 6: safety and reliability

Purpose: make live playback safer before adding perception.

Proofcheck:

- Max runtime guard exists.
- Ctrl+C becomes a controlled stop.
- Pressed buttons are released in failure paths.
- Optional Windows terminal stop key exists.
- Log rows can include `ok`, `stopped`, or `error`.
- Preflight summary displays the selected config, profile risk, event summary, and safety settings.

Optimization note: future safety improvements should include action allowlists/denylists per profile risk level.

### Phase 7: perception foundation

Purpose: capture screenshots without interpreting them.

Proofcheck:

- `mss` dependency installed and capture tested locally.
- `capture_sample_frame.py --list-monitors` exists.
- Profile/config screenshot settings are parsed and validated.
- Captures save PNG and JSON metadata sidecar.
- Metadata explicitly says no OCR and no decision logic.

Optimization note: the next region system should sit above this and reuse the same screenshot config rather than creating a separate capture path.

### Phase 8: image diagnostics

Purpose: inspect saved screenshots without controlling gameplay.

Proofcheck:

- Pillow dependency installed locally.
- `analyze_image.py --image` returns stats.
- Crop output works.
- Before/after snapshot runner works.
- Before/after comparison report measured screen changes after macro playback.
- Local result proved a real measurable screen delta:
  - changed pixels: `9697`
  - changed percent: `0.924327`
  - mean absolute difference: `0.945104`

Optimization note: do not jump directly from this to OCR. First create stable named regions.

## Remaining phases: optimized plan

### Phase 9: named screen regions

Goal: stop using one-off coordinates in command lines.

Add config like:

```yaml
regions:
  full_screen:
    left: 0
    top: 0
    width: 1366
    height: 768
  top_left:
    left: 0
    top: 0
    width: 320
    height: 240
  dialog_box:
    left: 100
    top: 520
    width: 1160
    height: 180
```

Add commands:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region dialog_box
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region top_left
```

Acceptance criteria:

- Regions validate bounds.
- Regions can be listed.
- Regions can be captured by name.
- Region crops write PNG and JSON metadata.
- Existing `--left --top --width --height` overrides still work.

Still not included:

- OCR
- Template matching
- Decisions

### Phase 10: region catalogs per emulator/game layout

Goal: make different games/layouts use different named region sets.

Add:

```yaml
region_sets:
  gba_4x3:
    full_game:
      left: 0
      top: 0
      width: 960
      height: 720
    dialog_box:
      left: 40
      top: 500
      width: 880
      height: 180
  retroarch_menu:
    menu_area:
      left: 150
      top: 80
      width: 1000
      height: 620
```

Acceptance criteria:

- Profile can select a region set.
- Region names resolve from the active set.
- Validation catches missing or duplicate names.
- Docs show how to calibrate a region set from screenshots.

### Phase 11: diagnostic overlays

Goal: visually confirm region boxes without OCR.

Add commands:

```powershell
python ".\scripts\draw_region_overlay.py" --profile retroarch_menu_test
python ".\scripts\draw_region_overlay.py" --profile retroarch_menu_test --region dialog_box
```

Acceptance criteria:

- Output image shows rectangles and region labels.
- Overlay output is ignored by Git.
- Works on screenshots already saved under `logs/screenshots/`.

Still not included:

- Reading text
- Detecting objects
- Acting on the overlay

### Phase 12: baseline snapshots and drift checks

Goal: compare current screenshots against manually approved baseline screenshots.

Add:

```powershell
python ".\scripts\save_baseline.py" --profile retroarch_menu_test --region menu_area --name retroarch_menu_open
python ".\scripts\compare_baseline.py" --profile retroarch_menu_test --baseline retroarch_menu_open
```

Acceptance criteria:

- Baseline metadata records profile, region, size, timestamp, and notes.
- Comparison fails clearly if image sizes differ.
- Comparison produces a JSON report.
- No input is sent by baseline comparison tools.

### Phase 13: threshold-only screen checks

Goal: add simple measurable checks without semantic interpretation.

Examples:

```yaml
checks:
  menu_changed:
    region: menu_area
    metric: changed_percent
    op: gt
    value: 0.5
```

Acceptance criteria:

- Checks only compare numbers from diagnostics.
- Checks cannot press buttons.
- Checks print pass/fail and write JSON.

This is the last phase before any real screen interpretation.

### Phase 14: template matching foundation

Goal: identify small manually supplied UI images inside named regions.

Examples:

```powershell
python ".\scripts\match_template.py" --profile retroarch_menu_test --region menu_area --template templates\retroarch_back_icon.png
```

Acceptance criteria:

- Template files are local and user-provided.
- Match results are diagnostic only.
- Output includes confidence, bounding box, and region name.
- No input is pressed based on match results.

### Phase 15: conditional wait diagnostics

Goal: wait for a measurable visual condition and then report pass/fail.

Examples:

```powershell
python ".\scripts\wait_for_template.py" --profile retroarch_menu_test --region menu_area --template templates\menu_ready.png --timeout 5
```

Acceptance criteria:

- Timeouts are mandatory.
- No input is pressed by the wait command.
- Results are logged.
- Safety docs explicitly warn that this is still not a gameplay decision loop.

### Phase 16: guarded action gates

Goal: allow exactly one predeclared action after a verified condition.

Example:

```yaml
gates:
  close_menu_when_ready:
    wait_for:
      check: menu_ready
      timeout_seconds: 5
    then:
      action: back
      hold_seconds: 0.08
```

Acceptance criteria:

- Only one action or one named macro can be triggered.
- Max runtime still applies.
- Gate actions require dry-run preview.
- Gate actions require profile risk level `medium` or higher.
- Gate actions log condition result and dispatched action.

This is the first controlled bridge from vision into action.

### Phase 17: state machine runner

Goal: formalize routes as states instead of loose macro chains.

Example states:

```yaml
states:
  open_menu:
    do: open_menu_macro
    expect: menu_ready
    on_success: move_cursor
    on_failure: stop
```

Acceptance criteria:

- Every state has timeout.
- Every state has max retry count.
- Every failure path stops safely.
- State transitions are logged.
- No unbounded loops.

### Phase 18: save-state and recovery integration

Goal: optionally coordinate emulator save-state workflows for offline testing only.

Acceptance criteria:

- User explicitly configures save/load hotkeys.
- Recovery is disabled by default.
- Destructive or irreversible actions require high-risk profile marking.
- Recovery never touches online games or networked gameplay.

### Phase 19: OCR experiments

Goal: test OCR only after regions, overlays, baselines, thresholds, and gates are stable.

Acceptance criteria:

- OCR is region-scoped.
- OCR is diagnostic by default.
- OCR text is logged with confidence and source region.
- OCR cannot trigger input until guarded action gates support it.

### Phase 20: autonomous route experiments

Goal: limited offline-only route automation with explicit risk controls.

Acceptance criteria:

- Offline emulator only.
- No online multiplayer, no anti-cheat bypass, no competitive automation.
- Full dry-run planning output.
- Human-readable state transitions.
- Hard stop key, max runtime, max transitions, max retries.
- Every action is logged with the reason it was taken.

## Agent-mode working rules

When building future phases, use this loop:

1. Create a branch from `main`.
2. Keep one phase per PR.
3. Add code.
4. Add docs.
5. Add local test commands in the PR body.
6. Ask the user to run the commands.
7. Merge only after user says the checks passed.
8. Keep output files under `logs/` and ignored by Git.
9. Do not add autonomy until diagnostics are stable.
10. Do not add online-game automation or anti-cheat workarounds.

## Recommended next PR

Next branch:

```text
phase9-named-screen-regions
```

Minimum files likely needed:

```text
src/perception/regions.py
scripts/list_regions.py
scripts/capture_region.py
scripts/analyze_region.py
docs/REGIONS.md
PHASE9_NOTES.md
README.md update
config/default.yaml region examples
profiles/_template.yaml region examples
```

Do not add OCR in Phase 9.
