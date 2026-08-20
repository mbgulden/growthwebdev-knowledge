# HDE PR proof: Cloudflare Pages pass + stale Workers Builds failure

Session pattern from HDE/PWP analytics proof work.

## Symptom

A PR branch can have contradictory Cloudflare checks:

- `Cloudflare Pages` passes and points at a valid Pages preview deployment for the branch.
- `Workers Builds: hd-platform` fails on the same commit.

For HDE, Pages is the canonical frontend deployment path. The Workers Builds check may be an older non-main branch trigger still attached to the repo.

## Verification path

1. Inspect GitHub checks:

   ```bash
   gh pr checks <PR_NUMBER> --watch=false
   gh pr view <PR_NUMBER> --json statusCheckRollup,mergeStateStatus,url
   ```

2. Query Cloudflare Pages deployments and confirm the branch preview succeeded:

   ```bash
   curl -s "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/pages/projects/hd-platform/deployments" \
     -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN"
   ```

   Look for the current branch/commit under `deployment_trigger.metadata` and `latest_stage.status: success`.

3. Query Workers Builds status/logs for the failing build UUID from the GitHub check details URL:

   ```bash
   curl -s "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/builds/builds/$BUILD_UUID" \
     -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN"

   curl -s "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/builds/builds/$BUILD_UUID/logs" \
     -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN"
   ```

## Known HDE stale-trigger signature

The Workers Builds response showed:

- `trigger_name`: `Deploy non-production branches`
- `build_command`: empty string
- `deploy_command`: `npx wrangler versions upload`
- branch includes `*`, excludes `main`

The log failed with:

```text
Missing entry-point to Worker script or to assets directory
```

That means Workers Builds is trying to run `wrangler versions upload` against an Astro/Pages artifact without a Worker `main` or Workers assets config. This is a CI trigger configuration issue, not proof that `npm run build` or the Pages preview failed.

## Operational rule

Do not mutate Cloudflare Workers Builds triggers as a side effect of a PWP/content/analytics PR. Treat trigger edits as infrastructure changes requiring explicit approval. Report the exact trigger/log evidence, keep the issue in review if local proof and Pages preview pass, and identify the failed Workers check as the remaining external blocker.
