# GRO-572/571/567/565/564/559/558/557/550/548 — Recurring Misrouted Sweep

**Status:** Active routing bug — same 10 items appear on every Ned cron tick for the past 24+ hours.
**First observed:** 2026-06-25 ~22:00Z.
**Last observed:** 2026-06-26 14:10Z.

## The pattern

The Prismatic Engine scanner (`scan_tasks.py`) is leaking P0 Backlog items into Ned's queue. Every issue carries `agent:ned` but the content is for other lanes:

| Issue | Title | Real lane |
|---|---|---|
| GRO-572 | Auto-generate social posts | kai / content |
| GRO-571 | Build photo tagging system | kai / content |
| GRO-567 | Pay Roberts Hart CPA balance | sam (manual money) |
| GRO-565 | Pay Q2 estimated taxes | sam (deadline past) |
| GRO-564 | Re-engage Roberts Hart CPA | sam |
| GRO-559 | Email Capture & Lead Magnet | kai / content |
| GRO-558 | Website landing pages | kai / dev |
| GRO-557 | Gumroad product page | kai / dev |
| GRO-550 | Priority Queue system | jules / agy |
| GRO-548 | Task Intake API | jules / agy |

Zero overlap with Ned's lane (infrastructure monitoring). Every cron tick produces the same 10 items.

## Documented prior triages on these items

- 2026-06-26 01:34–01:35Z: Ned posted "🔴 escalation" comments on GRO-567/565 and "not Ned-actionable" comments on GRO-572/571/564 (Michael Gulden user)
- 2026-06-26 06:44Z: Ned posted "first-time seen, not Ned-actionable" comments on GRO-559/558 (drift detection)
- 2026-06-26 14:10Z: All still in queue, no resolution. **No new comment posted** — prior triage thread is sufficient evidence.

## Items that have NOT been triaged in the last 24h

GRO-557, GRO-550, GRO-548 — first-time-seen at 14:10Z. If a fresh triage comment is warranted, these are the ones without prior documentation.

## Root cause

The Prismatic scanner's lane filter for Ned is set to `fallback_label: agent:fred` and does not have an explicit Ned-only lane gate. The cron context doesn't propagate `PRISMATIC_AGENT` (the env var is dropped at `subprocess.run(argv, ..., cwd=...)` invocation), so the scanner falls through to the fallback_label and surfaces whatever carries any `agent:*` label. The 10-item list is the global P0 Backlog spillover, not a Ned-specific filter result.

**Fix path:**
1. Edit `prismatic-engine/agents/ned/lane_config.yaml` (or equivalent) — set `fallback_label: null` and require explicit `agent:ned` label match.
2. Re-test: `python3 -m prismatic.scan_tasks --agent ned` should return only issues with `agent:ned` label and lane-matching content.
3. Re-assign the 10 items to their correct owners (`agent:kai`, `agent:sam`, `agent:jules`, `agent:agy`) so they leave the Ned queue permanently.

## What Ned cron ticks should do (recurrence gate)

Per `autonomous-task-ownership-validation` SKILL.md decision table (the SKILL.md is canonical — this file previously misquoted the 2-24h rule, see "Drift log" below for the correction):

- Items identical to last triage + last triage <2h → SUPPRESS (no Linear comment, infra delta only)
- Last triage 2-24h ago (regardless of item identity) → POST_FRESH_TRIAGE (previous triage is no longer "recent enough" to anchor the thread)
- Items drifted (any add/remove) at any age <24h → POST_FRESH_TRIAGE with "what changed" delta at top
- Last triage >24h ago → POST_FRESH_TRIAGE (likely new cron reader or backend state cleared)

## Drift log (chronological)

### 2026-06-26 17:13Z — drift detected (3 added, 3 removed)

**Current scanner items** (this tick):
GRO-571, GRO-567, GRO-565, GRO-564, GRO-559, GRO-558, GRO-557, GRO-546, GRO-545, GRO-543

**vs 11:40Z triage (baseline)**:
GRO-608, GRO-572, GRO-571, GRO-567, GRO-565, GRO-564, GRO-559, GRO-558, GRO-557, GRO-551

| Status | Issue | Title |
|---|---|---|
| ADDED | GRO-546 | Set up CRO and Analytics foundation (Beyond SaaS) |
| ADDED | GRO-545 | Add Social Proof and Testimonials section (Beyond SaaS) |
| ADDED | GRO-543 | Create Lead Magnet and Email Capture system (Beyond SaaS) |
| REMOVED | GRO-608 | LinkedIn 90-Day Calendar |
| REMOVED | GRO-572 | Auto-generate social posts from media library |
| REMOVED | GRO-551 | Error Handling and Retry (was already In Review) |

**Probe verdict:** `POST_FRESH_TRIAGE` — drift detected AND 332-min age (in 2h–24h window).

**Newly surfaced items (first-time-in-sweep):** GRO-546, GRO-545, GRO-543. All Beyond SaaS marketing/web lane. None match Ned (zero infra primitives).

**Posted:** triage comment `593b7c94-6e94-4c56-a0ca-5b8158346dad` on GRO-570 anchor at 2026-06-26T17:15:07Z.

**Lesson:** the recurrence probe MUST compare current scanner items to the items-in-last-triage, not just check age. The 16:35Z prior tick saw this same drift pattern but suppressed the Linear comment — that was a missed triage per the decision table (drift + 2-24h age → POST_FRESH_TRIAGE). The drift-detection step is in the SKILL.md decision table but easy to skip when item count and headline look "the same" at a glance.

### 2026-06-26 16:35Z — prior tick (missed triage, lesson learned)

This tick saw the same 10 items as 17:13Z (drift already present from 11:40Z) but the response was `[SILENT]` — Linear comment was suppressed despite drift. The 16:35Z session DID check recurrence via the inline probe (per its transcript) but did not cross-check current items against the items-in-the-last-triage. This is the drift-detection miss that the SKILL.md pitfall added 2026-06-26 17:13Z addresses.

## Future recurrence

If this same 10-item list appears on a cron tick >24h after this note was written, **do not re-validate from scratch** — the routing bug is now documented. Skip directly to: post a one-line recurrence note + infra-delta table. The scanner needs to be fixed at the lane-config level; Ned cron-side triage is not the durable fix.
