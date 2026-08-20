# Workspace Tree production route repair pattern (2026-07-15)

## Context

Michael reported that `https://prismatic.growthwebdev.com/workspace-tree` rendered as a black page on the dashboard. The authenticated browser state could not be inspected directly from Kai because Cloudflare Access redirected unauthenticated browser/curl sessions, but local gateway and repo inspection identified the likely repair class.

## Audit findings

1. **Local gateway route drift**

The public nginx host proxies `/workspace-tree` to the local gateway:

```nginx
location = /workspace-tree {
    proxy_pass http://127.0.0.1:9000/workspace-tree;
}
```

But local checks showed the running gateway was alive while dashboard/workspace routes were absent:

```text
http://127.0.0.1:9000/health -> 200
http://127.0.0.1:9000/workspace-tree -> 404
http://127.0.0.1:9000/api/workspaces -> 404
http://127.0.0.1:9000/api/workspace-tree/preview?... -> 404
http://127.0.0.1:9000/dashboard -> 404
```

This means nginx was probably not the primary failure. The service was running a gateway source whose route table did not contain the expected compatibility routes.

2. **Mutable production worktree risk**

`prismatic-gateway.service` was configured with:

```text
WorkingDirectory=/home/ubuntu/work/prismatic-engine
ExecStart=/home/ubuntu/.prismatic/venv_stable/bin/python3 -m prismatic.gateway.server --port 9000 --log-level info
```

During audit, that worktree was on a feature branch (`design/GRO-3837`) while `origin/deploy-fresh` contained newer dashboard/workspace-tree route code. Treat this as a production-governance problem: a shared development checkout should not be the live service source unless branch state is deliberately controlled.

3. **Black-page shell fragility**

`origin/deploy-fresh:prismatic/gateway/server.py` already had a `/workspace-tree` route that served a React plugin shell, but the shell depended on external scripts:

```html
<script src="https://cdn.tailwindcss.com"></script>
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<main id="workspace-tree-root" class="min-h-screen"></main>
<script src="/workspace-tree/index.js"></script>
```

The workspace-tree plugin bundle returns immediately if globals are absent:

```js
const sdk = window.__HERMES_PLUGIN_SDK__;
const registry = window.__HERMES_PLUGINS__;
if (!sdk || !registry) return;
```

If CDN/CSP/React/ReactDOM loading fails, the user can see a blank/black page. Future fixes should ensure visible fallback content exists before JS loads or use a no-CDN/self-contained route.

## Recommended repair pattern

1. **Work from a clean production-safe branch/worktree**
   - Do not patch production by editing a random checked-out feature branch.
   - Prefer a dedicated production worktree for the gateway service so Kai/Fred/AGY feature branches cannot accidentally change live source.
   - Capture `git status --short --branch`, HEAD, and recent log before and after.

2. **Reproduce local route state first**
   - Check route table using `PYTHONPATH=<repo>:<venv site-packages> python3 -c ...` and print routes containing `workspace`, `dashboard`, `/`, and `/health`.
   - Curl local gateway before public URL:
     - `/workspace-tree`
     - `/workspace-tree/index.js` if used
     - `/api/plugins/hermes-plugin-workspace-tree-navigator/tree`
     - `/api/plugins/hermes-plugin-workspace-tree-navigator/preview`
     - compatibility aliases such as `/api/workspaces` / `/api/workspace-tree/preview` if supported.

3. **Patch real root causes**
   - Ensure gateway source exposes `/`, `/dashboard`, `/workspace-tree`, `/workspace-tree/index.js`, and the workspace-tree plugin API mount.
   - Add safe compatibility aliases only if dashboard/public links rely on them.
   - Make `/workspace-tree` visibly render without depending solely on external CDN JS. At minimum, include a visible loading/failure shell: `Prismatic Workspace Tree`, diagnostic text, and API health links before the React/plugin bundle runs.
   - Preserve filesystem safety. Preview/download endpoints must resolve only under configured workspace roots and block traversal such as `../../etc/passwd`.

4. **Deploy deliberately**
   - After PR review/merge, update the production worktree/service to the intended commit.
   - Restart `prismatic-gateway`.
   - Reload nginx only if proxy config changed and `nginx -t` passes.

## Verification checklist

Use a focused `/tmp/hermes-verify-*` script and report as ad-hoc targeted verification, not full dashboard suite green.

Required checks:

```text
python3 -m py_compile prismatic/gateway/server.py
route table contains /workspace-tree
local /workspace-tree returns 200
page contains visible text: Prismatic Workspace Tree
page has non-empty fallback content before JS execution
/workspace-tree/index.js returns 200 if still used
tree API returns 200 and workspace_count > 0
safe preview returns expected repo file content
path traversal is blocked with 400/403
public/authenticated route is not 404 and screenshot is not black/blank
browser console has no fatal first-party JS errors
```

Expected marker:

```text
WORKSPACE_TREE_PRODUCTION_OK
```

If Cloudflare Access blocks automated public inspection, report the local proof plus authenticated browser/screenshot evidence from Michael/Fred rather than claiming unattended public proof.

## Pitfalls

- Do not assume nginx is the primary issue while local `127.0.0.1:9000/workspace-tree` returns 404.
- Do not treat `/health` as proof dashboard routes are loaded.
- Do not rely on an empty black React mount with all content supplied by external scripts.
- Do not loosen path safety to make the UI work.
- Do not claim production fixed until the running service source/HEAD and authenticated production route are verified.
