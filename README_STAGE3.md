# RetroArch Automation - Stage 3 Controller Expansion

This branch expands the virtual Xbox 360 controller actions used by the existing YAML macro runner.

## Apply after Phase 2 finish

Use this branch after the Phase 2 final patch is in place.

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
git checkout main
git pull
git checkout stage3-controller-expansion
```

## Verify

```powershell
cd "G:\VSC projects\gameplay-automation-retroarch"
python "G:\VSC projects\gameplay-automation-retroarch\src\scenarios\scripted_playback.py"
```

Then inspect the newest log:

```powershell
Get-ChildItem ".\logs" -Filter "*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

## Useful helper

```powershell
python ".\scripts\list_supported_actions.py"
```

This prints the action names the backend currently accepts.

## Commit summary

Stage 3 adds Start/Menu, Back/Select/View, LB/RB, stick clicks, triggers, and analog stick direction aliases.
