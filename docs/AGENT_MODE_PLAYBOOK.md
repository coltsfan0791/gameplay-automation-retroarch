# Agent Mode Playbook

This playbook defines how future work should be done when an AI assistant is acting as an implementation agent for this repository.

## Prime directive

Build safe offline tooling in small, reviewable phases.

Do not build online multiplayer automation, anti-cheat bypasses, competitive-game bots, or anything that hides automation from a protected system.

## Standard phase workflow

For every phase:

1. Start from clean `main`.
2. Create a branch named after the phase.
3. Make the smallest useful change set.
4. Update docs in the same branch.
5. Include local test commands in the PR body.
6. Wait for user local validation.
7. Merge only after user approval.
8. Keep generated logs/screenshots/reports out of Git.

## Branch naming

Use concise branch names:

```text
phase9-named-screen-regions
phase10-region-catalogs
phase11-diagnostic-overlays
phase12-baseline-drift-checks
```

Use non-phase branch names only for audits or cleanup:

```text
audit-roadmap-optimization
cleanup-docs
fix-profile-validation
```

## Commit style

Use direct commit messages:

```text
Phase 9: add named region parser
Phase 9: add region capture CLI
Phase 9: document named screen regions
Audit: simplify before-after snapshot filenames
```

Avoid vague messages such as:

```text
updates
changes
misc
fix stuff
```

## Pull request body format

Every PR should include:

````markdown
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

````

## Safety boundaries by layer

### Input layer

Allowed:

- Offline emulator input.
- Virtual controller testing.
- Explicit user-run profiles.

Not allowed:

- Online-game automation.
- Anti-cheat bypass.
- Hidden input automation.
- Competitive gameplay automation.

### Perception layer

Allowed:

- Screenshot capture.
- Region crops.
- Image stats.
- Difference reports.
- Manual template diagnostics.

Not allowed until later guarded phases:

- OCR-driven actions.
- Template-driven actions.
- Automatic recovery decisions.

### Decision layer

Allowed only after gated phases:

- Predeclared state transitions.
- Bounded retries.
- Hard timeouts.
- Explicit logs explaining every action.

Never allowed:

- Unbounded loops.
- Hidden decision-making.
- Online/competitive automation.
- Circumventing game protections.

## Local validation ladder

Use this ladder before live playback:

```powershell
python ".\scripts\validate_all_profiles.py"
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test --dry-run --show-events
python ".\scripts\capture_sample_frame.py" --profile retroarch_menu_test
python ".\scripts\analyze_image.py" --image "logs\screenshots\sample_frame-YYYYMMDD-HHMMSS.png"
```

Only then run live playback:

```powershell
python ".\src\scenarios\scripted_playback.py" --profile retroarch_menu_test
```

For before/after diagnostics:

```powershell
python ".\scripts\capture_profile_snapshots.py" --profile retroarch_menu_test --no-countdown
```

## Review checklist

Before opening a PR, check:

- Does the change preserve old commands?
- Does dry-run still work?
- Does all-profile validation still work?
- Are generated files ignored by Git?
- Are docs updated?
- Does the PR body include test commands?
- Is the phase boundary explicit?
- Is there any accidental OCR, object detection, or decision logic?
- Is there any risk of online-game automation? If yes, stop.

## Local stash warning

If `git pull` is blocked by local changes, use:

```powershell
git status
git stash push -u -m "local files before pull"
git pull
```

Do not blindly run `git stash pop` after a major README or docs change. Inspect the stash first:

```powershell
git stash list
git stash show --stat stash@{0}
```

## Preferred next implementation order

1. Named screen regions.
2. Region sets/catalogs.
3. Diagnostic overlays.
4. Baseline snapshots.
5. Threshold-only checks.
6. Template matching diagnostics.
7. Conditional wait diagnostics.
8. Guarded action gates.
9. State machine runner.
10. Save-state/recovery support.
11. OCR experiments.
12. Autonomous route experiments.
