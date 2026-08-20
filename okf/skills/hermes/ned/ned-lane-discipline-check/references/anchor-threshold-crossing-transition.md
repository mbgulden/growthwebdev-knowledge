---
title: Recurring-batch 5a.5 anchor threshold-crossing transition protocol
type: reference
status: validated (2026-06-29 ~18:33Z, pass-26 / r130)
linear_anchors: [GRO-485, GRO-484, GRO-486, GRO-487, GRO-488, GRO-490, GRO-492, GRO-499, GRO-500, GRO-502]
last_verified: 2026-06-29
verified_by: ned
---

# Recurring-batch 5a.5 anchor threshold-crossing transition

Validated at pass-26 / r130 / 2026-06-29 ~18:33Z. This pass executed the FULL threshold-crossing transition that pass-25 (~17:59Z) predicted in its own log:

> "Note: the anchor from 12:01Z is right at the edge of the 6h threshold. The next cron pass (r130 ~18:14Z) will likely see this anchor age past 6h and need to re-evaluate. At that point either (a) a fresh Ned-authored anchor comment will be required (FULL_REPORT) or (b) the recurring scanner-feed itself will have been cured (Michael commits the dispatcher patch)."

The dispatcher patch did NOT land, so path (a) fired. This document is the canonical reference for the validated 3-step transition sequence that occurred.

## When this protocol fires

Run this protocol when **all four of the following hold at the start of a cron pass:**

1. Scanner feed is byte-identical to the most recent Ned-style triage pass (same issue-ID set, no new entries, no relabels, no state drift).
2. **The most recent Ned-style triage note on the anchor issue is ≥6h old** (i.e., item [2] of the 5a.5 checklist FAILS because the 6h freshness gate has elapsed since the prior qualifying comment).
3. Items [1], [3], [4] of the 5a.5 checklist still hold (same batch, prior note still semantically covers the batch, no state drift).
4. The recurring batch is still classified as out-of-lane for Ned (recurring misroute, no Ned-actionable work).

The scorer output for this state is:

```json
{
  "5a5_item3_satisfied": false,
  "verdict": "FULL_REPORT",
  "rationale": "5a.5 item [3] NOT satisfied: no comment on <anchor> within 6.0h satisfies all three flags. Need to post a consolidated anchor acknowledgment before re-evaluating SUPPRESS."
}
```

`verdict: FULL_REPORT` here is **NOT** a request to execute the issue. It is a request to **re-arm the 6h suppression window** by posting a fresh consolidated anchor comment.

## The 3-step protocol (validated at r130)

### Step 1: Post a fresh consolidated anchor comment

The comment must satisfy all three §5a.5 item [3] flags simultaneously:

- `names_all_batch_ids: true` — names every issue ID in the scanner feed
- `has_standing_cure: true` — describes the cure (relabel + dispatcher patch)
- `has_lane_map: true` — maps each issue to its correct lane

Template structure (validated r130, 18:33:44.482Z):

```markdown
## Ned — recurring misroute batch, anchor pass N+X (cron YYYY-MM-DD ~HH:MMZ)

Scanner fed the same N `agent:ned`-labeled issues for the Kth time today: <ID list>.

Per `ned-lane-discipline-check` §5a (recurring misroute batch) and the GRO-508 reference, this is **anchor pass N+X** — the prior consolidated anchor from <prior TS> (X.YYh ago) has aged past the 6h threshold, so I am posting a fresh consolidated anchor per §5a.5 item [3] before re-entering SUPPRESS on subsequent cron passes.

### Lane-fit (0-of-N, unchanged across all passes)

| ID | Title | Correct lane | Why out-of-lane for ned |
|----|-------|--------------|--------------------------|
| ... | ... | ... | ... |

### Standing cure (unchanged, awaiting Michael)

1. **Relabel** the N issues off `agent:ned` to their correct lanes, OR
2. **Patch the dispatcher** in `prismatic/lanes/ned/scan_tasks.py` ...

### This cron pass — disposition

- **No code, no branch, no commit, no state transition** for any of the N issues (still Backlog, no lane-fit).
- **No `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh`** — would falsely transition Backlog → In Review.
- **No escalation to Michael/Telegram** — recurring-misroute is the documented disposition.

### Infra delta (thin probe)

- 🟡 GPU node: ...
- 🟢 Disk: ...
- 🟢 Swarm locks: clean
- 🟡 Other: ...

— Ned autonomous cron, recurring-pattern acknowledgment, no escalation needed
```

**GraphQL shape** (validated r130):

```bash
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($issueId: String!, $body: String!) { commentCreate(input: { issueId: $issueId, body: $body }) { success comment { id createdAt } } }",
    "variables": { "issueId": "<ANCHOR_ID>", "body": "<markdown above>" }
  }'
```

Confirm the response has `data.commentCreate.success: true` and capture the `comment.id` and `comment.createdAt` for the suppress log.

### Step 2: Write the suppress log for forensics

Filename pattern: `~/.hermes/profiles/ned/cron/output/<job_id>/gro-<anchor>-batch-recurring-pass-N-YYYYMMDDTHHMMZ.md` (or use the per-job dir structure if your cron job has a dedicated subdir, e.g. `output/20759afd096b/`).

The log must include:

1. **Job ID + run time + schedule**
2. **Scorer verdict (pre-anchor):** `FULL_REPORT` with the exact rationale string
3. **Most recent qualifying comment age at evaluation time** (the value that caused the threshold cross, e.g. `6.53h`)
4. **Action taken:** fresh anchor comment posted at HH:MM:SSZ, comment id `<uuid>`
5. **Disposition list:** all 5 "no" items (no code, no branch, no commit, no state transition, no finalize_task.sh call)
6. **No escalation note** (Telegram is intentionally not contacted; recurring-misroute is documented)
7. **Infra delta** (thin probe — GPU, disk, locks, anything else notable)
8. **Pass log entry** with anchor pass number, prior-pass age, and forward-looking prediction of when the next threshold cross will occur
9. **Standing cure verbatim** (for downstream reference)

### Step 3: Re-verify the scorer immediately after posting

Run the scorer again. Expected result:

```json
{
  "5a5_item3_satisfied": true,
  "verdict": "SILENT",
  "qualifying_comment": {
    "createdAt": "<newly posted comment TS>",
    "age_hours": <very small, e.g. 0.01>,
    "names_all_batch_ids": true,
    "has_standing_cure": true,
    "has_lane_map": true
  }
}
```

If this re-verification does NOT return `SILENT`, something is wrong with the comment (probably one of the three flags was not satisfied — most commonly `names_all_batch_ids` if the ID list is incomplete). Diagnose and re-post with corrections.

## Why the protocol is structured this way

### Why post a fresh comment instead of just `[SILENT]`-ing on this pass?

Because the prior qualifying comment is now ≥6h old, the next cron pass (~15min later) would also fail item [2] of the 5a.5 checklist and would itself need to either re-post a comment or do a full thread re-scan. Posting ONCE at the threshold-crossing moment re-arms the 6h window for ~24 subsequent cron passes (at 15min cadence), which is the right ratio of "noise on Linear" to "suppression protection".

### Why not call `finalize_task.sh`?

Because Batch B recipe (`references/batch-b-phase1-activeoahu-detector.md`) explicitly mandates `skip-finalize` for every Batch B pass regardless of 5a.5 status. Calling `finalize_task.sh` on a misrouted Batch B issue would:

- (a) post a generic `## Ned finalization report` comment that pollutes the thread, AND
- (b) acquire/release locks unnecessarily.

The anchor comment is the only valid Linear write for a threshold-crossing pass.

### Why not escalate to Telegram?

Per the recurring-misroute playbook: the cure (relabel + dispatcher patch) is awaiting Michael's commit, not a new Ned note. Escalating every threshold-crossing event to Telegram would produce a Telegram notification every ~6h on a 4-day-old misroute, drowning out actionable signals.

### Why include the infra delta in the anchor comment?

Because the anchor comment is the **only artifact that will exist on the next pass that lands outside the 6h window** (e.g., if the cron is interrupted for several hours, the next pass will see this comment as the most recent qualifying one and use it to evaluate 5a.5). Including a thin infra snapshot means the next pass has additional context for its `infra_delta` field without re-probing.

## Pitfall — threshold-crossing × chatter-cooldown interaction

**The chatter-cooldown rule** (`references/recurring-batch-suppress-pitfalls.md` pitfall 2) says: if the prior pass was <2h ago AND its verdict was SUPPRESS AND the scanner feed is byte-identical, do NOT post a fresh comment — the audit trail is already on disk in the prior pass's output file.

**The threshold-crossing protocol** says: post a fresh anchor comment when the prior qualifying comment is ≥6h old.

These two rules do not conflict, but they need to be evaluated in the right order:

1. **First:** run the scorer. The scorer's verdict is authoritative.
2. **If the scorer says `verdict: SILENT`:** chatter-cooldown wins. Deliver `[SILENT]`, do NOT post.
3. **If the scorer says `verdict: FULL_REPORT`:** threshold-crossing protocol wins. Post the fresh anchor comment per the 3-step protocol above.

A naive read of "the anchor is 6.5h old" without running the scorer might trigger the wrong path. **Always run the scorer first.**

## Pitfall — predicting the next threshold cross in the pass log

When writing the suppress log for a threshold-crossing pass, the log MUST include a forward-looking prediction:

```
(next)  | ~HH:MMZ    | ~0.25h (new anchor) | yes     | (predicted) SILENT
```

This is what pass-25 (17:59Z) did correctly, and it is what enabled pass-26 (r130, 18:33Z) to recognize the transition cleanly. The prediction is a debugging aid for the next pass and a forcing function for the current pass to articulate what changed.

## Pass log entries for this protocol

- **Pass-25 (r129, 17:59Z):** 5.96h old — just under threshold. Predicted the transition in its pass log.
- **Pass-26 (r130, 18:33Z):** 6.53h old — over threshold. First canonical execution of the 3-step protocol. Posted anchor `2068b000-99da-43ee-a95d-9e71ff7a58bf`, re-armed the 6h window, delivered `[SILENT]` after re-verification.
- **Pass-N+31 (cron 2026-06-30 ~01:47Z):** 7.20h old — over threshold. Second canonical execution of the 3-step protocol. Posted anchor `61ec882b-8e34-4e3f-8b44-0f70816f99bf` at 2026-06-30T01:47:16.249Z. Re-verification via `comments(last: 50)` (NOT `last: 3` — see chronological-ordering pitfall below) returned `verdict: SILENT` against the new anchor at age 0.016h. Suppress log at `cron/output/gro-485-batch-threshold-crossing-pass-31-20260630T0147Z.md`. **Two consecutive successful executions** across a 7-hour gap confirms the protocol is reproducible, not a one-off pattern. Pass-N+32+ should re-evaluate at ~07:47Z.

**Codification:** this document is the canonical reference for the 3-step protocol. The pass log entries for r130+ should reference this document rather than re-narrating the protocol from scratch.

## Pitfall — `comments(last: N)` returns OLDEST N, not newest N (re-verification step)

The re-verification step (Step 3) MUST query `comments(last: 50)` and slice the last entry in Python — `comments(last: 1)` / `last: 3` will silently return the OLDEST comments on the thread, not the newest. This is the same pitfall captured in `references/batch-b-phase1-activeoahu-detector.md` (tool-level lesson, pass #26 entry) and in `references/linear-dequeue-graphql-recipe.md` ("Quick reference — the `comments(last:)` footgun" section). **Pass-N+31 evidence:** first re-verification used `comments(last: 3)` and returned the 10:29Z anchor (15.31h old), which falsely computed `verdict: FULL_REPORT`. Re-queried with `comments(last: 50)` and sliced `[-1]` → returned the just-posted 01:47Z anchor at age 0.016h → `verdict: SILENT`. The cost of the wrong-query miss was ~1 extra GraphQL call (~1 tool call); the cost of trusting it would have been a wrong-ratchet PASS that could trigger an unnecessary follow-up cycle. Always fetch high-N and slice client-side for both the initial probe AND the re-verification.

## See also

- `references/recurring-batch-suppress-2026-06-29.md` — the 5a.5 silent-protocol gate (this protocol is the 5a.5-rearm edge case)
- `references/recurring-batch-suppress-pitfalls.md` — chatter-cooldown rule (pitfall 2) and the recipe deviation patterns
- `references/batch-b-phase1-activeoahu-detector.md` — Batch B recipe (mandates skip-finalize for every Batch B pass)
- `references/pass-log-2026-06.md` — append-only pass log; entries pass-25 and pass-26 are the validating evidence for this protocol
- `SKILL.md` § "Threshold-edge observation" — the pitfall that predicted this protocol
- `scripts/anchor_5a5_item3_scorer.py` — the scorer that returns `verdict: FULL_REPORT` at this transition
