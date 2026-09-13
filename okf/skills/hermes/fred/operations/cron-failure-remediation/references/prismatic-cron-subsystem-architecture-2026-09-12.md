# Prismatic Cron Subsystem Architecture (2026-09-12 audit)

Condensed from the full audit at `okf/audits/prismatic-cron-runner-status-audit-2026-09-12.md` (PR #57).

## Three layers

| Layer | What | Path | State (2026-09-12) |
|-------|------|------|---------------------|
| L3: Hermes native cron | Per-profile `jobs.json`, gateway tick loop | `~/.hermes/profiles/<name>/cron/jobs.json` | LIVE, fragile (import bugs) |
| L2: SwarmCron | Portable zero-dep scheduler, DAG, receipts | `~/Github/swarmcron/` (v0.3.0) | BUILT, not installed |
| L1: Prismatic cron authority | `cron_runner.py` + `cron_authority.py` + receipts | `prismatic/cron_runner.py` (1,814L) | BUILT, 97 tests pass, 0 callers |

## Key gap: nothing connects the layers

- L1 (`run_once()`) is a one-shot execution authority — takes a pre-built `CronTriggerEnvelope`, executes transactionally. NOT a scheduler.
- L2 (SwarmCron) has `CronScheduleEvaluator` + `registry.mutate()` but no tick loop.
- L3 (Hermes) is what's actually running everything.
- No adapter translates SwarmCron task fires → Prismatic trigger envelopes.

## SwarmCron package state

- Local clone: `~/Github/swarmcron/` (v0.3.0, MIT, zero external deps)
- Declared in `prismatic-engine/pyproject.toml` as `swarmcron @ git+https://github.com/mbgulden/swarmcron.git@main`
- **INSTALLED (2026-09-12, Phase 2 done):** `pip install -e ~/Github/swarmcron/` into the hermes-agent venv → `swarmcron 0.3.0 at /home/ubuntu/Github/swarmcron/swarmcron/__init__.py`, CLI at `venvs/hermes-agent/bin/swarmcron`. Editable install means local edits are live without reinstall. (Before this, only swarmlock, swarmledger, swarmsaga, swarmgate, swarmproof were installed.)
- **E2E-verified (2026-09-12):** `swarmcron register --id journal-snapshot --name ... --schedule "0 * * * *" --command /home/ubuntu/.local/bin/prismatic-journal-snapshot --group journal --cwd /home/ubuntu --timeout 300` → `swarmcron run journal-snapshot` returned a `CronRunReceipt` (`status: success`, `exit_code: 0`, `duration_ms: ~3900`, stdout = snapshot JSON). `swarmcron list` then showed `last_status: success`, `last_run_at` populated. NOTE: `register` has no `--description` flag (only `--id --name --schedule --command [--group --cwd --depends-on --tags --timeout]`).
- 17 swarm* packages declared in pyproject.toml, only 5 were installed (now 6 with swarmcron)

## Journal jobs (orchestrator profile)

| Job | Type | Schedule | Fix needed |
|-----|------|----------|------------|
| Hermes daily journal snapshot | no_agent | 60m | Shebang fix (system→venv python) |
| Hermes daily journal recap | agent | 23:59 UTC | `is_job_runnable` backport |
| Becca Journal Recap | agent | 23:59 UTC | same |
| Becca Journal Snapshot | no_agent | 60m | — |
| Weekly Journal Rollup | agent | Sun 10:00 | same |
| Monthly Journal Continuity Audit | no_agent | 1st 09:00 | — |

## Migration path (GRO-4214..4260, not started)

Phase 1: Unblock (fix import + shebang) ✅
Phase 2: Install swarmcron (`pip install -e ~/Github/swarmcron/`)
Phase 3: Build tick loop (daemon or gateway-integrated)
Phase 4: Bridge swarmcron ↔ prismatic authority (adapter class)
Phase 5: Migrate journal jobs to swarmcron
Phase 6: Generalize + CLI + dashboard

## Diagnostic recipes

```bash
# Check if a function exists in the gateway's import path
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "from cron.jobs import is_job_runnable; print('OK')"

# Check if a swarm* package is installed
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "import swarmcron; print(swarmcron.__file__)"

# Check where prismatic resolves from
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "import prismatic; print(prismatic.__file__)"

# Run the prismatic cron test suite
cd /home/ubuntu/work/prismatic-engine && /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -m pytest tests/test_cron_runner.py tests/test_cron_authority.py tests/test_cron_receipts.py tests/test_native_crons.py tests/test_seo_cron_extensions.py -q

# Check which swarm* packages are installed
for pkg in swarmcron swarmcurator swarmlock swarmrouter swarmledger swarmsaga swarmgate swarmproof; do
  /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "import $pkg; print('$pkg: OK')" 2>/dev/null || echo "$pkg: NOT INSTALLED"
done
```
