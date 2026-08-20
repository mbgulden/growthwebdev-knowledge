# Prismatic dashboard healthy route fix — 2026-07-09

## Symptoms

- `https://prismatic.growthwebdev.com` showed `DEGRADED` even though core services/endpoints were active.
- `https://prismatic.growthwebdev.com/dashboard` returned:

```json
{"detail":"Not Found"}
```

## Root causes

1. The deployed gateway served the dashboard only at `/`, not `/dashboard`.
2. The status page treated cumulative `NRestarts > 0` as permanent degradation even after services had been active for over a day.
3. Dashboard panels rendered stale durable-history entries as if they were current health:
   - `fake-broken-service`
   - `[SYNTHETIC TEST] ...`
   - `synthetic=true`

## Fix pattern

- Add `/dashboard` as an alias decorator on the existing dashboard handler:

```python
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    ...
```

- Treat restarts as degradation only during a fresh recovery window:

```python
any_service_restarted = any(
    stats["restarts"] > 0 and 0 < stats.get("uptime_seconds", 0) < 300
    for stats in service_stats.values()
)
```

- Filter stale synthetic alerts/recovery entries from the live dashboard presentation while leaving logs intact.

## Verification evidence shape

Local live checks after restart:

```text
root:      200 text/html; charset=utf-8 -> HEALTHY
dashboard: 200 text/html; charset=utf-8 -> HEALTHY
```

Browser proof against `http://127.0.0.1:9000/dashboard` and then public `https://prismatic.growthwebdev.com/dashboard` showed:

```text
Prismatic Engine Status
HEALTHY
First-failing layer: none
```

Ad hoc verifier contract:

```text
AD_HOC_VERIFY_PASS prismatic dashboard route
changed_path_exists=true
py_compile=passed
route_decorators=root_and_dashboard_present
live_health_endpoint=status_ok
root_route=200_html_HEALTHY
dashboard_route=200_html_HEALTHY
dashboard_not_found=false
cleanup_exists=false
```

Public Cloudflare verification required a scoped Fred verifier-IP Access bypass; see `cloudflare-access-incident-remediation/references/prismatic-verifier-ip-bypass-2026-07-09.md`.
