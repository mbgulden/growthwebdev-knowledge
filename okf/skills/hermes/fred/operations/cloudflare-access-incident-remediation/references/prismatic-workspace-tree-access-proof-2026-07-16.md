# Prismatic workspace-tree verifier-IP bypass + stale public asset repair — 2026-07-16

## Context

Michael rejected treating Cloudflare Access as a blocker for public `/workspace-tree` proof. The correct path was to use Cloudflare API credentials to grant a narrow verifier-IP bypass, then verify the real public HTTPS route.

## Durable pattern

1. Capture current verifier egress IP:

```bash
curl -sS --max-time 10 https://ifconfig.me
```

2. Confirm the public route is blocked by Access without following redirects:

```bash
curl -k -sS -o body -D headers -w 'status=%{http_code}\n' \
  'https://prismatic.growthwebdev.com/workspace-tree?file=README.md'
```

Expected before bypass: `302` to `growthwebdev.cloudflareaccess.com`.

3. Resolve the actual Cloudflare zone/account from the hostname, not env var names. For `prismatic.growthwebdev.com`, use the `growthwebdev.com` zone and the Access app named `Hermes Service (prismatic.growthwebdev.com)`.

4. Add a least-privilege Access policy:

```text
name: Bypass Fred Hermes verifier IP - workspace-tree proof YYYY-MM-DD
decision: bypass
precedence: 1
include: ip <verifier-ip>/32
```

Do not broaden to `everyone`. Do not remove Michael's email/PIN policy or webhook bypasses.

5. Re-test public HTTPS route, API, safe preview, and traversal through Cloudflare:

```bash
curl -k -sS -D headers -o body 'https://prismatic.growthwebdev.com/workspace-tree?file=README.md'
curl -k -sS -D headers -o body 'https://prismatic.growthwebdev.com/api/workspace-tree/preview?file=docs/prismatic-production-durability-standard.md'
curl -k -sS -D headers -o body 'https://prismatic.growthwebdev.com/api/workspace-tree/preview?file=../../etc/passwd'
```

Expected: page/API `200`; traversal `403`; body is app content, not Access login or origin `404`.

## Stale asset pitfall after Access is solved

If the public HTML is `200` but `/workspace-tree/index.js` is still `404`:

1. Check whether nginx proxies the exact asset path. A route like `location = /workspace-tree` does **not** cover `/workspace-tree/index.js`.
2. Add an exact nginx location for the asset and reload only after `nginx -t` passes.
3. If Cloudflare continues serving the old `404` with `cf-cache-status: HIT`, purge the exact file URL:

```text
https://prismatic.growthwebdev.com/workspace-tree/index.js
```

4. If a browser session still has the stale asset, cache-bust the script reference in the app, e.g. `/workspace-tree/index.js?v=YYYYMMDD`, merge/deploy, then purge both old and cache-busted URLs.
5. Verify from the browser context, not just curl:

```js
(() => ({
  title: document.title,
  h1: document.querySelector('h1')?.textContent,
  hasBlackPage: document.body.innerText.trim().length < 100,
  workspaceJsLoaded: document.documentElement.dataset.workspaceTreeJs || null,
  enhancementTextPresent: document.body.innerText.includes('Workspace tree enhancement loaded.'),
  scriptSrcs: [...document.scripts].map(s => s.src || 'inline')
}))()
```

Done requires `workspaceJsLoaded: "loaded"`, visible body text, no first-party JS errors, and a screenshot artifact.

## Proof packet markers from the worked case

```text
PRODUCTION_WORKTREE_DURABILITY_OK
WORKSPACE_TREE_PRODUCTION_OK
PRODUCTION_RUNTIME_WORKSPACE_TREE_REPAIR_OK
```

Label the final proof as ad hoc targeted verification unless the canonical full suite was also run.