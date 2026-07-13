---
type: Standard
title: Cron alert output contract
description: Contract for Hermes no-agent cron stdout, Telegram delivery, quiet mode, and user-facing alert bodies.
resource: okf/standards/cron-alert-output-contract.md
tags: [standard, hermes, cron, telegram, alerts, no-agent, output-contract]
timestamp: 2026-07-13T20:00:00Z
linear_issue: GRO-3792
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/cron-alert-output-contract.md
last_verified: 2026-07-13
verified_by: fred
status: current
---

# Cron alert output contract

## Standard

For Hermes `no_agent=True` cron jobs delivered to Telegram, stdout is the user
message. Therefore stdout must be either:

1. **empty** when there is no actionable alert, or
2. a **complete, user-facing alert** with no scratchpad, progress chatter, debug
   lines, raw API dumps, or internal agent scaffolding.

Anything else is a pager bug.

## Required behavior

| Condition | stdout | Delivery outcome |
|---|---|---|
| No production/actionable alert | empty | silent |
| Test/smoke/debris-only alert | empty | silent |
| Real blocker | concise Markdown alert | delivered |
| Upstream/agent failure with actionable impact | concise failure alert with exact blocker | delivered |
| Internal diagnostics | stderr, logs, or cron output artifact only | not user-paged |

## Forbidden stdout patterns

- `I am going to...`
- `I will...`
- `Let me...`
- `Thinking...`
- AGY background-task scaffolding such as `An update was received from a background task:`
- `[NIGHTLY-BACKLOG] ...` progress/debug lines
- raw token/env warnings that are not actionable to Michael
- green pulses / `[SILENT]` markers in Telegram-bound stdout

## Implementation requirements

1. Prefer a producer-level `--quiet` mode for scheduler use.
2. Do not send Telegram internally from a script when Hermes cron already has
   `deliver=telegram:...`.
3. Filter test/smoke issues before alert generation.
4. Sanitize LLM/AGY output before printing.
5. If sanitized output has no user-facing signal, print a deterministic compact
   fallback or stay silent, depending on whether an actionable delta exists.
6. Verify with a fresh `/tmp/hermes-verify-*` script that checks stdout length,
   representative noisy fixtures, and live scheduler config.

## Reference incidents

- [Post-publish stuck alert noise — 2026-07-13](../reports/post-publish-stuck-alert-noise-2026-07-13.md)
- [Nightly backlog cron output sanitization — 2026-07-13](../reports/nightly-backlog-cron-output-sanitization-2026-07-13.md)
- [Orchestrator cron hardening summary — 2026-07-13](../reports/orchestrator-cron-hardening-summary-2026-07-13.md)
