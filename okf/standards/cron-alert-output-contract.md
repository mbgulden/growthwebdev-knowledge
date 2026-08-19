---
type: Standard
title: Cron alert output contract
description: Contract for Hermes no-agent cron stdout, Telegram delivery, quiet mode, and user-facing alert bodies.
resource: okf/standards/cron-alert-output-contract.md
tags: [standard, hermes, cron, telegram, alerts, no-agent, output-contract]
timestamp: 2026-07-29T05:30:00Z
linear_issue: GRO-3792
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/cron-alert-output-contract.md
last_verified: 2026-07-29
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

## Companion skills (2026-07-29 sweep)

- Micro-skill: `~/.hermes/profiles/orchestrator/skills/micro/telegram-cron-output-contract/` — single-page recipe for the contract, including forbidden stdout patterns and implementation requirements.
- Verifier: `~/.hermes/profiles/orchestrator/skills/verifiers/telegram-cron-output-check/verify.py` — scans Telegram-bound cron scripts for forbidden stdout patterns. Run on every cron script change.

## Concrete fixes shipped in the 2026-07-29 sweep

The verifier flagged 10 scripts with violations; all were fixed:

- `golden_thread_cross_project_sync.py` — silent when stale=0 and missing=0; bolded action line otherwise.
- `cf_access_health_check.py` — silent when no problems; concise alert otherwise. Removed double-delivery (script's own send_telegram + cron deliver=origin).
- `consulting_pipeline_delta.py` — moved `[CONSULTING-PIPELINE]` scaffolding to stderr.
- `peer_review_orchestrator.py`, `post_publish_doc_update.py`, `jules_dispatcher.py`, `kai_delta_dispatcher.py` — removed `[SILENT]` stdout prints (silent exit means *no* stdout, not a marker).
- `delta_cache.py` — removed `[SILENT]` print from `exit_silent()` method.
- `post_publish_stuck_alert.py` — replaced `[SILENT]` print with `pass` (gated by `not args.quiet`, never reached in cron mode).
- `agy_golden_thread_delta.py`, `content_engine_delta.py` — moved `AGY exit` scaffolding to stderr.
- `morning_digest.py` — moved `Telegram send failed` warning to stderr.
