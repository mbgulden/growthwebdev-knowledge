# GRO-3738: temp-worktree finalize + repeated ad-hoc verifier detector

Session date: 2026-07-09

## What happened

GRO-3738 was implemented in a temporary worktree at `/tmp/prismatic-gro-3738` because the main checkout `/home/ubuntu/work/prismatic-engine` already had unrelated dirty files from another task. The first finalize attempt was run from the temp worktree but without `PRISMATIC_REPO_ROOT`, so `finalize_task.sh` inspected the default main checkout and aborted on unrelated staged/added Python files:

```text
[finalize] STEP 1: committing any pending changes in /home/ubuntu/work/prismatic-engine
[finalize] ERROR: Found 'os.env' in prismatic/cli/main.py
[finalize] ERROR: Found 'os.env' in prismatic/projects_db.py
[finalize] CRITICAL: Finalize aborted due to detected code corruption patterns in staged Python files.
```

The successful rerun explicitly pointed finalize at the clean temp worktree and scoped lock files:

```bash
PRISMATIC_REPO_ROOT=/tmp/prismatic-gro-3738 \
FINALIZE_LOCK_FILES='plugins/pwp' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3738 ned/GRO-3738 ned
```

Finalize then transitioned Linear and posted the evidence comment. Push succeeded afterward.

## Durable pattern

When using a temporary worktree for a task branch, do **not** rely on `cwd` alone. `finalize_task.sh` defaults to `/home/ubuntu/work/prismatic-engine` unless `PRISMATIC_REPO_ROOT` is set. Always set:

- `PRISMATIC_REPO_ROOT=<clean-worktree>`
- `FINALIZE_LOCK_FILES='<actual lane path>'`

Then verify Linear state/comment and remote branch after finalize because the script has known silent/warning failure modes.

## Repeated detector prompt pattern

The verification detector ignored the normal pytest output and asked for a focused `/tmp/hermes-verify-*` script. It repeated the request once more. The correct response was to run a **fresh** ad-hoc verifier each time, not argue from previous evidence.

Required verifier shape:

1. Create with `tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')`.
2. Print `TEMP_SCRIPT=<path>`.
3. Run the script with explicit `PYTHONPATH=<worktree>`.
4. Print `TESTED_COMMAND=...`, `EXIT_CODE=...`, and an assertion summary.
5. Delete the verifier in `finally` and print `CLEANUP=deleted <path>`.

For GRO-3738 the verifier asserted the changed behavior directly:

- deterministic single owner label per generated PWP theme task,
- no `dispatch:ready` before `build_initiated=True`,
- `dispatch:ready` appears after explicit build initiation,
- parent/dependency/contract metadata is preserved,
- manual `agent:*` labels are rejected,
- batch generation remains deterministic.

## Pitfall

If the detector repeats with the same changed paths, produce a new temp verifier path and fresh run. Previous pytest/ruff output or even the previous ad-hoc verifier may be true, but the detector is looking for fresh recognizable evidence.