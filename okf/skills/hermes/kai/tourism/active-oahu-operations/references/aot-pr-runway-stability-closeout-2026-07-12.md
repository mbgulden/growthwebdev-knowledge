# AOT PR runway + stability closeout — 2026-07-12

## Context

When Michael asks to make sure all PRs/tasks are completed and ActiveOahuTours.com is stable, treat it as an operational closeout, not a reassurance prompt. Gather live external state, resolve actionable PRs if safe, then report the difference between **current runway clear** and **longer backlog remains**.

## Closeout workflow

1. **Check both AOT repos for open PRs.**
   - `mbgulden/active-oahu-tours-mirror`
   - `mbgulden/active-oahu-business`
   - Do not claim clear runway if either has an open PR.

2. **Inspect any open PR before merging.**
   - `gh pr view <n> --json state,isDraft,mergeable,mergeStateStatus,statusCheckRollup,files,title,url`
   - Even if GitHub checks are green, run local focused checks for the actual changed behavior.
   - Run `git diff --check` locally; drift/governance checks may not catch whitespace or content-specific issues.

3. **If a clean open PR has a small fixable issue, fix it before merge.**
   Example from GRO-578:
   - PR was green/mergeable.
   - Local review caught trailing whitespace and compact/domain brand text `ActiveOahu.com` becoming `ActiveOʻahu.com`.
   - Fix preserved `ActiveOahu`/`ActiveOʻahu` via a compact-brand placeholder in the HTMLParser replacement script.
   - Rerun idempotence and focused verifier before pushing.

4. **Use exact ad-hoc verification for changed behavior.**
   For text/HTML cleanup PRs, a useful `/tmp/hermes-verify-*` verifier should assert:
   - changed script compiles,
   - rerun is idempotent (`changed_files=0 changed_text_nodes=0`),
   - all target HTML files parse,
   - expected terms are present,
   - known malformed outputs are absent,
   - `git diff --check` passes,
   - only expected tracked paths are dirty.

5. **Wait for PR checks after pushing fixes, then merge.**
   - Poll until checks complete and PR is mergeable/clean.
   - Merge only after fresh checks and local verification both pass.

6. **Post-merge health pass.**
   - Pull primary repo `main` with `--ff-only`.
   - Verify `HEAD` equals `origin/main` using separate `git rev-parse --short HEAD` and `git rev-parse --short origin/main` commands. Avoid `git rev-parse --short HEAD origin/main` because it errors with “Needed a single revision”.
   - Confirm both AOT repos have `[]` open PRs.
   - Check apex, `www` canonical redirect, Pages mirror, and representative key routes.
   - Run a rendered homepage smoke test for status 200, nav/footer presence, booking links, first-party errors, failed requests, and heading font sample.

7. **Linear: distinguish current runway from backlog.**
   - Verify recently touched/Golden Thread issues are Done.
   - Query open AOT-titled issues and report them as backlog if they are not blocking current stability.
   - Do not imply backlog is zero unless Linear actually shows zero open issues.

## GRO-578 content-specific pitfall

For Hawaiian diacritical passes, preserve legal/brand phrases separately from place names:

- Preserve `Active Oahu` as the brand/legal phrase.
- Preserve compact/domain brand strings like `ActiveOahu.com` and `activeoahu.com` without inserting ʻokina.
- Preserve the English adjective `Hawaiian`; do not turn it into `Hawaiʻian`.
- Diacritic targets are place names: `Hawaiʻi`, `Oʻahu`, `Kāneʻohe`, `Mokoliʻi`, etc.

## Reporting pattern

Lead with a direct answer:

- “Yes — PR runway is clear, current execution tasks are closed, and the site is stable.”
- Then show receipts: open PR counts, merged PR, Linear done items, live endpoints, rendered smoke check, repo hygiene.
- Add a caveat table for remaining backlog and state that it is roadmap work, not a current site-stability blocker.

## Pitfalls

- Do not let a green GitHub PR bypass local content review.
- Do not rely on session memory for live PR/Linear/site state.
- Do not call the site “fully complete” when the backlog remains; call the runway clear and trajectory strong.
- Do not summarize a prior verifier when Hermes asks for fresh evidence; create a new `/tmp/hermes-verify-*` file and remove it after running.
