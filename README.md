# Gameplay Automation - RetroArch

This folder contains a staged automation framework for controlling RetroArch externally.

## What this project does

- Runs deterministic, YAML-defined controller macros for offline RetroArch/emulator workflows.
- Validates config/profile YAML before live playback.
- Provides safe dry-run and safety guards (countdown, max runtime, emergency stop).
- Captures diagnostic screenshots and image diagnostics for perception groundwork.

## What this project does not do yet

- OCR-driven gameplay logic.
- Autonomous decision-making loops.
- Online/multiplayer automation.
- Anti-cheat bypassing or hidden automation.

## Architecture

- `src/core/interfaces.py`: shared contracts for input adapters and perception adapters.
- `src/core/scheduler.py`: deterministic frame-timed control loop with safety guards.
- `src/input/vgamepad_backend.py`: Windows virtual gamepad backend using `vgamepad`.
- `src/perception/screenshot_backend.py`: diagnostic screenshot capture backend.
- `src/scenarios/scripted_playback.py`: YAML-driven input sequence/profile replay runner.
- `config/default.yaml`: default timing, macro, safety, perception, and logging config.
- `profiles/`: reusable playback profile YAML files.
- `logs/`: runtime JSONL traces and ignored local diagnostic output.

## Design goals

- Keep platform-specific code isolated behind adapter interfaces.
- Use a monotonic scheduler for repeatable timing.
- Log all dispatched actions with timestamps for drift analysis.
- Keep macro authoring in YAML instead of editing Python for every route.
- Keep profiles code-only: no ROMs, BIOS files, save states, screenshots, or private logs.
- Prefer safe, testable, reversible steps before adding autonomy.

## Quick start

1. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

1. Validate default config:

```powershell
python ".\scripts\validate_config.py" --config config/default.yaml
```

1. Validate all profiles:

```powershell
python ".\scripts\validate_all_profiles.py" --profiles profiles
```

1. List available profiles:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
```

1. Dry-run a profile without pressing controller buttons:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
```

1. Capture a diagnostic frame without pressing controller buttons:

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

1. Run a profile with normal safety prompts/countdown:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

1. Inspect ignored local output in `logs/`.

## Documentation index

- `docs/QUICKSTART.md`
- `docs/PROFILE_SCHEMA.md`
- `docs/PERCEPTION.md`
- `docs/IMAGE_DIAGNOSTICS.md`
- `docs/SAFETY.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ROADMAP.md`
- `docs/REGIONS.md`
- `docs/PROJECT_INFO_PACKAGE.md`
- `docs/AGENT_MODE_PLAYBOOK.md`
- `docs/VERIFICATION.md`

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

## Phase 7: perception foundation

Phase 7 adds screenshot capture for observation/debugging only.

No OCR, template matching, or autonomous decision-making is included yet.

### Screenshot config

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

### List monitors

```powershell
python ".\scripts\capture_sample_frame.py" --list-monitors
```

### Capture using config/default.yaml

```powershell
python ".\scripts\capture_sample_frame.py"
```

### Capture using a profile

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
```

### Capture a region override

```powershell
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test --left 0 --top 0 --width 1280 --height 720
```

Capture writes a PNG and a JSON metadata file under `logs/screenshots/` by default. Those outputs are ignored by Git.

## Phase 9: named screen regions

Phase 9 adds a reusable named region system so you can define screen areas in YAML once and refer to them by name.

### Define regions in config/profile

```yaml
regions:
  full_screen:
    left: 0
    top: 0
    width: 1366
    height: 768
  menu_area:
    left: 200
    top: 100
    width: 966
    height: 568
```

### List regions

```powershell
python ".\scripts\list_regions.py" --profile retroarch_menu_test
python ".\scripts\list_regions.py" --profile retroarch_menu_test --validate
```

### Capture a region by name

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --region menu_area
```

### Capture with legacy CLI coordinates

```powershell
python ".\scripts\capture_region.py" --profile retroarch_menu_test --left 200 --top 100 --width 966 --height 568
```

### Analyze a region (fresh capture or existing image)

```powershell
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region menu_area --image "logs/screenshots/menu_area-*.png"
python ".\scripts\analyze_region.py" --profile retroarch_menu_test --region full_screen --json
```

For full documentation see `docs/REGIONS.md`.

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
