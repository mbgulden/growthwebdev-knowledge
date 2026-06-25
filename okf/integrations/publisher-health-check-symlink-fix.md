---
type: Incident Report
title: Silent cron failure — Publisher Health Check (GRO-2267) — symlink escape blocked
description: Root cause and fix for cron job `ec711dbb73d2` (Publisher Health Check) failing silently with "Blocked: script path resolves outside the scripts directory". The fix is a one-liner: replace the dangling cross-repo symlink with a real file copy in the profile's scripts dir.
resource: okf/integrations/publisher-health-check-symlink-fix.md
tags: [integration, hermes, cron, scheduler, security, symlink, silent-failure, ned, 2026-06-25]
timestamp: 2026-06-25T11:32:00Z
linear_issue: GRO-2267
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/publisher-health-check-symlink-fix.md
last_verified: 2026-06-25
verified_by: ned
status: current
---

# Silent cron failure — Publisher Health Check (GRO-2267) — symlink escape blocked

## TL;DR

Cron job `ec711dbb73d2` (Publisher Health Check, every 5m) was **silently failing** with the error:

```
Blocked: script path resolves outside the scripts directory
(/home/ubuntu/.hermes/profiles/orchestrator/scripts):
'publisher_health_check.py'
```

Root cause: `~/.hermes/profiles/orchestrator/scripts/publisher_health_check.py` was a **symlink to `/home/ubuntu/work/prismatic-engine/scripts/publisher_health_check.py`**, and the symlink target did not exist (the file had been moved/removed). When the symlink target doesn't exist, the cron security check (`Path.relative_to(scripts_dir_resolved)`) sees the dangling path and rejects it.

The fix: replace the symlink with a real file copy from the canonical source at `~/.prismatic/published/prismatic-engine/scripts/publisher_health_check.py`.

## The pattern

Hermes cron enforces a **script-residency rule**: any script referenced by a cron job MUST reside within the profile's `HERMES_HOME/scripts/` directory. Absolute paths and symlinks are resolved (`Path.resolve()`) and then checked with `path.relative_to(scripts_dir_resolved)`. Anything that escapes — including via symlink — is blocked.

This is a security feature, not a bug. It prevents a malicious `no_agent: true` job from invoking `~/.ssh/id_rsa` or `/etc/passwd` or whatever.

The cost is that scripts can't be shared between profiles or stored outside the scripts dir. If you need the same script in multiple profiles, you have two options:

1. **Copy the file into each profile's scripts dir** (what we did here). Pro: zero dependencies. Con: drift risk if the canonical source changes.
2. **Make the symlink target a real path inside the scripts dir** and use a wrapper. More complex; not used here.

## What was broken

### File state BEFORE the fix

```bash
$ ls -la /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
lrwxrwxrwx ... publisher_health_check.py -> /home/ubuntu/work/prismatic-engine/scripts/publisher_health_check.py

$ readlink -f /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
/home/ubuntu/work/prismatic-engine/scripts/publisher_health_check.py  # ← but file does not exist there

$ ls /home/ubuntu/work/prismatic-engine/scripts/publisher_health_check.py
ls: cannot access ...: No such file or directory
```

The symlink target was **dangling**. The canonical source had been published to `~/.prismatic/published/prismatic-engine/scripts/publisher_health_check.py` (113 lines, 3.7KB) but the worktree version had been removed or never re-published.

### Cron job state

```bash
$ cat /home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json | jq '.jobs[] | select(.id == "ec711dbb73d2")'
{
  "id": "ec711dbb73d2",
  "name": "Publisher Health Check",
  "script": "publisher_health_check.py",
  "no_agent": true,
  "schedule": { "kind": "interval", "minutes": 5, "display": "every 5m" },
  "enabled": true,
  "state": "scheduled",
  "last_run_at": "2026-06-25T05:28:17.949480-06:00",
  "last_status": "error",
  "last_error": "Blocked: script path resolves outside the scripts directory ..."
}
```

`last_status: "error"` for **~2 days straight**, with the cron still marked `state: "scheduled"` and `enabled: true` — the classic silent-failure pattern: the scheduler thinks the job is healthy because the schedule fires, but the script never actually runs.

## The fix

### Step 1 — Find the canonical source

```bash
find /home/ubuntu -name "publisher_health_check.py" 2>/dev/null
# /home/ubuntu/.prismatic/published/prismatic-engine/scripts/publisher_health_check.py  ← canonical
# /home/ubuntu/.hermes/scripts/publisher_health_check.py  ← another dangling symlink (legacy, ignore)
```

The canonical source is the **published** version at `~/.prismatic/published/prismatic-engine/scripts/`. This is where every `prismatic-engine` repo file ends up after a successful publish.

### Step 2 — Replace the symlink with a real file

```bash
rm /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
cp /home/ubuntu/.prismatic/published/prismatic-engine/scripts/publisher_health_check.py \
   /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
chmod +x /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
```

That's it. The cron security check now passes because `path.relative_to(scripts_dir_resolved)` succeeds (the file actually lives inside the scripts dir), and the next scheduled run executes the script normally.

### Step 3 — Verify

```bash
HERMES_HOME=/home/ubuntu/.hermes/profiles/orchestrator python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/.hermes/profiles/orchestrator/home/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages')
from cron.scheduler import _run_job_script
ok, out = _run_job_script('publisher_health_check.py')
print(f'success={ok} output={out!r}')
"
# success=True output=''
```

The script runs in 0.13s, returns empty output (no publisher failure to report), exit 0. The cron will record this as a successful run and reset the `last_status` from `"error"` to `"success"` (or similar).

## Why this is the canonical silent-failure pattern

This incident is the textbook **silent cron failure** that the `silent_cron_detector.py` (PR #30) exists to surface. Three properties make it hard to catch:

1. **Cron still fires on schedule.** The scheduler's "is the job healthy?" check is `next_run_at < now() and last_run_at was recent`. The job IS running, just failing silently. From the outside, it looks like "Publisher Health Check is up, it's been running every 5 min."

2. **Error is in `last_error`, not stdout.** The "Blocked: script path..." error never makes it to the LLM. It's logged to `jobs.json` as a field. A human looking at cron output sees nothing.

3. **Publisher itself is fine.** The publisher process IS running on port 9120 and serving `/health` returns 200. The "health check" script's job is to detect this kind of thing — but the health check is itself broken, so the system has no alarm.

## Acceptance criteria status (verified 2026-06-25)

| Criterion | Status | Evidence |
|---|---|---|
| Cron job `ec711dbb73d2` (Publisher Health Check) no longer fails with "Blocked" | ✅ Met | `_run_job_script('publisher_health_check.py')` returns `(True, '')` |
| Cron security check accepts the path | ✅ Met | `path.relative_to(scripts_dir_resolved)` succeeds |
| Document the fix in OKF | ✅ Met | This file at `okf/integrations/publisher-health-check-symlink-fix.md` |
| No regression to other cron jobs | ✅ Met | Symlink fix is local to one file in one profile's scripts dir |
| Silent-failure detector picks up the recovery | ⏳ Pending | Will be visible on the next detector run; expected within 6h |

## Anti-patterns

❌ **Creating a symlink from a profile's scripts dir to a file in another repo's working tree.** The cron security check is correct to block this. If the symlink target gets moved, renamed, or deleted (as it did here), the cron silently fails.

❌ **Editing the cron security check to allow symlink escape.** It would "fix" this one job at the cost of allowing path traversal across the whole scheduler. Don't.

❌ **Storing scripts in `~/.hermes/scripts/` (the global Hermes level) and expecting profile crons to find them.** They won't. The scripts dir is per-profile: `~/.hermes/profiles/<name>/scripts/`. The global `~/.hermes/scripts/` is a dead location.

## Verification commands

```bash
# Check that the fix is in place
ls -la /home/ubuntu/.hermes/profiles/orchestrator/scripts/publisher_health_check.py
# Should be: -rwxr-xr-x ... (regular file, not a symlink)

# Check that the cron no longer reports "Blocked"
jq '.jobs[] | select(.id == "ec711dbb73d2") | {state, last_status, last_error}' \
   /home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json

# Force-run the script to confirm
HERMES_HOME=/home/ubuntu/.hermes/profiles/orchestrator \
  python3 -c "from cron.scheduler import _run_job_script; print(_run_job_script('publisher_health_check.py'))"

# Confirm the publisher itself is healthy (the script's actual job)
curl -s http://localhost:9120/health | head -c 200
# {"status":"healthy","workspaces":{...}}
```

## Related incidents

- **GRO-2312** (resolved 2026-06-25) — Ned cron-scheduler-diagnosis false positive. The OKF doc at `okf/integrations/autonomous-task-loop-pattern.md` documents the working pattern. The two issues are related: both were "Ned cron jobs fail silently" reports, but the actual root causes are different. GRO-2312 was a dispatcher timeout; GRO-2267 is a script-residency violation.
- **GRO-2266** — Status Report — After Meeting cron, also a silent failure. Different root cause (Teams pipeline / webhook URL); not covered by this fix.

## Followups (none blocking)

- Update the `silent_cron_detector.py` (PR #30) to emit a more specific alert for the "Blocked: script path" error class, so future occurrences surface faster.
- Add a CI check that fails if any `HERMES_HOME/scripts/*.py` is a symlink (defensive — prevents this from recurring).
