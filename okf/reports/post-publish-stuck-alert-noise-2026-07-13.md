---
type: Report
title: Post-publish stuck alert noise — 2026-07-13
description: Incident report for test/smoke post-publish issue paging Michael as a stuck production alert.
resource: okf/reports/post-publish-stuck-alert-noise-2026-07-13.md
tags: [report, incident, hermes, cron, telegram, post-publish, alert-noise]
timestamp: 2026-07-13T20:00:00Z
linear_issue: GRO-2268
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/post-publish-stuck-alert-noise-2026-07-13.md
last_verified: 2026-07-13
verified_by: fred
status: current
---

# Post-publish stuck alert noise — 2026-07-13

## Incident

The post-publish stuck alert cron paged Michael for a test/smoke issue instead
of staying silent.

| Field | Value |
|---|---|
| Cron job | `73dc208351d6` — Post-Publish Stuck Alert daily Telegram digest |
| Script | `/home/ubuntu/.hermes/profiles/orchestrator/scripts/post_publish_stuck_alert.py` |
| Wrapper | `/home/ubuntu/.hermes/profiles/orchestrator/scripts/post_publish_stuck_alert.sh` |
| Noisy issue | GRO-2268 — `[TEST] Post-publish integration review end-to-end smoke test` |
| Root cause | Test/smoke debris matched production stuck-alert criteria; script also had an unused internal Telegram-send path. |

## Fix

- Exclude `[TEST]`, `TEST:`, and `Smoke test` issues from Michael-facing stuck alerts.
- Remove the internal Telegram sender from the Python producer.
- Let Hermes cron delivery own Telegram delivery.
- Run scheduler wrapper with `--quiet`.
- Preserve empty stdout when no production stuck alerts exist.

## Verification

Scope label: **ad hoc targeted verification, not full suite-green**.

| Check | Result |
|---|---:|
| Python compile | pass |
| Producer executable | pass |
| Wrapper executable | pass |
| Source markers present | pass |
| Live dry-run issue count | `total_issues=1`, `stuck_count=0`, `new_alerts=0` |
| Quiet wrapper stdout | `0` bytes |
| Cron config | `no_agent=true`, script `post_publish_stuck_alert.sh`, deliver `telegram:8190664947` |
| Scheduler status | `ok`, no delivery error |

## Prevention rule

Test/smoke fixtures must not page Michael from production alert jobs. If a cron
is intended to surface production blockers, test debris belongs in logs or test
reports, not Telegram-bound stdout.

Related standard: [Cron alert output contract](../standards/cron-alert-output-contract.md).
