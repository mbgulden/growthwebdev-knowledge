# Ned r154 — Batch B 4th-pass-of-day SUPPRESS (manual curl, no scorer)

**Date:** 2026-06-29 ~10:34Z
**Pass kind:** cron-fired, recurring-misroute, lane-guard trip, 4th pass on the same Batch B feed within the same calendar day.
**Outcome:** `[SILENT]`. One anchor comment posted (GRO-485). No `finalize_task.sh`. No branch. No lock. No state mutation.

## What made this pass different from r150 / r152

The earlier Batch B passes (09:25Z, 10:22Z, 10:29Z, 10:30Z) ran `anchor_5a5_item3_scorer.py` as the first action. **This pass (r154, 10:34Z) ran without the scorer** — the script wasn't accessible from the active shell (different shell snapshot than the prior passes, or scorer env path mismatch). The disposition logic was therefore applied by hand:

1. Read cron preamble IDs (10 Batch B IDs — identical to the prior passes' feed).
2. Fetched GRO-485 comments(last: 5) → confirmed the recurring-misroute dequeue narrative from the 09:25Z anchor comment + three follow-up acknowledgments at 10:22Z / 10:29Z / 10:30Z.
3. Per-issue triage table produced inline (matches the standing cure verbatim — same 10 IDs, same lane mapping).
4. Lane-filter sanity check via `labels:{name:{eq:"agent:ned"}}` + active states — same real-Ned-queue confirmation (GRO-2934 etc. are the actual Ned targets, none in this batch).
5. `swarm.js status` → no active locks.
6. No execution. Single anchor comment posted to GRO-485. `[SILENT]` cron reply.

**Lesson:** the scorer is an optimization, not a gate. When the scorer is unavailable, the manual sequence above is the fallback. The disposition is the same — SUPPRESS with a single anchor comment.

## The reusable pitfall: inline-GraphQL-JSON escaping

This pass exposed a new **durable, reusable pitfall** that applies beyond Ned's lane:

### Symptom

```
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"mutation { commentCreate(input: { issueId: "GRO-485", body: "## Ned — recurring misroute batch..." }) { success } }"}'
```

Returns:
```json
{"errors":[{"message":"Syntax Error: Unterminated string.\n\nGraphQL request:1:131\n...","extensions":{"code":"GRAPHQL_VALIDATION_FAILED","type":"graphql error","userError":true}}]}
```

### Root cause

Shell single-quote nesting + JSON `\"` escaping + GraphQL body content with shell-sensitive characters (backticks, markdown headings `##`, parentheses with `~`) — the backslash-escape chain breaks somewhere in the chain when the body is multi-line markdown. The error message points to a specific column inside the body where the unterminated string starts; this column never aligns with the actual error site because shell escaping has already mangled the payload before it reaches curl.

### Fix (validated r154)

**Write the GraphQL payload to a JSON file, then `curl -d @file.json`.** Bypasses shell quoting entirely.

```bash
# 1. Write the payload to a JSON file
write_file /tmp/linear_mutation.json '{"query":"mutation($id: String!, $body: String!) { commentCreate(input: { issueId: $id, body: $body }) { success } }","variables":{"id":"GRO-485","body":"## Ned — recurring misroute batch, 4th cron pass (2026-06-29 ~10:34Z)\n\nFull body here with backticks, ##, parentheses, etc.\n\n— Ned"}}'

# 2. POST it
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d @/tmp/linear_mutation.json
```

Use GraphQL **variables** rather than inlining the body — `$id` and `$body` as variables sidesteps the entire body-escaping problem. The `commentCreate` mutation accepts `issueId` and `body` as string variables directly.

### When this pitfall fires

- Any Linear comment post with a multi-line markdown body (dequeue narratives, evidence posts, triage deltas).
- Any Linear mutation with a body that contains backticks (inline code), `##` (markdown headers), parentheses with `~`, or non-ASCII chars.
- Pitfall also fires for `issueUpdate`, `issueCreate`, `attachmentCreate`, and any other mutation that takes a multi-line string field.

### When this pitfall does NOT fire

- Single-line body, ASCII-only, no markdown structure → inline `-d '{...}'` works.
- Body used as a GraphQL **variable** (`$body`) rather than inline string literal → works (recommended).

## Action checklist (r154 manual pass)

- [x] Read cron preamble IDs (Batch B, 10 items).
- [x] Re-query anchor GRO-485 `comments(last: 5)` → confirmed recurring-misroute narrative + 3 prior acknowledgments.
- [x] Per-issue triage: 5 → fred (active-oahu hardware), 1 → agy (GRO-490), 3 → fred (content), 1 → kai-content (GRO-499).
- [x] Lane-filter query (`labels:{name:{eq:"agent:ned"}}`) confirmed scanner batch ≠ real Ned queue.
- [x] `swarm.js status` → no active locks.
- [x] NO `finalize_task.sh` (Backlog state preserved).
- [x] NO branch creation under `ned/`.
- [x] NO `swarm.js lock`.
- [x] NO state mutation.
- [x] Single anchor comment posted to GRO-485 (via `curl -d @/tmp/ned_lane_ack_gro485.json` — file-based GraphQL).
- [x] Cron reply: `[SILENT]`.
- [x] **New pitfall captured:** inline-GraphQL-JSON escaping → file-based GraphQL with variables (above).

## Cross-reference

- Standing cure verbatim: see `references/recurring-misroute-batch-playbook.md`.
- Batch B-specific detector: see `references/batch-b-phase1-activeoahu-detector.md`.
- Scorer (when accessible): `scripts/anchor_5a5_item3_scorer.py`.
- Threshold-crossing protocol (FULL_REPORT path): see `references/anchor-threshold-crossing-transition.md`.
- Earlier Batch B passes with scorer: r150 (09:25Z), r152 (10:22Z, 10:29Z, 10:30Z).
- r154 is the first Batch B pass WITHOUT scorer → manual fallback validated.

## Cumulative Batch B noise-free rate (r154)

4 cron passes on 2026-06-29 within ~1h09m (09:25Z → 10:34Z), 1 anchor comment posted (this r154 pass), 3 prior passes followed r59 mechanical-SUPPRESS (recurring-batch identical-items rule). **Pass comment ratio: 1/4 = 75% noise-free on the first day of Batch B churn.** The standing cure (`ned_delta_dispatcher` patch) remains overdue.