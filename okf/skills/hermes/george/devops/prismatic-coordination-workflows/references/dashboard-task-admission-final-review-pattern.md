# Dashboard Task Admission — Final Review / Fresh Verification Pattern

Use this reference when coordinating a Prismatic dashboard task-admission slice or any similarly sensitive dashboard-to-control-plane admission feature.

## Durable lesson

A dashboard admission feature is not merge-ready merely because the API/UI looks correct. It needs three separate gates:

1. **Admission contract proof** — strict exact tuple, operator auth, no launch in HTTP request, durable ledger/outbox/audit, idempotent exact replay, stale/moved-worktree conflict handling, and no token retention.
2. **Durability/concurrency proof** — database-level immutability for admission/audit history plus concurrent submit stress that proves no duplicate rows/events and no SQLite setup lock race.
3. **Exact-head independent review** — final reviewer verdict must bind to the exact current commit/tree after every repair. Earlier `CLEAN`/`REPAIR` reviews are stale once the head moves.

## Specific pitfalls captured from the session

- API-level immutability is not enough. Add database-enforced protections, e.g. SQLite triggers that fail closed on `UPDATE`/`DELETE` for durable admission rows and append-only audit rows.
- SQLite WAL/journal setup can race under concurrent admission requests. Serialize one-time DB setup and use a bounded busy timeout; then run repeated concurrent-submit stress, not just one request/replay test.
- A launch-free admission endpoint should write a pending outbox event only. It must not call the producer, legacy dispatcher, or event consumer during the POST request.
- Browser proof should verify transient bearer/token clearing and durable readback/replay behavior, not only that the form renders.
- If GitHub Actions fails before jobs start because of billing/spending infrastructure, report it as `INFRA_BLOCKED_NO_JOB_START`; do not call it product failure and do not call it CI green.
- After final report/checkpoint/deployment-gate Markdown edits, run a fresh ad-hoc closeout verifier against both source behavior markers and the report artifacts. Label it ad-hoc targeted, not canonical suite green.
- If Hermes repeats the same post-edit verification warning after a same-turn compliant rerun, perform one visible rerun first; after that, preserve log hashes and state detector non-recognition instead of looping indefinitely.

## Required proof packet fields for this class

```text
COMMAND=<exact focused/canonical command or grouped summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<admission API/UI/db/concurrency/report artifacts>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
HEAD=<exact commit>
TREE=<exact tree>
FINAL_INDEPENDENT_REVIEW=<pending|CLEAN_TO_MERGE|REPAIR|BLOCKED + reviewer id>
GITHUB_CI=<PASS|FAIL|INFRA_BLOCKED_NO_JOB_START|not run>
NOT_CLAIMING=<independent acceptance, merge, deployment, restart, live admission, producer launch unless actually done>
MARKER=<stable marker>
```

## Merge/deploy boundary

Standing merge authorization can apply only after exact-head local proof and exact-head independent acceptance. Deployment/restart remains a separate explicit gate. A deployment-gate artifact should say what runtime config, smoke proof, stop conditions, and one-shot consumer slice are still required.
