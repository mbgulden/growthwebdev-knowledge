# GRO-4003 blocked PR recovery and state hygiene

Session signal: a previously finalized-but-blocked task had a local evidence branch that could not push during the original pass. In a later cron pass, GitHub push credentials worked again. The correct move was not to rerun the whole task or mark it green; it was to recover the repo-side artifact and keep Linear honest.

## Pattern

When acceptance is blocked but repo-side evidence/work exists on a local `ned/...` branch:

1. Re-read the autonomous task skeleton and the Linear issue/comments.
2. Re-check blocker sources before continuing to call it blocked:
   - OKF integrations under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`
   - `session_search`
   - relevant `.env`/credential files, without printing secrets
3. Recreate or attach a clean worktree for the existing branch.
4. Push the existing `ned/...` branch if credentials now work.
5. Open a PR for the evidence/doc artifact if that improves recoverability/review.
6. Re-run cheap live proof checks that do not require the blocked credential.
7. Post fresh Linear evidence with the PR URL and exact remaining blocker.
8. Unlock any held files.
9. If Linear is `In Review` or `In Progress` while acceptance is still not green, move it back to `Todo` and comment why.

## Pitfall

Do not let a successful push/PR create false completion. A PR for an evidence document is repo recoverability, not acceptance. For Search Console/GSC-style tasks, keep the issue not-green until the live API submission/coverage proof succeeds.

## GRO-4003 concrete evidence

- Branch: `ned/GRO-4003`
- PR opened after push recovered: `https://github.com/mbgulden/hd-platform/pull/46`
- Fresh non-credential live proof:
  - `https://humandesignengine.com/sitemap.xml` HTTP 200, 14,831 bytes, 171 parsed URLs
  - `https://humandesignengine.com/robots.txt` HTTP 200 and advertises the sitemap
- Remaining blocker: scoped OAuth artifact absent at `/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json`; `gcloud auth list --format=json` had no authenticated accounts; API-key-only GSC remained HTTP 401.
- State hygiene: reset Linear to `Todo` because Search Console submission/coverage proof was still blocked.
