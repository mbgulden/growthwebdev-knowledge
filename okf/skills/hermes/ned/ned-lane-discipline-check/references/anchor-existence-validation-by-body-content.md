---
title: Anchor-existence validation by body content (not user.id)
type: reference
status: current
linear_anchors: [GRO-146]
codified: 2026-06-30
codified_by: ned (Pass-N+33)
---

# Anchor-existence validation by body content

## Problem

Ned posts Linear comments via the orchestrator's Linear API key, which authenticates as **Michael Gulden** (`user.id: 4a8a76b2-63f2-4706-b501-3ab2f0709866`). **All sub-agent comments — Ned, Kai, AGY, etc. — post under the same `user.id`** because they share the orchestrator's Linear app-token.

When validating whether a prior-pass Ned-authored anchor comment actually landed on an issue, filtering by `user.id`/`user.name` will return **zero matches** because the comment was posted under Michael's identity, not a "Ned" identity.

## Naive (wrong) validation recipe

```bash
# WRONG: will return zero matches for Ned-authored comments
query='{"query":"{ issue(id: \"GRO-XXX\") { comments(last: 10) { nodes { id createdAt user { name id } } } } }"}'
# Filter on user.id == "ned-id" or user.name == "Ned" → empty result
# Conclude "anchor didn't land" → incorrectly trigger full fresh-misroute-batch disposal recipe
```

## Correct validation recipe — grep body for Ned-authored markers

```bash
# CORRECT: validate by body content, not user.id
query='{"query":"{ issue(id: \"GRO-XXX\") { comments(last: 10) { nodes { id createdAt body } } } }"}'
# For each comment node, grep the body for 2+ of these Ned-authored markers:
#   - "Pass-N+\d+"                (e.g. "Pass-N+32", "Pass-N+18")
#   - "Standing cure"             (verbatim cure-section header)
#   - "Lane partition walk"       (per-issue triage table header)
#   - "HARD-SKIP `finalize_task.sh`" (ratchet verdict marker)
#   - "rotation-equivalence ratchet" (criterion-(c) gate)
#   - "fresh-misroute-batch-disposal" (Pass-N+19 recipe marker)
# 2+ matches = Ned-authored anchor confirmed regardless of user.id
```

## Why this matters for the rotation-equivalence ratchet

The Pass-N+25 sustained-byte-identical-feed ratchet recipe requires the prior-pass anchor to exist and name all 10 IDs. A false-negative on anchor-existence flips criterion (c) from HOLD to FAIL → triggers the full fresh-misroute-batch disposal recipe unnecessarily (write audit doc + post fresh anchor comment + commit + lock/unlock ≈ 15-30 tool calls per false-positive vs ~6 tool calls for the lightweight ratchet recipe).

**False-positive cost:** ~24 tool calls wasted per occurrence. Pass-N+33 was a near-miss — I almost concluded the Pass-N+32 anchor didn't land based on user.id filtering. Re-checking the body saved the false-positive.

## Edge case — `terminal()` JSON-escape breakage on body fields

GraphQL queries that include `body` in fragments sometimes produce stdout that fails `json.loads` in `terminal()` output:

- Error: `Invalid \escape: line 1 column NNNN (char NNNN)` (when body contains backslashes)
- Error: `Invalid control character at: line 1 column NNNN (char NNNN)` (when body contains literal newlines)

**Workaround when you need body content but `terminal()` parsing fails:**

1. Query WITHOUT `body` first to identify target comment IDs and `createdAt` timestamps:
   ```bash
   query='{"query":"{ issue(id: \"GRO-XXX\") { comments(last: 10) { nodes { id createdAt } } } }"}'
   ```
2. Validate anchor-existence by `createdAt` timestamp alone if the pass log already records the anchor's `createdAt` (no body content needed).
3. If body content IS needed, use the file-based JSON payload pattern:
   ```bash
   write_file /tmp/anchor_query.json '{"query":"{ issue(id: \"GRO-XXX\") { comments(last: 10) { nodes { id body createdAt } } } }"}'
   curl -s "https://api.linear.app/graphql" \
     -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
     --data-binary @/tmp/anchor_query.json
   # Extract body manually via Python: read stdout, json.loads with strict=False, then walk escape sequences
   ```

**Simpler path (recommended for ratchet validation):** validate by `createdAt` timestamp only. The pass log records the anchor's `createdAt` at the moment the anchor comment is posted. A subsequent cron pass can re-query the issue and confirm a comment exists at that exact `createdAt` without parsing body content. This is what Pass-N+33 actually did.

## Marker reference — Ned-authored anchor comment template

For future Ned passes writing anchor comments, the canonical Ned-authored anchor template includes these markers (in order of appearance):

1. **Lane partition walk table** — per-issue triage verdict + correct lane
2. **Rotation-equivalence ratchet criteria walk** — (a) + (b) + (c) HOLD/FAIL each
3. **Standing cure (verbatim from Pass-N+N)** — relabel + dispatcher-patch + pool-growth
4. **Codification updates** — new heuristics or detector extensions
5. **HARD-SKIP `finalize_task.sh`** — ratchet verdict marker
6. **Recommended Michael action** — specific label changes + GRO-559 reference

If a comment body contains ≥3 of these 6 markers, it's a Ned-authored anchor.

## Cross-reference

- `references/recurring-batch-suppress-pitfalls.md` — related pitfalls (updatedAt drift, byte-identical feed cadence)
- `references/curator-flag-stale-backlog-misroute-fingerprint.md` — Pass-N+32 batch disposition
- `references/pass-n25-sustained-byte-identical-feed-ratchet.md` — Pass-N+25 lightweight 3-step recipe
- SKILL.md Pass-N+33 SILENT-pass update entry (2026-06-30 ~03:02Z)

## Standalone evidence

Pass-N+33 commit `552889f8` on `ned/gro-485-triage-pass-1` (audit doc `scripts/ops/gro-146-165-batch-routing-33rd-pass-infra-findings.md`) — first application of the body-content validation pattern, replaced a naive user.id filter that would have triggered a false-positive full fresh-misroute-batch disposal (~24 wasted tool calls).