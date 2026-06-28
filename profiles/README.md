# Playback Profiles

Profiles are YAML files that describe reusable controller macros.

Run a profile:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

Dry-run a profile without sending controller input:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
```

List profiles:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
```

Validate every profile:

```powershell
python ".\scripts\validate_all_profiles.py"
```

## Profile naming

You can pass either a profile name or a path:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile gba_basic_movement
python ".\src\scenarios\scripted_playback.py" --profile profiles\gba_basic_movement.yaml
```

## Safety

Keep profiles generic and code-only. Do not commit ROMs, BIOS files, save states, copyrighted game files, private logs, or game screenshots.
