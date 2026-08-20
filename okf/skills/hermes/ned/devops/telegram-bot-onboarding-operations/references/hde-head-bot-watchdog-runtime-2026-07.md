# HDE head-bot watchdog runtime checks — 2026-07

Use this when the script-only `HDE head-bot router watchdog` emits broad dependency failures such as DB zero users, Redis unknown, Docker unknown, and no guest containers.

## Reusable pattern

1. Treat simultaneous `DB/Redis/Docker unknown` as a possible **metrics collection failure** before assuming an HDE outage.
2. Inspect the cron job definition and the watchdog script path. For this profile the job may call `hde_router_metrics_watchdog.py`, which shells out to `scripts/hde_router_metrics.py` through the service/runtime Python.
3. Run the metrics command directly from the staging checkout with the same `PYTHONPATH` and Python path used by the watchdog.
4. Compare that with live service state:
   - `hde_router.service`, `hde_orchestrator_staging.service`, `hde_api_staging.service` active status
   - Docker `guest-hermes-*` running/healthy counts
   - Redis queue pending counts/consumer presence
   - DB backend/user/invitation/bot-instance counts
5. If the metrics runtime is missing packages or the Python path is absent, restore the runtime dependencies/path first; do not restart live customer-facing services unless the services themselves are failing.
6. Re-run the watchdog in force mode to verify metrics are populated, then run the cron job once. Healthy script-only watchdogs should emit empty stdout.

## Interpretation

- Broad `unknown` fields with active services and healthy containers usually means the watchdog could not execute metrics, not that all dependencies failed at once.
- Redis stream `length` is retained history. Alert on `pending`, missing consumers, dependency failures, or extreme retention growth.
- A script-only watchdog is fixed only when a forced run shows populated metrics and a normal cron-triggered run stays silent.

## Verification shape

Report concrete values, not vibes:

```text
status=ok
DB backend=postgres users=<n> invitations=<n> bot_instances=<n>
Docker guest containers=<running>/<healthy>
Queues chat/wake/media pending=0 consumers>0
cron execution_success=true with no stdout
```
