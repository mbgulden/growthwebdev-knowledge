# Failed producer candidate proof boundary

When a producer terminates failed but leaves useful source diffs, compact verification packets must separate three states:

1. **Producer contract result** — failed/not completed unless the required result artifact exists and validates.
2. **Recovered source candidate** — may be independently reproducible after containment, formatting, tests, and commit.
3. **Deployable artifact** — only after exact-head independent review, push/PR/live-head verification, exact-tree merge, and deployment provenance proof.

## Same-task operator recovery pattern

If the producer timed out or failed after leaving uncommitted diffs, recovery is allowed only as a bounded candidate-construction step, not as producer success:

1. Read the task contract and existing diffs.
2. Preserve only in-scope implementation/test/package-data edits.
3. Remove undeclared artifacts such as ad-hoc `STARTED.md`/scratch files before candidate commit.
4. Repair concrete contract defects found during operator inspection; do not launch a second producer unless explicitly authorized.
5. Run focused behavior proof, package/resource proof, and the project-defined canonical local target when feasible.
6. Commit once, record `HEAD`, tree, exact changed paths, worktree cleanliness, and log digests.
7. Dispatch/read an independent exact-head review before acceptance/push/merge/deploy/dependent-task admission.

Do not let a green focused/canonical rerun erase the producer failure. Report both:

```text
PRODUCER_STATUS=failed
PRODUCER_COMPLETED=false
CANDIDATE_VERIFICATION=PASS
REVIEW=<pending|CLEAN|BLOCKED>
DEPLOYED=false
NOT_CLAIMING=producer PASS; completed result artifact; deployment
```

If standing deployment authorization exists, phrase it as contingent authorization:

```text
DEPLOYMENT_AUTHORIZED=true_after_CLEAN_exact_review_and_merge
```

This keeps Michael's preferred boundary clear: authorization is preserved, but raw failed-run output is not promoted without review.
