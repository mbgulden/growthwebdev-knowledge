# Cron/temp-worktree finalize path expansion pitfall

Observed during a Ned cron task after work was committed in `/tmp/hd-platform-gro3990`.

## Symptom

Running the skeleton-style command:

```bash
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3990 ned/GRO-3990 ned
```

failed with a doubled path:

```text
bash: /home/ubuntu/.hermes/profiles/ned/home/.hermes/profiles/ned/scripts/finalize_task.sh: No such file or directory
```

The task was not blocked; the path expansion context was wrong.

## Fix

Rerun immediately with the absolute script path and explicit repo/lock env when operating from a temp worktree:

```bash
PRISMATIC_REPO_ROOT=/tmp/<clean-worktree> \
FINALIZE_LOCK_FILES='<actual files>' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

Then perform the normal post-finalize checks:

1. Re-query Linear state/comments. Do not trust the finalize transcript alone.
2. If Linear drifted back to `In Progress`, manually run `issueUpdate` to restore `In Review`.
3. Add a concise evidence-refresh comment if the issue is partial/not-green.
4. Confirm locks are actually cleared; if stale locks remain, unlock by exact path.

## Why this belongs in the finalize class

This is not an environment-specific missing binary. It is a recurring shell-context hazard in cron/temp-worktree finalization. The durable rule is: use absolute finalize paths when cron/profile wrappers have ambiguous HOME expansion, then verify Linear because finalize can still silently half-succeed.
