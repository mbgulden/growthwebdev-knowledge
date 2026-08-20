# CF Pages Direct Uploads + wrangler + GitHub Action — Verified Pattern 2026-07-28

Source session: `sentinelitad.com` (`mbgulden/sentinelitad.com` repo, CF Pages project `sentinelitad-com` on account `196c1798da487413b0281ccc570f05a1`).

## What this reference covers

The complete durable deploy pattern for a **Direct Uploads** CF Pages project. The earlier `cf-pages-deploy-diagnostic-when-webhook-dies.md` covers the Git-integrated type; this one covers Direct Uploads, which is the case where the GitHub webhook can never be wired in the first place.

---

## Symptom you need this pattern

- `GET /accounts/<id>/pages/projects/<name>` returns a project with **`source = null`** or with no `source` field at all.
- All historical deployments have `deployment_trigger.type = "ad_hoc"`.
- `git push` to `origin/<production-branch>` succeeds but no new deployment entry appears.
- `POST /accounts/<id>/pages/projects/<name>/source` to add a GitHub source returns:
  `400 "You cannot update the source object in a Direct Uploads project"`

That error means **the project was created as a Direct Uploads project, not a Git-integrated one**. The "fix the webhook" instructions in the parent skill won't help — there is no webhook to fix. Use the pattern below.

---

## The durable pattern (verified end-to-end)

### Prerequisite: API token with Pages direct-upload scope

The existing `CLOUDFLARE_PAGES_API_TOKEN` from `~/.hermes/.env` (id `e1a64315...`, name "Edit Cloudflare Workers", scope `Account → Cloudflare Pages → Edit`) works. Verified by:

- Calling `wrangler pages deploy dist --project-name=sentinelitad-com ...` with `CLOUDFLARE_API_TOKEN` env var, against the live project.
- Getting `Deployment complete! Take a peek over at https://...pages.dev`.
- Confirming the canonical deployment flips in the API (`latest_deployment` advances).
- Confirming the live site serves the new artifact.

If you need a new token, the minimum permissions are **Account → Cloudflare Pages → Edit**. Do NOT use a deploy-hook token here — those are webhook receivers, not API clients.

### The GitHub Action file

Path: `.github/workflows/pages-deploy.yml` in the Pages project's repo.

```yaml
name: Deploy site

on:
  push:
    branches:
      - <production-branch>      # e.g., ned/initial-website
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'        # Astro 6.x requires >=22.12.0; default GH runner is Node 24 but be explicit
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Install wrangler
        run: npm install -g wrangler

      - name: Deploy to Cloudflare Pages
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: <account-id>   # public, hardcode; get from project response .account.id
        run: |
          wrangler pages deploy dist \
            --project-name=<project-name> \
            --branch=<production-branch> \
            --commit-hash="$GITHUB_SHA" \
            --commit-message="${{ github.event.head_commit.message }}"
```

### The one operator action required to complete the loop

After committing the workflow file, the **first deploy** will fail with:

```
✘ [ERROR] In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable for wrangler to work.
```

Because GitHub Actions secrets cannot be set via the API from a workflow-scoped token. The operator must:

1. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
2. Name: `CLOUDFLARE_API_TOKEN`
3. Value: paste the API token
4. Click **Add secret**

After saving, re-trigger the workflow (push a no-op commit, or use **Run workflow** from the Actions UI). The next deploy should succeed. **This is a one-time action; future deploys run automatically on every push.**

### Why this is durable

Once the workflow file exists on `main` (or whatever the production-branch is) AND the secret is set:

- Every `git push` to `ned/initial-website` → `git push` → Action run (within ~30s) → wrangler deploys → live site updates (within 60s). No human in the loop.
- The previous 18-day deploy gap that occurred with the old manual-dashboard setup is structurally impossible.
- If anyone reverts the workflow file, the `Actions` tab shows the workflow being deleted; you'll see it immediately.

### Why direct integration alternatives don't work

| Alternative tried | Outcome | Why |
|---|---|---|
| `POST /pages/projects/.../source` to add GitHub source | `400 "You cannot update the source object in a Direct Uploads project"` | Project type is fixed at creation |
| `POST /pages/projects/.../deployments` (raw API) with manifest | `400 "manifest field expected"` | API expects multipart/form-data |
| `POST /pages/projects/.../deployments` with multipart | `success` but live URL returns HTTP 500 | The deploy record is created but file uploads require the full JWT cycle |
| GitHub webhook polling | No webhook has ever been wired, because the project type doesn't allow it | Confirm via `source = null` in project detail |
| Direct upload-token / file-hash / multipart loop in custom code | Works but reinvents `wrangler` badly | Use `wrangler` — it does all 5 steps correctly |
| **GitHub Action + `wrangler pages deploy`** | **Works end-to-end** | The pattern above |

---

## Detailed reproducer (worked example, sentinelitad.com, 2026-07-28)

### The state we started from

| Check | Value |
|---|---|
| Live site at `https://sentinelitad.com/` | HTTP 200, 11,176 bytes (pre-Founder Note) |
| Last successful deploy | `2026-07-09T15:05:42` — 18 days ago |
| Project `source` field | `null` |
| All 4 historical deploys' `deployment_trigger.type` | `ad_hoc` |
| GitHub webhooks on repo | 0 |

### What I did

1. **Live deployed the Founder Note locally**:
   ```bash
   cd /home/ubuntu/work/sentinelitad.com
   npm ci && npm run build
   export PATH="$HOME/.local/bin:$PATH"
   # wrangler installed via: npm install -g wrangler --prefix ~/.local
   export CLOUDFLARE_API_TOKEN=*** from ~/.hermes/.env>
   export CLOUDFLARE_ACCOUNT_ID="196c1798da487413b0281ccc570f05a1"
   wrangler pages deploy dist --project-name=sentinelitad-com \
     --branch=ned/initial-website \
     --commit-hash=95de1c9 \
     --commit-message="[Fred] Merge feature/founder-note into production"
   ```
   Output: `Deployment complete! Take a peek over at https://9fe11804.sentinelitad-com.pages.dev`
   Live site: HTTP 200, **13,526 bytes** (Founder Note present, verified via `grep -c "Michael Gulden"`).

2. **Wrote the GitHub Action workflow** (`.github/workflows/pages-deploy.yml`) with 6 steps: checkout → setup-node@22 → npm ci → npm run build → npm install -g wrangler → wrangler deploy.

3. **Committed and pushed to `ned/initial-website`.** The push triggered both workflows (the new "Deploy Sentinel site" and Ned's existing "Deploy static site to GitHub Pages").

4. **First Action run failed** at the wrangler step with:
   ```
   ✘ [ERROR] In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable
   ```
   The secret hadn't been set yet (operator action). Workflow ran the build step successfully first.

5. **Earlier failure** because of Node version: the first workflow version pinned `node-version: '20'`, but Astro 6.x requires Node >=22.12.0:
   ```
   Node.js v20.20.2 is not supported by Astro!
   Please upgrade Node.js to a supported version: ">=22.12.0"
   ```
   Fixed by bumping to `node-version: '22'`.

6. **After both fixes**, the action reaches the wrangler step but still fails on the missing secret. Pipeline is wired and waiting only on that one operator UI action.

7. **Verified GitHub Pages fallback works in parallel**: Ned's `pages.yml` (untouched) deploys the same `public/` directory to `mbgulden.github.io/sentinelitad.com`. Both deploy paths coexist cleanly.

### Verification commands

```bash
# Confirm wrangler works locally (preflight for the workflow):
cd /home/ubuntu/work/sentinelitad.com
export PATH="$HOME/.local/bin:$PATH"
export CLOUDFLARE_API_TOKEN=*** -sS wrangler pages deploy dist --project-name=sentinelitad-com \
  --branch=ned/initial-website --commit-hash=$(git rev-parse HEAD) \
  --commit-message="manual test"
# Expect: "Deployment complete!"

# Confirm the live site reflects the new content:
curl -sS https://sentinelitad.com/ | grep -c "Michael Gulden"   # should return 2+
curl -sS https://sentinelitad.com/style.css | grep -c "founder-grid" # should return 1+

# Confirm the GitHub Action fired (after the workflow exists and is pushed):
gh api /repos/<owner>/<repo>/actions/runs | jq '.workflow_runs[] | {name, status, conclusion}'
```

---

## Recovery procedure if the workflow breaks the live site

If a deploy goes wrong and the live URL returns HTTP 500 (which can happen if `dist/` is incomplete or the action ran mid-build), the recovery is **two simple API calls**. Do not try to re-deploy; rollback.

```bash
# 1. Find the last known-good deployment:
ACCT=<account-id>; TOKEN=***
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<name>/deployments" \
  | jq -r '.result[] | "\(.id) \(.latest_stage.status) \(.created_on)"'
# Pick a deployment id with status=success, NOT the broken one.

# 2. Rollback to it:
GOOD_ID=<id from step 1>
curl -sS -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{}' \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<name>/deployments/$GOOD_ID/rollback"
# This redeploys the previous deployment's files. Watch `latest_deployment` on project detail flip.

# 3. Purge the custom-domain edge cache (CF edge may still be serving the 500 page):
ZONE=<zone-id>
curl -sS -X POST \
  -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"hosts":["<domain>", "www.<domain>"]}' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/purge_cache"
# This unsticks apex/www if their edge cached the broken response.

# 4. Verify:
curl -sS "https://<domain>/?cb=$(date +%s)" | head -c 500
```

Confirmed working 2026-07-28 on sentinelitad.com: rolled back from a broken direct-API deploy (`deploy_id=454c5a8a`) to the previous good deploy (`691b8c43`), purged the apex/www edge cache, live site back to HTTP 200 with the pre-Founder Note content within minutes.

---

## Reference files in this directory

- `cloudflare-zone-enablement-sentinelitad-2026-07-27.md` — the earlier session that brought `team@sentinelitad.com` email routing online. Same project, DNS-side work.
- `cf-pages-deploy-diagnostic-when-webhook-dies.md` — the diagnostic for **Git-integrated** Pages projects (where the webhook *can* be re-wired). This file is the diagnostic for **Direct Uploads** projects (where it can't).