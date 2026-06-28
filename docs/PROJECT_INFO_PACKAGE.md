# RetroArch Gameplay Automation - Project Info Package

This is the single consolidated reference for the project. It combines the current state, completed phase history, local commands, safety rules, agent-mode workflow, remaining roadmap, and troubleshooting notes.

Use this file first when returning to the project after a break.

## Project identity

Repository:

```text
coltsfan0791/gameplay-automation-retroarch
```

Local path:

```powershell
G:\VSC projects\gameplay-automation-retroarch
```

Primary purpose:

```text
Offline RetroArch/emulator automation framework with safe, staged development.
```

Hard boundary:

```text
Offline emulator tooling only. No online multiplayer automation, no anti-cheat bypass, no hidden automation, no competitive-game botting.
```

## Current status

```text
Phase 1: scaffold complete
Phase 2: YAML macro runner complete
Phase 3: expanded controller backend complete
Phase 4: macro QoL complete
Phase 5: profiles and examples complete
Phase 6: safety and reliability complete
Phase 7: perception foundation complete
Phase 8: image diagnostics complete
Audit/roadmap optimization complete
Agent-mode playbook complete
Next: Phase 9 named screen regions
```

## Current core capabilities

The project can currently:

- Run controller input profiles through YAML.
- Expand named macros, waits, repeats, chords, and macro calls.
- Dry-run profiles without pressing buttons.
- Validate every profile.
- Use a Windows virtual Xbox 360 controller through `vgamepad`.
- Use a safety preflight, countdown, max runtime guard, Ctrl+C stop, optional terminal stop key, and best-effort button release.
- Capture screenshots with `mss`.
- Save PNG screenshots plus JSON metadata sidecars.
- Run read-only image diagnostics with Pillow.
- Crop saved screenshots.
- Compare two same-sized screenshots.
- Capture before/after screenshots around a normal profile run.
- Write comparison reports under `logs/screenshots/`.

The project cannot yet:

- Read text from the screen.
- Match templates.
- Recognize objects.
- Wait for visual conditions.
- Make decisions based on screenshots.
- Recover routes automatically.
- Run autonomous gameplay loops.

Those are intentionally deferred.

## Local sync commands

Use this after a PR has been merged:

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"

git checkout main
git pull
python -m pip install -r requirements.txt
python ".\scripts\validate_all_profiles.py"
```

## Local validation ladder

Run these in order when testing a fresh checkout or branch:

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"

python -m pip install -r requirements.txt
python ".\scripts\validate_all_profiles.py"
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

Then test image diagnostics with the actual PNG that was created:

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
```

Crop test:

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png" --crop-output "logs\screenshots\crop.png" --left 0 --top 0 --width 320 --height 240
```

Before/after profile snapshot test:

```powershell
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

Expected before/after filename pattern:

```text
sample_frame_before-YYYYMMDD-HHMMSS.png
sample_frame_after-YYYYMMDD-HHMMSS.png
sample_frame_before_after_report-YYYYMMDD-HHMMSS.json
```

## Local stash warning

A local stash may exist from the Phase 8 pull:

```text
stash@{0}: On main: local files before phase 8 pull
```

It contained:

```text
.vscode/settings.json
Downloads/RetroArch bot creation.html
Downloads/RetroArch bot creation_files/inline-styles.css
README.md local edit
```

Do not blindly pop it onto `main`. Inspect it first:

```powershell
git stash list
git stash show --stat stash@{0}
```

Leave it alone unless those files are needed.

## Repository structure

Important paths:

```text
config/default.yaml
profiles/
src/core/interfaces.py
src/core/scheduler.py
src/input/vgamepad_backend.py
src/perception/config.py
src/perception/screenshot_backend.py
src/perception/image_diagnostics.py
src/scenarios/scripted_playback.py
scripts/list_supported_actions.py
scripts/validate_config.py
scripts/validate_all_profiles.py
scripts/capture_sample_frame.py
scripts/analyze_image.py
scripts/capture_profile_snapshots.py
docs/
logs/
```

Generated runtime output goes under:

```text
logs/
logs/screenshots/
```

Those outputs are ignored by Git.

## Included profiles

```text
profiles/_template.yaml
profiles/generic_controller_test.yaml
profiles/retroarch_menu_test.yaml
profiles/gba_basic_movement.yaml
profiles/pokemon_menu_nav.yaml
profiles/analog_stick_trigger_test.yaml
```

## Completed phases

### Phase 1: scaffold

Goal:

```text
Create the project layout and adapter-oriented architecture.
```

Result:

- Core contracts under `src/core/`.
- Input backend under `src/input/`.
- Scenario runner under `src/scenarios/`.
- Later perception modules fit cleanly under `src/perception/`.

Proofcheck:

```text
The project did not become one giant script. New systems have clear homes.
```

### Phase 2: YAML macro runner

Goal:

```text
Move playback from hardcoded Python into YAML configuration.
```

Result:

- `config/default.yaml` drives runtime and playback.
- Legacy direct `playback.sequence` still works.
- Runtime and logging settings are read from config.

Proofcheck:

```text
Running without arguments still uses config/default.yaml.
```

### Phase 3: expanded controller backend

Goal:

```text
Make the virtual controller useful beyond A/B/D-pad.
```

Result:

Supported action families include:

- Face buttons: `a`, `b`, `x`, `y`.
- D-pad: `up`, `down`, `left`, `right`.
- Menu/system aliases: `start`, `menu`, `back`, `select`, `view`.
- Shoulders: `lb`, `rb`, `l1`, `r1`.
- Triggers: `lt`, `rt`, `l2`, `r2`.
- Stick clicks: `ls`, `rs`, `l3`, `r3`.
- Analog cardinal directions for left and right stick.

Useful command:

```powershell
python ".\scripts\list_supported_actions.py"
```

### Phase 4: macro quality-of-life

Goal:

```text
Make profile authoring easier and less repetitive.
```

Result:

- Named macros.
- Macro calls through `use_macro` / `macro`.
- Wait steps.
- Repeat blocks.
- Chords.
- Recursive macro calls rejected.

Example:

```yaml
playback:
  run: menu_wiggle_demo
  macros:
    menu_wiggle_demo:
      - action: start
        hold_seconds: 0.08
      - wait_seconds: 0.25
      - repeat: 2
        sequence:
          - action: down
            hold_seconds: 0.08
          - wait_seconds: 0.08
      - chord:
          - lb
          - rb
        hold_seconds: 0.10
```

### Phase 5: profiles and examples

Goal:

```text
Turn one config file into a reusable profile library.
```

Result:

- `profiles/` directory.
- Profile discovery.
- `--list-profiles`.
- `--profile` and `--config` support.
- Dry-run and show-events commands.
- Validate one profile or all profiles.

Commands:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement --dry-run --show-events
python ".\scripts\validate_config.py" pokemon_menu_nav --show-events
python ".\scripts\validate_all_profiles.py"
```

### Phase 6: safety and reliability

Goal:

```text
Make live playback safer before adding any perception layer.
```

Result:

- Preflight summary.
- Countdown.
- Optional Enter confirmation.
- Max runtime guard.
- Ctrl+C controlled stop.
- Optional Windows terminal stop key.
- Best-effort button release on stop/error.
- Log statuses: `ok`, `stopped`, `error`.

Safety config example:

```yaml
safety:
  countdown_seconds: 3
  max_runtime_seconds: 30
  enable_console_stop: true
  stop_key: q
  require_enter: false
```

Commands:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --no-countdown
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --max-runtime-seconds 10
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --require-enter
```

### Phase 7: perception foundation

Goal:

```text
Add screenshot capture only, without interpretation or decisions.
```

Result:

- `mss` dependency.
- Screenshot backend.
- Monitor listing.
- Full-monitor capture.
- Optional region capture.
- PNG output.
- JSON metadata sidecar.
- Screenshot config validation.

Commands:

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test --left 0 --top 0 --width 1280 --height 720
```

Screenshot config example:

```yaml
perception:
  screenshot:
    enabled: true
    backend: mss
    monitor_index: 1
    output_folder: logs/screenshots
    file_prefix: sample_frame
    region: null
```

### Phase 8: image diagnostics

Goal:

```text
Inspect saved screenshots without controlling gameplay.
```

Result:

- Pillow dependency.
- Image stats.
- Crop saved screenshots.
- Compare two screenshots.
- Before/after capture around a normal profile run.
- Comparison report JSON.

Commands:

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png" --crop-output "logs\screenshots\crop.png" --left 0 --top 0 --width 320 --height 240
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

Confirmed local test result from Phase 8:

```text
Changed pixels: 9697
Changed percent: 0.924327
Mean abs diff: 0.945104
```

Meaning:

```text
The project can measure that the screen changed after a macro. It still does not decide what to do based on that change.
```

## Audit and roadmap optimization

Goal:

```text
Proofcheck the completed work and make the remaining path explicit before Phase 9.
```

Result:

- `docs/AUDIT_AND_ROADMAP.md`.
- `docs/AGENT_MODE_PLAYBOOK.md`.
- README navigation/status update.
- Filename cleanup for before/after snapshots.

Important cleanup:

```text
Before:
sample_frame_before_20260628-185556-20260628-185556.png

After:
sample_frame_before-YYYYMMDD-HHMMSS.png
sample_frame_after-YYYYMMDD-HHMMSS.png
```

## Safety boundaries

### Allowed

- Offline RetroArch/emulator automation.
- Virtual controller testing.
- User-run macros/profiles.
- Diagnostic screenshots.
- Diagnostic image stats/crops/comparisons.
- Explicitly bounded future state machines for offline testing only.

### Not allowed

- Online multiplayer automation.
- Anti-cheat bypass.
- Hidden automation.
- Competitive-game bots.
- Unbounded loops.
- Image-driven actions before guarded gate phases.
- OCR-driven actions before explicit OCR/gate phases.

## Agent-mode workflow

Use this for every future phase:

1. Start from updated `main`.
2. Create a branch.
3. Keep the phase small.
4. Add code.
5. Add docs.
6. Add local test commands to the PR body.
7. User runs tests locally.
8. Merge only after user approval.
9. Keep generated output under ignored folders.
10. Do not add autonomy until diagnostics and gates are stable.

Branch naming examples:

```text
phase9-named-screen-regions
phase10-region-catalogs
phase11-diagnostic-overlays
phase12-baseline-drift-checks
```

PR body template:

```markdown
## Summary

What changed.

## Important boundary

What this phase does NOT do.

## Added

- Files/features added.

## Suggested local checks

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
git fetch
git checkout <branch>
git pull
python -m pip install -r requirements.txt
python ".\scripts\validate_all_profiles.py"
```

## Expected output

- What success looks like.

## Not included yet

- Explicit deferred features.
```

## Remaining roadmap

### Phase 9: named screen regions

Goal:

```text
Stop using one-off coordinates in commands. Define reusable named regions in config/profile files.
```

Example config:

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

Expected commands:

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region dialog_box
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region top_left
```

Acceptance criteria:

- Regions validate shape and bounds.
- Regions can be listed.
- Regions can be captured by name.
- Region crops write PNG and JSON metadata.
- Existing coordinate overrides still work.

Still not included:

- OCR.
- Template matching.
- Decisions.

### Phase 10: region catalogs per emulator/game layout

Goal:

```text
Support different region sets for different emulator layouts or games.
```

Examples:

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
- Validation catches missing names.
- Docs explain calibration.

### Phase 11: diagnostic overlays

Goal:

```text
Draw boxes and labels over screenshots so regions can be visually confirmed.
```

Expected command:

```powershell
python ".\scripts\draw_region_overlay.py" --profile retroarch_menu_test
```

Acceptance criteria:

- Output image shows rectangles and labels.
- Output is ignored by Git.
- Works on saved screenshots.

### Phase 12: baseline snapshots and drift checks

Goal:

```text
Compare current screenshots against manually approved baseline screenshots.
```

Expected commands:

```powershell
python ".\scripts\save_baseline.py" --profile retroarch_menu_test --region menu_area --name retroarch_menu_open
python ".\scripts\compare_baseline.py" --profile retroarch_menu_test --baseline retroarch_menu_open
```

Acceptance criteria:

- Baseline metadata records profile, region, size, timestamp, and notes.
- Comparison fails clearly if image sizes differ.
- Comparison produces JSON.
- No input is sent by baseline tools.

### Phase 13: threshold-only screen checks

Goal:

```text
Turn image diagnostics into pass/fail numeric checks, still with no actions.
```

Example:

```yaml
checks:
  menu_changed:
    region: menu_area
    metric: changed_percent
    op: gt
    value: 0.5
```

Acceptance criteria:

- Checks only compare numbers.
- Checks cannot press buttons.
- Checks print pass/fail.
- Checks write JSON.

### Phase 14: template matching foundation

Goal:

```text
Identify small manually supplied UI images inside named regions.
```

Expected command:

```powershell
python ".\scripts\match_template.py" --profile retroarch_menu_test --region menu_area --template templates\retroarch_back_icon.png
```

Acceptance criteria:

- Template files are user-provided.
- Match results are diagnostic only.
- Output includes confidence, bounding box, and region name.
- No input is pressed based on match results.

### Phase 15: conditional wait diagnostics

Goal:

```text
Wait for a visual condition and report pass/fail without pressing input.
```

Expected command:

```powershell
python ".\scripts\wait_for_template.py" --profile retroarch_menu_test --region menu_area --template templates\menu_ready.png --timeout 5
```

Acceptance criteria:

- Timeouts are mandatory.
- No input is pressed by the wait tool.
- Results are logged.

### Phase 16: guarded action gates

Goal:

```text
Allow exactly one predeclared action after a verified condition.
```

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
- Dry-run preview is required.
- Gate actions log condition result and dispatched action.

This is the first controlled bridge from vision into action.

### Phase 17: state machine runner

Goal:

```text
Formalize routes as bounded states instead of loose macro chains.
```

Example:

```yaml
states:
  open_menu:
    do: open_menu_macro
    expect: menu_ready
    on_success: move_cursor
    on_failure: stop
```

Acceptance criteria:

- Every state has a timeout.
- Every state has max retries.
- Every failure path stops safely.
- State transitions are logged.
- No unbounded loops.

### Phase 18: save-state and recovery integration

Goal:

```text
Optional emulator save-state support for offline testing only.
```

Acceptance criteria:

- User explicitly configures save/load hotkeys.
- Recovery is disabled by default.
- Risky actions require high-risk profile marking.
- No online games or networked gameplay.

### Phase 19: OCR experiments

Goal:

```text
Test OCR only after regions, overlays, baselines, thresholds, and gates are stable.
```

Acceptance criteria:

- OCR is region-scoped.
- OCR is diagnostic by default.
- OCR text is logged with confidence and region.
- OCR cannot trigger input until guarded gates support it.

### Phase 20: autonomous route experiments

Goal:

```text
Limited offline-only route automation with strict risk controls.
```

Acceptance criteria:

- Offline emulator only.
- Full dry-run planning output.
- Human-readable state transitions.
- Hard stop key.
- Max runtime.
- Max transitions.
- Max retries.
- Every action logged with reason.

Never include:

```text
Online multiplayer automation
Anti-cheat bypass
Competitive-game botting
Hidden automation
Unbounded self-driving loops
```

## Recommended next PR

Next branch:

```text
phase9-named-screen-regions
```

Minimum likely files:

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

## Fast commands reference

List profiles:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
```

Validate all:

```powershell
python ".\scripts\validate_all_profiles.py"
```

Dry-run:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
```

Live run:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

Capture screenshot:

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

Analyze screenshot:

```powershell
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
```

Before/after diagnostic:

```powershell
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

Emergency stop:

```text
Ctrl+C in terminal
```

Optional Windows terminal stop key:

```text
q while terminal is focused
```

## What to read next

For deeper details, read:

```text
docs/AUDIT_AND_ROADMAP.md
docs/AGENT_MODE_PLAYBOOK.md
docs/PROFILE_SCHEMA.md
docs/PERCEPTION.md
docs/IMAGE_DIAGNOSTICS.md
```

This file is the combined quick-reference package. The files above are the expanded technical sources.
