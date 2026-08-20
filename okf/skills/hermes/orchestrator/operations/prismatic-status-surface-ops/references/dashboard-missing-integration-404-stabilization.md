# Dashboard Missing Integration 404 Stabilization

Use this reference when the Prismatic governance dashboard loads but individual panes/buttons produce many HTTP 404s or browser console errors after a route/domain repair.

## Durable lesson

Do not stop after the top-level dashboard route returns 200. The real stability contract is: every dashboard fetch/action route used by the template returns a non-404 response, lazy-loaded tabs do not throw JS errors, and dangerous browser controls are auditable no-ops unless a real API-backed control path exists.

## Reproduce and inventory

1. Extract dashboard fetch calls from the canonical template:

```bash
python3 - <<'PY'
import re, pathlib
text = pathlib.Path('prismatic/gateway/templates/dashboard.html').read_text()
for m in re.finditer(r"fetch\(([^\n;]+)", text):
    print(text[:m.start()].count('\n') + 1, m.group(1).strip()[:220])
PY
```

2. Compare against FastAPI route decorators:

```bash
python3 - <<'PY'
import pathlib, re
text = pathlib.Path('prismatic/gateway/server.py').read_text()
for m in re.finditer(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', text):
    print(text[:m.start()].count('\n') + 1, m.group(1).upper(), m.group(2))
PY
```

3. Probe likely missing routes locally before editing. Typical panes observed missing after the Kai/PWP integration recovery:

```text
GET  /api/dispatcher/status
POST /api/dispatcher/{action}
GET  /api/webhooks/stats
GET  /api/webhooks/queue
POST /api/webhooks/queue/retry/{task_id}
POST /api/webhooks/queue/purge
GET  /api/recovery/status
GET  /api/foundation/peer_review
POST /api/foundation/control/{action}
GET  /api/quota
POST /api/quota/poll
GET  /api/gateway/overnight-report/latest
```

## Repair pattern

- Add compatibility endpoints in `prismatic/gateway/server.py` near related dashboard/report routes.
- GET pane routes should return real available state where possible and empty-but-shaped fallback payloads otherwise.
- POST browser control routes must not shell out, invoke service managers, run agent CLIs, or mutate unknown queues destructively. Return explicit payloads such as:

```json
{"ok": true, "status": "accepted_noop", "message": "... no shell command executed ..."}
```

- Keep the UI honest: use `accepted_noop`, `empty`, or `dashboard-compat` sources rather than pretending a real worker ran.
- Run `py_compile` after editing `server.py`.

## Frontend schema mismatch pattern

After backend 404s are fixed, do a browser tab sweep. In the worked incident, the Workspaces/locks pane still threw:

```text
Cannot read properties of undefined (reading 'split')
```

Cause: `/locks` returned current shape:

```json
{"path": "...", "agent": "fred", "heartbeat": 1784...}
```

but dashboard JS expected legacy shape:

```json
{"filePath": "...", "agentId": "fred", "timestamp": 1784..., "lastHeartbeat": 1784...}
```

Make the renderer tolerate both shapes:

```js
const stalePaths = new Set(stale.map(s => s.filePath || s.path).filter(Boolean));
const lockPath = lock.filePath || lock.path || "unknown";
const agent = lock.agentId || lock.agent || "unknown";
const rawTimestamp = lock.timestamp || lock.heartbeat || lock.lastHeartbeat || 0;
const timestampSeconds = rawTimestamp > 9999999999 ? rawTimestamp / 1000 : rawTimestamp;
```

Avoid raw assumptions:

```text
lock.filePath.split(...)
formatDate(lock.lastHeartbeat / 1000)
```

## Verification pattern

Create one `/tmp/hermes-verify-*` script and remove it before returning. Verify:

- branch/head/worktree state;
- stale verifier/body temp files are absent if the workspace guard reports them;
- `server.py` declares the missing compatibility routes;
- safe control routes include explicit no-op messaging;
- dashboard lock renderer accepts current and legacy shapes;
- `server.py` compiles;
- live local GET probes return 200;
- live local POST probes are non-404;
- expected no-op routes return `accepted_noop`;
- `/api/content/status` returns `content-plugin-compat` when applicable;
- `/dashboard` is governance, not marketing;
- targeted plugin tests still pass if PWP was involved.

Then use browser tools to load `http://127.0.0.1:9000/dashboard`, click every tab, and read console output. A stable pass means no 404 console errors and no JS errors; the Tailwind CDN production warning is separate hardening noise, not a missing integration.

## PR/merge discipline

- Use a clean branch from `origin/deploy-fresh` for dashboard hotfixes.
- If auto-checkpoint commits appear, squash/reset into one `[Fred] ... (#GRO-...)` commit before PR.
- PR body should list the route matrix and state clearly: ad-hoc targeted verification only, not suite green.
- Merge to `deploy-fresh`, restart `prismatic-gateway.service`, rerun live route matrix and browser tab sweep.
- Release Antigravity locks after verification.
