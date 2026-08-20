# AGY Portable Customization Security Review Repair Pattern

Use this when an independent review of an AGY/native-agent customization bundle finds security or durability flaws after local green proof.

## Trigger

- A review is stale by hash but reproduces behavior that still exists in the current candidate.
- A final exact-head review reports high-risk file-operation bugs, especially around installer force/backup/rollback/audit/manifest behavior.
- The PR already has proof, but review findings invalidate the trust model.

## Operator pattern

1. **Treat reproduced security findings as blockers even if the review head is stale.** Re-check whether the vulnerable path still exists in the current head; do not dismiss because the SHA changed.
2. **Simplify the trust model instead of layering narrow checks.** For customization bundles, mutable user manifest data must be inventory/status only, not overwrite/delete authorization.
3. **Make file operations fail closed before mutation.** Preflight ancestor collisions, non-regular files, symlinks, FIFOs, stale manifests, and platform boundaries before any install/uninstall writes.
4. **Use no-follow and exclusive create semantics for backups and managed-file writes.** Avoid timestamp-only backup names; ensure collision resistance and no symlink traversal.
5. **Make installs/uninstalls transactional.** Stage the plan, then rollback created files, previous bytes, and file modes if any step fails. Fault-inject rollback tests for pre-existing files, not only new files.
6. **Audit secret-safe metadata only.** Never dereference symlinks or include raw private frontmatter/config values in audit output.
7. **Version incompatible manifest semantics.** If behavior changes from digest authorization to exact shipped-bundle inventory, bump the schema/format identifier and update docs/changelog.
8. **Add adversarial tests for every reproduced path.** Cover symlink escape, mutable-manifest tampering, ancestor collision, audit disclosure, FIFO/non-regular input, rollback after partial write, and manifest-only adoption accounting.
9. **Separate verifier setup failures from candidate failures.** Missing release extras or guessed test paths are harness errors; repair the harness and rerun exact-head rather than overclaiming product failure.
10. **Keep PR draft/review-gated until independent exact-head re-review is clean.** Local canonical, wheel, canary, and direct exploit proof are not substitutes for the assigned independent gate.

## Proof classes to keep distinct

- focused adversarial regression tests;
- direct exploit-reproduction verifier outside pytest;
- canonical `pytest tests/`;
- non-editable installed-wheel release smoke with the correct extras;
- distribution fresh-install smoke;
- sandbox canary;
- OKF/docs validation;
- hosted GitHub CI if available;
- independent exact-head security review.

## Closeout packet expectations

Report:

```text
HEAD=<exact commit>
TREE=<exact tree>
PR_STATE=draft/open until independent review is clean
AD_HOC_OR_CANONICAL=<per gate, never conflated>
NOT_CLAIMING=merge, deploy, hosted CI if unavailable, independent CLEAN_TO_MERGE until returned
```

If proof-packet/checkpoint files or PR body are edited after final verification, run one final ad-hoc verifier that reads back the checkpoint/PR-bound evidence, asserts log digests and review-gate language, confirms worktree clean and remote head match, then cleans up `/tmp/hermes-verify-*`.
