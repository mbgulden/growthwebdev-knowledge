# Failed producer candidate recovery

Use this when an assigned-agent/AGY producer terminates failed or times out after leaving source changes or a spool/result fragment.

## Rule

A failed producer run is not PASS and is not deployment evidence, even if it leaves useful source changes. Treat the output as a bounded partial candidate that must be recovered, independently verified, committed, and reviewed before any push/merge/deploy.

## Recovery sequence

1. **Freeze the boundary**
   - Record the producer status, exit code, missing/invalid contract artifact, and current changed paths.
   - State explicitly: `PRODUCER_COMPLETED=false`; `DEPLOYED=false`; `NOT_CLAIMING=producer PASS`.
2. **Contain the candidate**
   - Remove only clearly unintended untracked run markers (for example a transient `STARTED.md`) after verifying they are not required artifacts.
   - Require changed paths to match the task's allowed path set. If extra paths remain, block and review before editing.
3. **Independently reproduce**
   - Run `git diff --check`, focused task tests, adjacent regression tests, Ruff check/format-check, and then canonical/full suite when feasible.
   - If Ruff format is the only failure, format only the allowed candidate paths and rerun focused/static proof.
4. **Commit only after proof**
   - Stage exactly the allowed candidate paths.
   - Commit to bind `HEAD`, `TREE`, parent/base, and a clean worktree.
   - Run a fresh post-commit ad-hoc verifier with an OS-safe `hermes-verify-*` temp script and log SHA-256.
5. **Review before publication**
   - Dispatch independent exact-head review with the task contract, exact head/tree/base, changed paths, proof logs, and non-claims.
   - Do not push, open PR, merge, deploy, invoke consumers, mutate policy, or launch agents until review returns `CLEAN`.
6. **Deploy only after exact merge**
   - Standing deployment authorization may be recorded, but it is contingent on CLEAN review, exact live PR head verification, exact-tree merge proof, and source/runtime provenance verification.

## Compact proof fields

```text
PRODUCER_STATUS=failed
PRODUCER_COMPLETED=false
CANDIDATE_HEAD=<sha>
CANDIDATE_TREE=<tree>
FOCUSED=<summary>
CANONICAL=<summary>
POSTCOMMIT_AD_HOC_LOG=<path>
REVIEW=<delegation id pending|CLEAN|BLOCKED>
DEPLOYMENT_AUTHORIZED=<true|false>
DEPLOYED=false
NOT_CLAIMING=producer PASS; deployment; live result correctness
```

## Pitfalls

- Do not let an explicit deploy request override the review gate when the producer did not complete its own contract.
- Do not count a spool fragment or source diff as a completed producer result unless the required `RESULT.md`/contract artifact exists and validates.
- Do not use historical/global claim counts as active-event proof; scope durable-state assertions to the event/launch under review.
- Preserve the task's exact allowed path set; formatting or repair must not broaden the candidate silently.
