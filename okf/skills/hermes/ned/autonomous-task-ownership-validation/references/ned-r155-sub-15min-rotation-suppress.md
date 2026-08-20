# r155 — Sub-15-min scanner rotation: classify independently, suppress via ratchet

**Date:** 2026-06-30 02:21Z (r136, 3 min after r135)

## What this case is

The scanner pool churned **within** a single cron cadence window. Two consecutive ticks:

| Tick | Time | Feed (10 IDs) | Verdict |
|---|---|---|---|
| r135 | 02:18Z | GRO-324/325/326/327/328/332/346/347/358/359 (AOT content cluster + SEO + schema + emergency legal scrub; 6 already-Done + 1 active AGY session + 3 read-only-lane content tasks) | SUPPRESS |
| r136 | 02:21Z | GRO-264/312/313/314/317/318/322/323/324/325 (AOT SEO completion + AGY Profile Retirement + HD Engine SEO + Honeybadger Trademark) | SUPPRESS |

Only 2 IDs overlap (GRO-324, GRO-325) — both already classified out-of-lane by r135. **8/10 are net-new IDs** that had to be classified independently this tick.

## Why disposition-equivalent SUPPRESS still applies

The 4-question gate answers identically for both ticks:

- **Q1 code in Ned's lane (scripts/, prismatic/, plugins/)?** — NO for both (r135 = 6 Done + 1 AGY-session + 3 content-injection read-only; r136 = 5 content-injection + 3 external/cross-profile + 2 close-calls on AGY-retirement/HD-platform repos).
- **Q2 single winner from 10-item batch?** — NO for both.
- **Q3 would `--dry-run` churn state?** — NO for both.
- **Q4 Linear issue was worked on?** — NO for both (audit-only triage).

Even though the ID sets are 80% different, the **disposition is identical**: 0/10 in Ned's lane. The r139 rotation-equivalence ratchet holds on disposition, not on identity:

> "The scanner is recycling through different stale issue pools; the cure (relabel or dispatcher patch) is unchanged."

This is documented behavior. The cure (relabel the issues off `agent:ned`, or patch the dispatcher regex per GRO-559) is awaiting Michael's commit regardless of how fast the scanner rotates. Posting a Linear comment every 3 minutes when the scanner churns would:
1. Pollute the Linear thread with redundant triage comments
2. Train reviewers (Michael) to ignore the channel
3. Burn 96+ Linear API budget per day instead of the current ~6

## What to do differently from a "normal" SUPPRESS tick

The r59 / r154 patterns assume *some* prior-triage continuity (same anchor, similar ID set). Sub-15-min rotation breaks that assumption in the ID-overlap dimension. **But anchor continuity still holds** because the canonical anchor (GRO-485) carries the most recent Ned-triage comment regardless of which 10-item subset the scanner surfaced. So:

1. **Check anchor age independently.** Don't assume r135's anchor age carries forward if r136's batch doesn't contain GRO-485 — re-query anchor's `MAX(comment.createdAt)` directly. In this case, GRO-485 last Ned-triage was 01:47:16Z (~34 min before r136), so the 6h anchor window still holds.
2. **Classify every new ID independently.** Don't trust prior-batch triage to cover held-over IDs (here GRO-324/325 were correctly flagged again because the ratchet is about *disposition stability*, not *identity carry-over* — a held-over ID could in principle have changed disposition since r135).
3. **Suppress the Linear comment** if anchor window holds AND disposition is unchanged. The 6h-suppression window is per-anchor, not per-batch — the r139 doctrine is explicit that 10/10 rotation doesn't restart the suppression clock.
4. **Re-probe infra regardless.** Sub-15-min rotation can mask real infra changes that happen on a real-time clock. GPU Tailscale, Ollama HTTP, disk %, swarm locks — all re-probed.
5. **Write the audit doc + index row even when suppressing the Linear comment.** The audit is the auditable record; Linear is the user-visible channel. Both need accurate current state.

## Reply shape

The same r154 template applies (full per-issue classification table, infra-delta table, explicit "what rotated in / out"). The 6-line minimum is for the <2h literal case where the reader has the prior triage fresh in mind; the 2h–24h case and the sub-15-min rotation case both warrant the fuller format because the reader is unlikely to remember the specifics.

## What's NOT new here

- The 4-question gate (Q1/Q2/Q3/Q4) is unchanged.
- The r59 mechanical-SUPPRESS rule is unchanged (anchor window + disposition-equiv → SUPPRESS).
- The r139 rotation-equivalence ratchet is the one that does the heavy lifting here.
- The r150 HARD-SKIP on `finalize_task.sh` is unchanged.
- The r152 relabel action (issueUpdate labelIds mutation) is the long-term cure but requires Michael.

## What IS new (the r155 contribution)

- **Sub-15-min rotation cadence is now observed in the wild.** The 24-run same-day burst (2026-06-26, 15-min cadence) had stable identity within the window; r135→r136 is the first observation of scanner pool churn *between* two consecutive 15-min crons.
- **Disposition-equivalence ratchet works across ID-set rotation.** This is a new empirical confirmation of r139 in a more extreme parameter regime (8/10 rotation vs 0/10 rotation or 100% identity).
- **The 6h anchor window holds across rotation.** Anchor continuity is per-anchor-comment, not per-batch — this is what keeps the noise-free ratio intact even when the scanner churns.

## Audit

`okf/audits/ned-scan-triage-2026-06-30-r136.md` written, index row appended. Commit `79f3e1f` on `ned/scan-triage-2026-06-27-r7` branch (no push — pre-push hook blocks `okf/audits/` per r21+r89; 15-tick local-only streak r122-r136 awaiting Michael decision on lane ownership).

## Tool budget

~14 tool calls (1 lock check + 5 infra probes + 1 Linear per-issue triage fetch + write audit doc + index row insertion). Under the cron tick budget.
