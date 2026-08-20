# 2026-07 Prismatic PR merge-train after AGY cleanup

Session pattern worth reusing when Michael asks to “follow the golden path” or “do the next step” after an AGY/Jules PR cleanup.

## User-facing operating lesson

For Michael, “do the next step” means continue concrete execution along the golden path: verify AGY output, merge/close/route safe PRs, dispatch the next AGY work item, and re-check live queue state. Do not stop at a passive status report when tools can still safely advance the queue.

## What worked

1. **Do not trust AGY self-report as final evidence.**
   - Read `RESULT.md` in the AGY sandbox.
   - Verify GitHub/Linear state yourself.
   - Treat AGY-created local branches as candidate work until there is a clean PR, check output, and/or merged commit.

2. **Clean extraction beats raw stale merge.**
   - AGY may identify a useful delta inside a broad/stale PR, but Ned should extract it into a fresh branch based on the current target branch.
   - Example verification shape:
     - focused unit test for the extracted behavior;
     - `python3 -m py_compile` on touched Python files;
     - GitHub check state after opening the clean PR.

3. **After each merge, re-query mergeability.**
   - A PR can be green before an earlier merge and become conflicting afterward.
   - Rule: merge-train state is not stable; every successful merge can invalidate later PRs. Re-query `mergeable` and checks before the next merge.

4. **Failed check cleanup can unblock merges, but still needs independent verification.**
   - If AGY fixes check blockers on remote branches, independently verify `statusCheckRollup` before merging or closing source PRs.

5. **Close conflict-source PRs after extracting or superseding.**
   - Once a clean extraction/merge lands, close the stale source PR with a comment naming the clean PR or follow-up task.

6. **Governance boundary: pyproject / out-of-lane conflict resolution.**
   - If the needed conflict resolution touches files outside Ned’s lane (for example `pyproject.toml`), do not `--no-verify` or bypass the pre-push guard from Ned.
   - Safe pattern:
     1. Resolve and verify locally if useful.
     2. Comment on the PR with exact resolution and local verification evidence.
     3. Create an AGY/governor Linear task with the needed patch shape and verification commands.
     4. After AGY/governor pushes, verify PR mergeability/checks yourself, then merge if safe.

7. **No-check PRs can still be merged, but only after local smoke verification.**
   - For old PRs with no GitHub checks, create a clean current worktree, merge with `--no-commit`, run focused compile/smoke checks, inspect blocker comments, then merge only if the prior blockers are resolved in the diff.
   - Example checks used for heartbeat/watchdog work:
     - `python3 -m py_compile prismatic/dispatcher.py prismatic/gateway/ipc_bridge.py scripts/watchdog.py`
     - a direct `validate_event({'type':'agent_heartbeat','source':'test'})` assertion
     - `python3 scripts/watchdog.py` smoke run, accepting environment-dependent status but not import/syntax failure.

8. **AGY supervisor lock and checkout hygiene.**
   - A stale `/home/ubuntu/.prismatic/run/supervisor.lock` can prevent a new supervisor from picking up newly created `agent:agy + dispatch:ready` tasks.
   - Safe recovery pattern: confirm no live supervisor process owns the PID in the lock; remove the stale lock; restart supervisor; verify logs show the new issue IDs queued/picked up.
   - The supervisor imports the repo in its current checkout. Before restarting after merges, put `/home/ubuntu/work/prismatic-engine` on a branch/commit that contains required runtime modules such as `prismatic.linear.budget`; otherwise the preflight may fail with `LinearBudget unavailable` even though the fix is merged elsewhere.

## Commands / checks used

```bash
gh pr view <PR> --repo mbgulden/prismatic-engine \
  --json number,title,mergeable,statusCheckRollup,files,url

gh pr list --repo mbgulden/prismatic-engine --state open --limit 200 \
  --json number,title,baseRefName,mergeable,statusCheckRollup,url
```

Summarize queue state after each cleanup wave:

```text
open_prs: N
mergeable: N
conflicting: N
failed_checks: N [list]
```

## Reporting shape

Lead with what changed and live counts:

- merged clean PRs;
- closed stale/unsafe/conflict-source PRs;
- AGY tasks created and whether they are started/done;
- current `open_prs / mergeable / conflicting / failed_checks`;
- next golden-path task already dispatched when keep-going mode is active.
