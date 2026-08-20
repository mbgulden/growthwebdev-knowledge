# AGY exact-task cache preflight

Use this reference when launching an exact-ID AGY producer from Linear or an issue batch. It captures a failure mode where the visible Linear issue/comment was corrected, but the supervisor consumed a stale local issue-batch cache instead.

## Durable lesson

Do not trust the Linear description/comment as the task AGY actually receives. Verify the generated sandbox `AGY_TASK.md` before the AGY child starts real work.

## Failure pattern

- Linear issue was updated with the correct cap-1 integration contract.
- Exact-ID supervisor was launched with `--issue <ID> --max-concurrent 1`.
- Generated sandbox `AGY_TASK.md` still contained an older broad task because `/tmp/issue-batches/<ID>.txt` had precedence over Linear fetch/readback.
- The stale task authorized push/PR/merge/Done even though the current George contract forbade all of those side effects.

## Guard pattern

1. Launch the supervisor with a fixed jitter long enough to inspect the generated task file before the AGY child begins substantive work.
2. Poll for `/archive/agy_sandboxes/<ISSUE>/AGY_TASK.md`.
3. Assert the task file contains the exact current-main/base marker and task-specific marker.
4. Assert the task file omits stale side-effect phrases such as push, PR creation, merge, deploy/restart, or Linear Done unless explicitly authorized for that slice.
5. Hash the task file and record the digest in the launch receipt/control state.
6. Inspect the process tree to confirm the child corresponds to the exact issue.
7. If the task file is stale, kill the supervisor/child immediately, quarantine the sandbox and stale cache, verify no commit/branch/PR was created, replace the issue-batch cache with the exact packet, and relaunch with another fixed-jitter preflight.

## Proof fields to record

```text
ISSUE=<exact issue id>
SUPERVISOR_SESSION=<Hermes process session>
SUPERVISOR_PID=<pid>
AGY_CHILD_PID=<pid after verified launch>
TASK_FILE=<sandbox AGY_TASK.md path>
TASK_SHA256=<sha256>
CURRENT_MAIN_BASE=<exact sha>
STALE_SIDE_EFFECT_CONTRACT=false
REMOTE_BRANCH_CREATED=false
PR_CREATED=false
QUARANTINE_PATHS=<if any stale launch occurred>
MARKER=<task-specific launch marker>
```

## Abandoned/partial producer repair loop

If the verified-task producer exits by SIGTERM/timeout or writes `RESULT.md` with `ABANDONED`, do not treat the run as accepted even if allowed-path source files look useful.

1. Classify the producer packet first: `COMPLETED`, `ABANDONED`, commit SHA, remote branch, PR URL, and claimed tests.
2. Verify side effects independently (`git ls-remote`, PR list/readback, sandbox git status) before accepting the packet's claims.
3. If useful uncommitted files exist, review them as a **candidate snapshot**, not as producer completion:
   - check changed paths are exactly allowed;
   - hash-bind candidate files before any relaunch;
   - run focused behavior tests and independent lint locally;
   - record a merge judgment such as `REPAIR`, not `PASS`, when commit/canonical/build/installed-wheel proof is missing.
4. Preserve/quarantine the abandoned run and stale `RESULT.md` so the next supervisor launch cannot mistake it for success.
5. Issue a same-issue repair prompt that explicitly references the candidate snapshot/hashes, narrows the missing work, and keeps side effects false.
6. Before relaunch, remove or isolate stale active sandbox artifacts and repeat the fixed-jitter `AGY_TASK.md` hash gate.
7. Record the repair iteration in control state; do not launch the next issue or raise cap while a same-issue repair is active.

## Boundary language

A clean task-file preflight proves only that AGY started from the intended packet. It is not producer completion, merge approval, cap promotion, or proof that the candidate integrates cleanly. Treat `RESULT.md` as an untrusted claim until George independently reviews the candidate diff and evidence. An abandoned run with passing local checks is still `REPAIR` until a valid commit and required proof packet exist.
