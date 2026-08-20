# Public Access Runtime Route Proof + Cache Purge Pattern

Use this when a protected Prismatic public route works locally but public/browser proof is blocked or inconsistent after a production durability repair.

## Trigger

- Local live gateway proof passes on `127.0.0.1:9000`.
- Public `https://prismatic.growthwebdev.com/...` redirects to Cloudflare Access or renders stale/cached behavior.
- The user explicitly says not to use Cloudflare Access as an excuse.

## Pattern

1. **Keep the production durability boundary intact**
   - Confirm `prismatic-gateway.service` uses the durable runtime checkout, not `/home/ubuntu/work/prismatic-engine`.
   - Verify local route/API/path-safety first.
   - Do not edit `/home/ubuntu/.prismatic/runtime/prismatic-engine` directly except through the intentional deploy/update procedure.

2. **Create a narrow Cloudflare Access verifier path**
   - Capture verifier egress IP: `curl -sS https://ifconfig.me`.
   - Locate the Access app for `prismatic.growthwebdev.com`.
   - Add or reuse a policy like:
     - `decision: bypass`
     - `include: ip <verifier-ip>/32`
     - `precedence: 1`
     - name it clearly, e.g. `Bypass Fred Hermes verifier IP - workspace-tree proof YYYY-MM-DD`.
   - Never broaden to `everyone`; never print Cloudflare secrets.

3. **Verify every public route layer**
   - Public HTML route: `200` and visible page marker.
   - Public API route: `200` and expected JSON shape.
   - Safe preview route: `200`.
   - Traversal: `403` or other safe blocked response.
   - Asset routes, especially exact JS/CSS used by the page: `200` with the expected content type.

4. **Do not trust curl alone for browser-visible fixes**
   - Load the exact public HTTPS URL in the browser.
   - Inspect DOM state (`title`, `h1`, body length, not black/blank).
   - Confirm first-party script execution markers if applicable.
   - Pull browser console; require zero fatal first-party JS errors.
   - Capture screenshot/browser artifact.

## Worked gotcha: stale Cloudflare 404 for a newly-proxied asset

After adding an nginx location for `/workspace-tree/index.js`, curl may still see a cached public `404` with `cf-cache-status: HIT` even though nginx and local gateway are fixed.

Fix sequence:

1. Patch nginx exact location and reload:

```nginx
location = /workspace-tree/index.js {
    proxy_pass http://127.0.0.1:9000/workspace-tree/index.js;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

2. Run `nginx -t` and `systemctl reload nginx`.
3. Purge only the affected Cloudflare URL, not the whole zone, when possible.
4. If browsers still reuse a stale 404, cache-bust the script tag in the app (`/workspace-tree/index.js?v=<date-or-build>`), land that through PR, update runtime checkout, restart gateway, and purge both old/new asset URLs.
5. Re-run public browser DOM/console proof. Do not claim route fixed until the browser sees the cache-busted asset and the JS-loaded marker (if applicable).

## Proof packet minimum

```text
PRODUCTION_WORKTREE_DURABILITY_OK=PASS
WORKSPACE_TREE_PRODUCTION_OK=PASS
public_html_200=PASS
public_asset_200=PASS
public_api_200=PASS
safe_preview_200=PASS
traversal_blocked=PASS
browser_not_blank=PASS
console_fatal_errors=0
screenshot_artifact=<path>
AD_HOC_VERIFICATION=PASS (not canonical suite green)
```

## Pitfalls

- A public `302` to Cloudflare Access is not the end of verification when Michael explicitly authorizes a verifier-IP access path.
- A route `200` can still be visually broken if a first-party asset is cached as `404`.
- `cf-cache-status: HIT` on a `404` after nginx repair means purge/cache-bust, not another app route rewrite.
- Do not leave a broad Access bypass behind; keep it `/32` and named for verifier purpose.
