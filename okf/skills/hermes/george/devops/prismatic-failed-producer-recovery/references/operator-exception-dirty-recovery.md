# Operator exception for reviewed dirty recovery blocked by deployed admission

## Trigger

Use this reference when all are true:

- A failed or interrupted producer left a reviewed dirty same-worktree recovery checkpoint.
- The dirty checkpoint has already been independently reproduced and accepted as a recovery contract/checkpoint, without producer-success claims.
- The currently deployed admission release rejects the required dirty tracked worktree before admission, e.g. `worktree_dirty`/HTTP 422.
- The user explicitly authorizes a narrow operator exception.

This is not a normal producer-recovery path. It is a fail-closed escape hatch for a compatibility deadlock between a reviewed dirty checkpoint and deployed clean-worktree admission policy.

## Required gates

1. **Accept and bind the deployed blocker first**
   - Freeze a compatibility blocker artifact.
   - Prove the deployed parser/policy rejects the exact dirty checkpoint in disposable storage.
   - Independently review the blocker and resolution choices.
   - Bind the blocker by exact path, SHA-256, and review id/verdict (for example `<delegation>:CLEAN/PASS`). A pathname alone is a mutable reference and is not sufficient.
   - In the operator-exception artifact, require blocker SHA/review revalidation as a **pre-stage gate**. Any blocker-byte or accepted-review-state mismatch stops before staging.
   - Keep future event count zero.

2. **Get explicit human authorization**
   - Authorization must be scoped to a single option, e.g. exact-byte operator commit exception.
   - It must stop before push, PR, merge, deploy/restart, event, producer, cron/timer, production DB, or Linear write unless separately authorized.

3. **Revalidate exact bytes before commit**
   - Verify base/head/tree/parent, tracked diff hash, path allowlist, and reviewed blob hashes.
   - Stage only the reviewed implementation/test files.
   - Exclude operational metadata such as `.prismatic-task/` and `STARTED.md` unless the authorization explicitly includes them.

4. **Create one normal descendant commit**
   - No amend, reset, rebase, stash, clean, force-update, or path drift.
   - Record commit, tree, parent, subject, tracked status, exact committed paths, and blob identities.
   - Do not claim producer completion or fabricate `RESULT.md`.

5. **Reproduce exact head in a fresh archive**
   - Use `git archive <HEAD>` into a disposable directory.
   - Prove no `.git` directory is present.
   - Prove 4/4 (or allowed-path count) blob identity against the accepted dirty checkpoint.
   - Run focused proof from the archive: diff-check, compile, lint, format, and focused tests.

6. **Classify canonical separately**
   - If full `tests/` is non-green, rerun/compare the exact parent baseline under the same command and interpreter.
   - Report `BLOCKED_CANONICAL_BASELINE_NO_REPAIR_REGRESSIONS` only when candidate and parent failure identities match and candidate-only failures are zero.
   - Never call this canonical green.

7. **Freeze an exact-head review packet**
   - Include authorization quote/boundary, blocker review, commit/tree/parent, exact blobs, focused logs, canonical baseline logs, and non-claims.
   - Dispatch fresh independent review of the exact head and implementation behavior; stale dirty-checkpoint reviews do not count for the committed candidate.

8. **Stop while review is pending**
   - Update handoff with exact head, proof hashes, review delegation id, and hard stop.
   - No additional edit/amend/commit, push, PR, merge, deploy/restart, event, producer, cron/timer, production DB, or Linear action.

## Minimum proof fields

```text
RESULT=PARTIAL_EXACT_HEAD_REVIEW_PENDING
AUTHORIZATION=<user-scoped option>
BLOCKER_REVIEW=<delegation>:CLEAN/PASS
HEAD=<candidate commit>
TREE=<tree>
PARENT=<parent>
PATHS=<exact committed path list>
BLOB_MATCH=<n>/<n>
TRACKED_STATUS=clean
METADATA_EXCLUDED=true
FOCUSED=<pass counts and log sha>
CANONICAL=<candidate counts, parent counts, failed-set comparison>
REPAIR_ONLY_REGRESSIONS=0
PRODUCER_COMPLETED=false
PRODUCER_RESULT=false
REVIEW=<delegation>:pending
NOT_CLAIMING=independent acceptance, producer completion, producer result, canonical green, task completion, push, PR, merge, deployment/restart, event, producer, cron/timer, production DB, or Linear write
```

## Pitfalls

- **Exception creep:** Do not treat the operator commit as general permission to bypass admission.
- **Mutable blocker reference:** If the exception artifact references a compatibility blocker only by file path, block it. Freeze a new version that records the blocker hash and accepted review id/verdict, and requires both to match before any `git add`.
- **Review reuse drift:** A blocked exception version remains evidence, not a reusable approval. Preserve `Vn` and create `Vn+1`; fresh reviewers must review the complete new artifact, not only the patched paragraph.
- **Byte drift:** Any source edit after dirty-checkpoint acceptance invalidates the exact-byte exception; return to artifact review.
- **Producer impersonation:** A normal descendant commit created by the operator is not a producer `RESULT` and must not be presented as one.
- **Baseline overclaim:** Identical inherited canonical failures permit no-regression classification only, not suite green.
- **Metadata contamination:** Untracked operational metadata should stay out of the commit unless separately reviewed and authorized.
