# Already-finalized task redispatch / cron refresh pattern

Use when the cron scanner re-dispatches a task whose branch/work already exists and Linear is already `In Review`.

## Trigger

A cron preamble says `TASK:<issue>`, but the task may already be complete. A redispatch is not proof that new implementation work is needed.

## Completion signals to check before touching the shared checkout

Check for all three:

1. Local batch result exists, e.g. `/tmp/issue-batches/<ISSUE>_RESULT.md`, and records prior branch/commit/evidence.
2. Linear issue state is already `In Review` with prior Ned/finalization evidence comments and/or PR attachment.
3. Remote branch exists at the recorded commit, e.g. `git ls-remote --heads origin ned/<ISSUE>`.

When all three are true, treat the run as a **verification-refresh pass**, not a rebuild.

## Safe sequence

1. Do not switch the active shared checkout if it is dirty or on another task branch.
   - If a file expected on the task branch appears missing from the shared checkout, treat that as evidence you are looking at the wrong branch, not as proof the task regressed. Confirm the remote task branch exists first, then inspect/test from a clean worktree.
2. Add a temporary clean detached worktree from the remote task branch:
   ```bash
   rm -rf /tmp/prismatic-<issue>-croncheck
   git worktree add --detach /tmp/prismatic-<issue>-croncheck origin/ned/<ISSUE>
   ```
3. Run the focused canonical test from that worktree.
4. If a detector or cron contract expects fresh evidence, create a `/tmp/hermes-verify-*` ad-hoc verifier that:
   - imports from the clean worktree,
   - asserts the changed behavior directly,
   - runs the focused pytest command,
   - prints verifier path, tested command, pytest exit, assertion summary, verification exit, and cleanup status,
   - deletes the verifier in `finally` and prints `CLEANUP_EXISTS=no`.
5. Update only the local `/tmp/issue-batches/<ISSUE>_RESULT.md` with fresh evidence.
6. Remove/prune the temporary worktree.
7. Do **not** post another Linear finalization comment and do **not** run `finalize_task.sh` again when Linear is already `In Review` and prior finalization evidence exists; duplicate comments create noise without changing task state.
8. If there is no new blocker or human decision needed, final cron response may be `[SILENT]`.

## Verifier execution pitfall: worktree cwd and temp-script imports

When creating a clean worktree for an already-finalized redispatch, remember that `git worktree add ... /tmp/<worktree>` does **not** change the shell's current working directory. Run focused tests in a separate command with `workdir=/tmp/<worktree>` or explicitly `cd /tmp/<worktree>` before invoking pytest. Otherwise pytest may execute from the shared dirty checkout and falsely report missing files.

**Hermes terminal cwd creation trap:** do not set `terminal(workdir="/tmp/<worktree>")` in the same tool call that creates that worktree. Hermes resolves the working directory before the shell command runs, so the call fails with `cd: /tmp/<worktree>: No such file or directory`. Use `workdir=/home/ubuntu/work` (or any existing directory) for the create-and-test compound command and include `cd /tmp/<worktree> && ...`, or split into two terminal calls: first `git worktree add`, then run tests with `workdir=/tmp/<worktree>`.

**Wrong-cwd false negative pattern:** a focused pytest command can fail with `ERROR: file or directory not found: plugins/pwp/tests/test_compiler_determinism.py` while a subsequent file search confirms the test exists inside the detached worktree. That is not a regression in the task branch; it means pytest ran from the parent/shared cwd (for example `/home/ubuntu/work`) instead of the worktree. Recovery is simple and non-blocking: rerun the focused pytest after `cd "$WT"`, keep the failed attempt out of the result file evidence block, and continue with the ad-hoc verifier/result refresh when the corrected run passes. Do not post a blocker or rerun finalization for a cwd mistake.

**Compound create-and-test trap:** when adding the detached worktree and running pytest in the same shell command, `git worktree add ... "$WT"` does not change cwd. A line like `python3 -m pytest plugins/pwp/tests/...` immediately after worktree creation still runs from the original shell cwd unless you explicitly `cd "$WT"` or use `git -C "$WT"` where applicable. Prefer this shape:

```bash
git -C "$REPO" worktree add --detach "$WT" origin/ned/<ISSUE>
printf 'WORKTREE=%s\n' "$WT" > /tmp/<issue>_worktree.path
cd "$WT"
python3 -m pytest plugins/pwp/tests/<focused_test>.py -v --tb=short | tee /tmp/<issue>_pytest.out
```

If you accidentally capture a wrong-cwd failure before the corrected pass, mention it only as a known false-negative note in the local RESULT.md; the durable evidence block should show the corrected `rootdir: $WT`, `PYTEST_EXIT=0`, verifier markers, and cleanup markers.

**`set -e` evidence-file trap:** if a create-and-test compound command runs pytest under `set -euo pipefail` and pytest fails before the worktree path or evidence markers are written, the shell aborts and later refresh steps may not know which temporary worktree was created. Write durable scalars such as `WORKTREE=...`, `HEAD=...`, and `/tmp/<issue>_worktree.path` **before** any command that may fail, or split creation and testing into separate terminal calls. This is especially important when using `pytest ... | tee /tmp/<issue>_pytest.out`: with `pipefail`, a failing pytest exits the whole compound command before trailing `printf`/cleanup lines run.

For `/tmp/hermes-verify-*` scripts, prefer the stable pattern: write the verifier file under `/tmp` (via `write_file`/skill script), then run it with `terminal(..., workdir=/tmp/<worktree>)` after the worktree already exists. Inside the verifier, insert the worktree root into `sys.path` before importing repo packages. If namespace-package imports such as `plugins.pwp` still fail from the temp-script context, do not declare the task blocked; either run the verifier from the worktree cwd via terminal or import the target module by file path with `importlib.util.spec_from_file_location`, while still running the focused pytest command from the worktree cwd.

## Nonessential inspection under `set -e`: don't abort before verification

During an already-finalized redispatch refresh, the only hard evidence required is the Linear/remote completion check, focused pytest/verifier output, result-file refresh, and cleanup. Treat extra inspection commands as optional. A `git diff --name-only origin/deploy-fresh...HEAD` inside a `set -e` compound command can abort the whole verification if the branch has no merge base with `origin/deploy-fresh`, even though the task branch is valid and tests would pass.

Preferred pattern:

- Run focused pytest/verifier first, without optional diff/listing commands in the same `set -e` chain.
- If you want a changed-file list, make it nonfatal:
  ```bash
  git merge-base --is-ancestor origin/deploy-fresh HEAD \
    && git diff --name-only origin/deploy-fresh...HEAD \
    || git diff --name-only HEAD~1..HEAD || true
  ```
- Do not report the no-merge-base diff failure as a task blocker when Linear is `In Review`, the remote branch exists, and the focused verifier passes.

## Fixture rule for ad-hoc verifiers

Use a **schema-valid fixture from the target branch/test file**, not a hand-rolled minimal object.

Concrete failure mode: for PWP token compiler verification, `compile_tokens_to_css()` validates the full design-token schema (`colors`, `typography.font_families`, `font_sizes`, `font_weights`, `line_heights`, `spacing`, `radii`, `shadows`, `animations`). A minimal token object or guessed typography shape fails validation before it tests determinism. Copy/adapt the fixture shape from `plugins/pwp/tests/test_compiler_determinism.py` before asserting deterministic sorted `--pwp-*` output.

If the first verifier attempt fails because the fixture is invalid, fix the fixture and rerun the verifier. Record the failed attempt only as a pitfall in the local result; do not report it as a task blocker when the corrected verifier passes.

## Verifier output ordering pitfall: Python buffering can hide metadata behind pytest

When an ad-hoc verifier prints `VERIFIER_SCRIPT=` / `TESTED_COMMAND=` and then runs `subprocess.run(pytest...)`, Python stdout buffering can cause the pytest output to appear **before** the metadata in captured logs even though the `print()` calls occur first. This is confusing for later detector/cron reviews that expect the verifier path and command at the top of the block.

Preferred fixes:

- Run the verifier as `python3 -u /tmp/hermes-verify-...py`, or
- use `print(..., flush=True)` for verifier metadata lines before invoking pytest, or
- call `sys.stdout.flush()` immediately before `subprocess.run(...)`.

If the output is already captured out of order but contains `VERIFIER_SCRIPT=`, `TESTED_COMMAND=`, `ASSERTION_SUMMARY=`, `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, `VERIFIER_RUN_EXIT=0`, and `CLEANUP_EXISTS=no`, treat the verification as valid; fix the buffering pattern on the next refresh rather than rerunning solely for aesthetics.

## Lock-command argument pitfall: do not pass repo name as agent

The Prismatic skeleton examples may show `node /home/ubuntu/.antigravity/swarm.js lock <path> prismatic-engine ned`. In the live `swarm.js` contract, the lock command interprets the second positional argument as the owner/agent. Passing `prismatic-engine` there creates a lock owned by `prismatic-engine`, then `heartbeat <path> ned` fails with `No lock found ... by ned`.

Use the two-argument form for Ned locks unless the script help says otherwise:

```bash
node /home/ubuntu/.antigravity/swarm.js lock plugins/pwp ned
node /home/ubuntu/.antigravity/swarm.js heartbeat plugins/pwp ned
node /home/ubuntu/.antigravity/swarm.js unlock plugins/pwp ned
```

If you already created the wrong-owner lock, unlock it explicitly with that owner, then reacquire correctly:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock plugins/pwp prismatic-engine || true
node /home/ubuntu/.antigravity/swarm.js lock plugins/pwp ned
```

This is a workflow pitfall, not a task blocker. Fix the lock owner and continue; do not rerun finalization or touch unrelated dirty checkout state just because the first heartbeat failed.

## Linear env-loading and shell expansion pitfalls in refresh passes

For already-finalized redispatch refreshes that need a Linear state/attachment re-query, prefer the known-good Ned backup env file when available:

```bash
set -a
if [ -r /home/ubuntu/.hermes/profiles/ned/.env.bak ]; then
  . /home/ubuntu/.hermes/profiles/ned/.env.bak
elif [ -r /home/ubuntu/.hermes/profiles/orchestrator/.env ]; then
  . /home/ubuntu/.hermes/profiles/orchestrator/.env
fi
set +a
```

Then verify without leaking the key:

```bash
KEYLEN=0
if [ -n "${LINEAR_API_KEY:-}" ]; then KEYLEN=${#LINEAR_API_KEY}; fi
printf 'LINEAR_KEY_LEN=%s\n' "$KEYLEN"
```

Do **not** use `${#LINEAR_API_KEY:-0}` — Bash treats that as invalid parameter expansion (`bad substitution`). Also avoid clever one-line `grep && source ... || source ...` chains for env selection in cron refreshes; a parse/source failure can abort the evidence pass before the actual verification runs. Keep env loading boring and explicit.

## Cleanup/status shell pitfall: avoid nested command substitution for booleans

During a redispatch refresh, cleanup is intentionally boring but still part of the evidence contract. Do **not** generate cleanup markers with nested command substitutions like:

```bash
printf 'WORKTREE_EXISTS=%s\n' "$([ -e "$WT" ] && echo yes || echo no)"
```

In cron/tool-wrapper shells this can trip quoting/eval edge cases and abort the command before the worktree is removed or the Linear re-check is captured. Prefer explicit, idempotent `if` blocks that can be safely rerun after a partial failure:

```bash
if [ -d "$WT" ]; then git -C /home/ubuntu/work/prismatic-engine worktree remove --force "$WT"; fi
git -C /home/ubuntu/work/prismatic-engine worktree prune
if [ -e "$WT" ]; then echo WORKTREE_EXISTS=yes; else echo WORKTREE_EXISTS=no; fi | tee /tmp/<issue>_cleanup.out
if [ -e /tmp/hermes-verify-<issue>.py ]; then echo VERIFIER_EXISTS=yes; else echo VERIFIER_EXISTS=no; fi | tee -a /tmp/<issue>_cleanup.out
```

If the first cleanup/status command fails before cleanup, rerun the explicit idempotent block, then proceed with result-file refresh. Treat the failed cleanup-marker attempt as a workflow pitfall, not a task blocker, when the rerun confirms `WORKTREE_EXISTS=no` and `VERIFIER_EXISTS=no`.

**Do not remove the worktree from inside itself.** If a cleanup command runs with `workdir=/tmp/prismatic-<issue>-croncheck-*` and then removes that same directory, later shell/tool calls in the same process can emit `pwd: error retrieving current directory: getcwd: cannot access parent directories`. That noise can leak into `/tmp/issue-batches/<ISSUE>_RESULT.md` and make a successful refresh look dirty. Run cleanup/status commands from a stable directory such as `/home/ubuntu/work` or the main repo, or immediately patch the result file to replace the `pwd` warning with explicit markers (`WORKTREE_EXISTS=no`, `VERIFIER_EXISTS=no`, `WORKTREE_REGISTRY_MATCHES=0`) after a separate registry check confirms no stale worktree remains.

## Linear comment ordering pitfall: do not treat `comments(last: 1)` as latest evidence

During an already-finalized redispatch refresh, a Linear GraphQL recheck using `comments(last: 1)` returned an older finalization comment timestamp even though `comments(last: 5)` in the same session showed newer comments. Do not use `nodes[-1]` from a one-comment query as authoritative "latest comment" evidence.

Preferred pattern:

- Query `comments(last: 5)` or `comments(last: 10)` for refresh evidence.
- Compute `max(createdAt)` client-side when you need the latest comment timestamp.
- Treat the issue state (`In Review`), PR attachment, remote branch SHA, focused pytest, verifier markers, and cleanup markers as the completion signals; comment timestamp is secondary context.
- If comment-order evidence looks stale while state/attachment/remote/test evidence is complete, do not rerun `finalize_task.sh` just to chase a timestamp.

## Result-file write pitfall: shell expansion can silently corrupt Markdown evidence

When refreshing `/tmp/issue-batches/<ISSUE>_RESULT.md` from a shell command, do **not** embed a large Markdown template containing backticks in an unquoted here-doc or shell-expanded Python string. Backticks such as `` `ned/GRO-3676` `` and `` `--pwp-*` `` are command substitution in the shell; the result file can be overwritten with blanks and `command not found` noise even when the verification itself passed.

Safer pattern:

1. Capture pytest/verifier output into temporary files (`/tmp/<issue>_pytest.out`, `/tmp/<issue>_verify.out`).
2. Export only scalar values (`HEAD_SHA`, `SHORT_SHA`, `TS`, exit codes, output-file paths).
3. Use a **single-quoted** Python here-doc (`python3 - <<'PY'`) that reads the output files and writes the Markdown result. Because the delimiter is quoted, backticks inside the Python triple-quoted Markdown template are not interpreted by the shell.
4. Re-read the result file after writing it. If lines like `Branch:` or `Linear state verified:` are blank, repair the result before ending the cron pass.

This is a workflow pitfall, not a task blocker: rerun the verifier with a valid fixture, rewrite the result safely, and continue.

## Result-file evidence capture pitfall: avoid `read_file` line-number prefixes

When refreshing `/tmp/issue-batches/<ISSUE>_RESULT.md`, do not embed Hermes `read_file(...)` output directly as verifier/test evidence. `read_file` returns lines prefixed as `1|...`, `2|...`; those prefixes are useful for inspection but pollute Markdown evidence blocks and can confuse later detector passes that expect raw markers like `VERIFIER_SCRIPT=...`, `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, and `CLEANUP_EXISTS=no`.

Preferred patterns:

- Capture command output with `tee /tmp/<issue>_pytest.out` / `tee /tmp/<issue>_verify.out`.
- When composing the result file, read those files as raw text from Python (`Path('/tmp/<file>').read_text()`), or use a terminal command that prints raw file contents inside a quoted Python here-doc.
- Use Hermes `read_file` only to inspect the finished result file after writing it, not as the source text inserted into the result.
- If a result file already contains numbered evidence blocks but the required raw markers are still present, treat it as nonfatal for the current pass; clean the capture pattern on the next refresh rather than posting duplicate Linear comments.

## Split-output marker pitfall: merge verifier-run exit back into the result

If the verifier command captures the Python verifier output and the shell wrapper's pipeline exit marker into separate files, the Markdown composer can accidentally include `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, and `CLEANUP_EXISTS=no` while omitting the wrapper-level `VERIFIER_RUN_EXIT=0`. Example pattern that creates the split:

```bash
REPO="$WT" python3 -u /tmp/hermes-verify-<issue>.py | tee /tmp/<issue>_verify.out
printf 'VERIFIER_RUN_EXIT=%s\n' "${PIPESTATUS[0]}" | tee /tmp/<issue>_verify.exit
```

When using this pattern, append `/tmp/<issue>_verify.exit` into the ad-hoc verifier evidence block before the final marker check. Then verify all required markers together:

```text
PYTEST_EXIT=0
VERIFICATION_EXIT=0
CLEANUP_EXISTS=no
VERIFIER_RUN_EXIT=0
WORKTREE_EXISTS=no
VERIFIER_EXISTS=no
```

If the first result write omitted `VERIFIER_RUN_EXIT=0` but the separate `.exit` file shows success, patch the local result file only; do not rerun verification or post duplicate Linear comments solely for this evidence-formatting miss.

## Concurrent result-file refresh warning

`write_file` may warn that `/tmp/issue-batches/<ISSUE>_RESULT.md` was modified by a sibling subagent. Treat this as a merge-safety warning, not as task failure. If the result file was read earlier in the pass and the new write is a complete evidence refresh with newer timestamp, focused pytest, ad-hoc verifier output, and post-refresh Linear check, the overwrite is acceptable **only after** immediately re-reading the file and confirming the expected fields survived. If the sibling change might contain distinct evidence or blocker text, re-read before writing and merge rather than replacing.

Checklist after any sibling-write warning:

1. Re-read `/tmp/issue-batches/<ISSUE>_RESULT.md` after the write.
2. Confirm branch, remote SHA, Linear state, PR attachment, verifier exit, and cleanup status are present.
3. If any field is blank/missing, repair the result file before returning `[SILENT]`.
4. Do not post duplicate Linear comments solely because the local result file had a concurrent refresh race.

## Final silent-response gate

Before returning `[SILENT]` on an already-finalized redispatch, do one last local consistency check after rewriting `/tmp/issue-batches/<ISSUE>_RESULT.md`:

1. Re-read the result file and confirm the required markers survived the write: `PYTEST_DIRECT_EXIT=0`, `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, `VERIFIER_RUN_EXIT=0`, `CLEANUP_EXISTS=no`, `WORKTREE_EXISTS=no`, `VERIFIER_EXISTS=no`, and `Linear state verified: `In Review``.
2. Check the repo worktree registry for leftover `/tmp/prismatic-<issue>-croncheck-*` entries (for example `git worktree list --porcelain | grep -F 'prismatic-<issue>' || true`). The result file can say cleanup succeeded while a stale worktree remains from an interrupted earlier pass; the registry check is the final proof.
3. Confirm the shared checkout still only contains the pre-existing unrelated dirt. Do not stage, commit, unlock, or finalize anything in the shared checkout for this refresh class.

If all three hold and Linear/remote/PR evidence is still complete, the correct final cron response remains exactly `[SILENT]`. Do not send a human-facing recap just because fresh local evidence was written.

## Result-file shape

Record enough fresh evidence for the next redispatch pass:

```markdown
# <ISSUE> Result

Status: already finalized / cron verification refreshed

Branch: `ned/<ISSUE>`
Commit: `<short-sha>`
Remote branch: `origin/ned/<ISSUE>` at `<full-sha>`
Linear state verified: `In Review`
Last refresh: `<UTC timestamp>`

Notes:
- Existing implementation is already present and pushed.
- Linear is already `In Review` with prior finalization comments/PR attachment.
- Current shared checkout was dirty/on another branch, so verification used a clean detached worktree.
- No new code changes were required; no duplicate Linear finalization comment was posted.

Focused pytest output:
```text
...
```

Ad-hoc verifier output:
```text
VERIFIER_SCRIPT=/tmp/hermes-verify-...
TESTED_COMMAND=...
ASSERTION_SUMMARY=...
PYTEST_EXIT=0
VERIFICATION_EXIT=0
VERIFIER_RUN_EXIT=0
CLEANUP_EXISTS=no
```
```

## 2026-07-10 redispatch confirmation

A later cron redispatch of GRO-3676 arrived after the task was already `In Review`, with `origin/ned/GRO-3676` at `966bfc93cdafd942f42fa3ab195ca54cb89dd277`, prior finalization comments/PR attachment present, and the shared checkout dirty on another Ned task branch. Correct handling was:

1. Re-query Linear and remote branch to confirm all completion signals still held.
2. Add a detached clean worktree from `origin/ned/GRO-3676`.
3. Run the focused pytest command in that worktree:
   `python3 -m pytest plugins/pwp/tests/test_compiler_determinism.py -v --tb=short`.
4. Run a fresh `/tmp/hermes-verify-gro3676-cron.py` verifier that asserted deterministic sorted CSS output directly, then ran the focused pytest command and deleted itself.
5. Refresh `/tmp/issue-batches/GRO-3676_RESULT.md` with the new timestamp/evidence.
6. Remove/prune the temporary worktree.
7. Return `[SILENT]` because there was no new blocker, no new code, and no reason to duplicate Linear comments or rerun `finalize_task.sh`.

A subsequent same-night redispatch repeated the same state (`In Review`, remote branch intact, PR attachment present, shared checkout dirty on another task). The correct behavior stayed the same: refresh evidence from a clean detached worktree, update only `/tmp/issue-batches/GRO-3676_RESULT.md`, remove the worktree, re-query Linear for state/attachment, and return `[SILENT]`. Do not let repeated scanner pings create duplicate Linear comments or duplicate `finalize_task.sh` runs.

A later same-night refresh at `2026-07-10T05:29:00Z` confirmed the repeatability of the pattern when `/tmp/issue-batches/GRO-3676_RESULT.md` already contained a recent refresh from minutes earlier. The correct action was still to gather fresh evidence, not to trust the stale local result blindly: create `/tmp/prismatic-gro3676-croncheck-*`, run the focused pytest in that worktree, run a fresh `/tmp/hermes-verify-gro3676-cron.py` ad-hoc verifier with `python3 -u`, rewrite the result file with raw `tee` output, remove/prune the worktree, confirm `WORKTREE_EXISTS=no` and `VERIFIER_EXISTS=no`, and return `[SILENT]` because Linear/remote/local completion signals remained complete.

A subsequent redispatch at `2026-07-10T05:44:33Z` reconfirmed the same steady-state behavior after multiple local result refreshes in the same night: Linear remained `In Review`, `origin/ned/GRO-3676` still pointed at `966bfc93cdafd942f42fa3ab195ca54cb89dd277`, PR attachment `#198` remained present, focused pytest still passed from a clean detached worktree, and the ad-hoc verifier still produced `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, and `CLEANUP_EXISTS=no`. The shared checkout was dirty on `ned/GRO-3672`, so the refresh deliberately avoided switching or staging anything there and updated only `/tmp/issue-batches/GRO-3676_RESULT.md`.

This confirms the pattern is not just for the first duplicate dispatch: repeated redispatches should still produce fresh local evidence when requested, but should stay silent externally when Linear/remote/local state remains complete.

A later 2026-07-10 redispatch with the pre-run warning `tasks piling up` confirmed the same rule: queue pressure is not evidence that the specific issue regressed. Re-query Linear and the remote branch, verify from a detached worktree, refresh `/tmp/issue-batches/<ISSUE>_RESULT.md`, and suppress external delivery when the completion signals still hold. The result file should include cleanup markers as first-class evidence (`WORKTREE_EXISTS=no`, `VERIFIER_EXISTS=no`, plus `CLEANUP_EXISTS=no` from the verifier) and a quick required-marker check after writing it; otherwise future detector passes can misread a successful refresh as incomplete cleanup.

A subsequent same-warning redispatch at `2026-07-10T06:29:18Z` reinforced that the local result file timestamp being only minutes old is not itself enough when the cron contract explicitly asks for execution. The safe refresh still creates a new clean worktree, reruns the focused pytest and `/tmp/hermes-verify-gro3676-cron.py` verifier with `python3 -u`, captures raw `tee` output into the result file, removes the worktree, rechecks Linear state/PR attachment, and validates required result-file markers (`PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, `CLEANUP_EXISTS=no`, `WORKTREE_EXISTS=no`, `VERIFIER_EXISTS=no`) before returning `[SILENT]`. This is the steady-state loop for noisy redispatches: fresh local evidence, zero duplicate Linear/finalize noise.

A follow-up redispatch at `2026-07-10T07:21:31Z` confirmed the same rule under heavy queue pressure (`tasks piling up` alert, 15 open Ned issues). The prior local refresh was only ~7 minutes old and already showed complete signals, but the correct action was still not to trust it blindly: re-query Linear (`In Review`, PR attachment present), verify the remote branch SHA, run focused pytest from a new detached worktree, run a freshly-written `/tmp/hermes-verify-gro3676-cron.py` ad-hoc verifier, rewrite `/tmp/issue-batches/GRO-3676_RESULT.md`, remove/prune the worktree, and return exactly `[SILENT]`. Queue pressure changes scheduling priority; it does not justify duplicate `finalize_task.sh`, duplicate Linear comments, or skipping fresh evidence when the cron contract explicitly asks for execution.

A subsequent same-queue-pressure redispatch at `2026-07-10T07:28:30Z` added one formatting lesson: when the prior result file is already complete, it is still worth rebuilding it from fresh raw `tee` output after the clean-worktree pytest/verifier pass and then immediately re-reading it. The post-write marker check should include both test/verifier success and cleanup/state markers: `PYTEST_DIRECT_EXIT=0`, `PYTEST_EXIT=0`, `VERIFICATION_EXIT=0`, `VERIFIER_RUN_EXIT=0`, `CLEANUP_EXISTS=no`, `WORKTREE_EXISTS=no`, `VERIFIER_EXISTS=no`, and `Linear state verified: \`In Review\``. If all are present and Linear/remote/PR evidence still holds, the final cron response remains exactly `[SILENT]`; do not post a human-facing recap just because fresh local evidence was written.

A later redispatch at `2026-07-10T08:13:50Z` clarified one scanner-output nuance: a pre-run line like `[NED-DISPATCH] Silent exit (no changes).` is not itself a permission to skip when the same preamble still includes `TASK:<ISSUE>`. Treat it like queue-pressure noise: re-check the three completion signals, create a new detached worktree from `origin/ned/<ISSUE>`, rerun focused pytest plus a fresh `/tmp/hermes-verify-*` verifier, refresh `/tmp/issue-batches/<ISSUE>_RESULT.md`, remove/prune the worktree, confirm registry/marker cleanup, and then return exactly `[SILENT]` if nothing changed. The dispatch script's silence means it found no new queue mutation; it does not satisfy the cron contract's fresh-evidence requirement for an explicitly redispatched task.

## Why this exists

Redispatched already-finalized issues otherwise tempt the agent to touch a dirty shared checkout, rerun `finalize_task.sh`, and post duplicate Linear comments. The safer class-level behavior is: verify Linear/remote/local completion signals, run fresh focused evidence from a clean detached worktree, refresh the local result file, clean up, and suppress user delivery unless a new blocker exists.