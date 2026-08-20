# Exact-byte checkpoint archive/environment verification

Use this reference when a failed/interrupted Prismatic producer has dirty bytes that Michael explicitly authorizes as a single exact-byte checkpoint commit, but the implementation is still blocked and not accepted.

## Session-derived pattern

1. **Bind the exception before staging**
   - Verify exact base/head/tree/parent relationship.
   - Verify the tracked path allowlist.
   - Verify every frozen blob hash.
   - Verify the blocker artifact by SHA-256 and prior review id/verdict.
   - Verify `.prismatic-task/` and operational metadata remain untracked/excluded.

2. **Use the same diff serialization as the frozen contract**
   - If the patch SHA mismatches while every resulting blob hash matches, check the diff format before treating it as byte drift.
   - In this session the mismatch was Git diff serialization: the frozen checkpoint used `git diff --binary --full-index`; the first comparison used abbreviated object IDs.
   - Recompute the patch with the exact frozen command shape before blocking or restaging.

3. **Commit only the exact reviewed bytes**
   - Stage only the frozen tracked path allowlist.
   - Commit as a normal descendant; no reset/rebase/amend/clean/stash/force update.
   - Keep the subject/body specified by the operator exception.
   - Do not push, PR, merge, deploy, update Linear, or create a second event unless separately authorized.

4. **Reproduce the committed checkpoint from a Git-free archive**
   - Materialize with `git archive <checkpoint-head> | tar -x` into a disposable directory.
   - Assert `.git` is absent.
   - Recompute committed file hashes from archive bytes, not the mutable worktree.
   - Run compile/lint/format/static checks against archive bytes.

5. **Use a fresh install environment when dependencies changed**
   - Do not use an old production/runtime venv as acceptance evidence if the checkpoint adds a dependency in `pyproject.toml`.
   - If focused tests fail on `ModuleNotFoundError` for a newly declared dependency, classify that attempt as verifier environment setup, not product failure.
   - Build a disposable venv from the archive and install the committed package extras needed for verification, e.g. `pip install --no-cache-dir "$ARCHIVE[release]"`, then run `pip check` and rerun the full focused proof from the start.

6. **Compare canonical boundary under one interpreter/environment**
   - If canonical stops on collection errors, archive the exact checkpoint and exact base, then run both with the same fresh venv and same pytest command.
   - Compare exact error node IDs, not just counts or tail text.
   - If node IDs are identical, report `no checkpoint-only canonical collection regression`; do not call canonical green.

7. **Report the boundary as checkpoint integrity, not implementation acceptance**
   - `CLEAN/PASS` can mean only: exact checkpoint integrity and suitability as a durable blocked repair base.
   - Keep known technical blockers explicit, especially migration-prevalidation, SQLite foreign-key pragma timing, and missing true prior-version fixtures.

## Proof packet fields

```text
FOUNDATIONAL_CHECKPOINT_HEAD=<sha>
FOUNDATIONAL_CHECKPOINT_TREE=<tree>
FOUNDATIONAL_CHECKPOINT_PARENT=<sha>
FOUNDATIONAL_CHECKPOINT_PATCH_SHA256=<sha256 from exact --binary --full-index command>
FOUNDATIONAL_CHECKPOINT_PATHS=<allowlist>
FOUNDATIONAL_CHECKPOINT_BLOBS=<path:sha256 list>
FOUNDATIONAL_CHECKPOINT_GIT_FREE_ARCHIVE=<path>
FOUNDATIONAL_CHECKPOINT_FOCUSED_ENV=<venv/install proof + pytest result>
FOUNDATIONAL_CHECKPOINT_CANONICAL_BOUNDARY=<base-vs-checkpoint same-env comparison>
FOUNDATIONAL_CHECKPOINT_KNOWN_BLOCKER=<technical blocker summary>
NOT_CLAIMING=producer success,producer result,implementation acceptance,candidate acceptance,canonical green,repair completion,PR,merge,deploy,Linear write
```

## Pitfalls

- **Patch hash false negative**: identical resulting blobs can still produce a different `git diff` hash if the verifier omits `--full-index` or otherwise changes diff serialization.
- **Production venv dependency lag**: a production venv from an older release may not include a newly declared dependency. Treat missing dependency in that venv as setup-only; install from the committed archive into a disposable venv and rerun.
- **Count-only comparison**: focused pass counts can differ across environments/plugins. Prefer exact command, exact node IDs, and explicit scope over forcing historical counts to match.
- **Integrity/acceptance collapse**: a clean checkpoint commit is only a durable base for a separate repair. It does not make the failed producer successful and does not approve the implementation.
