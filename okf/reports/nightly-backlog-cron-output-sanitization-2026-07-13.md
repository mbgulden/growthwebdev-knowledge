---
type: Report
title: Nightly backlog cron output sanitization — 2026-07-13
description: Incident report for AGY scratchpad/progress text leaking into the Nightly Autonomous Backlog Worker Telegram delivery.
resource: okf/reports/nightly-backlog-cron-output-sanitization-2026-07-13.md
tags: [report, incident, hermes, cron, telegram, agy, backlog, output-sanitization]
timestamp: 2026-07-13T20:00:00Z
linear_issue: GRO-3792
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/nightly-backlog-cron-output-sanitization-2026-07-13.md
last_verified: 2026-07-13
verified_by: fred
status: current
---

# Nightly backlog cron output sanitization — 2026-07-13

## Incident

The Nightly Autonomous Backlog Worker delivered AGY work-log text to Telegram.
The job was `no_agent=True`, so raw script stdout became the message Michael saw.

| Field | Value |
|---|---|
| Cron job | `0ce73bbeee4e` — Nightly Autonomous Backlog Worker |
| Script | `/home/ubuntu/.hermes/profiles/orchestrator/scripts/nightly_backlog_delta.py` |
| Root cause | Script printed progress lines and raw AGY stdout when AGY did not return clean green JSON. |
| User impact | Telegram received scratchpad such as `I am going to...`, AGY background-task scaffolding, and `[NIGHTLY-BACKLOG] ...` debug lines. |

## Fix

- Removed `[NIGHTLY-BACKLOG] ...` stdout progress lines.
- Added output sanitizer for AGY scratchpad/progress/scaffolding.
- Preserved actual blocker tables and recommendations.
- Green/no-delta path now exits with empty stdout.
- AGY noisy/failure path emits a deterministic compact delta table rather than raw thought/process text.
- Ensured script is executable.

## Verification

Scope label: **ad hoc targeted verification, not full suite-green**.

| Check | Result |
|---|---:|
| Python compile | pass |
| Script executable | pass |
| Scratchpad fixture sanitizes to empty | pass |
| Background-task scaffold stripped | pass |
| Blocker table + recommendation preserved | pass |
| Deterministic fallback compact/user-facing | pass |
| Green/no-delta live run | exit `0`, empty stdout, empty stderr |
| Cron config | `no_agent=true`, script `nightly_backlog_delta.py`, deliver `telegram:8190664947` |
| Scheduler output | `silent (empty output)` |

## Prevention rule

Any future cron that shells out to AGY/LLM tools must treat tool stdout as
untrusted. Sanitize before printing, and print only user-facing Markdown or
nothing.

Related standard: [Cron alert output contract](../standards/cron-alert-output-contract.md).
