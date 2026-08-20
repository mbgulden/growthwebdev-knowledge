---
name: cloudflare-pages-workers-build-checks
description: Use when a repository deployed by Cloudflare Pages also has a red GitHub `Workers Builds` check, especially HD Platform / HDE PRs where Pages is the canonical deployment path and Workers uses incompatible Wrangler semantics.
---

# Cloudflare Pages vs Workers Builds checks

Use this before changing `wrangler.jsonc` to satisfy a red `Workers Builds: ...` GitHub check. Load this skill before making any Wrangler/Cloudflare-check edits, not after a failed push.

## Core rule

Prefer the canonical product deployment path. If the repo is a Cloudflare Pages project, do not break Pages validation to appease a duplicate Workers Builds integration.

For HD Platform, the root Pages-compatible config is:

```json
{
  "pages_build_output_dir": "dist"
}
```

Do **not** add root-level `assets.directory` just because `npx wrangler versions upload` asks for it. That can make the local Workers dry-run pass while causing Cloudflare Pages preview builds to fail with:

```text
Configuration file for Pages projects does not support "assets"
```

## CF API token: map in-process, never inline in the shell

Wrangler wants `CLOUDFLARE_API_TOKEN`; this box carries `CLOUDFLARE_PAGES_API_TOKEN` (a `cfut_…` user token that works fine against the API directly). The trap: writing `CLOUDFLARE_API_TOKEN=*** npx wrangler …` in a terminal command line gets the token mangled/redacted by the shell layer (value arrives as literal `***` → wrangler fails with `Invalid format for Authorization header [code: 6111]`).

**Fix (verified 2026-08-19, HDE prod deploy):** pass the token through a Python subprocess env:

```python
import os, subprocess
env = dict(os.environ)
env['CLOUDFLARE_API_TOKEN'] = os.environ.get('CLOUDFLARE_PAGES_API_TOKEN', '')
subprocess.run(['npx', 'wrangler', 'pages', 'deploy', 'dist',
                '--project-name', 'hd-platform', '--branch', 'main'],
               env=env, capture_output=True, text=True, timeout=240)
```

Diagnose the redaction shape with `node -e "console.log(process.env.CLOUDFLARE_API_TOKEN.length)"` after an inline assignment — if it prints `3`, the shell layer ate it. Also redact `cfut_…` / token-shaped strings out of any logged wrangler output before reporting. See `references/2026-08-hde-prod-deploy-token-env-pitfall.md`.

## Preview vs production: `--branch` decides the environment

`wrangler pages deploy` picks the **environment** from the current git branch when you
are inside a git checkout. The `hd-platform` project has `production_branch: main`, so
deploying from any `ned/…` / feature branch **auto-creates a *preview***
(`<branch>.hd-platform.pages.dev`) and the production custom domain
(`humandesignengine.com`) **keeps serving the old production deployment** — a silent
no-op for production that looks like a successful deploy ("Deployment complete!").

- **Fix:** always pass `--branch=main` for a production ship:
  `npx wrangler pages deploy dist --project-name=hd-platform --branch=main`.
- **Verify** the new deployment's `environment` is `production` via the CF API
  (`/accounts/{acct}/pages/projects/{name}/deployments?per_page=3`), then **byte-compare**
  the served page to your built `dist` (`md5sum` of the file vs `curl … | md5sum`).
  A mismatch means the domain is still on the old deployment. Do not trust
  `?cache-bust=` query params or "the deploy succeeded" as proof the custom domain
  picked it up. See `references/2026-08-hde-prod-deploy-token-env-pitfall.md` (deploy
  record) and the Stripe skill's `references/2026-08-hde-stuck-redirecting-checkout.md`.

## Verification sequence

1. Verify the actual repo proof first:
   - `npm ci` if dependencies are absent/stale.
   - `npm run build`, `npm run pwp:verify`, or the issue-specific stronger proof command.
   - If a guard/system message says verification is stale after edits, rerun the relevant verification immediately even if you already saw a pass earlier; quote the fresh command and result.
2. Inspect PR checks:
   - `gh pr view <PR> --json statusCheckRollup,mergeStateStatus,headRefOid`
3. If Cloudflare Pages is red:
   - Fetch Pages deployment logs via Cloudflare API.
   - Fix the Pages-compatible config or build failure.
4. If Cloudflare Pages is green and Workers Builds is red:
   - Reproduce `npx wrangler versions upload --dry-run` locally only as diagnostic evidence.
   - Do not force incompatible root Wrangler config into a Pages repo.
   - Search OKF, session history, and env-backed API access before calling it a handoff.
   - Treat the remaining red check as a Cloudflare project-owner decision: disable/waive the duplicate Workers Builds trigger, or point it to a separate Worker config/command.
5. Finalize/report honestly:
   - Keep Linear `In Review`, not `Done`, while PR checks are red.
   - Remove stale `dispatch:ready` so the scanner does not keep redispatching completed code work.
   - Add `agent:needs-human-review` when the remaining fix requires Cloudflare project configuration.
   - Record the exact Pages deployment result, Workers build ID/check name, and local proof command output in the result file.

## HDE checkout smoke pitfall

For `api.humandesignengine.com/create-checkout`, a bare Python/urllib or curl POST from Ned's VM can return Cloudflare `403` / `error code: 1010` even when checkout is healthy. Before treating that as revenue-critical, retry with realistic browser headers:

```bash
python3 - <<'PY'
import json, urllib.request
headers = {
  'Content-Type': 'application/json',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
  'Origin': 'https://humandesignengine.com',
  'Referer': 'https://humandesignengine.com/buy-report/',
  'Accept': 'application/json,text/plain,*/*',
}
payload = json.dumps({'email':'ned-cron-smoke@growthwebdev.com','product':'basic'}).encode()
req = urllib.request.Request('https://api.humandesignengine.com/create-checkout', data=payload, headers=headers, method='POST')
with urllib.request.urlopen(req, timeout=20) as r:
    body = r.read(1000).decode('utf-8','replace')
    print({'status': r.status, 'has_stripe_checkout': 'checkout.stripe.com' in body})
PY
```

A browser-header 200 with a Stripe URL is a checkout smoke pass; a bare-request 1010 alone is bot/WAF friction, not proof the CSP/header change broke checkout.

## Supporting references

- `references/2026-08-hde-prod-deploy-token-env-pitfall.md` — CF API token env redaction pitfall (`CLOUDFLARE_API_TOKEN=*** in a command line → code 6111), in-process subprocess fix, and the 2026-08-19 HDE prod deploy record.
- `references/hde-pages-workers-build-conflict.md` — session-specific reproduction from GRO-3996: `assets.directory` passed Workers dry-run but broke Cloudflare Pages validation, so the branch restored Pages-compatible config and handed off the external Workers trigger decision.
- `references/hde-redispatch-completed-code-work.md` — redispatch/dequeue pattern when implementation already exists, Pages is green, and only the duplicate Workers build check remains red.
- `references/hde-gro3998-pages-workers-refresh.md` — GRO-3998 refresh showing the danger of late-loading this skill, why not to push `assets.directory`, and why stale-verification guard messages require an immediate fresh `npm run build` rerun.
- `references/hde-community-funnel-redispatch-refresh.md` — completed-code redispatch refresh pattern: clean detached `origin/ned/<issue>` worktree, fresh `npm run build` + focused route artifact proof, rerun finalize with `PRISMATIC_REPO_ROOT`, remove stale `dispatch:ready`, add `agent:needs-human-review`, and suppress cron delivery when the only remaining blocker is the known Workers Builds mismatch.
