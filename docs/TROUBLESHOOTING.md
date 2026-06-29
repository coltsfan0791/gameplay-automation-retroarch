# Troubleshooting

## `vgamepad` import/runtime errors

Symptom:

```text
RuntimeError: vgamepad is required
```

Fix:

```powershell
python -m pip install -r requirements.txt
```

Also ensure ViGEmBus is installed on Windows if required by your environment.

## Profile not found

Symptom:

```text
Profile not found: <name>
```

Fix:

```powershell
python ".\src\scenarios\scripted_playback.py" --list-profiles
python ".\src\scenarios\scripted_playback.py" --profile profiles\retroarch_menu_test.yaml --dry-run
```

## Validation failures in YAML

Symptom:

```text
FAIL: profiles/<file>.yaml
```

Fix:

```powershell
python ".\scripts\validate_config.py" --config config/default.yaml --show-events
python ".\scripts\validate_all_profiles.py" --profiles profiles
```

Common causes:

- Invalid action names
- Negative hold/wait durations
- Invalid repeat count
- Invalid screenshot region values

## Screenshot capture backend issues

Symptom:

```text
No module named 'mss'
```

Fix:

```powershell
python -m pip install -r requirements.txt
python ".\scripts\capture_sample_frame.py" --list-monitors
```

If monitor index fails, try a different `monitor_index` in profile/config.

## Live run starts too quickly

Increase countdown or force Enter confirmation:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --countdown-seconds 5 --require-enter
```

## Playback stopped unexpectedly

Check max runtime and stop key settings in config:

- `safety.max_runtime_seconds`
- `safety.enable_console_stop`
- `safety.stop_key`

Review newest log in `logs/` for `status`, `error_type`, and `error` fields.

## Git includes generated files

Make sure generated folders are ignored and untracked:

```powershell
git status
git rm -r --cached Downloads logs captures screenshots diagnostics
```

Then commit ignore updates.
