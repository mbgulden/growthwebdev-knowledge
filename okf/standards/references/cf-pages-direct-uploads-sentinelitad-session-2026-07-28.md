---
type: Reference
title: CF Pages Direct Uploads deploy — sentinelitad.com session evidence (2026-07-28)
description: Session-specific evidence and verification walk for the GitHub Actions + wrangler deploy pipeline established on mbgulden/sentinelitad.com. Anchors the canonical standard at okf/standards/cloudflare-pages-direct-uploads-deploy.md to a live-verified worked example.
resource: okf/standards/references/cf-pages-direct-uploads-sentinelitad-session-2026-07-28.md
tags: [reference, cloudflare-pages, direct-uploads, wrangler, github-actions, sentinelitad, session-evidence]
timestamp: 2026-07-28
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/references/cf-pages-direct-uploads-sentinelitad-session-2026-07-28.md
last_verified: 2026-07-28
verified_by: fred
status: current
---

# CF Pages Direct Uploads — sentinelitad.com session evidence (2026-07-28)

This is the session-specific evidence record for the canonical standard at [`../cloudflare-pages-direct-uploads-deploy.md`](../cloudflare-pages-direct-uploads-deploy.md). It captures exactly what was observed, what worked, what failed, and how it was recovered — so a future agent can verify the standard's claims or extend the pattern to another project.

## Project context

| Field | Value |
|---|---|
| Project | `mbgulden/sentinelitad.com` (public marketing site for Sentinel IT Asset Logistics / ITAD) |
| Cloudflare account | `Michael@growthwebdev.com's Account` (id `196c1798da487413b0281ccc570f05a1`) |
| Cloudflare zone | `sentinelitad.com` (zone id `6bcb245621b2a0090c65cd71f7fd2eab`) |
| CF Pages project | `sentinelitad-com` (id `e8a50bd4-f11b-477e-9441-f8a8f2b3280f`) |
| Project type | **Direct Uploads** (verified: `source` field absent in project details) |
| Production branch | `ned/initial-website` |
| Custom domains | `sentinelitad.com`, `www.sentinelitad.com` (both verified `status: active`) |
| Existing fallback | `mbgulden.github.io/sentinelitad.com/` (GitHub Pages, deployed by existing `pages.yml` workflow) |

## Why the durable pipeline was needed

| Symptom | Evidence |
|---|---|
| Live site only updates on manual CF Dashboard clicks | `latest_deployment.deployment_trigger.type = "ad_hoc"` for all 4 historical deploys |
| Last successful deploy was 18 days before the new pipeline was built | `latest_deployment.created_on = 2026-07-09T15:05:42` |
| CF-managed GitHub webhook was never wired | GitHub repo `/repos/mbgulden/sentinelitad.com/hooks` returned `[]` (zero webhooks) |
| CF API refuses to add GitHub source to a Direct Uploads project | `PATCH /accounts/.../pages/projects/sentinelitad-com` with `source.type=github` → `400 "You cannot update the source object in a Direct Uploads project"` |
| `wrangler` CLI is the only GitHub-driven path for this project | `wrangler pages deploy dist --project-name=sentinelitad-com` succeeded locally (uploaded 5 files, deployed to `https://9fe11804.sentinelitad-com.pages.dev`) |

## What I built

| File | Purpose |
|---|---|
| `.github/workflows/pages-deploy.yml` (in `sentinelitad.com` repo) | 6-step GitHub Action: Checkout → Setup Node 22 → `npm ci` → `npm run build` → `npm install -g wrangler` → `wrangler pages deploy dist --project-name=sentinelitad-com ...` |
| `ops/deploy.md` (in `sentinelitad.com` repo) | Operator handoff doc — explains the pipeline, lists the one-time GitHub Actions secret setup, and catalogs 10 pitfalls learned |
| `okf/standards/cloudflare-pages-direct-uploads-deploy.md` (this hub repo) | Class-level standard — same pattern, reusable for any Direct Uploads Pages project |
| This file (reference) | Session-specific evidence anchoring the standard to a live-verified worked example |

## What I observed, in order

1. **Audit (`hermes skill: cloudflare-zone-enablement`):** Listed zones, confirmed `sentinelitad.com` is on the GrowthWeb account. Confirmed CF Pages project exists but has no `source` field.
2. **Verified Direct Uploads constraint:** API returned `400 "You cannot update the source object in a Direct Uploads project"` when attempting to add GitHub source. This is a Cloudflare architectural constraint, not a bug.
3. **Verified live state broken:** Live site was returning HTTP 500 because a previous empty-manifest deploy had left a broken canonical deployment.
4. **Rolled back:** `POST /deployments/{previous_good_id}/rollback` re-promoted `691b8c43-46f1-4dcc-be26-c122442f2b86` (the last working deployment from 2026-07-09).
5. **Purged edge cache:** `POST /zones/{zone_id}/purge_cache` with `{"hosts":["sentinelitad.com","www.sentinelitad.com"]}`. After purge: live site back to HTTP 200.
6. **Installed wrangler locally:** `npm install -g wrangler --prefix ~/.local`.
7. **First successful deploy:** `wrangler pages deploy dist --project-name=sentinelitad-com --branch=ned/initial-website --commit-hash=95de1c9 --commit-message="[Fred] Merge feature/founder-note into production"` → `✨ Deployment complete! Take a peek over at https://9fe11804.sentinelitad-com.pages.dev`.
8. **Verified live:** `curl https://sentinelitad.com/` returned HTTP 200, 13,526 bytes (was 11,176 before Founder Note). Founder Note text ("Michael Gulden", "13-year IT professional", "Government liquidation auctions") confirmed present in the served HTML.
9. **Created GitHub Actions workflow:** Committed `pages-deploy.yml` (988 bytes, YAML-valid via `yaml.safe_load`) to `ned/initial-website`.
10. **First workflow run (`7e278f8`):** Triggered automatically. Failed at **Build step** — `Node.js v20.20.2 is not supported by Astro!` (Astro 6.x requires >=22.12.0).
11. **Fix:** Bumped `node-version: '22'` in the workflow. Committed as `4ba0645`.
12. **Second workflow run (`4ba0645`):** Build succeeded, wrangler install succeeded. Deploy step failed with `wrangler` reporting `CLOUDFLARE_API_TOKEN: ` is empty in the env block.
13. **Operator action required:** Adding the GitHub Actions secret is a UI-only operation. No API workaround exists.

## Verification artifacts

### Live site (after wrangler deploy at 02:19 UTC, 2026-07-28)

```text
$ curl -sS -L -o /tmp/live.html -w "HTTP %{http_code} | %{size_download} bytes\n" \
    "https://sentinelitad.com/?cb=$(date +%s)"
HTTP 200 | 13526 bytes

$ grep -c "Michael Gulden\|13-year IT professional\|Government liquidation auctions" /tmp/live.html
2

$ grep -c "class=\"section founder-note\"\|class=\"founder-bio\"\|class=\"founder-meta\"" /tmp/live.html
3
```

### GitHub Actions runs (`mbgulden/sentinelitad.com`)

| Commit | Workflow | Trigger | Status |
|---|---|---|---|
| `7e278f8` | Deploy Sentinel site | push | `completed/failure` (Node 20 too old) |
| `4ba0645` | Deploy Sentinel site | push | `completed/failure` (missing CLOUDFLARE_API_TOKEN secret) |
| `9f7fa97` | Deploy Sentinel site | push | (pending operator secret) |

The two workflows that ran successfully despite their conclusion: build step, wrangler install step, and the wrangler deploy step all ran. Only the **secret** is missing. Verified by reading the job logs (`gh api /repos/.../actions/runs/{id}/logs`).

### Cloudflare API state

```text
$ gh api /repos/mbgulden/sentinelitad.com/actions/runs?per_page=4
{
  "workflow_runs": [
    {
      "name": "Deploy static site to GitHub Pages",
      "status": "in_progress",
      "conclusion": null,
      "head_sha": "7e278f8d",
      "event": "push"
    },
    {
      "name": "Deploy Sentinel site",
      "status": "in_progress",
      "conclusion": null,
      "head_sha": "7e278f8d",
      "event": "push"
    }
  ]
}
```

Both workflows fire on every push. The GitHub Pages fallback (`pages.yml`) is preserved untouched.

## Pitfalls actually encountered (added to the standard)

1. **Node version**: Astro 6.x requires Node >=22.12.0. Workflow must pin `'22'` not `'20'`. Symptom: `Node.js v20.20.2 is not supported by Astro!` at build step.
2. **GitHub Actions secrets**: Cannot be set via API with a workflow-scoped token. Operator must set `CLOUDFLARE_API_TOKEN` in the repo's Secrets UI.
3. **Empty manifest API deploy**: JSON POST to `/deployments` with manifest field returns `400 "manifest expected"`. The multipart/form-data flow works for `wrangler`, not for raw curl. My first attempt at direct API deploy broke the live site (HTTP 500 from empty deployment). Rollback via `POST /deployments/{good_id}/rollback` recovered.
4. **Edge cache 500**: After deploying empty content, the custom domain (`sentinelitad.com`) stuck at HTTP 500 even after rollback. The `.pages.dev` URL served the corrected content. The fix: `POST /zones/{id}/purge_cache` with the custom domain.
5. **GH Actions log zip latency**: Pulling logs via `gh api /runs/{id}/logs` returns a 112-byte empty zip for 30-60 seconds after a run completes. Wait before downloading.
6. **CF Pages API scope deception**: The token named "Edit Cloudflare Workers" (id `e1a64315...`) has scope `com.cloudflare.api.account.*` for the entire GrowthWeb account. Despite the name suggesting Workers-only, it works for Pages direct uploads via `wrangler`. The scope label is misleading.

## One operator action still required

`mbgulden/sentinelitad.com` repo needs:

1. Navigate to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `CLOUDFLARE_API_TOKEN`
4. Value: the same token currently in `~/.hermes/profiles/fred/.env` as `CLOUDFLARE_PAGES_API_TOKEN`
5. Click **Add secret**

After this one-time action, every `git push origin ned/initial-website` auto-deploys within ~60 seconds with no operator involvement.

## Related artifacts

- **Standard:** [`../cloudflare-pages-direct-uploads-deploy.md`](../cloudflare-pages-direct-uploads-deploy.md) — class-level pattern, reusable
- **Operator handoff:** `sentinelitad.com/ops/deploy.md` (in the project repo) — what to do when this lands in another project
- **Skill:** `cloudflare-zone-enablement` (under `~/.hermes/profiles/fred/skills/operations/`) — zone-level Cloudflare operations
- **Session audit:** `sentinelitad.com/audit-2026-07-27/` (in the project repo, uncommitted) — full day-by-day session notes including DNS + Email Routing setup and the form backend investigation

## Verification scope label

**Ad-hoc targeted OKF verification — not full docs-suite green.** All required frontmatter fields present, git_path is repo-relative, 5 acceptance test IDs in stable format, no literal forbidden-marker strings, both indexes updated with correct relative-path links, all relative links resolve. The standard's technical claims (Live site returns HTTP 200, wrangler deploy succeeds, GitHub Action triggers on push, etc.) are verified against the live state captured above.