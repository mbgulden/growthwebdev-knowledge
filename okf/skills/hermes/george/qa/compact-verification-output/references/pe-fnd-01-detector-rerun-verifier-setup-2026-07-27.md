# PE-FND-01 detector rerun: verifier setup failure vs product failure

## Trigger

After documentation edits, the Hermes verification guard repeated:

- changed paths were four Markdown docs/index files;
- warning said no canonical test/lint/build command was detected;
- required a temporary `/tmp/hermes-verify-*` script using OS-safe `tempfile` path;
- required ad-hoc labeling rather than suite-green overclaim.

## Useful pattern

1. Create the temporary verifier with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` or `NamedTemporaryFile`.
2. Make the terminal transcript visibly run:
   - `python3 "$VERIFY"` for content/behavior assertions;
   - the relevant docs validator or project checker;
   - focused scoped tests when available;
   - `git diff --check` and `git status --porcelain`.
3. Assert exact changed paths, exact HEAD/tree, clean worktree, index links, and behavior markers in the changed docs.
4. Remove the verifier and report `VERIFIER_CLEANUP=PASS`.
5. If an older failed temporary verifier remains in `/tmp`, remove it and have the rerun assert the stale verifier is absent; report `STALE_VERIFIER_CLEANUP=PASS`.
6. Label as `AD_HOC_OR_CANONICAL=ad-hoc targeted detector rerun`; do not call the scoped validator/tests canonical full-suite green.

## Pitfall observed

The first rerun failed because the custom verifier asserted the wrong wording (`canonical run state`) while the actual ADR section was `Canonical AGY run`. Treat this as **verifier setup failure**, not product failure:

- inspect the failed log;
- correct the assertion to match the intended artifact contract;
- rerun the whole closeout sequence, not only the failed assertion;
- report both the setup failure boundary and the final passing proof.

## Final proof packet shape

```text
COMMAND=python3 /tmp/hermes-verify-...
COMMAND=<project docs validator>
COMMAND=<focused pytest/check command>
COMMAND=git diff --check HEAD^ && git status --porcelain=v1
RESULT=PASS
LOG=/tmp/<name>.log
LOG_SHA256=<sha256>
SCOPE=exact changed paths and mapped behavior markers
AD_HOC_OR_CANONICAL=ad-hoc targeted detector rerun; focused project commands passed, not canonical full suite
VERIFIER_CLEANUP=PASS
STALE_VERIFIER_CLEANUP=PASS
WORKTREE_CLEAN=PASS
NOT_CLAIMING=canonical full-suite green, independent review decision, PR, merge, release, deployment, production proof
MARKER=<TASK>_DETECTOR_RERUN_OK
```

## Stop condition

If the same guard repeats after this current-turn visible compliance rerun with unchanged files and cleanup proven, stop rerunning identical checks. Preserve the log SHA and classify the repeat as detector non-recognition, with explicit non-claims.

When the repeat arrives after a repaired exact-head commit, include immutable state in the closeout so the boundary is audit-friendly:

```text
HEAD=<exact repaired commit>
TREE=<exact repaired tree>
WORKTREE_STATUS=CLEAN
LAST_VERIFICATION_LOG_SHA256=<sha256 of latest passing log>
CHANGED_DOC_SHA256=<sha256 for each changed doc/report artifact>
POST_VERIFICATION_MUTATION=NO
DETECTOR_CLASSIFICATION=NON_RECOGNITION_AFTER_REPEATED_COMPLIANT_RERUNS
```

Do not reclassify the work as canonical suite green just because focused pytest/docs validators passed. Keep the pending independent-review gate separate from detector compliance.
