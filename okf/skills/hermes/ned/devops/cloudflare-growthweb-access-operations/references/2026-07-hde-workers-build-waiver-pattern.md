# HDE PR Workers build failure waiver pattern — 2026-07 demo promotion

Session learning from PR #43-style HDE Cloudflare checks.

## Situation

GitHub showed:

```text
Cloudflare Pages — SUCCESS
Workers Builds: hd-platform — FAILURE
```

The failing Workers check exposed:

- GitHub check run with no annotations.
- Cloudflare Workers build ID in the check summary.
- Cloudflare Workers logs endpoint returning HTTP `204` with no body.
- Workers service metadata only, not actionable build failure text.

At the same time, the Pages deployment for the same commit exposed preview URLs, and the Pages preview routes returned HTTP 200.

## Waiver criteria

Treat the Workers check as a noisy/non-blocking duplicate integration only when all of these are true:

1. Cloudflare Pages check for the same commit succeeds.
2. The Pages preview URL serves the relevant changed route(s), e.g. `/sanctuary-demo/` HTTP 200.
3. The preview contains expected source markers, e.g. POST target `/api/demo/start`, `noindex`, and Telegram/deep-link content where applicable.
4. Local canonical build (`npm run build`) passes.
5. Focused promotion verifier passes (`git diff --check`, Python compile, `systemd-analyze verify`, changed-file secret scan, route smoke checks).
6. GitHub Workers annotations are empty and Cloudflare read-only log endpoint gives no actionable diagnostic body.
7. The production site path is Cloudflare Pages, not the Worker service named in the failed check.

## Reporting

Do not silently ignore the failure. Add a PR comment with:

- GitHub Workers check-run URL/id.
- Cloudflare Workers build ID.
- Pages preview URL and route evidence.
- Local/canonical verification evidence.
- Explicit conclusion: noisy/non-blocking Workers integration for this Pages promotion.

Keep the final report clear: `Pages promotion ready; Worker check waived with evidence; production merge/deploy still requires explicit approval and post-merge gate/timer verification.`

## Useful commands

```bash
gh api repos/mbgulden/hd-platform/commits/<sha>/check-runs \
  --jq '{total_count, check_runs:[.check_runs[] | {id,name,status,conclusion,details_url,html_url,output}]}'

gh api repos/mbgulden/hd-platform/check-runs/<check-run-id>/annotations --jq '.'

curl -sS -i \
  -H "Authorization: Bearer $CLOUDFLARE_PAGES_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_PAGES_ACCOUNT_ID/workers/scripts/hd-platform/builds/<build-id>/logs"
```
