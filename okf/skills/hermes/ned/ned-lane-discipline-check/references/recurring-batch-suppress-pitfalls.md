---
title: Recurring-batch SUPPRESS pitfalls (pass-14, 2026-06-29 ~01:43Z)
type: reference
status: current
linear_anchors: [GRO-537, GRO-503, GRO-504, GRO-505, GRO-507, GRO-508, GRO-509, GRO-510, GRO-511, GRO-512]
last_verified: 2026-06-29
verified_by: ned
---

# Recurring-batch SUPPRESS pitfalls

Two concrete pitfalls observed on pass-14 (2026-06-29 ~01:43Z) of the recurring GRO-503..512 + GRO-537 misroute batch. Pass-14 ran 16 min after pass-13 and reached the same SUPPRESS verdict by the same recipe — but surfaced two edge cases worth documenting.

## Pitfall 1 — `issue.updatedAt` is NOT a freshness signal for comments

`issue.updatedAt` can drift **without** any new comment, label change, or state transition. Observed on GRO-537 this pass:

- `issue.updatedAt`: 2026-06-29T01:28:30.573Z (1 min after pass-13 cutoff 01:27:14Z)
- newest comment `createdAt`: 2026-06-27T23:48:21.893Z (36+ hours before pass-13 cutoff)
- Cause: Linear bumps `updatedAt` on metadata-only events (subscription/notification churn, internal ref refresh, viewer read receipt). No substantive activity.

If a future pass uses `updatedAt > previous_pass_cutoff` as the "is there new activity?" check, it will misclassify metadata drift as new work and incorrectly break a SUPPRESS streak, posting a redundant triage comment.

**Correct freshness signal:** compare `comments.nodes[].createdAt > cutoff`, NOT `issue.updatedAt > cutoff`. The `comments(last:N).nodes` array is the authoritative activity log.

**When `updatedAt > cutoff` but no new comments exist:**
- Still SUPPRESS — the prior pass covered the state.
- Do NOT post a new "new activity detected" comment — the activity is internal, not user-visible.
- Note in the local cron output for the audit trail: `updatedAt advanced (metadata only); no new comments since <prior-cutoff>`.

This is a strict tightening of the SUPPRESS decision matrix, not a relaxation: the criterion is "new user-visible activity on the issue", which is comments / state / labels — not the timestamp on the issue envelope.

## Pitfall 2 — Recurring-batch SUPPRESS is the same recipe every pass

When the scanner feed is byte-identical (same 10 issue IDs, same titles, same `agent:ned` label, same Michael dequeue comments) for consecutive passes and the prior pass already wrote a triage audit doc + commit, the correct disposition is **always SUPPRESS** — even if the prior pass was only minutes ago. Pass-13 ran at 01:27:14Z; pass-14 ran at 01:43Z (16 min later). Same recipe, same verdict, same outcome.

**Why this matters:** Michael's prior triage notes explicitly stated "new comments at <2h interval pollute the thread." Re-running the full audit+commit cycle at sub-hour cadence adds noise without signal.

**Cadence rule:** if `last_cron_output_age < 2h` AND `scanner_feed_byte_identical` AND `prior_pass_verdict == SUPPRESS`, this pass is also SUPPRESS. Skip the linear comment, skip the commit, skip the Linear state audit, return `[SILENT]`. The audit trail is already on disk in the prior cron output.

**Wall-clock check recipe (in `scripts/suppress_class_detect.py`):**
- `find /home/ubuntu/.hermes/profiles/ned/cron/output/<job_id>/ -name '*.md' -mmin -120 | head -1` → if non-empty, prior pass exists within 2h window
- Compare current scanner-feed issue ID list against the `scanner_feed` field in the prior cron output's markdown header
- If identical AND prior response contains "SUPPRESS" → SUPPRESS without further Linear calls

**Reference:**

- `references/pass-log-2026-06.md` — per-pass archive (passes #1–#24+); pass-13 documented at 2026-06-29 01:27Z
- `scripts/suppress_class_detect.py` — canonical SUPPRESS detector; pass-14 confirmed it returns `verdict: SILENT` correctly when invoked with `--issues "GRO-537,GRO-512,...,GRO-503"` (comma-separated, NOT space-separated)
- `references/linear-dequeue-graphql-recipe.md` — the GraphQL footgun compendium
- SKILL.md SILENT-execution section (line ~301) — the prose decision matrix that the above two pitfalls tighten

## Pitfall 3 — On-disk pass-{NN} doc recipe is stale (post-2026-06-28)

**Lesson from pass-18 (r148, 2026-06-29 ~0537Z):** the recurring-batch-suppress recipe in `references/recurring-batch-suppress-2026-06-29.md` is the canonical authority. The on-disk `scripts/ops/gro-537-triage-pass-NN-batch-recurring.md` chain (passes 11–15) is a HISTORICAL ARTIFACT — its tail "No `finalize_task.sh` call this pass" guidance is pre-2026-06-28 and is now STALE.

**Why:** the 2026-06-28 finalize_task.sh out-of-lane guard addition (see `finalize-task-script-bug` skill item C) made the pre-2026-06-28 recipe obsolete. The guard auto-skips state transition when the comment thread contains "out-of-lane", "relabel", "wrong-agent", "misroute", or "lane-violation" — so calling `finalize_task.sh` on a misrouted issue is now SAFE and is the canonical end-of-pass action.

**Anti-pattern (this pass):** I read the on-disk pass-14 doc, trusted its "No `finalize_task.sh`" recipe over the references/ file, and produced a full new pass-15-batch-recurring.md (158 lines) + commit + lock/unlock. Should have:
- Verified 5a.5 eligibility (all 4 checklist items pass on this batch)
- Called `finalize_task.sh GRO-537 ned/gro-537-triage-pass-13 ned` (guard auto-skips state transition, posts generic finalization comment, clears stale locks)
- Delivered `[SILENT]`

**Trust hierarchy when sources disagree:**
1. **CANONICAL:** `references/recurring-batch-suppress-2026-06-29.md` (recipe + detector-script drift notes)
2. **AUTHORITATIVE:** `references/pass-log-2026-06.md` (per-pass deviation/lesson — most recent wins)
3. **AUTHORITATIVE:** SKILL.md description (frontmatter — auto-injected into context)
4. **HISTORICAL ONLY:** `scripts/ops/gro-537-triage-pass-NN-batch-recurring.md` (any pass ≥ pass-14 is now stale; do NOT follow its end-of-pass "no finalize" recipe)

**If you find yourself writing a new `gro-537-triage-pass-NN-batch-recurring.md`:** STOP. That pattern is deprecated. Produce a smaller `output/gro-537-routing-triage-<TS>.md` artifact (matching r146's pattern) and rely on `finalize_task.sh` for the canonical end-of-pass action. Pass-15 should be the LAST file in the on-disk pass-{NN} chain.