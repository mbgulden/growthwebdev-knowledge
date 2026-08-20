# Cron Silent-Success Detection

Silent `no_agent=true` crons should remain quiet when healthy, but they still need a durable proof-of-run trail. The profile-audit watchdog uses the following pattern.

## Profile audit watchdog pattern

Script: `/home/ubuntu/.hermes/profiles/ned/scripts/hermes_profile_audit_watchdog.sh`

On every run, including clean runs with empty stdout:

1. Run the real audit command: `python3 hermes_profile_audit.py --apply --verify`.
2. Parse the summary counters: profiles scanned, critical findings, warnings, and patches.
3. Emit a heartbeat event to `/home/ubuntu/work/prismatic-engine/prismatic_state/event_bus.db` with `source='profile-audit-watchdog'`.
4. Insert a compact metrics row into `/home/ubuntu/work/prismatic-engine/prismatic_state/curator_metrics.db`:
   `audit_runs(run_at, profiles_scanned, issues_found, critical, warnings, patches, status, runtime_ms, exit_code)`.
5. Keep stdout empty when status is clean; print only on warnings, critical findings, patches, or audit execution failure.

## Staleness monitor

Script: `/home/ubuntu/.hermes/profiles/ned/scripts/check_profile_audit_heartbeat.sh`

Default threshold is 12 hours. The profile audit runs every 6 hours, so 12 hours allows one missed run before alerting and catches two consecutive misses.

Healthy state is silent. Alert state prints one line naming the source, latest heartbeat timestamp, and age.

## Verification query

Use Python because sqlite3 CLI is not guaranteed on the host:

```bash
python3 - <<'PY'
import sqlite3
for db, sql in [
    ('/home/ubuntu/work/prismatic-engine/prismatic_state/event_bus.db',
     "select source, timestamp, payload from events where type='heartbeat' and source='profile-audit-watchdog' order by id desc limit 1"),
    ('/home/ubuntu/work/prismatic-engine/prismatic_state/curator_metrics.db',
     "select run_at, profiles_scanned, issues_found, status, runtime_ms, exit_code from audit_runs order by id desc limit 1"),
]:
    print(db)
    with sqlite3.connect(db) as conn:
        print(conn.execute(sql).fetchone())
PY
```

## Rule

Do not make healthy silent crons noisy just to prove they ran. Record heartbeat + metrics, then alert only on stale heartbeat or real findings.
