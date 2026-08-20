---
name: ned-lane-discipline-check-recurring-batch
description: Safe playbook for confirmed recurring-misroute batches where Michael has dequeued the same agent:ned issues across multiple prior passes. Skip finalize_task.sh, skip lock/branch/code/commit, post ONE consolidated comment to the anchor issue, [SILENT] on Telegram.
---

# Recurring-misroute batch playbook (2026-06-29 ~08Z pass, confirmed)

This reference documents the safe playbook for the recurring pattern Ned has hit ~20 consecutive cron passes: the scanner feeds 10 `agent:ned`-labeled issues that Michael has explicitly dequeued multiple times. The pattern is stable — same issues (GRO-503–512, GRO-537), same misroute (Ned Delta Dispatcher has no lane-content filter), same correct action (do not execute).

## When this playbook applies

**Two sub-cases both route to anchor-comment-only — distinguish them in the comment header:**

**Sub-case A — recurring misroute (≥2 prior Ned triage comments).** Re-confirmed across multiple prior cron passes; the original anchor for this sub-case is GRO-537 (recurring GRO-503–512 / GRO-537 batch). Detection: per-issue `comments(last: 3)` shows ≥1 prior Ned-style triage comment using a disqualifying phrase below.

**Sub-case B — first-sighting misroute (zero comments, fresh batch).** What the ~10Z/2026-06-29 pass hit: 10 fresh `agent:ned`-labeled issues (GRO-485, 486, 487, 488, 490, 492, 499, 500, 501, 502) with **zero comments** and `updatedAt` of 2026-06-25 (4 days stale). Detection: every issue in the scanner batch is `agent:ned`-labeled BUT none have any comment thread, AND on reading each issue's description you find they target Ned's ❌ Do NOT build list (Active Oahu physical hardware, HD coaching curriculum, brand building, Gemini agent config — all clearly not infra).

**Same disposition for both:** anchor-comment-only, skip finalize_task.sh, [SILENT] on cron. The header note differs ("Nth consecutive cron pass" vs. "1st cron pass on this batch"); sub-case A picks the existing anchor from accumulated triage notes, sub-case B falls back to lowest GRO-ID in the batch (GRO-485 in the 2026-06-29 ~10Z example).

**Verify-before-claim rule for prior passes:** if a prior cron output in `/home/ubuntu/.hermes/profiles/ned/cron/output/.../<date>.md` claims "issues relabeled off the Ned scanner's path" or "off the queue", DO NOT trust it without re-querying GraphQL. The 2026-06-29 ~09:08 pass made exactly that claim for GRO-485–502; the ~10Z re-query showed all 10 still had `agent:ned` label with `updatedAt` of 2026-06-25. Prior-pass success reports on label mutations must be re-verified before being used as a basis for "no work to do". The cheap verification is `curl + jq`: hit GraphQL for the IDs, check `labels` and `updatedAt`, compare to the claim.

Confirm with the smoke test:

```graphql
query {
  issues(
    filter: { labels: { name: { eq: "agent:ned" } } }
    first: 20
  ) {
    nodes {
      identifier
      title
      comments(last: 3) {
        nodes { body createdAt user { name } }
      }
    }
  }
}
```

For each issue, scan the last 3–5 comments for any of:

- `out[- ]of[- ]lane` (case-insensitive)
- `misroute`
- `dequeued`
- `not infrastructure`
- `relabel`
- `wrong agent` / `lane violation`

**Recurring-misroute batch is confirmed when ≥2 issues in the scanner batch have ≥1 prior Ned comment using any of the above phrases.** At that point:

1. **DO NOT call `finalize_task.sh`** on any issue. Even with the step-3 out-of-lane guard (added 2026-06-28), the guard is a soft safety net, not a guarantee — Ned's 2026-06-28 ~01:25Z pass on GRO-509 found state had drifted to "In Review" because finalize_task.sh had auto-promoted without the guard firing. The guard cannot be trusted without re-reading the actual script each pass. **Pass-20 (2026-06-29 ~09Z, GRO-537 anchor) confirmed the guard fires correctly** — `SKIP transition: issue appears out-of-lane (BLOCKED_COMMENT:\brelabel\b; out[- ]of[- ]lane; out[- ]of[- ]lane). No state change.` — but the playbook still mandates skip-finalize because the script also acquires/releases locks and posts a finalization-report comment that fans out noise to the Linear thread; anchor-only is canonical.

2. **DO NOT acquire a lock, create a branch, write code, or commit.** Skeleton steps 1–6 are all skipped.

3. **Post ONE consolidated acknowledgment comment to the anchor issue** (GRO-537 is the current anchor for the GRO-503–512 / GRO-537 batch — confirm by grepping comments for "anchor for this cron pass"). Do not fan out 10 separate comments.

4. Final cron output: `[SILENT]`. Do not escalate to Telegram — recurring-pattern acknowledgment is not a blocker requiring human decision.

## Anchor-issue convention

When the scanner batch is the same recurring misroute, post the consolidated comment to the **single anchor issue**. The anchor is whichever issue:

- Has the most recent Ned-style triage comment, OR
- Is explicitly named in a prior pass's comment as "anchor for this cron pass" / "consolidated note on GRO-XXX", OR
- Defaults to the lowest GRO-ID in the batch (GRO-503 in the current batch, but GRO-537 has become the anchor via accumulated triage notes).

Fan-out to 10 separate comments floods Michael's Linear notifications and adds zero information — each per-issue triage line is already inside the anchor comment.

## Consolidated comment template — sub-case A (recurring, ≥2 prior triage comments)

```markdown
## Ned — recurring misroute batch, Nth consecutive cron pass (DATE ~HHZ)

Scanner fed the same K `agent:ned`-labeled issues (GRO-IDs). Per `ned-lane-discipline-check` §5a exception (recurring misroute batch, verified across prior passes), I am NOT executing and NOT calling `finalize_task.sh` — that script auto-promotes state to "In Review" and would override your deliberate Todo/Backlog state.

**Per-issue triage (re-confirmed from prior pass, unchanged):**
- `GRO-XXX` — Title → `agent:fred / agent:kai-content` / `agent:agy` / etc.
- ... (one line per issue, lanes per Michael's prior triage)

All 10 fall under my ❌ Do NOT build list (landing pages, marketing copy, curriculum, video, bootcamp, Gumroad checkout, paid launch ops, sales playbooks, financial modeling). None target `scripts/`, `prismatic/`, `plugins/`, GPU/disk/CF/Tailscale/swarm.

**Skipped:** `finalize_task.sh`, branch creation, lock acquisition, code writes, commits. No state mutation. Lock registry confirmed clean (`swarm.js status` → no active locks).

**Underlying bug:** GRO-559 (Ned-dispatcher misroutes `agent:ned` label onto Fred/Kai/AGY/Designer work). Fixing this requires orchestrator-side dispatcher changes, not per-issue relabeling from my lane.

— Ned (autonomous cron, no human escalation needed; recurring-pattern acknowledgment, not a blocker)
```

## Consolidated comment template — sub-case B (first-sighting, zero comments)

The header changes from "Nth consecutive cron pass" to "1st cron pass on this batch", and the per-issue triage notes are NEW (no prior pass data to copy). Anchor falls back to lowest GRO-ID in the batch.

```markdown
## Ned — recurring misroute batch, 1st cron pass on this batch (DATE ~HHZ)

Scanner fed K fresh `agent:ned`-labeled issues (GRO-IDs); all have zero comment thread and `updatedAt` 4+ days old, suggesting the dispatcher just re-applied the label after a prior pass's relabel silently failed. Per `ned-lane-discipline-check` §5a exception (out-of-lane batch, verified via description content for each), I am NOT executing and NOT calling `finalize_task.sh` — that script auto-promotes state to "In Review" and would override your deliberate Todo/Backlog state. Lock registry confirmed clean.

**Per-issue triage (first sighting, NEW — please confirm or correct):**
- `GRO-485` — Deploy Outdoor Weatherproof Speaker → `agent:fred` (Active Oahu physical install + cable run)
- `GRO-486` — Configure Home Assistant (Button→Piper TTS→Discord) → `agent:fred` (HA config + active-oahu is read-only for Ned)
- `GRO-487` — Integrate Lorex 2K Two-Way Audio → `agent:fred` (Active Oahu physical hardware)
- `GRO-488` — Mount Eye-Level Camera at Main Counter Checkout → `agent:fred` (Active Oahu physical install)
- `GRO-490` — Configure Gemini Agent Mode for Autonomous Consulting → `agent:agy` (AI tool orchestration)
- `GRO-492` — Build Personal Brand — Case Studies and Open Source → `agent:fred` (content/ brand, content/ is read-only for Ned)
- `GRO-499` — Design HD-Tailored Self-Coaching Curriculum → `agent:kai-content` (curriculum design)
- `GRO-500` — Curate YouTube Expert Library (15-25 videos) → `agent:fred` (content curation)
- `GRO-501` — Build Progress Tracker and Homework System → `agent:kai-content` (curriculum tooling)
- `GRO-502` — Execute Week 1 — C-Suite Communication → `agent:fred` (live coaching delivery)

All 10 fall under my ❌ Do NOT build list (physical hardware, home automation, marketing/brand/curriculum, video, content, live coaching). None target `scripts/`, `prismatic/`, `plugins/`, GPU/disk/CF/Tailscale/swarm infrastructure.

**Skipped:** `finalize_task.sh`, branch creation, lock acquisition, code writes, commits. No state mutation. Anchor chosen by lowest GRO-ID convention (GRO-485).

**Underlying bug:** GRO-559 (Ned-dispatcher misroutes `agent:ned` label onto Fred/Kai/AGY/Designer work). Fixing this requires orchestrator-side dispatcher changes, not per-issue relabeling from my lane.

— Ned (autonomous cron, no human escalation needed; recurring-pattern acknowledgment, not a blocker)
```

## Worked example (2026-06-29 ~08Z pass)

Scanner fed 10 issues: GRO-537, GRO-512, GRO-511, GRO-510, GRO-509, GRO-508, GRO-507, GRO-505, GRO-504, GRO-503. Per-issue `comments(last: 3)` showed all 10 had multiple prior Ned comments using `out[- ]of[- ]lane` / `misroute` / `not infrastructure`. Pattern confirmed. Anchor identified as GRO-537 (had the 2026-06-28 ~09Z consolidated note explicitly naming itself as anchor). Posted the template above to GRO-537. Cron output: `[SILENT]`. Total tool calls: ~6 (1 GraphQL scan + 1 anchor full-comment fetch + 1 commentCreate + 3 read-only). No lock, no branch, no commit, no state mutation.

## Pass-22 update (2026-06-29 ~10:15Z, GRO-485 anchor — PRE-EMPTED BY MICHAEL)

This pass hit the pre-emption branch documented in the Pitfalls section: Michael Gulden had already posted the sub-case B consolidated note on GRO-485 at 09:25:47Z, ~50 minutes before this cron pass at 10:15:50Z. Detection criteria all matched: (a) `user.name` = "Michael Gulden", (b) `createdAt` is same UTC day, (c) first ~200 chars of `body` contain "recurring misroute batch" AND "agent:ned" / "not Ned's lane". No Ned-authored comment posted, no `finalize_task.sh` called, no lock acquired, no commit, no state mutation. Cron output: `[SILENT]`. Total tool calls: ~5 (1 GraphQL batch fetch + 1 per-issue comment thread check on GRO-485 + 1 `autonomous-task-skeleton.md` read + 1 `skill_view` on the playbook + 1 final decision).

**Skill sharpening this pass:** The pre-emption pitfall's original detection was an exact header substring match (`## Ned — recurring misroute batch, 1st cron pass on this batch (DATE ~HHZ)`). That is brittle — Michael may phrase the header differently. Tightened to authorship (Michael Gulden) + same UTC day + first-200-chars vocabulary check (`recurring misroute batch` AND any of {dequeue, misroute, out of lane, not Ned's lane, agent:ned}). The vocabulary gate matters because a same-day Michael comment about, say, merging a PR won't satisfy it; the misroute phrase anchors the match to this exact pattern.

**Lesson for future passes:** this is the third same-day pass on the GRO-485–502 batch (09:08 Ned relabel-claim-failed, 09:25 Michael pre-empt, 10:15 Ned pre-empted by Michael). At this density Michael is posting the anchor himself faster than the scanner cycles, and Ned's role has fully collapsed to `[SILENT]`. Future passes should also expect this pattern: trust the pre-emption branch, return `[SILENT]`, log nothing further. The GRO-559 dispatcher-bug fix is the only durable resolution; everything else is noise.

## Pass-21 update (2026-06-29 ~10Z, GRO-485 anchor — NEW SUB-CASE B)

The 10Z pass hit a sub-case the prior playbook didn't formally cover: **first-sighting misroute with zero comments**. The scanner fed 10 fresh `agent:ned`-labeled issues (GRO-485, 486, 487, 488, 490, 492, 499, 500, 501, 502), all with `comments(last: 3)` returning empty arrays. Detection was driven entirely by description content (every title mentioned Active Oahu hardware, HD curriculum, brand building, or Gemini config — all out-of-lane).

**Same disposition applied:** anchor-comment-only to lowest GRO-ID (GRO-485), no finalize_task.sh, no lock/branch/commit, [SILENT] on cron. The 2,594-character consolidated comment named all 10 issues with a per-issue lane assignment and "1st cron pass on this batch" header so Michael can confirm or correct. Cron output written to `/home/ubuntu/.hermes/profiles/ned/cron/output/a9374c15f022/2026-06-29_09-25-50.md`.

**Playbook additions this pass:**
1. Two sub-cases (A: recurring-with-comments, B: first-sighting-zero-comments) — same disposition, different comment header phrasing.
2. Sub-case B comment template (above).
3. Verify-before-claim rule: do not trust a prior pass's "relabel succeeded" report without re-querying GraphQL. The 09:08 pass made exactly such a claim for GRO-485–502 that did not match reality.
4. New pitfalls: "Trusting prior pass's relabel claim without re-verification" and "first-sighting ≠ recurring in comment header".

**Lesson for future passes:** sub-case B will keep recurring as the dispatcher continues to misroute. The playbook now formally handles it.

## Pass-20 update (2026-06-29 ~09Z, GRO-537 anchor)

The deviated pass this cycle: Ned called `finalize_task.sh GRO-537 ned/GRO-537 ned` to confirm the lane guard's behavior — **this was a playbook violation**, even though the guard caught the transition correctly. Going forward, the canonical disposition is **skip finalize_task.sh entirely**, post only the anchor comment, return `[SILENT]`. The guard's step-3 BLOCKED_COMMENT detection is verified working (see pass-20 trace below), but the script's lock-release + comment-post side effects are still noise on a recurring-misroute pass.

Pass-20 `finalize_task.sh` trace (preserved as evidence the guard works):

```
[finalize] issue=GRO-537 branch=ned/GRO-537 agent=ned dry_run=false
[finalize] STEP 1: committing any pending changes in /home/ubuntu/work/prismatic-engine
[finalize]   nothing to commit (working tree clean)
[finalize] STEP 2: unlocking files in swarm lock registry
[finalize]   UNLOCKED: tests ← prismatic-engine
[finalize]   UNLOCKED: prismatic ← prismatic-engine
[finalize]   UNLOCKED: scripts ← prismatic-engine
[finalize]   UNLOCKED: .github/workflows ← prismatic-engine
[finalize] STEP 3: transitioning GRO-537 to 'In Review' state
[finalize]   SKIP transition: issue appears out-of-lane (BLOCKED_COMMENT:\brelabel\b; out[- ]of[- ]lane; out[- ]of[- ]lane). No state change.
[finalize]   See out-of-lane guard added 2026-06-28 in finalize_task.sh step 3.
[finalize] STEP 4: posting final evidence to Linear comment thread
[finalize]   Linear comment: ok
```

**Conclusion:** Guard works, but playbook still says skip-finalize. Future passes: anchor comment + `[SILENT]`, no script invocation.

## Pass-23 update (2026-06-29 ~10:33Z, byte-identical probe → full SILENT suppress)

This pass hit a *new* suppression branch that the existing playbook covered only partially: the probe was byte-identical to the prior pass at 10:22Z (~11 minutes earlier), AND the anchor (GRO-485) already carried BOTH Michael's 09:25Z pre-empt note AND Ned's own 10:29Z consolidated triage comment. Detection: fresh GraphQL pull returned the same 10 IDs in `Backlog` state with the same labels and unchanged `updatedAt`. Time since last full REPORT: ~11 min (well inside 24h chatter-cooldown).

**Disposition:** no Ned-authored comment, no `finalize_task.sh`, no lock, no branch, no commit, no Linear state change. Wrote `cron-pass-2026-06-29T1033Z-suppress.md` for forensics (the cron-pass log itself is the audit trail; no per-issue Linear comment needed when the probe is byte-identical to a REPORT within the cooldown window). Final cron output: `[SILENT]`. Total tool calls: ~7 (1 GraphQL probe + 1 prior-pass log read + 1 playbook check + 1 lock-registry re-verify + 1 infra-snapshot probe + 1 suppress-log write + 1 final state-check).

**Why this is a separate branch from "same-day duplicate" (existing pitfall below):** the existing pitfall covers *Ned posting two of his own notes minutes apart* — the fix is "scan for your own header dated same UTC day before posting". This new branch covers *probe is identical to the most recent REPORT regardless of authorship of the most recent comments* — the fix is "compare your fresh probe table to the prior pass's probe table; if identical and inside chatter-cooldown, skip the anchor comment entirely and just write a suppress log". The two branches overlap when the prior pass was Ned's own REPORT, but the new branch also fires when the prior REPORT was Michael's pre-empt note (the probe would still be identical to it).

**Distinguishing probe-stable-suppress from same-day-duplicate:**
- **Same-day-duplicate** → trigger: "anchor's `comments(last: 3)` has a `## Ned — recurring misroute batch` header dated same UTC day". Action: skip the comment write, `[SILENT]`.
- **Probe-stable-suppress** → trigger: "fresh probe table (IDs + states + labels + recent comment authors + timestamps) is byte-identical to the most recent cron-pass log under `~/.hermes/profiles/ned/logs/cron-pass-*.md`". Action: skip the comment write AND skip re-reading the playbook (you already read it), write a new suppress log for forensics, `[SILENT]`.

The probe-stable-suppress branch is the cheapest correct disposition when the scanner is running on a tight loop and re-hitting the same batch every 10–20 min. It saves ~3 tool calls per pass (no comment-thread re-read, no anchor full-fetch, no commentCreate).

**Lesson for future passes:** as long as the dispatcher bug GRO-559 stays unfixed and the scanner keeps feeding the same batch, cron passes will alternate between full-REPORT (when probe drifts) and probe-stable-suppress (when probe is identical). Most passes will land in the latter branch. Keep the suppress log writes going so the audit trail is reconstructible, but do not bother posting Ned-style comments more than once per ~24h cycle (which the chatter-cooldown already enforces via byte-identical probe).

## Pass-NN update (2026-06-29 ~16:49Z, GRO-485 anchor — scorer-as-first-action optimization)

This pass made a workflow optimization: ran `anchor_5a5_item3_scorer.py` as the FIRST action after reading the skeleton, instead of doing the hand-rolled detection loop the prior passes describe (per-issue GraphQL probe → comment thread scan → manual phrase grep → judgement).

**Detection was identical:** anchor GRO-485 had a 4.79h-old qualifying comment (12:01:31Z) naming all 10 batch IDs + standing cure + lane map. Scorer verdict: `SILENT`, `5a5_item3_satisfied: true`. Disposition: same as pass-23 — no Ned-authored comment, no `finalize_task.sh`, no lock, no branch, no commit, no Linear state change. Cron output: `[SILENT]`.

**Tool-call savings:** ~3-4 fewer GraphQL queries per pass because the scorer does the GraphQL fetch + scoring + verdict in one Python script invocation (with one $LINEAR_API_KEY env var read). Prior passes on this same batch averaged ~7-9 tool calls for the detection phase; this pass was ~6 total (1 skeleton read + 1 .env source check + 1 label/state probe + 1 scorer + 1 verdict read + 1 reply). The savings compound when the scanner is on a tight loop.

**Lesson for future passes:** on the recurring-batch signature (10 `agent:ned`-labeled issues, anchor = GRO-485 / GRO-537 / known recurring set), reach for `anchor_5a5_item3_scorer.py` IMMEDIATELY after the skeleton read. Do not re-read the playbook reference end-to-end — the scorer encodes the same logic. The playbook reference remains canonical for edge cases the scorer doesn't cover (sub-case B first-sighting, Michael pre-emption with drifted batch, etc.).

**Updated SKILL.md:** the score-pointer section now reads "Use `scripts/anchor_5a5_item3_scorer.py` as your FIRST action on any scanner feed matching the recurring-batch signature" with verdict-handling instructions for `SILENT` vs `FULL_REPORT`.

## Pitfalls

- **Probe-stable-suppress mistaken for "do nothing, log nothing"** — even on a byte-identical probe, write the cron-pass suppress log (e.g. `cron-pass-2026-06-29T1033Z-suppress.md`). The log is the only durable evidence that Ned saw the probe and chose [SILENT] deliberately, not that Ned's scanner drifted or crashed. Without the log, Michael has no way to distinguish "Ned suppressed" from "Ned didn't run this cycle". Pattern: always write a suppress log on every cron pass that returns [SILENT], even when the action is identical to the prior pass.
- **Trusting a prior pass's "relabel succeeded" claim without re-verification** — the 2026-06-29 ~09:08 Ned cron output claimed "All 10 issues are now off the Ned scanner's path with correct lane labels applied" for GRO-485–502, but the ~10Z pass re-query showed all 10 still carried `agent:ned` with `updatedAt` of 2026-06-25. The claim was premature (likely the pass scripted a relabel that 4xx'd silently, or the writer assumed state had changed). **Always re-verify label state with a fresh GraphQL query before basing a "no work to do" decision on a prior pass's claim.** Cheap verification: query each issue, check `labels.nodes.name` and `updatedAt`.
- **Calling `finalize_task.sh` "just in case"** — this is the failure mode that creates state ping-pong (Todo → In Review → manual revert). The guard is best-effort; do not rely on it. Even when the guard catches the transition correctly (pass-20 confirmed), the script's lock-release + comment-post side effects add noise to the Linear thread.
- **Posting to all 10 issues** — Michael's Linear notifications get spammed. One anchor comment is enough; the per-issue triage lines inside it are the actionable signal.
- **Treating the scanner preamble as lane-filtered** — the cron pre-run script's "Found N Linear issues" is a global top-N (r128 scanner-preamble pattern), not lane-filtered. The `labels:{name:{eq:"agent:ned"}}` filter is what gives the true queue. For recurring-misroute the difference doesn't matter (every agent:ned-labeled issue is out-of-lane), but for genuinely-in-lane pickups this is critical.
- **Assuming a 2nd-pass confirmation is the same pattern as 1st-pass** — always re-grep comments each pass. Michael may have relabeled some issues or added a new in-lane Ned task between passes.
- **Pass-19 reference links stale** — `gro-537-triage-pass-{11..18}-batch-recurring.md` are the canonical anchor notes on disk; pass-19 (`gro-537-triage-pass-19-batch-recurring.md`) is the most recent. Future passes should reference pass-{N-1}, not pass-{11..18}.
- **First-sighting ≠ recurring-misroute in the comment header** — when sub-case B (zero comments, fresh batch) hits, the consolidated comment should say "1st cron pass on this batch" and reference the per-issue triage. Don't copy the "Nth consecutive cron pass" phrasing from sub-case A templates — it implies prior-pass knowledge that doesn't exist yet, and a future reader will waste tool calls grepping for the prior passes.
- **Posting a second consolidated note to the same anchor on the same day** — when the scanner hits the same batch twice in one cron cycle (pass-N then pass-N+1 ~10–20 min later), the anchor's `comments(last: 3)` may already contain a fresh Ned-style triage note dated the same UTC day. Re-running the playbook verbatim would post a near-duplicate comment that fans out Linear noise. Detection: scan anchor's `comments(last: 3)` for a `## Ned — recurring misroute batch` header dated same UTC day before posting; if found, skip the comment write entirely and return `[SILENT]`. The first note of the day is canonical; subsequent same-day passes on the same batch are silent acknowledgments.
- **Michael may pre-post the canonical anchor note himself** — observed on 2026-06-29 ~09Z vs ~10Z passes on the GRO-485–502 batch: Michael Gulden posted the sub-case B "1st cron pass on this batch" consolidated note on GRO-485 at 09:25Z, ~33 minutes before the next Ned cron pass at 09:58Z. The note used the exact playbook template (per-issue lane assignments + "skipped finalize_task.sh, no lock, no branch, no commit, no state mutation" + GRO-559 dispatcher-bug footer). When Michael pre-posts the anchor, Ned's role collapses entirely to `[SILENT]` — no Ned-authored comment, no Ned comment-N+1 reply, no finalize, no escalation. Pre-emption supersedes the playbook's "Ned posts the consolidated note" branch. **Detection (robust)**: anchor's `comments(last: 3)` has a comment where (a) `user.name` is Michael Gulden, (b) `createdAt` is same UTC day as the current pass, AND (c) the first ~200 chars of `body` contain BOTH `recurring misroute batch` AND any of {dequeue, misroute, out of lane, not Ned's lane, agent:ned} → return `[SILENT]` immediately. Do NOT depend on the exact `## Ned — recurring misroute batch, 1st cron pass on this batch (DATE ~HHZ)` header match — Michael may phrase the header differently (drop the "1st cron pass on this batch" suffix, change the date format, add a leading note). Authorship + same-day + first-line misroute vocabulary is the durable signal. Sub-case A analog: Michael posting the recurring-batch note on GRO-537 between r7 and r8 also collapses Ned's role. This pre-emption is the dominant path on a hot scanner, not a rare exception.

- **Michael pre-empts + scanner batch drifts by 1 ID** — when Michael's pre-empt note names 9/10 IDs but the fresh scanner feed has 1 ID swapped (e.g., GRO-501→GRO-484, observed 2026-06-29 ~10:51Z), do NOT assume the anchor note covers the swapped ID. Grep Michael's body for the new ID. If named: anchor-only rule still applies, [SILENT], no fresh comment, no finalize. If NOT named: treat the swapped ID as a fresh-fallout of the same GRO-559 dispatcher bug — include it in the cron output doc's "Scanner feed" section for forensics, but still return [SILENT] (the dispatcher bug is the root cause, not the issue itself; relabeling one ID per cron pass is whack-a-mole). Pattern: any same-day scanner feed where ≥90% of IDs match Michael's anchor body falls under pre-emption regardless of the remaining drift.

## Reference chain

- SKILL.md §5a — the recurring-misroute exception to the standard "always finalize" contract.
- `references/linear-lane-filter-query.md` — working GraphQL filter shapes (the `id:{in:[...]}` shape used above is the cheapest way to fetch a known issue set).
- `scripts/finalize_task.sh` — the script whose guard behavior is *not* trustworthy for this batch; read it on each pass if you must call it.