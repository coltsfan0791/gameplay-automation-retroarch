# Phase 5 - Profiles and Examples

Phase 5 turns the project from a single configurable macro runner into a reusable profile-based automation toolkit.

## Goals

- Keep `config/default.yaml` working as the default config.
- Add `profiles/` as the home for reusable YAML playback files.
- Let profiles be selected from the command line.
- Let profiles be dry-run and inspected before the virtual controller sends input.
- Add several practical starter profiles for RetroArch/GBA-style workflows.

## New runner options

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
python ".\src\scenarios\scripted_playback.py" --profile profiles\retroarch_menu_test.yaml
python ".\src\scenarios\scripted_playback.py" --config config/default.yaml
python ".\src\scenarios\scripted_playback.py" --profile pokemon_menu_nav --dry-run --show-events
```

## New scripts

```text
scripts/validate_config.py
scripts/validate_all_profiles.py
```

`validate_config.py` validates one selected config/profile.

`validate_all_profiles.py` validates `config/default.yaml` plus every YAML file under `profiles/`.

## Included profiles

```text
profiles/generic_controller_test.yaml
profiles/retroarch_menu_test.yaml
profiles/gba_basic_movement.yaml
profiles/pokemon_menu_nav.yaml
profiles/analog_stick_trigger_test.yaml
```

## Profile strategy

Profiles should be small and composable.

Good profile categories:

- Generic controller tests
- RetroArch menu tests
- GBA movement loops
- Pokemon-style menu navigation
- Analog/trigger hardware checks
- Later: game-specific route profiles

Avoid committing:

- ROMs
- BIOS files
- Save states
- Screenshots
- Private logs
- Anything copyrighted or personally sensitive

## Not included yet

- Computer vision
- OCR
- Screen capture
- Conditional wait-until-screen logic
- Save-state orchestration
- Game-specific perception adapters

Those belong after profiles are stable.
