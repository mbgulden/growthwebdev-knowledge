# HDE staging → production source-of-truth cutover — 2026-07-17

## Context

Michael asked to push HDE staging to production so agents stop confusing staging with an older production surface. The visible symptom was that `deploy-fresh` had the restored Astro/staging content, but `humandesignengine.com` still served old legacy static docs content (`Human Design Engine — The Engine Behind Every Chart`).

## Durable lesson

For HDE/Cloudflare Pages cutovers, merging the staging branch into `main` is not enough proof. Verify what Cloudflare Pages is configured to build and serve.

In this incident:

- `origin/main` became an ancestor/superset of `origin/deploy-fresh` via PR merge.
- Cloudflare Pages production still served old content because project `build_config.destination_dir` was `docs` and `build_command` was empty.
- The source code already had the Astro homepage under `src/pages/index.astro`, but production was publishing `docs/index.html`.

## Correct pattern

1. Merge staging source into production source:
   - verify `git merge-base --is-ancestor origin/main origin/deploy-fresh` before opening PR,
   - open/merge PR from `deploy-fresh` to `main` if staging is canonical.
2. Check Cloudflare Pages project config, not just deployment status:
   - `production_branch` should be `main`,
   - `build_config.build_command` should be `npm run build`,
   - `build_config.destination_dir` should be `dist` for Astro/PWP builds.
3. Keep repository config aligned:
   - `wrangler.jsonc` for Pages should include `"pages_build_output_dir": "dist"`,
   - do **not** keep Workers-style `assets.directory` in a Pages config once `pages_build_output_dir` is used; Wrangler Pages validation rejects `assets`.
4. Verify the live production route content, not just HTTP 200:
   - cache-bust the URL,
   - assert new Astro/staging markers are present,
   - assert old legacy docs markers are absent,
   - check representative routes like `/free-human-design-reading-generator/`.

## Useful Cloudflare API shape

When Wrangler auth/environment is noisy, use the Pages API directly with the Pages token:

```bash
curl -sS \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/pages/projects/hd-platform"
```

Patch project build config:

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/pages/projects/hd-platform" \
  --data '{"build_config":{"build_command":"npm run build","destination_dir":"dist","root_dir":""}}'
```

List deployments without Wrangler:

```bash
curl -sS \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/pages/projects/hd-platform/deployments"
```

## Verification markers from the fix

Good production content contained:

- `Human Design Engine — Verifiable calculations, premium reports, and deconditioning tools`
- `menuTrigger`
- `nav-inner`
- `Free Human Design Reading Generator`

Bad old docs content contained:

- `Human Design Engine — The Engine Behind Every Chart`

## Pitfalls

- A successful `main` production deployment can still publish the wrong directory if Pages is set to `docs`.
- A direct Wrangler deploy can temporarily fix production but does not prevent the next Git deployment from reverting unless project build config and repo config are fixed.
- Redacting tokens incorrectly in shell examples can produce Cloudflare 9106/6003 auth noise. The durable fix is to export/use `$CLOUDFLARE_PAGES_API_TOKEN` exactly, not to conclude Wrangler or the API is broken.
