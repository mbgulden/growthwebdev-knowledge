# GRO-3696 already-finalized RESULT refresh pattern

Use this when a cron scanner redispatches an issue that is already genuinely complete, but the local `/tmp/issue-batches/<ISSUE>_RESULT.md` artifact is missing or stale.

## Preconditions

- Linear issue is already `In Review` (or otherwise final-review state).
- Remote `origin/ned/<ISSUE>` branch exists.
- PR/finalization evidence already exists in Linear comments.
- The shared checkout is dirty or on another task, so touching it would risk cross-task contamination.

## Safe refresh sequence

1. Query Linear and confirm state, labels, recent comments, and PR/finalization evidence.
2. Fetch/check remote branch exists: `git ls-remote --heads origin ned/<ISSUE>`.
3. Create a detached clean worktree from the remote branch, not from the dirty shared checkout:
   ```bash
   WT=$(mktemp -d /tmp/ned-<ISSUE>-refresh-XXXXXX)
   rmdir "$WT"
   git -C /home/ubuntu/work/prismatic-engine worktree add --detach "$WT" origin/ned/<ISSUE>
   ```
4. Run focused verification in the detached worktree.
5. If the detector may require fresh targeted evidence, create a `/tmp/hermes-verify-*` script that asserts the changed behavior directly, prints:
   - verifier path
   - repo/worktree path
   - tested command
   - command exit code
   - assertion booleans
   - `verification_exit=0`
   - cleanup status
6. Write `/tmp/issue-batches/<ISSUE>_RESULT.md` with Linear state, PR, branch SHA, focused test output, ad-hoc verifier output, and shared-checkout note.
7. Remove the detached worktree and verifier script.
8. Do **not** rerun `finalize_task.sh` or post duplicate Linear comments when Linear is already correctly finalized and no blocker exists.
9. Verify cleanup explicitly after removing the detached worktree and verifier script. If the first cleanup check still shows the worktree path exists, run an explicit `git -C <repo> worktree list --porcelain` + `git -C <repo> worktree remove <WT> --force`, then re-check the path before finishing.
10. Final cron response should be exactly `[SILENT]` if nothing new needs Michael's attention.

## Pitfalls caught on GRO-3696

### Already-finalized is not necessarily CI-clean

On redispatch, do not stop at `Linear=In Review` + remote branch + prior finalization comments + refreshed local verifier. Query the PR check rollup (`gh pr view <PR> --json statusCheckRollup` or `gh pr checks <PR>`) before returning `[SILENT]`. If a required/visible PR check is failing, treat the redispatch as a repair pass, not a no-op refresh.

Concrete GRO-3696 sequence:

1. Linear was already `In Review`, branch `origin/ned/GRO-3696` existed, and focused local PWP verification passed.
2. `gh pr view 203 --json statusCheckRollup` showed `Verify shipped plugins load` failing.
3. Rerunning/inspecting the GitHub Actions job exposed package metadata gaps, not PWP diff logic failures:
   - `PluginLoader import failed: No module named 'packaging'` → `packaging` belongs in root runtime dependencies because `prismatic.core.registry.PluginLoader` imports it.
   - Next rerun: `No module named pytest` → the workflow installs `pip install -e ".[dev]"`, so the root `dev` extra must include `pytest`.
   - Local clean venv then exposed `jsonschema not installed` warnings that broke PWP validator tests → `jsonschema` is a runtime dependency for theme schema-contract validation, not a local-machine assumption.
4. Fix on the existing task branch, commit with `[Ned] ... (#GRO-3696)`, push to `origin/ned/<issue>`, rerun/observe PR checks, then rerun `finalize_task.sh` and verify Linear state/comment.

Reusable rule: for already-finalized redispatches with an open PR, the completion-signal set includes **PR checks green or explicitly explained**. A failing PR check is new actionable work even if Linear is already `In Review`.

### GitHub workflow reproduction path for dependency metadata failures

When a GitHub check fails with missing Python modules, reproduce the workflow install path in a clean venv from a clean worktree, not the warm/shared shell:

```bash
python3 -m venv /tmp/<issue>-venv
. /tmp/<issue>-venv/bin/activate
python -m pip install -q --upgrade pip setuptools wheel
pip install -q -e '.[dev]'
python -m prismatic.quality.plugin_load
python -m pytest tests/test_plugin_load_gate.py -v
PYTHONPATH=$PWD pytest plugins/pwp/tests/test_theme_validator.py plugins/pwp/tests/test_theme_diff.py -q
```

This catches dependency declarations that the shared Hermes environment masks. Capture the dependency fix in docs in the same commit (for GRO-3696: `prismatic/quality/README.md` documented runtime/dev dependency contracts).

### `pwp theme diff --json` success contract

Do not assume a nonzero command exit from `pwp theme diff --json` for breaking diffs. In GRO-3696 the JSON diff command returned `0` while expressing failure through `payload["ok"] == false` and populated `breakingChanges`. The ad-hoc verifier should assert the command's actual contract: JSON emitted successfully, `ok` is false, expected versions are detected, and the compatibility breaking change appears in `breakingChanges`.

Compatibility breaking changes are only reported when the CLI is asked to evaluate a target engine. A plain `pwp theme diff --from <before> --to <after> --json` can return `ok: true` and `breakingChanges: []` for an `engineCompatibility` range change, because without `--engine-version` it is only reporting the manifest delta. For the GRO-3696 refresh verifier, pass `--engine-version 0.3.0` while mutating the target theme to `engineCompatibility: ">=0.4.0"`; the expected contract is process exit `0`, JSON parse success, `ok: false`, and one `kind: "compatibility"` breaking change.

### Linear recent-comments query depth

When checking for prior finalization evidence, do not rely on `comments(last: 2)` as the sole evidence query. Linear comment ordering can be surprising in small windows; a `last: 2` check may surface older AGY start/partial-result comments while omitting the actual Ned finalization comments seen in a wider query. Use `comments(last: 10)` or `comments(last: 15)` and sort/inspect by `createdAt` before deciding that finalization evidence is absent.

### Detached worktree cleanup verification

After writing the local RESULT refresh, remove the detached worktree and verify both the filesystem path and `git worktree list --porcelain`. If a combined cleanup command reports the worktree still exists, rerun the removal explicitly and print the before/after worktree-list stanza. Do not leave `/tmp/ned-<ISSUE>-refresh-*` worktrees behind; they can block later refresh/finalize passes or confuse branch ownership.

Ad-hoc verifier cleanup must survive verifier failure. If the verifier command can exit nonzero while the wrapper shell has `set -e`, a later `rm -f "$VERIFIER"` line will never run and stale `/tmp/hermes-verify-<ISSUE>-*` scripts will remain. Use one of these patterns: `trap 'rm -f "$VERIFIER"' EXIT`, or run the verifier with `set +e; ...; rc=$?; set -e; rm -f "$VERIFIER"; exit $rc`. Always finish with `find /tmp -maxdepth 1 -name 'hermes-verify-<ISSUE>-*' -print` and remove stale failed-attempt scripts before claiming cleanup.

Run cleanup and post-cleanup verification from a stable directory outside the temporary worktree (for example `workdir=/home/ubuntu/work`). If the shell's current directory is inside the temp worktree and you remove it, a later `pwd`/`git worktree list` segment may print `pwd: error retrieving current directory: getcwd: cannot access parent directories` even though cleanup succeeded. Treat that as a verification-shell artifact: rerun only the cleanup check from a stable cwd, confirm the worktree path and verifier are gone, then record the clean result.

### Ad-hoc verifier fixture validity

For `pwp theme diff` refresh verifiers, do not hand-roll a minimal `theme.json` unless the goal is to test validator failures. The command validates full theme packages before computing compatibility diffs; a minimal manifest without `$schema`, entrypoints, modules, and module contracts exits nonzero with schema errors and no `breakingChanges`, which is a bad verifier for GRO-3696 behavior. Copy the branch fixture `plugins/pwp/tests/fixtures/pwp_theme/valid_theme` into temporary `before`/`after` directories, then mutate only the fields under test (for example `version` and `engineCompatibility`). Keep `engineCompatibility` in the schema's actual string form (for example `">=9.9.0"`), not an object like `{ "min": "9.9.0" }`; the object form turns the verifier into a schema-validation failure (`command_exit=1`, no `breakingChanges`) instead of exercising the compatibility resolver. That keeps the verifier focused on diff/compatibility behavior and preserves the real command contract: process exit `0`, payload `ok=false`, and populated `breakingChanges` for an incompatible target engine.

### `/tmp/issue-batches/*_RESULT.md` sibling-write warning

When refreshing an already-finalized redispatch, `write_file` can warn that a sibling subagent modified `/tmp/issue-batches/<ISSUE>_RESULT.md` and this agent has not read it. Treat that warning as a merge-risk signal, not harmless noise. Immediately read the current RESULT file and preserve any sibling evidence before rewriting or patching. Prefer writing an initial draft only after a read, then use `patch` for cleanup/status updates. Do not silently overwrite another worker's verifier output in a queue-pressure cron run.

### RESULT artifact self-check before suppressing delivery

Before returning `[SILENT]` on an already-finalized redispatch, re-read the refreshed `/tmp/issue-batches/<ISSUE>_RESULT.md` header and completion-signal section. If any evidence line contains a tool/setup failure instead of the intended signal (for example `gh pr view` run outside a git repo prints `fatal: not a git repository`), repair the artifact with the verified value before finishing. For GitHub PR evidence, run `gh pr view <PR> ...` from the repository checkout or pass `--repo owner/name`; do not leave a failed helper command embedded in the local RESULT file just because the core verification passed.
