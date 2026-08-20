# Ned — anchor detection logic (r153, 2026-06-29)

The pre-build lane check on Ned's cron pickups always starts by picking the **right anchor** for recurrence-detection. The canonical anchor is `GRO-570` (June 2026 photo-sweep anchor) — but only when it's in the current scanner feed.

## Detection algorithm

1. Run `python3 scripts/probe_recurrence.sh` (default anchor = GRO-570). Note the reported age.
2. Cross-check the **scanner feed** against the canonical anchor's identifier. If `GRO-570 in current_feed`, the probe's age is authoritative.
3. If `GRO-570 not in current_feed`, scan the current feed for the batch-member carrying the most recent Ned-triage comment:
   ```python
   candidates = [(issue, max(comments.createdAt)) for issue in current_feed
                 if has_ned_triage_comment(issue, user_email='mbgulden@gmail.com')]
   effective_anchor = max(candidates, key=lambda x: x[1])
   ```
4. Use `effective_anchor[1]` (the latest triage timestamp on the most-touched batch member) as the recurrence baseline.
5. Compare `current_feed` set to the per-issue list inside that latest triage comment. If identical → SUPPRESS. If drift → POST_FRESH_TRIAGE with drift delta.

## Worked example (2026-06-29 r1)

- Scanner feed: `GRO-484/485/486/487/488/490/492/499/500/502`
- Canonical anchor GRO-570 → not in feed. Probe reports 34.8h old (irrelevant; that's a different batch's anchor).
- Most-touched batch member: GRO-485 (6 prior Ned-triage comments today, latest at 12:01:31Z).
- Recurrence baseline: 12:01:31Z = 90 min ago.
- Item-identity vs 12:01:31Z triage comment: 10/10 identical.
- Decision: r59 mechanical-SUPPRESS (literal case — items identical + last triage <2h).

## Files

- `references/ned-r153-batch-anchor-shift-20260629.md` — the canonical session log + probe future-improvement recommendation.
- Parent skill: `autonomous-task-ownership-validation` (the r153 case study is also recorded there in §"Real-World Case Study").