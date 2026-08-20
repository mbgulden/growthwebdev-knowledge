# Stale Async Review Triage for Prismatic Exact-Hash Work

Use this when Fred/Ned/AGY/delegated reviewers return `BLOCKED` or `CLEAN` after the candidate artifact has already changed.

## Rule

A review verdict is binding only for the exact artifact/commit/script SHA it reviewed. Do not apply a stale `CLEAN` to a newer artifact, and do not dismiss a stale `BLOCKED` without checking whether its finding still describes the current artifact.

## Workflow

1. Record the returned review's reviewed SHA/path and verdict.
2. Compare it to the current candidate SHA/path.
3. If hashes differ, label the review explicitly:

```text
REVIEW_STATE=STALE
STALE_SHA=<reviewed sha>
CURRENT_SHA=<current sha>
VERDICT_SCOPE=obsolete artifact only
```

4. Triage each finding:
   - **Still valid**: port the concern into the current artifact/script, rerun local proof, update SHA, and request fresh independent review.
   - **Already fixed**: cite the current exact evidence that closes it; do not relaunch the same fix.
   - **No longer applicable**: explain the changed invariant or removed surface.
5. Never execute, merge, deploy, or authorize mutation based on a stale `CLEAN` or on a fixed stale `BLOCKED` without a new exact-SHA review.
6. For repeated async returns, keep a concise stale-review ledger so chat stays readable and each next review targets only the current artifact.

## Reporting packet

```text
STATUS=PARTIAL|BLOCKED|PASS
REVIEW_STATE=<FRESH|STALE>
STALE_SHA=<sha or n/a>
CURRENT_SHA=<sha>
VALID_FINDINGS_PORTED=<count/list>
LOCAL_PROOF=<command/log/marker>
NEXT_REVIEW=<delegation id or required reviewer>
NOT_CLAIMING=<execution/merge/deploy/approval until fresh exact review>
```

## Pitfalls

- Do not call a stale `BLOCKED` verdict wrong just because the artifact changed; mine it for portable defects first.
- Do not keep re-reviewing an obsolete SHA after patching. Recompute and report the current SHA every time.
- Do not let stale-review churn authorize a live write. Live mutation still needs explicit Michael authorization and fresh exact-SHA `CLEAN` when that gate applies.
