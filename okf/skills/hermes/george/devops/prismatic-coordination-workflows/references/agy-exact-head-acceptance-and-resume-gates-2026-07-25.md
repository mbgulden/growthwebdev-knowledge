# AGY exact-head acceptance and GRO resume gate pattern — 2026-07-25

Use for Prismatic Engine AGY runtime/dashboard changes before opening PRs or resuming queued AGY work.

## Durable lessons

- **No wall-clock cap is a product contract.** AGY runs may take as long as needed. Dashboard activity classification is evidence for operators, not a kill switch. Stopping requires an explicit exact-run cancel.
- **Bind every acceptance claim to exact commit and tree.** Record both `COMMIT=<sha>` and `TREE=<sha>` before independent review, PR creation, or downstream resumption.
- **Separate proof classes.** Focused AGY regressions, OKF/docs validation, public/release smoke, clean-room wheel proof, canonical `tests/`, browser/dashboard proof, hosted CI, and production proof are distinct. Passing one does not imply the others.
- **Canonical fresh-env proof may need verifier-environment repair.** Missing optional dev dependencies or packaging tools in the verifier environment are setup blockers, not product blockers. Repair the verifier environment, rerun exact-head, and preserve the failed setup logs without treating them as candidate failures.
- **AGY auth preflight should use the same runtime home expected for the producer.** If an isolated profile home lacks credentials, do not launch work from it. Run a tiny `--print` preflight from the active AGY home, record only `PASS/FAIL`, log path, and hash; never expose token contents.
- **Resume dependent tasks only after exact-head review is CLEAN.** It is safe to prepare a resume preflight while review is active, but do not launch the next producer until independent exact-head review accepts the candidate.
- **Preserve existing admitted events.** For a paused task such as GRO-4210, reconcile the existing admitted event as the next attempt instead of creating a duplicate admission unless explicitly directed.

## Recommended closeout packet additions

```text
COMMIT=<candidate commit>
TREE=<candidate tree>
FOCUSED_AND_AGY_RELATED=<count passed>
CANONICAL_TESTS=<count passed/skipped/warnings/subtests>
CANONICAL_LOG=<path>
CANONICAL_LOG_SHA256=<sha256>
WHEEL_CLEAN_ROOM=<result>
PUBLIC_SMOKE=<result>
RELEASE_SMOKE=<result>
AUTH_PREFLIGHT=<PASS|FAIL|not applicable>
AUTH_LOG=<path if applicable>
AUTH_LOG_SHA256=<sha256 if applicable>
ACTIVE_PRODUCERS=<count before dependent resume>
ATTEMPT2_STARTED=<true|false>
NOT_CLAIMING=<review clean, PR, merge, deploy, production proof, cap increase unless actually done>
```

## Launch gate for downstream AGY repair work

1. Verify candidate commit/tree and final local gates.
2. Dispatch independent exact-head review.
3. While review runs, inspect the downstream admitted event/worktree and prepare a preflight report only.
4. Run AGY auth/model/protocol preflight from the intended runtime home.
5. If and only if review returns CLEAN, reconcile the existing admitted event as the next attempt and start exactly one cap-one producer.
6. Monitor via durable dashboard activity receipts; do not impose elapsed-time or inactivity termination.
