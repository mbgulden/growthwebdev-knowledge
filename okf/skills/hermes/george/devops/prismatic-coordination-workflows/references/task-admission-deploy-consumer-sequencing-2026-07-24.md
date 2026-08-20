# Task admission deployment + consumer sequencing lesson — 2026-07-24

Use this reference when closing a dashboard admission PR and immediately moving into the one-shot consumer slice under the Prismatic North Star: **Don't trust, Verify**.

## Reconcile before deployment

When a late/async independent review returns `CLEAN_TO_MERGE` for an exact candidate after several repair cycles:

1. Bind the review to the exact candidate SHA and tree.
2. Bind the merge commit to the same tree when GitHub creates a merge commit.
3. Update the durable handoff/checkpoint before or immediately after deployment authorization.
4. Preserve CI/billing boundaries separately from test failure boundaries. If GitHub jobs were billing-blocked, say `not CI green`, not `failed`.
5. Treat deployment authorization for the admitted dashboard slice as **not** automatically authorizing the next consumer/producer deployment.

## Fixture-only deployment smoke pattern

For an admission-control deployment before real task launch:

- restart from a detached immutable release checkout and dedicated venv;
- verify runtime process cwd/executable point at the release/venv, not a mutable dev worktree;
- provision owner-only external auth/policy/env/database files;
- perform a fixture admission only;
- assert unauthenticated and wrong-credential readback fail, authenticated readback succeeds;
- assert first admission returns `201`, exact replay returns `200`, durable counts are exactly `1/1/1`;
- assert outbox status remains pending and legacy event publication did not occur;
- assert no launch occurred and no producer started;
- assert credentials are absent from response, SQLite, and logs;
- perform browser/render proof for visible dashboard state when the feature is UI-visible.

If the first smoke fails because the gateway is not yet bound or the fixture payload is invalid, classify it as harness/startup readiness until rerun proves otherwise. Keep the failed log path, but do not overclaim product failure without a corrected fixture/readiness rerun.

## Consumer slice design checklist

A one-shot admission consumer should not be a loose poller. Require:

- atomic `BEGIN IMMEDIATE` claim;
- singleton writer lease enforcing cap one;
- stable claim id and monotonic attempt tracking;
- complete immutable admission/outbox tuple revalidation at claim time;
- second complete revalidation immediately before launcher execution;
- append-only lifecycle ledger;
- stable event ID used as the launcher idempotency key;
- retryable vs terminal failure classification;
- expired-lease crash recovery;
- launch-start crash replay using the same stable event key;
- heartbeat/lease renewal during long launches;
- owner-only launcher config validation;
- absolute canonical non-writable executable validation;
- shell-free subprocess execution;
- bounded launcher output;
- process-group termination on timeout;
- strict launch receipt schema.

## Verification/acceptance boundary

Before claiming the consumer is accepted, require:

1. focused tests for the consumer contract;
2. package/wheel or isolated import proof when applicable;
3. canonical project test suite proof if the change is intended for merge;
4. exact-head independent review of the committed candidate;
5. repair/review loops until exact-head `CLEAN_TO_MERGE`;
6. detached release proof after merge;
7. separate explicit authorization before consumer deployment/restart;
8. no real task admission or producer launch unless separately authorized.

## Reporting shape

Use Michael's preferred Prismatic report order:

1. Problem found
2. What changed
3. Why it matters
4. Current state
5. Exact next move
6. IDs/hashes/logs for traceability

Lead with behavior and impact before SHA/log detail. Always include explicit non-claims for: CI green, canonical suite, deployment, consumer acceptance, producer launch, and real task admission when any are not proven.
