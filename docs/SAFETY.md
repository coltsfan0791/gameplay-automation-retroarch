# Safety Guide

This project sends controller input to RetroArch from outside the emulator. Treat every live playback as real controller input.

## Safe workflow

Use this order every time:

```powershell
python ".\scripts\validate_all_profiles.py"
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

Dry-run first. Live-run second.

## Emergency stop

Primary stop:

```text
Ctrl+C
```

Optional Windows console stop key:

```text
q
```

The console stop key only works when the terminal has focus. If RetroArch has focus, use Ctrl+C from the terminal after switching back, or keep test profiles short.

## Countdown

Profiles default to a countdown before playback starts:

```yaml
safety:
  countdown_seconds: 3
```

This gives you time to focus RetroArch.

Override from CLI:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --countdown-seconds 5
```

Skip countdown only when you are sure:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --no-countdown
```

## Max runtime guard

Profiles default to a max runtime guard:

```yaml
safety:
  max_runtime_seconds: 30
```

Override from CLI:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --max-runtime-seconds 10
```

## Require Enter

For riskier profiles, require an explicit Enter before the countdown:

```yaml
safety:
  require_enter: true
```

or use the CLI:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --require-enter
```

## Risk levels

Profiles declare an informational risk level:

```yaml
profile:
  risk_level: low
```

Allowed values:

```text
low
medium
high
```

Use them honestly:

- `low`: short test/profile, reversible, safe menu movement.
- `medium`: longer route or repeated movement where mistakes can matter.
- `high`: anything that could change saves, delete data, spend resources, or get stuck without supervision.

## Logging

Logs are written as JSONL rows under `logs/` unless disabled by config.

Status values:

```text
ok
stopped
error
```

Stopped/error rows may include:

```text
error_type
error
```

## Repo hygiene

Never commit:

- ROMs
- BIOS files
- save states
- private logs
- screenshots with personal/private content
- copyrighted game files

Keep the repository code-only.
