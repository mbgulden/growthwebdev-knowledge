# AOT Golden Thread Execution Notes — 2026-07-09

Use this as the session-specific playbook for turning the Golden Path plan into executed Linear/GitHub/Cloudflare progress.

## Golden Path Linear structure that worked

The effective structure was five parent Linear issues with child tasks:

1. `AOT Golden Path 01 — Clean Board & PR Runway`
2. `AOT Golden Path 02 — Clean Site Foundation`
3. `AOT Golden Path 03 — Booking & Mobile Conversion`
4. `AOT Golden Path 04 — Compounding SEO Content Engine`
5. `AOT Golden Path 05 — Measurement & Operating Cadence`

Best sequencing:

1. Finish the weekly status/review child first if Michael explicitly asks for a golden-thread update.
2. Clear PR duplication and stale Linear state before starting more implementation.
3. Close parent epics only after every child is completed with evidence.
4. Move from Clean Board → Clean Site Foundation → Booking/Mobile → SEO compounding.

## Linear creation / rate-limit pattern

When Linear rate-limits while creating many parent/child issues:

- Do not claim tasks were created.
- Create a one-shot retry job after the rate-limit window only if Michael has asked for the plan to be created and the prompt is fully self-contained.
- On retry, search exact parent titles before creating anything to avoid duplicates.
- Verify parent/child relationships after creation with `children { nodes { identifier title state } }`.

## PR runway reconciliation pattern

For duplicate PRs touching the same file/issue:

1. Inspect both PRs live (`gh pr view <n> --json state,mergeable,mergeStateStatus,statusCheckRollup,files,commits,url`).
2. Identify the newer/more complete PR by commits and verification evidence.
3. Comment on the superseded PR, then close it.
4. Merge the current PR only after checks are green/clean.
5. Verify post-merge on GitHub, Cloudflare Pages production deployment, and production URLs.
6. Update the child issue with exact evidence and mark Done.

In this session: PR #60 was closed as superseded by PR #61; PR #61 was merged and `/llms.txt` was verified live after cache purge.

## Cloudflare Pages production verification pattern

Use the Cloudflare API with AOT email/API key when Pages token is not valid for the project:

- `CLOUDFLARE_AOT_EMAIL`
- `CLOUDFLARE_AOT_API_KEY`
- `CLOUDFLARE_AOT_ACCOUNT_ID`
- `CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS`

Useful endpoint:

```text
GET /client/v4/accounts/{account_id}/pages/projects/active-oahu-tours-mirror
```

Verify:

- `source.config.production_branch == main`
- `build_config.destination_dir == site`
- latest/canonical deployment trigger commit hash equals the GitHub `main` SHA
- latest stage status is `success`

If production/mirror returns stale content after merge:

1. Purge exact URLs through Cloudflare cache API.
2. Re-fetch with a cache-busting query param and `Cache-Control: no-cache`.
3. Verify content markers, not just HTTP status.

## Ad-hoc verification repeats

If Hermes repeats the “edited code but no fresh verification evidence” system prompt after verification was already run, run a brand-new `/tmp/hermes-verify-*` verifier anyway. Do not argue that it was already verified.

The fresh verifier should:

- be created with Python `tempfile.mkstemp` / `NamedTemporaryFile` under `/tmp` and prefix `hermes-verify-`
- target the exact changed file path named by the system prompt
- assert the specific old behavior is absent and new behavior is present
- check local file targets where applicable
- optionally verify production reflects the merged behavior with cache busting
- clean up the verifier and print `AD_HOC_VERIFY_PASS`

For the GRO-3637 stylesheet prompt, the verifier checked:

- local changed guide page exists
- target CSS file exists
- exactly two corrected `/wp-content/themes/activeoahu/css/style.css` refs
- no old `/wp-content/themes/activeoahu/style.css` hrefs locally
- all stylesheet hrefs resolve locally
- `git grep` finds no old tracked `site/` refs
- production page returns 200 and has corrected refs only

## Clean Site Foundation examples

Two small but high-value clean-site fixes completed after runway cleanup:

- GRO-3637: bad guide stylesheet references were changed from `/wp-content/themes/activeoahu/style.css` to `/wp-content/themes/activeoahu/css/style.css`, then verified locally, via PR checks, Cloudflare deployment, cache purge, and production fetch.
- GRO-3634: stale skip links pointing to `/ja/author/mbgulden/index#content` were changed to same-page `#content` links where pages had local `id="content"` targets. The Japanese author page itself remained intact.

## Reporting shape Michael responded well to

After executing a chain, report:

- table of issues completed
- GitHub PR actions taken
- production verification summary
- current Golden Thread board status
- remaining next paddle strokes

Keep it concise but evidence-backed. Michael asked to “just finish” and then “do the next suggested steps,” so continue autonomously through the ordered task list until a real blocker or risky irreversible action appears.