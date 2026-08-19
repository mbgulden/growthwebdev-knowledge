---
type: Standard
title: Cloudflare Pages Direct Uploads deploy pipeline (sentinelitad.com)
description: Canonical pattern for deploying Astro static sites to a Cloudflare Pages "Direct Uploads" project via a GitHub Action that calls `wrangler pages deploy`. Established 2026-07-28 on mbgulden/sentinelitad.com after manual deploys proved non-durable.
resource: okf/standards/cloudflare-pages-direct-uploads-deploy.md
tags: [standard, cloudflare-pages, direct-uploads, wrangler, github-actions, deploy, durable, sentinelitad, astro]
timestamp: 2026-07-28
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/cloudflare-pages-direct-uploads-deploy.md
last_verified: 2026-07-28
verified_by: fred (live deploy verified at sentinelitad.com; HTTP 200, 13,526 bytes, Founder Note rendered)
status: current
---

# Cloudflare Pages Direct Uploads deploy pipeline

## What this standard is

For static sites hosted on **Cloudflare Pages projects of type "Direct Uploads"**, the durable deploy path is a GitHub Action that calls `wrangler pages deploy` on every push to the production branch. This pattern replaces manual CF Dashboard clicks and any reliance on a CF-managed GitHub webhook (which **does not exist** for Direct Uploads projects and **cannot be added** via the API).

## When this standard applies

Use this pattern when:

- The CF Pages project was created via **Direct Upload** (not connected to a Git provider).
- The CF Pages project's `source` field is `null` or absent in the API response (verified via `GET /accounts/{acct}/pages/projects/{name}`).
- The repo is on GitHub (or any git host where CI runs can be triggered on push).
- The site is small enough that `wrangler pages deploy` finishes within ~60 seconds (15 dist files at ~750KB hero image is fine; 100MB+ would need different limits).

## When NOT to use this pattern

- If the CF Pages project **is** connected to GitHub (the dashboard setup created a webhook during project creation), use that webhook directly — no GitHub Action needed.
- If `wrangler pages deploy` returns a 401/403 scope error, the API token lacks Pages direct-upload scope. Either widen the token's scope, or fall back to the dashboard.
- If the repo is private and you can't create GitHub Actions, fall back to a CI runner (GitLab CI, Jenkins, local cron) calling `wrangler pages deploy`.

## The standard

### Step 1 — Get a Cloudflare API token with the right scope

Create a token in **Cloudflare Dashboard → My Profile → API Tokens → Create Token**:

- Use template **Edit Cloudflare Pages** (or custom with `Account → Cloudflare Pages → Edit`)
- Account Resources: include the target CF Pages project (e.g. `sentinelitad-com`)
- Zone Resources: optional (only if the same token will also mutate DNS records)
- TTL: 90 days (rotate before expiry)

Verify the token works locally before adding it to GitHub:

```bash
CLOUDFLARE_API_TOKEN=<token>
CLOUDFLARE_ACCOUNT_ID=<account_id>     # from CF Dashboard → Account Home → API section
wrangler pages deploy dist \
  --project-name=<project-name> \
  --branch=<production-branch> \
  --commit-hash="$(git rev-parse HEAD)" \
  --commit-message="$(git log -1 --pretty=%s)"
```

Should end with `Deployment complete! Take a peek over at https://<short-id>.<project>.pages.dev`.

### Step 2 — Add the token as a GitHub Actions secret

In `https://github.com/<owner>/<repo>/settings/secrets/actions`:

- Click **New repository secret**
- Name: `CLOUDFLARE_API_TOKEN`
- Value: paste the token from Step 1
- Click **Add secret**

The token is encrypted at rest and only available to Actions workflows in this repo. **No API token can be set via the GitHub Actions API** with a workflow-scoped token — adding the secret is an operator-side action in the GitHub UI.

### Step 3 — Add the workflow file at `.github/workflows/pages-deploy.yml`

```yaml
name: Deploy <site-name>

'on':
  push:
    branches:
      - <production-branch>      # e.g. ned/initial-website, main, production
  workflow_dispatch:              # manual trigger from Actions UI

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
          node-version: '22'        # Astro 6.x requires Node >=22.12.0
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
          CLOUDFLARE_ACCOUNT_ID: <account-id-here>
        run: |
          wrangler pages deploy dist \
            --project-name=<project-name> \
            --branch=<production-branch> \
            --commit-hash="$GITHUB_SHA" \
            --commit-message="${{ github.event.head_commit.message }}"
```

Replace `<site-name>`, `<production-branch>`, `<account-id-here>`, and `<project-name>` with your actual values.

### Step 4 — Commit the workflow

```bash
cd <repo>
git add .github/workflows/pages-deploy.yml
git commit -m "Add durable Cloudflare Pages deploy pipeline"
git push origin <production-branch>
```

The push triggers the workflow. Within ~60s, the site should be live with the change. Verify:

```bash
gh api /repos/<owner>/<repo>/actions/runs?per_page=4 \
  | python3 -c "import json,sys; [print(f\"{r['name']}={r['status']}/{r['conclusion']}\") for r in json.load(sys.stdin)['workflow_runs'][:2]]"
```

Both should show `completed/success`. If `completed/failure`, check the failed step logs:

```bash
gh api /repos/<owner>/<repo>/actions/jobs/<job_id>/logs
```

### Step 5 — Verify the live site

```bash
curl -sS -L --max-time 15 -o /tmp/live.html -w "HTTP %{http_code} | %{size_download} bytes\n" \
  "https://<custom-domain>/?cb=$(date +%s)"
```

Expected: `HTTP 200` + non-zero size. If `HTTP 500`, see "Failure recovery" below.

## Why this works (architectural notes)

### Cloudflare Pages project types

There are two kinds of CF Pages projects:

1. **Git-integrated:** The CF Dashboard "Connect to Git" flow sets up a webhook. Deploy pipeline: `clone_repo → build → deploy`. Webhooks can silently die (verified 2026-07-28 on sentinelitad.com: 18-day gap between deploys after webhook died).
2. **Direct Uploads:** Only the `deploy` stage runs. Files are uploaded via `wrangler pages deploy` (or a custom implementation of the upload-JWT flow). GitHub integration is **architecturally impossible** — verified: API returns `400 "You cannot update the source object in a Direct Uploads project"` when attempting to add GitHub source.

**If your project is Direct Uploads, the GitHub Action that calls `wrangler pages deploy` is the only GitHub-driven path that exists.**

### Why `wrangler` is the right primitive

`wrangler pages deploy` is the canonical, supported CLI for Direct Uploads. It:

1. Calls `GET /accounts/{acct}/pages/projects/{name}/upload-token` to get a short-lived JWT.
2. Uploads every file via `POST /pages/assets/upload` with the JWT — correct blake3 hashing, multipart handling.
3. Calls `POST /pages/assets/upsert-hashes` to register the uploaded files.
4. Calls `POST /accounts/{acct}/pages/projects/{name}/deployments` with `multipart/form-data` (the manifest as a form field) to create the deployment.

**Direct API attempts to create deployments fail with `400 "A 'manifest' field was expected"`** unless the request is `multipart/form-data`. This is the most common cause of "JSON POST that worked in curl but rejected by the API" confusion.

### Edge cache layer

CF Pages edge cache is **separate from the `.pages.dev` canonical URL**. The custom domain (`sentinelitad.com`) goes through the Cloudflare proxy with its own cache. Failure mode:

- Deployment succeeds, `.pages.dev/<id>` returns HTTP 200 with new content
- But `sentinelitad.com` still returns HTTP 500

This is **not** a deploy failure. It's an edge cache problem. Fix:

```bash
curl -sS -X POST -L --max-time 15 \
  -H "X-Auth-Email: $CLOUDFLARE_GROWTHWEB_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_GROWTHWEB_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"hosts":["<custom-domain>","www.<custom-domain>"]}' \
  "https://api.cloudflare.com/client/v4/zones/<zone-id>/purge_cache"
```

Then re-verify. The cache TTL on CF Pages custom domains can hold a 5xx for several minutes if no cache-busting path is exercised.

## Failure recovery

### "wrangler pages deploy returns 401/403"

API token scope insufficient. Check `wrangler` debug output:

```bash
CLOUDFLARE_API_TOKEN=<token> wrangler pages deploy dist --project-name=X --dry-run
```

If the dry-run returns 401, the token lacks Pages write scope. Re-create with **Edit Cloudflare Pages** template.

### Build step fails with "Node.js vX is not supported by Astro!"

Astro 6.x requires Node >=22.12.0. Pin `node-version: '22'` (not `'20'`).

### Deploy step succeeds, live site is HTTP 500

1. Wait 30s — CF Pages edge cache may be stale.
2. Purge the cache via `/zones/{id}/purge_cache` (command above).
3. If still 500, verify the canonical deployment is the new one:
   ```bash
   curl -sS -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
     "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/$PROJECT" \
     | jq .canonical_deployment.id
   ```
4. If a broken deployment is canonical, rollback:
   ```bash
   curl -sS -X POST -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
     "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/$PROJECT/deployments/<previous-good-id>/rollback"
   ```
   Then purge the cache.

### Workflow shows "completed/failure" but no error in steps

GH Actions logs may take 30-60s to be downloadable. Wait, then re-pull. If the deploy step log shows `wrangler 4.x.x` followed by `ERROR: ...`, the failure is real — check token scope.

## Worked example: sentinelitad.com (2026-07-28)

- **Project:** `sentinelitad-com` (CF Pages, Direct Uploads, prod branch `ned/initial-website`)
- **Repo:** `mbgulden/sentinelitad.com`
- **Files added:** `.github/workflows/pages-deploy.yml`, `ops/deploy.md` (in-repo operator handoff)
- **Workflow behavior verified:** Both push events (commits `7e278f8` and `4ba0645`) triggered the action. Node-version fix (`22`) unblocked the build step. Wrangler step ran successfully when run locally with the same token.
- **Live site verified:** `https://sentinelitad.com/` returns HTTP 200, 13,526 bytes, Founder Note ("Michael Gulden", "13-year IT professional", "Government liquidation auctions") present.
- **Operator-side remaining:** Add `CLOUDFLARE_API_TOKEN` to GitHub Actions secrets on `mbgulden/sentinelitad.com` (one-time, ~30 seconds).

## Pitfalls

1. **Don't assume CF Pages has a working GitHub webhook.** Verify by checking `latest_deployment.deployment_trigger.type`. If `ad_hoc` for every deploy, the project is Direct Uploads and webhook-based automation is impossible.
2. **Don't try to add GitHub source to a Direct Uploads project.** The API will refuse (`400 "You cannot update the source object in a Direct Uploads project"`). The architectural fix is `wrangler`, not configuration.
3. **Don't use JSON for the deploy API.** CF Pages Direct Uploads requires `multipart/form-data`. Use `wrangler` to avoid getting it wrong.
4. **Don't ignore the edge cache.** After any rollback or fix-up, purge `sentinelitad.com` and `www.sentinelitad.com` zone cache. A HTTP 500 stuck on the custom domain (with `.pages.dev` returning 200) is a cache problem, not a deploy problem.
5. **Don't pin Node 20 if the site uses Astro 6.x.** Build step will fail silently with "Node.js v20.20.2 is not supported by Astro!" Use Node 22.
6. **Don't store the API token in the repo.** It goes in GitHub Actions secrets (`Settings → Secrets and variables → Actions`), never in YAML or comments.
7. **Don't skip the local smoke test.** Run `wrangler pages deploy` from your dev machine first to confirm the token works, before wiring the GitHub Action. Saves a debug cycle.
8. **Don't roll forward past a broken canonical deployment.** If a bad deploy is canonical, the `wrangler` deploys will still succeed but the live site keeps showing the broken content. Always verify the canonical deployment ID before and after a deploy.

## Acceptance test IDs

- **CF-PAGES-DU-DEPLOY-01:** Live site `https://<custom-domain>/` returns HTTP 200 after the workflow runs.
- **CF-PAGES-DU-DEPLOY-02:** `latest_deployment.deployment_trigger.type` is `ad_hoc` (not `github`), confirming Direct Uploads pattern is being used correctly.
- **CF-PAGES-DU-DEPLOY-03:** Custom domain and `www` subdomain both return 200 (verify both aliases).
- **CF-PAGES-DU-DEPLOY-04:** Workflow run shows `completed/success` end-to-end (Checkout → Setup Node → Install deps → Build → Install wrangler → Deploy to CF Pages).
- **CF-PAGES-DU-DEPLOY-05 (negative):** Workflow run with missing `CLOUDFLARE_API_TOKEN` secret fails at the Deploy step with `wrangler` reporting "In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable" — confirms the secret is actually being used.

## References

- `okf/standards/active-oahu-tours-architecture-template.md` — the GitHub-integrated Pages pattern for projects where it works. Sentinel ITAD is the contrast case where this pattern is NOT applicable.
- `okf/standards/cloudflare-access-okf-publisher.md` — Cloudflare Access pattern (different concern: securing dashboard access vs deploying sites).
- `okf/integrations/cloudflare-account-activeoahu.md` — multi-account Cloudflare setup (relevant when CF Pages is on a different account than DNS).
- `references/cloudflare-pages-direct-uploads-deploy-2026-07-28.md` (in this same standard's docs repo) — session-specific evidence and verification walk for the sentinelitad.com deployment of this standard.