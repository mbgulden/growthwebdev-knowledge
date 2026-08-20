# BN-00 repair after revoked clean review and second-review gate

Use this reference when a Prismatic self-build candidate previously marked `CLEAN` is later contradicted by an async or independent reviewer.

## Trigger

- A delegated/external reviewer returns `REPAIR` after George already produced a local `CLEAN` or opened a PR.
- The blocker is a narrow semantic edge case, especially in journal-tail, freshness, timestamp-window, or Git-wrapper behavior.
- A same-task repair produces a new candidate before PR head is updated.

## Required response pattern

1. **Reproduce the blocker on the exact previously reviewed head.** Do not accept the review abstractly; bind `PR_HEAD`, `EXPECTED`, `ACTUAL`, `RESULT`, `LOG`, and `LOG_SHA256`.
2. **Revoke the prior clean verdict explicitly.** Write a superseding artifact or PR comment so the old `CLEAN` receipt cannot be mistaken for merge authority.
3. **Keep the PR held on the old head.** Do not fast-forward the public PR to the repair candidate until the new candidate has fresh independent exact-head review.
4. **Repair the same task only.** Keep successor tasks `QUEUED_NOT_DISPATCHED`; do not use the defect as a reason to launch another issue.
5. **Preserve the repair candidate before review.** Create a local preserve ref/bundle, record tree/path/parent, and classify any hung producer as failed-after-result rather than completion.
6. **Run George’s adversarial suite, then require a second fresh independent review.** A local green probe after a missed edge is not enough to push or approve; transition durable state to `EXACT_HEAD_REVIEW_PENDING` with `ACTIVE_PRODUCERS=0`.
7. **Only after the fresh reviewer returns `CLEAN` and the exact head/tree/path allowlist is unchanged:** write a superseding source review, fast-forward the PR, then rerun/read hosted CI truth.

## Journal-tail adversarial checklist

For `read_recent_text`/journal-tail candidates, include all of these cases before clean review:

- empty file;
- zero, negative, and tiny byte budgets;
- one complete line exactly at budget;
- newest complete line larger than budget;
- complete lines followed by an unterminated suffix;
- file containing only one unterminated ASCII line;
- file containing only one unterminated multibyte line;
- byte window beginning inside a line or multibyte sequence;
- CRLF line endings;
- invalid UTF-8 fail-closed behavior if contract-relevant;
- multibyte complete suffix and multibyte unterminated suffix.

For timestamp and Git wrappers, pair the tail checklist with:

- `Z`, positive-offset, and negative-offset timestamps normalized to UTC;
- exact lower/upper bounds and just-outside exclusions;
- proof that `now` is sampled once;
- successful Git stderr suppression;
- failed Git behavior preserved.

## Proof packet shape

```text
STATUS=PARTIAL|PASS|BLOCKED
PREVIOUS_CLEAN_REVOKED=<old head/review path>
BLOCKER_REPRO=<expected/actual/log/sha>
REPAIR_HEAD=<sha>
REPAIR_TREE=<tree>
PARENT=<sha>
PATHS=<allowlist>
LOCAL_ADVERSARIAL=<PASS/FAIL log sha>
CANONICAL=<pass/fail counts and inherited-baseline note>
HOSTED_CI=<green|red|billing-blocked|pending>
INDEPENDENT_REVIEW=<delegation id and pending/clean/repair>
PR_STATE=<held old head|fast-forwarded exact head>
NOT_CLAIMING=<merge/deploy/successor/cap/production claims>
```

## Non-claims

- Local targeted green does not equal merge approval after a missed edge.
- A producer `RESULT.md` plus useful commit is not completion if the worker remains alive after result.
- Hosted CI billing/preflight failure is not product-test failure, but it is also not CI green.
- PR opened/updated is not merge authorization unless exact-head independent review and required CI have passed.
