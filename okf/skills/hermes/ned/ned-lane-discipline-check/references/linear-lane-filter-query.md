---
name: ned-lane-discipline-check-linear-queries
description: Canonical Linear GraphQL filter shapes for Ned's cron pickup lane-discipline check. Working as of 2026-06-29.
---

# Linear GraphQL — working filter shapes for Ned's pickup triage

## Pitfall: `identifier` filter is undefined

The natural-looking filter does **not** work:

```graphql
# ❌ GRAPHQL_VALIDATION_FAILED: Field "identifier" is not defined by type "IssueFilter"
issues(filter:{identifier:{eq:"GRO-537"}}, first: 1){ ... }
```

Use `id` (which accepts the human-readable identifier like `"GRO-537"`):

```graphql
# ✅ works
issues(filter:{id:{eq:"GRO-537"}}, first: 1){ nodes{ identifier title description state{ name } labels{ nodes{ name } } comments(first: 20){ nodes{ body createdAt user{ name } } } } }
```

Confirmed working: 2026-06-29 ~0545Z during pass-14 of the GRO-537 misroute chain.

## Pitfall: `id:` value is case-sensitive — must be UPPERCASE

The `id` filter accepts the human-readable identifier like `"GRO-537"`, but the value **must be uppercase**. Lowercasing the ID (e.g. via `"GRO-537".lower()` → `"gro-537"`) returns HTTP 400 with no useful error body.

```graphql
# ✅ works
issue(id: "GRO-485") { identifier ... }

# ❌ HTTP 400, empty error body
issue(id: "gro-485") { identifier ... }
```

**Confirmed failing:** 2026-06-29 ~16:31Z during pass-25 of the Batch B misroute chain. A hand-rolled GraphQL probe loop in `execute_code` built issue IDs via `i.lower()` and every call returned 400. Switching to the literal uppercase identifier string fixed it.

**Rule of thumb:** keep the issue ID in its canonical uppercase form throughout the probe (don't transform it). The `anchor_5a5_item3_scorer.py` script gets this right because it passes `--anchor GRO-485` as-is.

## Lane-filtered pickup queue (the one Ned actually wants)

The cron pre-run script emits a **global top-N** that includes every issue with the `agent:ned` label, regardless of whether it's in Ned's infra lane. To get the *true* lane-filtered queue, apply both filters:

```graphql
query {
  issues(
    filter: {
      labels: { name: { eq: "agent:ned" } }
      state:  { name: { nin: ["Done", "Cancelled"] } }
    }
    first: 20
  ) {
    nodes {
      identifier
      title
      state { name }
    }
  }
}
```

Returns 20 results on 2026-06-29. Compare against the pre-run script's "Found N" count — if they diverge, the script's count is the r128 scanner-preamble pattern (global top-N, not lane-filtered). Apply suppress-class logic.

## Comment-thread triage check

Before building anything, pull the last 5–10 comments and grep for:

- `out[- ]of[- ]lane` (case-insensitive)
- `BLOCKED_COMMENT:\brelabel\b`
- "Dequeued", "misroute", "not infrastructure"

If any hit, treat the issue as triaged-out and run `finalize_task.sh` for the bookkeeping, then `[SILENT]`.

## Finalize guard confirmation (2026-06-29)

`finalize_task.sh` step 3 has an out-of-lane guard (added 2026-06-28) that scans the comment thread for the same markers and **skips** the Linear In Review transition when found. The evidence comment is still posted. Verified today on GRO-537 — state stayed at "Todo", guard log line:

```
[finalize] STEP 3: transitioning GRO-537 to 'In Review' state
[finalize]   SKIP transition: issue appears out-of-lane (BLOCKED_COMMENT:\brelabel\b; out[- ]of[- ]lane; out[- ]of[- ]lane). No state change.
```

This is the canonical safety net for recurring misroute pickups. The agent does **not** need to duplicate this guard inline — just call `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE_ID> ned/<ISSUE_ID> ned` and let the script handle the state-transition decision.

## Reference chain for related artifacts

These paths are referenced by SKILL.md but were missing on disk as of 2026-06-29:

- `scripts/suppress_class_detect.py` — canonical detector (planned)
- `scripts/ops/gro-537-triage-pass-NN-batch-recurring.md` — pass-N chain log (planned)
- `references/recurring-batch-suppress-2026-06-29.md` — quick card (planned)

If a future session needs them, create them based on the patterns documented here. Do not block a `[SILENT]` decision on their absence.