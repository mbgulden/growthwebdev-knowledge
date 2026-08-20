# GRO-3989 GA4 Admin OAuth / partial-verification pattern

When Ned receives a Google Analytics / GA4 / GTM / Search Console task, do not jump straight to "blocked" and do not mark green from a known measurement ID alone.

## Durable sequence

1. Read the issue and comments first, then validate lane fit. GA4/GTM/GSC observability work is Ned-relevant when labeled `observability` / workflow-governance.
2. Before claiming missing access, perform the required three-way credential search:
   - OKF integration docs under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`.
   - `session_search` for prior Google/GA4/Admin-auth history.
   - relevant `.env*` files, with values redacted.
3. If API-key access is the only Google credential available, prove the Google-side requirement with a safe probe. Analytics Admin returns HTTP 401 `UNAUTHENTICATED` with the message that API keys are not supported; it requires OAuth bearer credentials asserting a principal.
4. Still produce useful work before finalizing:
   - record the known measurement ID in repo docs;
   - add a reusable verifier script that scans committed files and selected live pages for the expected `G-...` ID;
   - probe the public `https://www.googletagmanager.com/gtag/js?id=<ID>` endpoint;
   - document sampled live coverage and missing pages.
5. Status remains partial / In Review unless Analytics Admin confirms the account/property/web stream and live tag coverage is green or intentionally excluded.

## Concrete evidence shape from GRO-3989

- Recorded HDE GA4 Measurement ID: `G-Q6TPL08VM7`.
- Repo scan found the ID in many committed files, but sampled live coverage was not site-wide.
- Analytics Admin API proof stayed blocked without OAuth scopes `analytics.readonly` / `analytics.edit`.
- The correct result state was `In Review`, not Done.

## GTM child-task variant

For GTM tasks like GRO-3990, the same rule applies: do useful repo-side work before declaring OAuth blocked, but keep the issue partial / In Review until real Tag Manager API + live container proof exists.

Recommended repo artifact shape:

- Add a read-only verifier under `scripts/operations/verify_gtm_container.py` or the current repo's equivalent operations lane.
- Verify all of these without printing credentials:
  - committed `GTM-...` IDs, if any;
  - known GA4 ID coverage such as `G-Q6TPL08VM7`;
  - sampled live production pages for GTM/GA4 snippets;
  - public `https://www.googletagmanager.com/gtag/js?id=<GA4_ID>` returns HTTP 200;
  - Tag Manager accounts API without OAuth returns the expected 401/403, proving API-key/no-auth is insufficient.
- Add a concise `docs/operations/...gtm...verification...md` note with the required green path: OAuth consent, scope verification, account/container lookup or creation, GA4 config tag, conversion events, publish, and live production tag proof.
- Result state remains `partial` / `In Review`; add `agent:needs-human-review` and `requires:human-approval` when the missing step is human Google OAuth consent.

Fresh verification should include `npm run build`, `python3 -m py_compile` for the verifier, the verifier command itself, `git diff --check`, doc/result assertions, and a secret-prefix scan. If the platform repeats the unverified-code nudge, rerun the exact build plus a fresh `/tmp/hermes-verify-*` ad-hoc assertion script; do not rely on the previous run's transcript.

## Post-finalize pitfall

After `finalize_task.sh` prints a successful transition, re-query Linear. On GRO-3989 the script printed `GRO-3989 → In Review`, but the issue had drifted back to `In Progress`; manual `issueUpdate` plus an evidence-refresh comment was required before reporting completion. GRO-3990 repeated the same drift class after finalize/PR creation: the issue was left in `In Progress` until a manual `issueUpdate` restored `In Review`, then human-review labels were added.

If a PR has Cloudflare Pages green but `Workers Builds: hd-platform` red, keep the issue In Review and record the check-run/build ID. Use the Cloudflare Worker diagnostics pattern from `cloudflare-growthweb-access-operations`; do not mark Done just because the repo-side verifier passed.