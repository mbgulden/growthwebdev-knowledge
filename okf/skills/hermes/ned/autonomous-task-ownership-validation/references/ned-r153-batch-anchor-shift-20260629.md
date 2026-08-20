# Ned r153 — Anchor may shift when the scanner rotates to a fresh misroute batch

**Date:** 2026-06-29 ~13:31Z
**Trigger:** This tick surfaced a fresh 10-item recurring misroute batch (GRO-484/485/486/487/488/490/492/499/500/502). The canonical anchor probe (`probe_recurrence.sh`, default anchor = GRO-570) reported "34.8h old, POST_FRESH_TRIAGE" — but that anchor belongs to a *different* misroute batch (the 2026-06-28 bootcamp rotation), and GRO-570 is not in the current scanner feed.

## What went right

This tick recognized that the **batch anchor for recurrence-detection** is whichever issue in the current scanner feed has the most recent Ned-triage comment — not GRO-570. Today that's **GRO-485** (6 prior Ned-triage comments between 09:25Z and 12:01Z, all carrying the dequeue pattern). Cross-check via `comments(last: 10)` on GRO-485 showed last triage at 12:01:31Z (90 min ago). Combined with item-identity check (10/10 identical to today's prior passes), the **r59 mechanical-SUPPRESS rule applied literally** for the first time on this batch.

## Decision (r153)

When the scanner feed contains zero matches with the canonical anchor (GRO-570 default) but has ≥3 issues with prior Ned-triage comments between 09:00Z and now, the **effective anchor is the batch-member with the most recent Ned comment**. Use that issue's `comments(last: 10).MAX(createdAt)` as the recurrence baseline. The probe's default-anchor age is informational only — what matters for SUPPRESS-vs-POST is the age of the latest triage on the *current batch's effective anchor*.

## Probe future improvement (recommendation, not yet implemented)

`scripts/probe_recurrence.sh` should:
1. Accept the current scanner feed's identifiers as input.
2. Pick the anchor = argmax(`MAX(comments.createdAt where user.email matches Ned agent)`) across the input set.
3. Return that anchor's age plus the input-set identity delta vs the last triage's per-issue list.

Currently the probe hard-codes GRO-570 and is unreliable for batch-rotated scans. Until patched, always sanity-check by manually querying `comments(last: 10)` on the most-touched batch member.

## File path reminder

Audit convention: `~/work/okf/audits/ned-scan-triage-YYYY-MM-DD-rN.md` with `rN` per calendar day. Index row added to `~/work/okf/audits/index.md`.