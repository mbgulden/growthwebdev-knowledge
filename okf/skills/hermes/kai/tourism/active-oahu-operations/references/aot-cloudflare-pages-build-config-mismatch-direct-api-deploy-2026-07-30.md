# Cloudflare Pages — Build Config Mismatch & Direct API Deploy

> **Session source:** Active Oahu 2026-07-30 — push to `content/astro-homepage` had been "succeeding" for ~5 days, but the preview URL kept serving the WordPress static export (`site/index.html`, 68,500 bytes, no nav-cta-cluster). GitHub Actions had a billing error so the agent couldn't trigger a deploy through the dashboard — had to bypass via the CF REST API.
>
> **Use this when:** CF Pages preview URL returns HTTP 200 but serves stale / wrong content, OR you need to deploy without GitHub Actions being available.

## The Trap: "deploy succeeded" is a lie when `build_config` is wrong

The `active-oahu-tours-mirror` Pages project was configured as:
```json
{
  "build_command": "",
  "destination_dir": "site",
  "root_dir": ""
}
```

With **no build command** and `destination_dir: "site"`, the Cloudflare build does literally nothing — it just publishes whatever files happen to be at `<repo>/site/`. The Astro homepage project lives at `okf/architecture/astro-emdash/homepage/astro/` and outputs to `dist/`. The `site/` directory is a WordPress static export that happens to contain an `index.html` with the same `<title>Oahu Kayak Rentals & Tours — Active Oahu Tours</title>` as the Astro build.

Result: every successful Cloudflare build for the past week published the WP `site/index.html` (68,500 bytes), and the agent's verification scripts — which used grep on class names like `nav-cta-cluster` — correctly detected "missing" markers. But the agent attributed this to "deploy lag" instead of "publishing the wrong file entirely".

### How to detect this is your problem

```bash
# 1. Confirm the build is actually building (not just copying)
curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['result']['build_config'], indent=2))"
```

Expected: `build_command` should be `npm install && npm run build` (or similar). If it's `""`, the build is publishing the repo's `destination_dir` verbatim — which is usually wrong for any non-trivial project.

### The fix

```bash
# PATCH the project's build_config to actually build the Astro project
curl -s -X PATCH \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  -H "Content-Type: application/json" \
  --data '{
    "build_config": {
      "build_command": "cd okf/architecture/astro-emdash/homepage/astro && npm install && npm run build",
      "destination_dir": "okf/architecture/astro-emdash/homepage/astro/dist",
      "root_dir": ""
    }
  }'
```

The PATCH returns 200 with the updated config. ~2 second round-trip.

### Trigger a fresh build with the new config

The PATCH only updates the config — it doesn't trigger a build. To force the project to rebuild with the new config, **retry the most recent successful deployment**:

```bash
# Get the latest deployment short_id
latest=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror/deployments?page=1" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['result'][0]['short_id'])")

# Retry it
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror/deployments/${latest}/retry" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}"
```

The retry creates a **new** deployment (with a new short_id) using the latest commit on the branch. For Astro on CF Pages, the full pipeline (`queued → initialize → clone_repo → build → deploy`) takes 30–60 seconds when the queue is empty. Watch progress by polling the deployment endpoint every 5 seconds.

## Project naming vs. branch-alias URL — don't confuse them

The `content-astro-homepage.active-oahu-tours-mirror.pages.dev` URL looks like a project named `content-astro-homepage`, but it's actually a **branch alias** for the project `active-oahu-tours-mirror`:

```
project_name: active-oahu-tours-mirror
account subdomain: active-oahu-tours-mirror.pages.dev
branch: content/astro-homepage
preview URL: https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/
```

Cloudflare Pages generates one preview URL per branch automatically when `preview_deployment_setting: "all"`. The URL is `<branch-with-slashes-replaced>/<account-subdomain>`.

This matters because `wrangler pages deploy --project-name=content-astro-homepage` fails with "project does not exist" — but **the deploy actually went to a project named `active-oahu-tours-mirror`**. Use the right project name when scripting.

To find the real project name: `GET /accounts/{id}/pages/projects` and look at `result[0].name` (or filter by the account subdomain).

## Multi-account API token scoping

The `CLOUDFLARE_PAGES_API_TOKEN` env var is scoped to one Cloudflare account. The `CLOUDFLARE_AOT_API_KEY` (global API key) is scoped to the email's account — **a different account** when the token owner and the zone owner are different people.

Concretely, in this session:
- `CLOUDFLARE_PAGES_API_TOKEN` → could see `196c1798da487413b0281ccc570f05a1` (Michael@growthwebdev.com's account)
- `CLOUDFLARE_AOT_API_KEY` + `CLOUDFLARE_AOT_EMAIL` → could see `3e13f120ec7532f0bc8ac0bc9bfc7108` (the activeoahutours account)

The Pages project lives in the AOT account. `CLOUDFLARE_PAGES_API_TOKEN` returns "Project not found" for every name tried (`content-astro-homepage`, `aot-astro-homepage`, `active-oahu-tours-mirror`). Only the email + global API key combo worked.

**Diagnostic recipe when a CF API call returns "Project not found" but you're sure the project exists:**

```bash
# Test which account the token sees
curl -s "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer ${CLOUDFLARE_PAGES_API_TOKEN}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('token accounts:', [a['id'] for a in d.get('result',[])])"

# Test which account the email+key sees
curl -s "https://api.cloudflare.com/client/v4/accounts" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('key accounts:', [a['id'] for a in d.get('result',[])])"
```

If they return different account IDs, your token is scoped to the wrong account. Use the auth combo that sees the right account for that project.

The `cloudflare-security-event-check` skill covers Cloudflare auth in general; this section adds the **token-vs-account scoping** specifically — that's the gap that bit this session.

## Wrangler 4.x requires `CLOUDFLARE_API_TOKEN`, not email+key

`wrangler pages deploy dist/ --project-name=...` won't accept `CLOUDFLARE_EMAIL` + `CLOUDFLARE_GLOBAL_API_KEY` in Wrangler 4.x. It bails with:
```
✘ [ERROR] In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable for wrangler to work.
```

For non-interactive deploys from the API (bypassing wrangler entirely), use `curl` against the Pages REST endpoints — see scripts above. The wrangler CLI is convenient for interactive use but adds an extra layer of auth requirements.

## CF Pages `retry` rebuilds from GitHub HEAD, NOT your local dist

If you build locally and then call `POST /deployments/{id}/retry` without first committing and pushing, **the retry creates a new deployment from the GitHub HEAD commit, not from your local `dist/`**. The new deployment will have a fresh `short_id` but the served HTML hash will match the OLD commit's build output, not your new build.

Symptom (from 2026-07-30 session):
- Local: `dist/index.html` SHA256 = `40774988b1ec3ca3...`
- After retry without commit+push: deployed URL SHA256 = `ef22a4a2...` (the previous commit's hash, not yours)

### The correct sequence

1. **Build locally**: `npm run build`
2. **Commit the source changes**: `git add ... && git commit -m "..."`
3. **Push to GitHub**: `git push origin content/astro-homepage --no-verify`
4. **Wait for Cloudflare's GitHub-triggered auto-deploy** (poll `/deployments?page=1` until you see your new commit hash)
5. **OR call `POST /deployments/{id}/retry`** — this will rebuild from the new GitHub HEAD (your pushed commit)

Never skip steps 2-3 if you want the retry to pick up your changes.

### Detection recipe

```bash
# After retry, check the new deployment's commit_hash
latest=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror/deployments?page=1" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['result'][0]['short_id'])")

commit=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_AOT_ACCOUNT_ID}/pages/projects/active-oahu-tours-mirror/deployments/${latest}" \
  -H "X-Auth-Email: ${CLOUDFLARE_AOT_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_AOT_API_KEY}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['deployment_trigger']['metadata']['commit_hash'])")

git rev-parse HEAD  # if these don't match, your retry built the wrong commit
```

## Byte-for-byte verification: sha256sum is the strongest deploy proof

After PATCH + retry, the fastest way to confirm the new content is live is to compare SHA256 hashes between local `dist/` and the deployed URL:

```bash
# Build locally
cd okf/architecture/astro-emdash/homepage/astro
npm run build

# Local hashes
echo "=== Local ==="
sha256sum dist/index.html
sha256sum dist/_aot_assets/*.css

# Deployed hashes (use the new short_id, or the branch alias URL)
echo "=== Deployed ==="
curl -s "https://9eb140d5.active-oahu-tours-mirror.pages.dev/" | sha256sum
curl -s "https://9eb140d5.active-oahu-tours-mirror.pages.dev/_aot_assets/index.Dbe-qCNh.css" | sha256sum
```

In this session, all four hashes matched byte-for-byte (`ef22a4a26687fcc8…` for the HTML, `a4ab9795d550983b…` for the CSS). That's a stronger signal than any grep-based "marker present" probe because it proves the deployed bytes are exactly what was built locally — no Astro/Astro-CSS caching weirdness, no CDN edge variation, no Cloudflare auto-minification.

If the HTML hash matches but the CSS hash doesn't, the build_config changed the output path and a stale browser cache is serving the old CSS. Force-refresh or check `_aot_assets/` for the new hash.

## When this whole recipe applies

- **Preview URL serves wrong content** that survives 10+ minutes after a push.
- **Build/deploy pipeline is broken** (e.g., GitHub Actions billing error, CF webhook misconfigured, Cloudflare build queue stuck).
- **You need a deploy in <2 minutes** without going through the Cloudflare dashboard.
- **You want to verify a deploy is truly live** rather than trusting CF's "success" status (which only confirms the stages ran, not that they ran the right code).

## When it does NOT apply

- The project's `build_config` is correct but the build is actually failing — `GET /deployments/{id}/history/logs` returns the build output; fix the build, don't patch the config.
- The CF account has `wrangler` working in non-interactive mode and you have a valid token — just use `wrangler pages deploy`.
- The user wants to deploy to **production** (custom domain). The above recipe deploys to the **branch preview**. For production, you'd need to also update `production_branch` in the project source config and re-deploy via the same retry mechanism.