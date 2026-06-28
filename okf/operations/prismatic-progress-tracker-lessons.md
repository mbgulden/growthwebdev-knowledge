# Prismatic Progress Tracker — Lessons

**Date:** 2026-06-28
**Owner:** Fred (orchestrator)
**Status:** ✅ DEPLOYED — cron `288ffc3213fe` now runs `prismatic_progress.py` every 30 min

---

## What it does

Replaces the outdated `prismatic_port_progress.py` cron (which only queried Linear). The new tracker pulls from 5 real sources:

1. **Git log** — `git log --since=7.days` for commits, `gh pr list` for PR stats
2. **Test count** — `pytest --collect-only` for current count + sprint delta
3. **OKF docs** — `okf/operations/*.md` count + per-phase breakdown
4. **Linear API** — Prismatic Engine project status (de-emphasized)
5. **Telemetry DB** — `event_router.db` queries for review/hook/plugin events (Phase 3 / Gap 12 data source)

## Output format

Emoji-header digest covering:
- Sprint status (per gap)
- PR counts (merged/open/draft in last 7d)
- Test count + progress bar to sprint target
- Factory activity (telemetry, 24h rolling)
- Phase roadmap (Phase 2-5 status)
- Momentum (7-day rolling)
- Today's events
- Next up
- 5 Horizons (always)

## Schedule

- **Every 30 min** — Autobot relay gets the digest
- **Every 2h** (every 4th tick) — Michael's Telegram home gets the digest
- **State file:** `~/.hermes/profiles/orchestrator/cron/.prismatic_progress_state.json`

## Files

- `prismatic_progress.py` — new tracker (14.9KB, 346 lines)
- `prismatic_port_progress.py.bak-2026-06-28` — archived old tracker
- Cron job ID `288ffc3213fe` updated to point at new script

## Sprint info — currently hardcoded

The `sprint_info` dict in `main()` is hardcoded for Sprint 1 of Phase 3. Future improvements:
- Derive sprint state from Linear + OKF docs (e.g., grep `okf/operations/phase*-tracker-*.md` for current phase)
- Auto-update gap statuses from PR labels (`agent:fred`, `lane:ned`, `gap-N`)
- Compute velocity from PR merge timestamps (rolling 7-day)

These are Sprint 2 improvements. For now, hardcoded is fine because Sprint 1 has known gaps + statuses.

## Honest concerns

1. **Sprint info is hardcoded** — if Phase 3 / Sprint 2 starts, I need to manually update the dict. Sprint 2 carry-forward: derive from Linear + OKF docs.
2. **Telemetry data is sparse** — Gap 12 just shipped; real telemetry data flows as factory cron ticks. Currently shows 0/0/0 because no real reviews have happened since Gap 12 landed.
3. **OKF doc count is high (29)** — includes docs from Phase 1+2 + Phase 3. Could be misleading. Could split per-phase, but currently labeled correctly.
4. **PR "open" count is 4** — those are stale PRs from Phase 2 (not Sprint 1 blockers). Could be filtered by PR age or labels.
5. **No alerting** — script posts the digest but doesn't flag regressions (e.g., if test count drops, PR merge rate falls). Sprint 2 carry-forward.

## What worked

- **Live data is motivating.** The first run showed: 9 PRs merged in 7d, +31 tests this sprint, 280/280 ✅. That's real momentum.
- **Emoji + counters format matches the existing Autobot style** — no UX change for Michael.
- **Sprint target + progress bar** gives a clear visual indicator of sprint completion (90% to Sprint 1 target = 310).

## Lessons carried forward

- **Always test live data, not just structure.** First run showed real numbers immediately; that's the value.
- **Replace + archive, not replace + delete.** Old script is at `*.bak-2026-06-28` in case we need to revert.
- **Update cron job in `jobs.json` directly.** No need for a fancy migration; just edit the JSON.

---

*Filed 2026-06-28 by Fred (orchestrator).*
