---
type: Audit
title: Prismatic Engine Verification Gap — Ground Truth (2026-06-29)
description: Machine-readable evidence that the Prismatic Engine was recording dispatches but never completing them — 635 runs, 0 completed, GRO-2051 re-dispatch loop (178 dispatches, 125 in one week). Promoted from profiles/ned/journals/ (journal audit gap G7).
tags: [prismatic-engine, telemetry, audit, verification-gap, ground-truth]
status: historical
owner: kai
last_verified: 2026-06-29
verified_by: ned
related:
  - audits/pe-verification-gap-rootcause-2026-06-29.md
---
> **Promoted 2026-08-21** from `profiles/ned/journals/2026-06-29-verification-gap-evidence.md` (journal audit gap G7 — curated, audit-grade evidence belongs in OKF, not a profile journal dir). Original author: Ned, 2026-06-29.
> **Superseded context:** the completion-loop remediation this audit drove is tracked under the 2026-08-21 journal audit, gap G8 (dashboard visibility + read APIs).
# 2026-06-29 — Prismatic Engine Verification Gap (Ground Truth)

**Source:** Direct query against `/home/ubuntu/work/prismatic-engine/prismatic_state/event_router.db` at 2026-06-29 ~21:45 UTC by Ned, in response to Michael's meta-question and Kai's critique that Ned's "the engine works" claim was overclaimed without evidence.

## TL;DR

The Prismatic Engine is **recording dispatches but never completing them**. The completion-loop exists in code (GRO-2024 marked Done), but telemetry shows **zero runs ever transition out of `dispatched` state**. Real machine-readable ground truth ≠ "the engine works." It works at the *dispatch layer*. It is broken or unwired at the *completion layer*.

## Numbers (all from event_router.db, no narrative)

### Agent runs (`telemetry_agent_runs`)

| metric | value |
|---|---|
| Total runs all-time | **635** |
| Status values seen | `dispatched` only — single value, ever |
| Runs this week (since 2026-06-23) | **503** |
| Completed runs this week | **0** |
| Completed runs all-time | **0** |
| Runs with non-null `end_time` | **0** |
| Latest run | 2026-06-25 10:21 UTC (silence for 4+ days) |
| GRO-2051 dispatches (single issue) | **178** total, **125** this week — same task re-dispatched in a loop |
| Runs by agent (this week) | kai:226, fred:152, agy:125 |

### Reviews (`telemetry_review_completed`)

| metric | value |
|---|---|
| Total rows all-time | **2** |
| Last entry | 2026-06-28 21:12 UTC |
| Both rows | `reviewer=probe`, `verdict=approve`, `impact=trivial` — smoke tests, not real review |

### Pipeline actions (`telemetry_pipeline_action`)

| metric | value |
|---|---|
| Total rows all-time | **0** |
| Latest entry | (empty table) |

### Hooks (`telemetry_hook_fired`)

| metric | value |
|---|---|
| Total rows all-time | **0** |

### Credit / token telemetry (works)

| metric | value |
|---|---|
| `telemetry_credit_ledger` | 86,105 rows, latest 2026-06-29 21:03 |
| `telemetry_media_artifacts` | 84,002 rows |
| `telemetry_token_metrics` | **0 rows** |
| `gcp_vertex_spend_events` | **0 rows** |
| `telemetry_circuit_breakers` | **0 rows** |
| `telemetry_validation_events` | **0 rows** |
| `telemetry_plugin_registered` | **0 rows** |
| `telemetry_pipeline_action` | **0 rows** |

### Engine freshness

Last write timestamp per table on 2026-06-29:

| table | last write |
|---|---|
| telemetry_credit_ledger | 2026-06-29 21:03 ✅ fresh |
| telemetry_media_artifacts | recent ✅ |
| telemetry_review_completed | 2026-06-28 21:12 (probe) |
| telemetry_agent_runs | **2026-06-25 10:21 — 4-day silence** |
| telemetry_plugin_metrics | 2026-06-16 (13-day silence) |
| Everything else | empty or older |

## The verification gap, stated cleanly

1. **The dispatch side works.** The engine reliably accepts tasks, records them, dispatches them to kai/fred/agy, and burns credits (86k ledger entries). PRs and crons route through the system.

2. **The completion side does not work.** Zero runs have ever transitioned past `dispatched`. GRO-2024 was marked **Done P0** ("Enforced self-review + peer review loop in dispatcher") on a date that pre-dates the bulk of these dispatches — the loop enforcement is in code, but the status column never advances.

3. **GRO-2051 was re-dispatched 178 times** (Jun 19 → Jun 25) and still ended with `end_time=NULL` on every row. The retry logic fires; the completion event never does.

4. **Pipeline action / hook_fired / plugin_registered tables have ZERO rows all-time.** The dispatcher writes telemetry at dispatch but never fires the completion hook.

5. **Vertex spend ledger is empty** despite the engine being set up to track GCP spend (GRO-2656 done Mar, schemas in place). Either Lyria / Vertex was never invoked, or the telemetry writer is unwired.

6. **4-day silence on telemetry_agent_runs since Jun 25.** Either the dispatcher stopped running, or dispatches are going somewhere I can't see.

## Relationship to existing tasks

These existing issues are *adjacent but not identical*:

- GRO-2845 SILENT-CRON: Prismatic Engine Ned autonomous task loop — symptom of this gap
- GRO-2886, GRO-2892, GRO-2894: Gap 7/8 (failure classification + peer-review wiring) — direct work on the completion path
- GRO-2034: Webhook handler Linear-budget coverage silent loophole
- GRO-2024 (Done): Self-review + peer review loop — **appears done but telemetry shows closure never fires**

The hole: nobody is tracking the actual *measured completion rate* as a metric. The Done columns say work shipped; the SQLite says it didn't.

## Action taken

Created 4 Linear tasks today to make the verification gap visible at the issue level (so the gap itself is a tracked entity with status, owner, and an end-state measurable in `event_router.db`):

- [Ned] Verify completion-loop fix: assert at least 1 row in `telemetry_agent_runs` with non-null `end_time` after a real GRO-### run in current week
- [Ned] Investigate GRO-2051 retry storm (178 dispatches, 0 completions) — root-cause + write a regression-prevention rule
- [Ned] Close telemetry_schema_gap: why is `telemetry_token_metrics` empty if the dispatcher records `telemetry_credit_ledger`? Track down the missing writers
- [Ned] Investigate 4-day telemetry silence since 2026-06-25 10:21 UTC on `telemetry_agent_runs`

## Posture this exposes in me (Ned)

I had a 70% memory profile last session claiming "the engine is the means, not the end" and "cron fires, persistence is real, journals survived." True. Incomplete. The means layer is partially wired:

✅ dispatch layer
✅ credit/media ledger
❌ completion layer
❌ validation hooks
❌ token/vertex spend writers
❌ observable engine freshness

Kai's critique was correct: "things work, but 'working' is claimed more than demonstrated." The Demonstrated column is short.

I should not have answered "yes the engine is working" without first running this query. The watchdog slept on its own signal.
