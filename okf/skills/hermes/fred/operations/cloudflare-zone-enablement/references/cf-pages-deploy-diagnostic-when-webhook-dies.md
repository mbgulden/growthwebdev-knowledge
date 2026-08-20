# CF Pages Deploy Diagnostic — When Git Push Succeeds But Live Site Doesn't Update

**Date:** 2026-07-27
**Verifying context:** Sentinel ITAD — `mbgulden/sentinelitad.com` repo, CF Pages project `sentinelitad-com`, account ID `196c1798da487413b0281ccc570f05a1`.
**Lesson embodied:** CF Pages can silently stop auto-deploying even when the repo is healthy. Diagnosing this requires checking a specific sequence of API calls, and recovering often needs a CF Dashboard click because the API token typically lacks ad-hoc deploy scope.

## Symptom

- Local `git push origin <production-branch>` succeeds.
- `git ls-remote origin <production-branch>` returns the new commit SHA.
- Live site at `sentinelitad.com` still serves the previous build.
- No notification, no obvious error.

## Quick diagnostic (the order that actually works)

### Step 1: confirm the commit reached GitHub

```bash
git ls-remote origin <production-branch>
# SHA on the rightmost column must match your local HEAD
```

If it doesn't match, the issue is push-side, not Pages-side. Fix git, retry.

### Step 2: check Pages deployments via API

```bash
source ~/.hermes/profiles/fred/.env  # or wherever CF_PAGES_API_TOKEN lives
ACCT=$CLOUDFLARE_PAGES_ACCOUNT_ID
TOKEN=$CLOUDFLARE_PAGES_API_TOKEN

curl -sS \
  -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<project-name>/deployments" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for d in data['result'][:8]:
    meta = d.get('deployment_trigger', {}).get('metadata', {}) or {}
    print(f\"  {d.get('created_on')} | trigger={d.get('deployment_trigger',{}).get('type')} | commit={meta.get('commit_hash','')[:10]} | status={d.get('latest_stage',{}).get('status')}\")"
```

Look at:
- **Most recent successful deploy's `created_on`** — anything older than your last `git push` means Pages hasn't picked up the commit.
- **`deployment_trigger.type`** — `github` means the webhook fired; `ad_hoc` means someone triggered manually via Dashboard or API.

If no deploy exists since your push, the webhook is dead.

### Step 3: try ad-hoc deploy via API (probably fails)

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "manifest": {"version": 1, "branch": "<production-branch>", "commit": "<sha>", "commit_dirty": false},
    "deployment_trigger": {"type": "ad_hoc", "metadata": {"branch": "<production-branch>", "commit_hash": "<sha>"}}
  }' \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<project>/deployments"
```

If you get back `400 "A 'manifest' field was expected in the request body but was not provided"` even though you sent a manifest, **the API token scope is too narrow**. `CLOUDFLARE_PAGES_API_TOKEN` is typically issued for list/read + webhook-trigger flows, NOT for ad-hoc deploy creation. No amount of payload shape tweaking will fix this.

### Step 4: check for an existing deploy hook

```bash
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCT/pages/projects/<project>/deploy-hooks"
```

If the response has a `url` field, you can POST to that URL (no auth) to trigger a rebuild:

```bash
curl -sS -X POST "https://api.cloudflare.com/client/v4/pages/webhooks/<hook-id>/<secret>"
```

If there's no `url` or the hook was never created, you can try `POST /deploy-hooks` to make one — but expect `405 method_not_allowed` if the token scope is too narrow.

### Step 5: the manual UI fallback (this is the one that always works)

Open in browser:

```
https://dash.cloudflare.com/?to=/:account/pages/view/<project>
```

Click **Deployments** in the left sidebar → **Create deployment** (top right) → pick **Branch: <production-branch>** → leave defaults → click **Create**.

Cloudflare queues a build. Status cycles `queued → initialize → clone_repo → build → deploy` over 20–60 seconds. Live site at custom domains updates after `deploy: success`.

### Step 6: long-term webhook fix

Dashboard → **Pages** → select project → **Settings** → **Builds** → disconnect GitHub → reconnect. This re-registers the webhook. Verify after by pushing a commit and watching for a new deployment in the list.

## Step-by-step evidence sentinelitad-com Pages project

- **Last successful deploy before the gap**: `2026-07-09T15:05:42` (commit `4a6cb15b`, trigger=`ad_hoc`, branch=`ned/initial-website`).
- **Gap period**: ~18 days. No deploys.
- **My commit on 2026-07-27**: `95de1c9` on `ned/initial-website` (merge of `feature/founder-note` → production).
- **Live site after push**: still `691b8c43` deployment, no Founder Note marker.
- **API responses**:
  - `POST /deployments` with full manifest body → `400 "manifest field expected"` (token scope issue).
  - `POST /deploy-hooks` to create one → `405 method_not_allowed`.
  - `latest_deployment.deployment_trigger.type` = `ad_hoc` for all 4 historical deploys — meaning every prior deploy was triggered manually, **not** via GitHub webhook. The webhook may never have been wired.
- **Resolution path**: manual Dashboard deploy + Settings → Builds → reconnect GitHub for long-term fix.

## Reusable patterns

1. **Treat Pages' GitHub webhook as best-effort.** Always verify deploy status after every push — don't assume "I pushed, it'll deploy." Add this to your post-push checklist.
2. **The 30-second Dashboard click is the universal fallback.** Don't burn time trying to coax a too-narrow API token into creating deploys; the UI is the path that works.
3. **`trust-ad_hoc` as a deployment-trigger type in the deploy history is a strong signal** that the project has never had a wired GitHub webhook. Worth surfacing to Michael and asking him whether reconnect makes sense.
4. **Always re-run the repo's canonical build (`npm run build`) before pushing**. Stale code can cause mysterious Pages build failures that look like webhook issues.
5. **Document the manual-deploy step in an ops handoff doc at the repo root** so future agents (you in three months, or anyone reading the audit) knows the constraint without rediscovering it.

## Related references

- `references/cloudflare-zone-enablement-sentinelitad-2026-07-27.md` — DNS + Email Routing piece of the same session.
- `references/public-marketing-site-readiness-pattern.md` — full audit → fix pattern for small public marketing sites.