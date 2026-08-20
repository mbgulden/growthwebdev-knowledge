---
name: cloudflare-zone-enablement
description: Enable a Cloudflare-managed domain for production use — DNS records (MX, SPF, A, CNAME), Cloudflare Email Routing (forwarders, catch-alls), and Pages custom-domain binding. Use when Michael says "fix the dns," "set up email forwarding," or asks to enable email/MX on a domain that currently can't receive. Distinct from `cloudflare-access-incident-remediation` (which covers Zero Trust / Access / tunnel bypass), and from `hermes-agent` (which covers Hermes profile plumbing).
category: operations
---

# Cloudflare Zone Enablement

Use this skill when a Cloudflare-managed domain needs to be brought online for a concrete operator goal: deliver email, accept forms, host a site, expose a service. Typical triggers from Michael:

- "Set up email forwarding from X@domain.com to my real address."
- "Fix the DNS so X@domain.com actually receives."
- "Wire MX records for X."
- "Bind the Pages project to a custom domain."

This skill is **not** for Access / Zero Trust hardening, webhook classification, or tunnel routing — those are `cloudflare-access-incident-remediation`.

## Core principles

1. **Resolve zone by hostname, never by env-var name.** Env vars like `CLOUDFLARE_*_ZONE_*` are usually named after one specific zone and lie about others. `hermes profile list` + the CF API list-zones call is the only safe way to find the right zone ID for an unfamiliar domain. See `references/growthweb-zone-list-and-id-map.md` for the known GrowthWeb zone list.
2. **Use the right credential tier.** Global API key (`X-Auth-Email` + `X-Auth-Key`) is for zone-level DNS / Email Routing / Pages binding across the whole account. `CLOUDFLARE_PAGES_API_TOKEN` is per-page-binding and won't unlock zone-level endpoints. Mixing them up produces "Authentication error" with no clear cause.
3. **Verify externally, not just from the API.** After every mutation, query `dig @1.1.1.1 <domain> <record-type> +short` to confirm the public resolver sees what you created. Reading your own API result is necessary but not sufficient — propagation or API-delay can mask a bad record.
4. **Email Routing has two halves.** Cloudflare Email Routing requires both (a) the MX records (Cloudflare-side, route1/2/3.mx.cloudflare.net) and (b) the routing rule (matchers + actions on `/zones/:id/email/routing/rules`). Either alone doesn't deliver mail. The zone-level `/email/routing` PATCH endpoint is unreliable (often returns `success: true` but does not flip `enabled`); create MX records via `/zones/:id/dns_records` instead and create the rule via `/zones/:id/email/routing/rules`.
5. **Destination addresses must already be verified.** Custom routing rules fail to create if the destination email address hasn't been added + verified via the `/accounts/:id/email/routing/addresses` endpoint (sender gets a confirmation email). For Michael's GrowthWeb account, `michael@growthwebdev.com` has been verified since 2026-06 — safe to reuse without re-verification.
6. **Never delete records you didn't create.** Before mutating, list current records and read prior state. If `git log` or OKF audit indicates someone else (AGY, Ned, a previous agent) created a record, don't overwrite unless Michael explicitly authorizes.
7. **End-to-end smoke from this host is usually blocked.** Outbound SMTP on port 25 is normally blocked by VM network policy (`OSError: Network is unreachable`). DNS + API + rule verification are the only local proof. The final hop (does the email actually land in the inbox?) must be confirmed by the operator from a normal network connection.
8. **Michael works async — produce the check-list, don't wait for clarifications.** When asked to fix the DNS layer (or any zone-level operator action), don't block on `clarify` prompts for option picking when Michael has already given the direction. Default to the recommended option in the skill / reference, lay out the alternatives as a checklist, and let Michael tick them off on his schedule. Verified 2026-07-27 sentinelitad.com session: a `clarify` asking "Option A, B, or C?" with no reply left the work paused; switching to "Option A is what I'd run by default, here's the 5-minute checklist for A/B/C, ping me when you've picked" unblocked him.

## Quick API reference (Global API key, base URL `https://api.cloudflare.com/client/v4`)

```bash
EMAIL="michael@growthwebdev.com"           # from CLOUDFLARE_GROWTHWEB_EMAIL
KEY="$CLOUDFLARE_GROWTHWEB_API_KEY"        # Global API key
ZONE="<zone_id_resolved_by_listing>"

# List zones (find by hostname)
curl -sS -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  "https://api.cloudflare.com/client/v4/zones?per_page=50" | jq '.result[] | {id,name,status}'

# Get zone details (returns the canonical account ID)
curl -sS -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE" | jq '.result | {id,name,account}'

# List current DNS records
curl -sS -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records?per_page=100" | jq '.result[]'

# Create MX (Cloudflare Email Routing defaults)
curl -sS -X POST -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  -H "Content-Type: application/json" \
  --data '{"type":"MX","name":"<domain>","content":"route1.mx.cloudflare.net","priority":10,"proxied":false,"ttl":1}' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records"

# Create SPF
curl -sS -X POST -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"<domain>","content":"v=spf1 include:_spf.mx.cloudflare.net ~all","ttl":1}' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records"

# Create routing rule
curl -sS -X POST -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Forward X@<domain> to real@inbox",
    "matchers": [{"type":"literal","field":"to","value":"X@<domain>"}],
    "actions": [{"type":"forward","value":["real@inbox"]}]
  }' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/email/routing/rules"

# List verified destination addresses (per account, not per zone)
curl -sS -H "X-Auth-Email: $EMAIL" -H "X-Auth-Key: $KEY" \
  "https://api.cloudflare.com/client/v4/accounts/<account_id>/email/routing/addresses?per_page=50" | jq '.result[]'
```

## Standard workflow for "enable email forwarding for X@domain.com"

1. **Confirm zone:** list zones, find zone ID whose `name` matches the domain.
2. **Confirm destination is verified:** query the account's `/email/routing/addresses`; if not present, ask Michael to add+verify it through the CF dashboard (or via API — creates a verification email to send).
3. **List current DNS:** snapshot what exists, especially any old MX or SPF records. Don't overwrite without authorization.
4. **Create MX records:** three Cloudflare-hosted MX records at priorities 10/20/30 pointing to `route1/2/3.mx.cloudflare.net`. Use `proxied: false`, `ttl: 1`.
5. **Create SPF TXT:** `v=spf1 include:_spf.mx.cloudflare.net ~all`. **Never blindly overwrite an existing SPF** — if a record exists with `include:_spf.mx.cloudflare.net` already, leave it. If it has different content (e.g. `include:sendgrid.net`), ask Michael whether to merge.
6. **Create routing rule:** POST to `/zones/:id/email/routing/rules` with literal matchers and forward actions to verified addresses.
7. **Verify DNS externally:** `dig @1.1.1.1 <domain> MX +short; dig @1.1.1.1 <domain> TXT +short`.
8. **Verify rule:** re-list `/zones/:id/email/routing/rules`, confirm `enabled: true` and matcher/action match what you created.
9. **Build/audit check:** if there's a repo in the workspace (e.g. Astro static site), re-run `npm run build` and `verify-theme.py` (or whatever canonical verifier exists) to confirm no live-site breakage from any file you touched.
10. **Hand off smoke:** tell Michael the path is live and the only thing not auto-verifiable is "did the email actually land in his inbox" — ask him to send a test message from another account.

## Pitfalls

- **Do not trust `/zones/:id/email/routing` PATCH** — it returns `success: true` but does not flip `enabled`. Use `/zones/:id/dns_records` for MX/SPF and `/zones/:id/email/routing/rules` for routing.
- **Do not assume zone-ID-from-env-var-name** — always list zones.
- **Do not use `CLOUDFLARE_PAGES_API_TOKEN` for zone-level endpoints** — it's a per-page-credential. Use Global API key.
- **Do not assume `CLOUDFLARE_PAGES_API_TOKEN` can deploy** — token scope is typically list/read + webhook trigger, NOT ad-hoc deploy creation. POST to `/accounts/:id/pages/projects/:name/deployments` returns `400 "manifest field expected"` from a token without the right scope. No deploy-hook URL configured? Same answer.
- **Do not POST JSON to `/pages/projects/.../deployments` expecting it to deploy files.** For Direct Uploads projects, the API accepts the deploy record but does NOT serve the files at the edge — HTTP 500s result. The full upload-JWT cycle (token → upload → upsert-hashes → multipart deploy) is required, and `wrangler pages deploy` is the canonical implementation. Don't try to roll your own.
- **Do not try to "convert" a Direct Uploads Pages project to Git-integrated.** The API returns `400 "You cannot update the source object in a Direct Uploads project"`. Architecturally distinct — use the wrangler GitHub Action pattern instead.
- **Do not delete or overwrite existing MX/SPF records without listing first** — operational email may already be routed.
- **Do not skip the external `dig @1.1.1.1` check** — local API readback can race propagation.
- **Do not claim "Done" on an email forwarding task without Michael confirming the email landed** — outbound SMTP from this VM is usually blocked; the only end-to-end check is a real human sending a real message.
- **Do not print API keys** — show env var presence, zone/account/rule IDs, and redacted target addresses only.
- **Do not forget to purge edge cache after a deploy rollback that left 500s.** `POST /zones/<id>/purge_cache` with `{"hosts":["<domain>", "www.<domain>"]}` flushes the CF edge. Confirmed working 2026-07-28 on sentinelitad.com after wrangler deploy left the apex 500'ing while `.pages.dev` served correctly — the canonical was fine, only the custom-domain edge cache was stuck.
- **Do not pin Astro/Next/etc. to old Node versions in CI.** Astro 6.x requires Node >=22.12.0; pinning Node 20 fails the build step with "Node.js v20.20.2 is not supported by Astro!". Set `node-version: '22'` in `actions/setup-node@v4`.

- **A failed CI check is not always a code failure — read the Actions run annotations before reaching for a code fix.** When a PR appears blocked, the failed check may be a code error, an org-level billing/spending-limit failure, a runner-availability issue, a quota exhaustion, or a required-check the PR doesn't satisfy. Step 1 of any PR-decode investigation is reading the GitHub Actions run log annotations, not just the PR's `status`/`check_runs` summary. **Recipe:** (1) `gh pr checks <N> --json name,state,bucket,workflow` to list checks, (2) `gh run view <run-id> --log-failed` (or the GitHub web UI → Actions run → failed step → annotations) to read the actual failure text, (3) classify as code / billing / quota / authorization before reaching for a code change. Confirmed in 2026-07-31 on PR #382 (JOURNAL P1 evidence-cited recaps): 4/5 checks passing, the stuck one was `billing/spending-limit job-start failures` — a code fix was the wrong move entirely. The merge-authorization gate (`Only George YES may authorize merge`) was a separate, later gate. The diagnostic shortcut that breaks the dead-end: a stuck Actions job that names "billing," "quota," "spending limit," or "rate limit" in its annotation is not solvable from inside the repo.

## CF Pages deploy diagnostics (when a commit lands but the live site doesn't change)

CF Pages can silently stop auto-deploying. Sympton: `git push` succeeds, new commits show up on `origin/<branch>`, but the live site keeps serving the previous build. Steps to diagnose, in order:

1. **Confirm the commit reached GitHub**: `git ls-remote origin <production-branch>` — the SHA must match your local HEAD.
2. **Inspect recent Pages deployments**: `GET /accounts/:id/pages/projects/:name/deployments`. Note the `created_on`, `deployment_trigger.type` (`ad_hoc` vs `github`/push), and the `commit_hash` of the most recent successful deploy.
3. **If `latest_deployment.commit_hash` is older than your most recent push**, the GitHub webhook is not firing. Common causes:
   - The project was connected to a different GitHub account and the connection was revoked
   - The webhook secret rotated and was never re-entered in the CF Pages project
   - The repo's default branch was renamed and the CF Pages `production_branch` setting still points at the old name
4. **Try ad-hoc deploy via API** (likely fails with `CLOUDFLARE_PAGES_API_TOKEN`): `POST /accounts/:id/pages/projects/:name/deployments` with body `{"manifest": {...}, "deployment_trigger": {...}}`. A token that can list but not create deploys returns `400 "manifest field expected"` even when manifest is correctly supplied — that's a scope signal, not a malformed-payload signal.
5. **Check for a project deploy_hook URL**: `GET /accounts/:id/pages/projects/:name/deploy-hooks`. If present, POST to that URL (no auth) to manually trigger a rebuild. `POST /deploy-hooks` to create one will return `405 method_not_allowed` if the token scope is too narrow.
6. **The manual fix**: `https://dash.cloudflare.com/?to=/:account/pages/view/<project>` → **Deployments** → **Create deployment** → pick `production_branch` → click **Create**. Build runs in 20-60s.
7. **Long-term fix for the webhook**: dashboard → **Settings** → **Builds** → disconnect and reconnect the GitHub repo. This re-establishes the webhook cleanly.

Always re-run `npm run build` (or the repo's canonical builder) + the repo's verifier script after a Pages deploy to confirm the deployed artifact matches expected state. Browsing the live site is also cheap and catches dashboard-managed redirects or stale edge cache.

Pre-deploy verification of the code itself is the same as any other commit: `npm run build` (or repo equivalent) green before `git push`.

### CF Pages project type detection — read this before you try to "fix the webhook"

CF Pages projects come in **two architecturally distinct types**. Which one you have determines what's possible.

**Detect via API:**

```bash
# Project type A: Git-integrated. `source.type` is non-null.
# Project type B: Direct Uploads. `source.type` is null OR `source` key absent.
ACCT=<id>; TOKEN=<pages-api-or-bearer>
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<name>" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['result']; print('source:', d.get('source'))"
```

| Project type | Can have CF-managed GitHub webhook? | Right durable deploy path |
|---|---|---|
| **Git-integrated** (`source.type = "github"`) | ✅ yes — webhook fires on push | Should already work; if not, fix the webhook per "Long-term fix" step above |
| **Direct Uploads** (`source = null` or absent) | ❌ **architecturally impossible** — API returns `400 "You cannot update the source object in a Direct Uploads project"` if you PATCH `source` onto it | **GitHub Action that calls `wrangler pages deploy`** — the canonical durable path |

**Symptoms of a Direct Uploads project where someone tried the wrong fix:**
- All historical deployments have `deployment_trigger.type = "ad_hoc"` — meaning every prior deploy was a manual dashboard click.
- `git push` does not produce a new deployment entry in the API list.
- `wrangler pages deploy` from a local shell works perfectly; only GitHub-CF integration is missing.

**Why "Direct Uploads" projects exist:** owners want to publish files without source code (Snapshots, ZIPs, content-managed assets, or just decoupled build artifacts). CF Pages treats them as file-stores, not as Git-backed services.

**The wrangler GitHub Action pattern (Direct Uploads durable fix).** Verified working on `mbgulden/sentinelitad.com` 2026-07-28.

```yaml
# .github/workflows/pages-deploy.yml
name: Deploy site
on:
  push:
    branches: [<production-branch>]
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'        # Astro 6.x requires >=22.12.0
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - run: npm install -g wrangler
      - name: Deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: <account-id>   # public, hardcode
        run: |
          wrangler pages deploy dist \
            --project-name=<project> \
            --branch=<production-branch> \
            --commit-hash="$GITHUB_SHA" \
            --commit-message="${{ github.event.head_commit.message }}"
```

**Why `wrangler pages deploy` works where the raw API does not.** `wrangler` uses the upload-JWT flow: `GET /accounts/.../pages/projects/<name>/upload-token` → POST to `/pages/assets/upload` with the JWT → `POST /pages/assets/upsert-hashes` → `POST /pages/projects/<name>/deployments` with **multipart/form-data** containing the manifest. The Direct Uploads API returns `400 "manifest field was expected"` for raw JSON bodies; wrangler handles the multipart shape correctly end-to-end.

**Why the raw API alone is not enough for Direct Uploads.** The raw API accepts the deploy record (`success: true`) but does NOT serve the files at the edge. Empty files at the served URL produces HTTP 500. You must complete the full upload-JWT cycle for files to actually be served.

## Reference Files

- `references/growthweb-zone-list-and-id-map.md` — known GrowthWeb Cloudflare zones as of 2026-07-27 (zone names + IDs + account ID), with pointers for resolving new zones.
- `references/cloudflare-zone-enablement-sentinelitad-2026-07-27.md` — worked example: bringing `sentinelitad.com` online for email forwarding to `michael@growthwebdev.com` (the session that produced this skill).
- `references/cf-pages-deploy-diagnostic-when-webhook-dies.md` — diagnostic + recovery flow when `git push` succeeds but live CF Pages site doesn't update (verified 2026-07-27 on sentinelitad-com Pages project).
- `references/cf-pages-direct-uploads-wrangler-github-action-2026-07-28.md` — **Direct Uploads** Pages projects can't wire a CF-managed GitHub webhook. The durable fix is a GitHub Action that calls `wrangler pages deploy` with `CLOUDFLARE_API_TOKEN`. Full worked example, recovery procedure, and verification commands for the sentinelitad.com session.
- `references/public-marketing-site-readiness-pattern.md` — the full audit → fix → DNS → form backend → founder note → commit + blocked-by-deploy pattern, with checklist + reusable artifacts (Founder Note HTML template, Cloudflare Worker form backend stub).
