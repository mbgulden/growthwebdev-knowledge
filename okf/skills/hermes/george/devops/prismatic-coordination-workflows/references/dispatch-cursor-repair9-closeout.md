# Dispatch Cursor Repair 9 Closeout Addendum

Use this addendum when a Prismatic dispatch-cursor/generation repair has accumulated repeated `REPAIR` verdicts, AGY transport timeouts, or exact-head review churn.

## Launch discipline after repeated AGY timeouts

- If AGY attempts time out before edits or die by SIGTERM, classify them as transport/no-candidate only after verifying exact head, tree, worktree cleanliness, changed paths, log content, and surviving task-owned processes.
- Preserve orphan evidence before terminating only task-owned groups. Recursive filesystem searches (`find /`, broad repo scans) can survive as detached children; contract retries should explicitly ban broad recursive search and point to exact source/test/doc paths.
- Relaunch the same hashed contract from the same exact clean base; do not raise cap or advance to another task.
- When an AGY child is still inside the authorized producer process tree, do not classify it as an orphan. Use ancestry-aware process classification: authorized root PID/session plus descendants are producer-owned; detached PPID=1 children need separate containment.

## Candidate acceptance sequence

1. Treat normal AGY exit code `0` as an untrusted candidate, not success.
2. Inspect producer log, exact `HEAD`, tree, dirty state, allowed changed paths, and commit diff.
3. Run fresh exact-head local proof: focused tests, idempotency/adjacent tests, canonical suite, compile/static/diff checks, build/install-wheel proof, and external adversarial probes that do not rely only on producer-added tests.
4. For descriptor/lock/cursor repairs, add external probes for public-mode same-owner lock rejection before `fchmod`/`flock`, raced absent->public lock no-mutation, present->gone cursor rejection, absent->created cursor rejection, and stable absent handling.
5. Treat cleanup/descriptor-close failure as material, even after the primary no-side-effect rejection path is correct. If a snapshot/open path rejects an identity race but then `os.close()` fails, the candidate must preserve both the primary rejection and close failure, e.g. with an `ExceptionGroup`; swallowing close errors or leaking the descriptor is a `REPAIR` verdict. Regression probes should inject close-before-effect and close-after-effect failures, assert exception ordering/group semantics, and explicitly close any intentionally leaked test descriptor after restoring the real `os.close`.
6. Clean verification artifacts that appear in the worktree before state transition. Build tools may create untracked files such as `uv.lock`; remove or isolate them and recheck `git status --porcelain`.
6. Hash proof logs, verify task-owned process count is zero from outside the task worktree to avoid self-matching the scanner, and only then transition durable state to `EXACT_HEAD_REVIEW_PENDING`.
7. Dispatch a fresh independent exact-head review bound to the new candidate SHA/tree. Prior `REPAIR` and prior candidate reviews do not carry forward.

## Proof packet fields

```text
HEAD=<exact candidate sha>
TREE=<exact tree sha>
WORKTREE=<CLEAN|DIRTY>
CHANGED_PATHS=<allowed list>
LOCAL_PROOF=<focused/idempotency/canonical/static/build/adversarial summary>
LOG_SHA256=<proof log digests>
TASK_OWNED_PROCESSES=0
REVIEW=<fresh delegation id>
NOT_CLAIMING=independent CLEAN, PR, merge, deploy, restart, live DB/cursor mutation, Linear write, dispatch resume, cap increase
```
