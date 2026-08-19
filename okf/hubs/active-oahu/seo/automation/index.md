---
type: Index
title: Automation Stack
description: Cron job configs, reporting scripts, alert thresholds, MCP refresh procedures for the AOT SEO initiative.
tags: [index, automation, cron, scripts, alerts]
timestamp: 2026-06-19T13:30:00Z
linear_issue: null
git_path: okf/automation/index.md
status: current
visibility: private
resource: okf/hubs/active-oahu/seo/automation/index.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Automation Stack

## Cron schedule (Hermes)

These cron jobs run the day-by-day / week-by-week / month-by-month reporting cadence.

| Frequency | Cron | Job | Owner | Output |
|---|---|---|---|---|
| Daily 06:00 UTC | `0 6 * * *` | rank-tracker-aot | kai | `okf/reports/daily-rank-YYYY-MM-DD.md` |
| Daily 06:30 UTC | `30 6 * * *` | broken-link-checker-aot | kai | appended to `okf/reports/broken-links.md` |
| Daily 07:00 UTC | `0 7 * * *` | token-expiry-check | kai | alerts to Kai if tokens expire in <7d |
| Weekly Mon 08:00 UTC | `0 8 * * 1` | weekly-digest | kai | Telegram + `okf/reports/weekly-digest-YYYY-MM-DD.md` |
| Weekly Mon 09:00 UTC | `0 9 * * 1` | weekly-ubs-sweep | kai | `okf/reports/weekly-sweep-YYYY-MM-DD.md` |
| Monthly 1st 09:00 UTC | `0 9 1 * *` | monthly-competitor-velocity | kai | `okf/reports/monthly-competitor-velocity-YYYY-MM.md` |
| Monthly 1st 10:00 UTC | `0 10 1 * *` | monthly-content-audit | kai | `okf/reports/monthly-content-audit-YYYY-MM.md` |
| Monthly 1st 11:00 UTC | `0 11 1 * *` | monthly-conversion-audit | kai | `okf/reports/monthly-conversion-audit-YYYY-MM.md` |
| Quarterly | (manual) | full-baseline-audit | kai | `okf/audits/baseline-YYYY-MM-DD/` |

## Alert thresholds

| Metric | Threshold | Action |
|---|---|---|
| Any rank drop ≥3 positions (single day) | Telegram alert to Michael within 30 min | Kai investigates immediately |
| Organic traffic drop >20% week-over-week | Telegram alert + Linear ticket | Kai runs diagnostic sweep |
| New broken internal link | Linear ticket auto-created | Kai-CSS assigns fix |
| New 5xx server error | Linear ticket (P0) | Kai-CSS investigates within 1 hour |
| Token expiry within 7 days | Kai alert | Re-auth flow triggered |
| GA4 conversion event anomaly | Linear ticket | Kai investigates booking funnel |
| Ubersuggest MCP rate-limit (429) | Auto-retry with backoff | Switch to monthly scope if persistent |

## Scripts (to be authored)

These are the cron scripts to build. Each has:
- Shebang `#!/usr/bin/env python3`
- Logging to `~/.hermes/profiles/kai/cron/output/aot-seo/`
- JSON output for machine-readable + Markdown summary for human-readable
- Telegram delivery on alerts

| Script | Purpose |
|---|---|
| `scripts/rank_tracker.py` | Daily rank check for top 50 keywords |
| `scripts/broken_link_checker.py` | Daily broken-link scan |
| `scripts/token_expiry_check.py` | Token health check |
| `scripts/weekly_digest.py` | Monday morning Telegram digest |
| `scripts/weekly_ubs_sweep.py` | Lighter weekly Ubersuggest re-sweep |
| `scripts/monthly_competitor_velocity.py` | Track competitor content output + backlinks |
| `scripts/monthly_content_audit.py` | Score every published page on quality dimensions |
| `scripts/monthly_conversion_audit.py` | GA4 funnel for top 10 revenue pages |
| `scripts/build_full_photo_index.py` | Full library scan with EXIF + GPS |

## Refresh procedures

- **Ubersuggest MCP token:** `/tmp/ubs_token` (2-day TTL on tier1 re-auth). Refresh via `/tmp/ubs_refresh` before expiry.
- **Google OAuth token:** `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json` (mbgulden@gmail.com). Currently has Drive/Gmail/Sheets/Docs scopes. Needs re-auth with `webmasters.readonly` + `analytics.readonly` for GSC + GA4 access. Procedure documented in `okf/integrations/google-oauth-extended.md`.

## Telegram delivery

Daily digest at 8 AM Monday:
- Channel: Michael's Telegram DM with Kai
- Format: Markdown with bold/italics, links to reports
- Length: concise — top 3 movers, top 3 issues, top 3 priorities for the week

Alert messages (any time):
- One-line summary with link to report
- Severity emoji: 🔴 critical, 🟡 warning, 🟢 informational

## Cron install commands

Once scripts are ready, install via:
```bash
crontab -e
# Add the cron jobs from this index.md
```

All cron output goes to `~/.hermes/profiles/kai/cron/output/aot-seo/` for debugging.
