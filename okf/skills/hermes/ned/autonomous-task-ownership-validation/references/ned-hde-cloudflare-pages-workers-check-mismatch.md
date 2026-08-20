# HDE Cloudflare Pages vs Workers Builds check mismatch (GRO-4000 pattern)

## When this applies

Use this reference when an HD Platform PR is locally green (`npm run build`, postbuild, and focused verifiers pass) but GitHub shows:

- `Cloudflare Pages` check status, and/or
- `Workers Builds: hd-platform` check status

especially when the repo has `wrangler.jsonc` with `pages_build_output_dir: "dist"` and no Worker `main` entry point.

## Confirm before changing code

1. Re-run the local canonical build from the task worktree:

   ```bash
   python3 scripts/verify_seo_metadata.py --root .
   npm run build
   python3 scripts/verify_seo_metadata.py --root . --include-dist
   ```

2. Query PR checks:

   ```bash
   gh pr view <PR> --json statusCheckRollup,mergeable,state,url,headRefOid
   gh pr checks <PR> || true
   ```

3. If Cloudflare API creds are available, read Pages deployment logs, not only the GitHub check label:

   ```bash
   curl -sS \
     -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
     "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/pages/projects/hd-platform/deployments/<deployment-id>/history/logs"
   ```

## Durable pitfall

Do **not** add `assets.directory` to the root `wrangler.jsonc` just to satisfy a local `npx wrangler deploy --dry-run` or a red `Workers Builds` check when the repo is configured as Cloudflare Pages.

Observed behavior:

- `npx wrangler deploy --dry-run` without Worker `main` or `assets.directory` fails with:

  ```text
  Missing entry-point to Worker script or to assets directory
  ```

- Adding:

  ```jsonc
  "assets": { "directory": "./dist" }
  ```

  can make local Workers dry-run read `dist`, but Cloudflare Pages build validation rejects it:

  ```text
  Configuration file for Pages projects does not support "assets"
  ```

For Pages projects, keep `pages_build_output_dir: "dist"` and preserve Pages green. Treat the Workers Builds failure as an external check-configuration mismatch unless the task specifically authorizes splitting Pages vs Workers configuration.

## Reporting pattern

If local build and Pages are green but Workers Builds remains red:

- Keep Linear `In Review`, not `Done`.
- Comment with exact local verification evidence.
- Name the check mismatch plainly: Cloudflare Pages config vs Workers deploy semantics.
- Do not claim full green/live proof until the external Workers Builds integration is disabled, repointed, or split to a Worker-specific config.
