# PWP/content status stabilization pattern

Use when the Prismatic governance dashboard or content/plugin panes show errors such as `PWP status refresh failed: HTTP 404`, or when plugin work appears to have disappeared after branch promotion.

## Durable lesson

Do not assume a 404 means the plugin work was deleted. In the Prismatic repo, PWP/plugin work can be split across `main`, `deploy-fresh`, local branches, and untracked local theme files. Stabilization requires checking both route compatibility and whether the actual plugin package/manifest is present on the branch that the live gateway uses.

## Triage sequence

1. Probe canonical and legacy status routes locally:

```bash
for p in \
  /api/pwp/status \
  /pwp/status \
  /api/content/status \
  /content/status \
  /api/plugins/catalog \
  /dashboard; do
  curl -sS -o /tmp/body -w "$p HTTP %{http_code}\n" "http://127.0.0.1:9000$p"
  head -c 200 /tmp/body; echo
done
```

2. Compare live branch contents against the branch where work may already be merged:

```bash
git diff --name-status origin/main..origin/deploy-fresh -- plugins/pwp scripts/pwp prismatic/gateway/server.py
git ls-tree -r --name-only origin/main plugins/pwp | head
git ls-tree -r --name-only origin/deploy-fresh plugins/pwp | head
```

3. Check for stranded local work before cleaning untracked files:

```bash
find plugins/pwp/themes -type f | sort | sed -n '1,80p'
git ls-tree -r --name-only origin/main plugins/pwp/themes | wc -l
git ls-tree -r --name-only origin/deploy-fresh plugins/pwp/themes | wc -l
```

If local theme files exist but are absent from both branches, preserve them intentionally in the stabilization branch rather than deleting them as test junk.

## Stabilization pattern

- Restore the actual `plugins/pwp` package/manifest onto the live/staging branch.
- Restore the matching `scripts/pwp` CLI shim if targeted tests expect newer subcommands such as `credentials status` / `credentials refresh`.
- Preserve stranded Kai/reference theme files under `plugins/pwp/themes/` when they are real theme assets.
- Keep canonical `/api/pwp/status` and add compatibility aliases for stale panes instead of breaking the dashboard:

```python
@app.get("/pwp/status")
async def pwp_status_compat() -> dict[str, Any]:
    return integration_status()

@app.get("/api/content/status")
@app.get("/content/status")
async def content_status_compat() -> dict[str, Any]:
    pwp = integration_status()
    catalog = plugin_catalog()
    return {
        "ok": True,
        "status": "ready" if pwp.get("manifest", {}).get("exists") else "degraded",
        "surface": "content-plugin-compat",
        "pwp": pwp,
        "plugins": {
            "count": catalog.get("count", 0),
            "ready_count": catalog.get("ready_count", 0),
            "invalid_count": catalog.get("invalid_count", 0),
        },
    }
```

## Verification checklist

Run a fresh `/tmp/hermes-verify-*` ad-hoc verifier after the final merge/restart. It should confirm:

- repo is on the expected live/staging branch and clean;
- `HEAD` matches `origin/deploy-fresh` after merge;
- old temp verifier/body files are absent;
- `server.py` declares `/api/pwp/status`, `/pwp/status`, `/api/content/status`, `/content/status`;
- `plugins/pwp/plugin-manifest.yaml` exists;
- `plugins/pwp/themes/` contains the expected preserved theme files;
- `scripts/pwp` supports credential/status commands;
- `server.py` compiles;
- `prismatic-gateway.service` is active;
- live local routes return HTTP 200, not 404:
  - `/api/pwp/status`
  - `/pwp/status`
  - `/api/content/status`
  - `/content/status`
  - `/api/plugins/catalog`
  - `/dashboard`
- `/api/pwp/status` reports `manifest.exists == true`;
- `/api/content/status` returns `ok: true` and `surface: content-plugin-compat`;
- dashboard loads governance UI, not marketing;
- targeted PWP tests pass, e.g. `plugins/pwp/tests/test_compiler_determinism.py` and `plugins/pwp/tests/test_oauth_credentials.py`.

Report this as **ad-hoc targeted verification only — not full suite green**.

## Pitfalls

- Do not delete untracked `plugins/pwp/themes/` before checking whether they are real Kai/reference theme assets.
- Do not call PWP stable just because `/api/pwp/status` returns 200; confirm the manifest exists and targeted PWP tests pass.
- Do not leave legacy status panes returning 404 when adding compatibility aliases is safe and non-breaking.
- Do not confuse `disconnected` with broken. After stabilization, PWP may be installed and reachable but intentionally disconnected until an operator connects/runs the lifecycle.
