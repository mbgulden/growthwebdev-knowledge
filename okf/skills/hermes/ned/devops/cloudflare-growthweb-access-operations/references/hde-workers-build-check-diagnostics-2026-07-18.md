# HDE Workers Build check diagnostics — 2026-07-18

Context: GRO-3995 opened a PR where Cloudflare Pages succeeded but the GitHub check `Workers Builds: hd-platform` failed. The local implementation/build was green, so the next step was to inspect the remote proof check without guessing.

## Pattern

1. Query the PR commit check-runs, not only `gh pr view`, because deprecated project fields can make `gh pr view --json statusCheckRollup` fail in some repos.

```bash
gh api repos/mbgulden/hd-platform/commits/<sha>/check-runs \
  --jq '{total_count, check_runs:[.check_runs[] | {name,status,conclusion,details_url,html_url,output}]}'
```

2. If the failing check is `Workers Builds: hd-platform`, record both handles:
   - GitHub check run id / `html_url`
   - Cloudflare Workers build id from `output.summary` / `details_url`

3. Before declaring a credential blocker, search OKF integrations and profile `.env` files for Cloudflare credentials. HDE/GrowthWeb tokens are documented in OKF `integrations/api-key-locations.md`; Ned profile `.env` commonly has `CLOUDFLARE_PAGES_API_TOKEN` and `CLOUDFLARE_PAGES_ACCOUNT_ID`.

4. Cloudflare API probes that were safe/read-only:

```bash
# Some Workers build log endpoints can return 204 with no diagnostic body.
curl -sS -i \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/workers/scripts/hd-platform/builds/<build-id>/logs"

# Service build endpoints may return metadata for the current service/env but not the failure log.
curl -sS \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/workers/services/hd-platform/environments/production/builds/<build-id>"
```

## Reporting rule

If GitHub exposes no annotations/log text and Cloudflare read-only API probes return only `204` or service metadata, do **not** mark the Linear issue Done. Keep it In Review, include the GitHub check run and Cloudflare build IDs in Linear/RESULT, and state that live/proof is not green yet. Local green build evidence is useful but does not override an explicit remote proof check failure.
