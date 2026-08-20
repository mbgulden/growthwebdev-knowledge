# Recurring-batch SUPPRESS pattern — quick reference (2026-06-29)

## ⚠️ 5a.5 silent-protocol gate — CHECK FIRST (added pass-17, 2026-06-29 ~0430Z)

Before running the 5a.3 path below (anchor comment + skip finalize), check
whether the **5a.5 silent-protocol** is eligible. If yes, deliver `[SILENT]`
without ANY Linear API calls — no comment, no finalize, no audit query.

**5a.5 eligibility checklist (ALL FOUR must be true):**
1. Scanner feed is byte-identical to the most recent Ned-style triage pass
   (same issue-ID set, no new entries, no relabels, no state drift).
2. Most recent Ned-style triage note on the anchor issue is <6h old.
3. That prior note already names every issue in the batch + correct lane
   mapping + standing cure (so a fresh note adds no new info).
4. No state drift on any issue in the batch (all still in {Todo, Backlog}).

If all four hold: deliver `[SILENT]` as the final response and stop.
The cron capture preserves prior-pass reports — nothing is lost.

**Why this matters (pass-17 lesson):** the 5a.3 anchor-comment path produces
1 extra Linear comment per pass. At <2h cron cadence on a 4+-day-old batch,
that's 12+ comments/day of "still misrouted, no action" noise. GRO-537 now
carries 38 comments — half of them are Ned triage notes saying the same thing.
The 5a.5 path collapses to 0 comments when prior triage is fresh.

**The 5a.3 path below is for the case where 5a.5 is NOT eligible** — i.e.,
prior triage is 6–24h old, or the batch composition drifted, or a new
contributor joined the thread and a fresh note closes the loop.

---

## TL;DR

When the Ned cron scanner feeds the same N-issue misroute batch every tick
(GRO-503/504/505/507/508/509/510/511/512 + GRO-537 as of 2026-06-29) and
Michael has already dequeued each issue 10+ times, **check the 5a.5 silent-
protocol gate above first.** If all four 5a.5 items hold, deliver `[SILENT]`
and stop — no Linear API calls, no finalize, no audit query, no anchor
comment. That is the lightest-touch path and is the canonical end-of-pass
action for sustained recurring batches.

**Fallback for batches where 5a.5 is NOT eligible** (prior triage is 6–24h
old, batch composition drifted, or a new contributor joined the thread):
deliver `[SILENT]`, but **DO run `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE_ID> ned/<ISSUE_ID> ned`** as the last action. The script's step-3 out-of-lane guard (added 2026-06-28) detects dequeue-pattern keywords in the comment thread and SKIPS the state transition, so no ping-pong occurs. It also clears stale locks and posts a standard finalization comment — do NOT post a separate dequeue comment, since the thread already carries Michael's "Scanner keeps re-feeding them" note (2026-06-27T23:36Z) and re-stating it at <2h cadence pollutes the thread.

> **Pre-2026-06-28 recipe (DEPRECATED):** earlier versions of this file said
> "do NOT run `finalize_task.sh`" and "do NOT post another Linear comment."
> That recipe is wrong now that the out-of-lane guard exists — running
> finalize is the canonical end-of-pass action *when 5a.5 is NOT eligible*.
> Use `--dry-run` only if you need to inspect the guard output before the
> real run (e.g., debugging a new dequeue pattern).

> **Batch B exception (added pass-20, 2026-06-29 ~11Z):** for Batch B
> (GRO-484..502), Michael's standing notes explicitly REJECT `finalize_task.sh`
> even when 5a.5 is not eligible, because the script's noise-fanout is
> unacceptable on those threads. Follow `references/batch-b-phase1-activeoahu-detector.md`
> instead — it mandates skip-finalize for every Batch B pass.

## Canonical entry point

`scripts/suppress_class_detect.py` in this skill. Invocation pattern:

```bash
python3 ~/.hermes/profiles/ned/skills/ned-lane-discipline-check/scripts/suppress_class_detect.py \
  --issues GRO-503,GRO-504,GRO-505,GRO-507,GRO-508,GRO-509,GRO-510,GRO-511,GRO-512,GRO-537 \
  --repo /home/ubuntu/work/growthwebdev-knowledge \
  --cron-output-dir ~/.hermes/profiles/ned/cron/output \
  --include-linear
```

**Two invocation gotchas** (verified pass-15, 2026-06-29 ~02Z):

1. **Always prefix with `python3`** — script is not chmodded. `bash <path>` floods with `command not found`.
2. **`--issues` is comma-separated** — argparse takes ONE arg. Space-sep fails.

## Token sourcing (the canonical Linear pitfall)

The detector needs `LINEAR_API_KEY` in the env. Source from the profile .env:

```bash
source /home/ubuntu/.hermes/profiles/ned/.env
```

Do NOT `source ~/.env` (the system shell env) — it does not contain the key.
Do NOT inline-export from a previous shell. Always source the profile .env
at the start of any Linear GraphQL call.

## Detector-script drift notes (2026-06-29)

### Verdict rationale drift (NEW, pass-15)

The detector prints:

```json
"rationale": "5a.7a-bis 4-of-4 match: same recurring batch, fresh audit trail
              (triage doc / cron output / linear state), no drift,
              no dispatch:ready label"
```

In pass-15 (2026-06-29 ~02Z), `triage_doc_fresh` failed (`no triage doc found in git log`)
and `prior_cron_output_fresh` failed (`newest_age_hours: 2.65 > 2.0`).
Both probes reported `pass: false`. The verdict still came back SILENT
because the **Linear audit** was load-bearing:

```json
"linear_state_audit": {
  "pass": true,
  "min_dequeue_count": 11,    // threshold: 3
  "dispatch_ready_count": 0,
  "drift_count": 0
}
```

**Lesson:** the printed rationale is aspirational ("4-of-4") but the actual
load-bearing check on a stale-evidence pass is the Linear audit's
`min_dequeue_count` + `dispatch_ready_count`. When reading the JSON, weight
`linear_state_audit`, not the rationale string. Future passes should patch
the rationale to reflect which probe actually flipped the verdict.

### Hardcoded signature gap

`RECURRING_BATCH_SIGNATURES` in the detector used to contain exactly one entry
(`gro-504-512-537`). As of pass-N on 2026-06-29 ~13:07Z it now contains two:

- `gro-504-512-537` — original Active Oahu hardware + curriculum batch
  (12+ dequeue comments, anchor GRO-537).
- `gro-484-502` — Active Oahu storefront hardware (intercom, speaker, HA,
  camera, Lorex audio) + HD/coaching content (curriculum, expert library,
  personal brand, Week 1 delivery) + Gemini agent config. Anchor GRO-485
  carries Michael's batch enumeration comment (8 comments as of 2026-06-29
  ~13Z); the other 9 issues have 0 dequeue comments of their own but are
  explicitly dequeued by inclusion in GRO-485's thread.
- `gro-594-2976` — homelab/inventory pipeline (GRO-594/597/616/617/701/702
  — all `agent:fred`, most with Dispatcher "routed to Fred" ×2–3) +
  cross-profile orchestrator memory targets (GRO-2436/2976, write-guarded
  cross-profile territory) + MANUAL Google Workspace setup (GRO-2533,
  `[MANUAL]` tag — human required) + already-Done Gumroad integration
  (GRO-2434, `agent:peer-review`, AGY sandbox self-reviewed 21:04:54Z).
  Added 2026-06-29 ~21:08Z (Pass-N+18). Anchor: GRO-594 (lowest GRO-ID;
  no prior Ned-triage thread exists for this batch).

If a future recurring misroute batch emerges with different issue IDs, follow
the validation recipe in `references/recurring-batch-suppress-pitfalls.md`
(verify anchor + per-issue correct-lane mapping + state distribution) before
appending a new signature. The script is a TOOL, not a decision-maker — but
with the right signatures registered, its verdict is reliable.

**Fresh-batch detector gap (Pass-N+18 GRO-594..2976 finding):** When a fresh
misroute batch IS NOT yet in `RECURRING_BATCH_SIGNATURES`, the detector
returns `verdict: FULL_REPORT` AND `min_dequeue_count: 0` — because Michael's
Dispatcher vocabulary ("routed to <lane>") doesn't match the dequeue
keyword list. The detector's verdict is technically correct ("doesn't match
known signatures") but loses the practical disposition signal. **The
canonical handling for this edge case is in
`references/fresh-misroute-batch-detector-gap.md`** — manual partition walk
+ 5-step disposal recipe + patch instructions for extending the detector's
vocabulary to include `routed to\s+(?:fred|kai|agy|designer|orchestrator)`.

**Workaround for unregistered batches:** if `issue_ids_match_recurring_batch.pass: false`
but the per-issue correct-lane mapping is all-Ned-mismatch AND Michael has
explicitly dequeued the anchor (or the entire batch by enumeration on one
issue's thread) AND `dispatch_ready_count == 0` AND no state drift, the pass
is still SUPPRESS-ELIGIBLE — apply the verdict manually per 5a.5 silent-protocol
gate and add the new signature to the detector script so future passes
classify automatically.

## Pass-log chain

`references/pass-log-2026-06.md` tracks each cron pass with:
- Pass number, UTC timestamp
- Detector verdict + each probe's pass/fail
- Final response (SILENT / REPORT / EXECUTE)
- Any new dequeue signature or pattern shift

Add a new entry per cron pass. Never rewrite history — append only.

## What the detector will NEVER handle

- Issues not yet labeled `agent:ned` (e.g., a brand-new misroute that
  hasn't been dequeued yet → must use 5a.3 / 5a.11 / execute path).
- Issues with `dispatch:ready` label → in-lane work, must execute.
- State drift (any issue outside {Todo, Backlog}) → re-route via the
  fallback path in SKILL.md §"When suppress does not hold".

## See also

- `references/recurring-batch-suppress-pitfalls.md` — historical pitfalls
- `references/pass-log-2026-06.md` — append-only pass log
- `references/mixed-batch-triage-recipe.md` — when the batch is MIXED
  (some in-lane, some misroute)
- `references/linear-dequeue-graphql-recipe.md` — the canonical dequeue
  comment GraphQL shape
- `templates/systemic-misroute-dequeue-comment.md` — boilerplate for
  posting new dequeue comments (rarely needed when prior passes cover it)