# GRO-4003 Search Console ownership-refresh pattern

When a Search Console sitemap task is redispatched after earlier OAuth blockers, do not stop at the old blocker text. Re-probe every available Google credential source, including Application Default Credentials, before keeping the task blocked.

## Pattern

1. Re-read Linear comments and the local result file first; decide whether this is a blocked refresh, not a fresh implementation.
2. Run the mandatory blocker search before saying blocked:
   - OKF integration docs under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`.
   - `session_search` for the issue ID, Search Console, GSC, and OAuth artifact names.
   - relevant `.env*` and Google credential files, redacting values.
3. If ADC exists, try refreshing it and include the quota project header when calling Search Console:
   - refresh token from `~/.config/gcloud/application_default_credentials.json`;
   - pass `x-goog-user-project: <quota_project_id>`.
   Without the quota-project header, Search Console may return a misleading 403 about local ADC / quota project even when the token is otherwise usable.
4. Use `sites.list` to distinguish credential failure from property-ownership failure.
5. If the property is absent, `sites.add` may return HTTP 204 and create a URL-prefix property as `siteUnverifiedUser`; this is progress, but **not** enough for sitemap submission or URL Inspection.
6. Re-run the actual acceptance probes:
   - sitemap submit (`PUT .../sitemaps/...`);
   - sitemap list (`GET .../sitemaps`);
   - URL Inspection API for the homepage;
   - live homepage scan for existing `google-site-verification` meta tag;
   - optional Site Verification token request if scopes permit.
7. If submit/list/inspection return 403 because the principal is only `siteUnverifiedUser`, keep the issue not green. The blocker is now Search Console ownership/full permission, not raw OAuth refresh.
8. Update the repo evidence doc and local RESULT with the refined blocker, commit/push if changed, run `finalize_task.sh` per the skeleton, then immediately restore `Todo` + human-review labels when acceptance still is not green. Query Linear afterward.
9. Run the canonical build after any repo doc change (`npm run build` for HD Platform). If the clean worktree lacks dependencies, run the install from the lockfile (`npm ci`) and rerun the build; capture the passing rerun, not just the initial missing-binary failure.

## Evidence shape

Record these without secrets:

- ADC refresh HTTP status and scopes.
- `sites.list` result category: absent / owner / `siteUnverifiedUser`.
- `sites.add` HTTP 204 if it succeeded.
- sitemap submit/list HTTP status and Google error message.
- URL Inspection HTTP status and error message.
- live sitemap/robots HTTP status, bytes, URL count, and hash.
- build command and result.

## Linear state rule

If `finalize_task.sh` moves the issue to `In Review` but the acceptance proof is blocked on Search Console ownership, manually move it back to `Todo` and add `agent:needs-human-review` / `requires:human-approval` so the scanner does not present it as green work. Post a concise blocker-refresh comment with the new proof and the exact human action required.