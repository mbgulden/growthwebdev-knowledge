# Resources budget caps port + stale-guard proof pattern

Use this reference when porting a bounded dashboard-adjacent slice from an older/dirty worktree into the durable Prismatic dashboard without replacing the current shell.

## Trigger

Michael asks for a clean branch like:

```text
Create feature/fred-resources-budget-caps from origin/main.
Port only the GRO-3355 Resources budget-cap pieces from /home/ubuntu/work/kai-gro-3355-resources-panel.
Preserve current dashboard shell and /api/gateway conventions.
Do not port the older dashboard shell.
Verify with budget cap tests, dispatcher guard tests, dashboard JS check, and local API proof.
```

## Porting rules

1. Start from current `origin/main`, not the source worktree branch:

```bash
cd /home/ubuntu/work/prismatic-engine
git fetch origin --quiet
git switch -C feature/fred-resources-budget-caps origin/main
```

2. Lock only the files in the bounded slice:

```text
prismatic/budget_caps.py
tests/test_budget_caps.py
prismatic/gateway/server.py
prismatic/gateway/templates/dashboard.html
prismatic/dispatcher.py
tests/test_dispatcher_activation.py
```

3. Port backend/helper/tests directly from the source only when they are small and self-contained:

```text
prismatic/budget_caps.py
tests/test_budget_caps.py
```

4. For gateway routes, preserve public dashboard conventions by adding both local and gateway-prefixed aliases:

```python
@app.get("/api/quota/caps")
@app.get("/api/gateway/quota/caps")
async def get_budget_caps() -> dict[str, Any]:
    return read_budget_caps()

@app.post("/api/quota/caps")
@app.post("/api/gateway/quota/caps")
async def set_budget_caps(body: dict[str, Any]) -> dict[str, Any]:
    return write_budget_caps(body)
```

5. For dashboard HTML, do **not** port an older shell. Patch only the current durable quota/resources section and preserve these markers:

```text
workspace-tree-mobile-responsive
dashboard-tabs-mobile-wrap
dashboard-header-mobile-wrap
```

Add a specific marker for the new slice:

```html
data-proof-marker="resources-budget-caps-controls"
```

6. In dashboard JS, use the public gateway convention:

```javascript
fetch(`${API_PREFIX}/quota/caps`)
```

not bare `/api/quota/caps` in the dashboard path.

7. Add dispatcher guard coverage, not just helper tests. The guard test should prove:

- saved/configured caps are detected;
- telemetry daily spend above cap blocks before launcher execution;
- Linear comment is posted;
- pipeline metrics are logged as blocked;
- dedup is marked processed;
- `counts["budget_paused"] == 1`.

Watch for dispatcher label normalization: the processed label can be `agent:fred` even if the query lane was `agent::fred`.

## Verification pattern

Use one focused `/tmp/hermes-verify-*` script. Check all changed paths plus any stale temp path named by the guard.

Minimum checks:

```text
python3 -m py_compile prismatic/budget_caps.py prismatic/gateway/server.py prismatic/dispatcher.py
python3 -m pytest -q tests/test_budget_caps.py tests/test_dispatcher_activation.py
node --check /tmp/hermes-dashboard-inline-resources-budget-caps.js
route registration includes /api/quota/caps and /api/gateway/quota/caps
local API proof: GET/POST /api/gateway/quota/caps and GET /api/quota/caps
```

For local gateway API proof, run the server with an isolated temp `HOME` and `PRISMATIC_STATE_DIR` so the test does not read or write real operator budget caps. If the default `python3` environment lacks gateway dependencies such as FastAPI, use the existing stable Prismatic venv for the gateway subprocess while keeping the main tests under the branch environment:

```text
/home/ubuntu/.prismatic/venv_stable/bin/python3 -m prismatic.gateway.server --host 127.0.0.1 --port <free-port>
```

This captures the fix/setup path, not a durable claim that any tool is broken.

## Stale-guard shape

When Hermes reports an old mobile overflow proof but changed paths are budget-cap files, do not chase the old mobile proof. Run a fresh verifier scoped to the actual changed paths and explicitly include stale temp files as absent, e.g.:

```text
changed_paths_checked=/home/ubuntu/work/prismatic-engine/prismatic/budget_caps.py,...,/tmp/hermes-verify-resources-budget-caps.py
stale_temp_path_absent=true
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=production_deployed,canonical_full_suite_green,older_dashboard_shell_ported
MARKER=RESOURCES_BUDGET_CAPS_PORT_OK
```

Clean up both the exact stale temp path and the fresh verifier prefix before reporting `cleanup=PASS`.

## PR hygiene

Hermes auto-checkpoint commits can appear mid-session. Before final PR, inspect `origin/main..HEAD` and squash auto-checkpoints into one clean Fred commit:

```bash
git log --oneline --decorate --stat origin/main..HEAD
git reset --soft origin/main
git commit -m "[Fred] Add Resources budget caps guard (#GRO-3355)"
git push --force-with-lease
```

Then confirm the PR contains one intended commit and CI is green/clean before reporting. Do not merge/deploy unless explicitly asked.
