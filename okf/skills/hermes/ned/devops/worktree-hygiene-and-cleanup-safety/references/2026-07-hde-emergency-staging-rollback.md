# HDE emergency staging rollback pattern — 2026-07-17

## When this applies

Use this when Michael reports that staging was visually/content-regressed by a recent branch or agent run and asks to roll back the last few hours without losing the offending work.

## Proven rollback shape

1. **Identify the regression window mechanically.**
   - `git log --since='4 hours ago' --oneline --decorate --all --date=iso`
   - For deploy branches, inspect recent merge commits with `git show --stat --summary <merge>`.
   - In the incident, the bad HDE staging state came from two `deploy-fresh` merge commits: PR #6 / `81a07f6` and PR #7 / `2aae296`.
2. **Do not rewrite the deploy branch.**
   - Create a new Ned rollback branch from the current deploy branch.
   - Revert the bad merge commits with `git revert -m 1`.
   - Squash/reset the two reverts into one clean rollback commit if helpful for review history.
3. **Prove the rollback restores the pre-regression tree.**
   - Compare against the last known-good parent: `git diff --quiet <known-good>..HEAD`.
   - Run the project verifier (`npm run build`, then the PWP verifier when available).
4. **Push through the normal branch/PR path.**
   - Keep the bad branch and commits available for later forensic review.
   - Merge a rollback PR instead of force-pushing or deleting history.
5. **Verify the deployment surface that users actually hit.**
   - Cloudflare Pages may deploy a new preview for the rollback branch and for the merged deploy branch, but `staging.humandesignengine.com` may still be served from the local staging checkout/`dist` behind nginx/tunnel.
   - Compare live response content against the preview using quick text probes for known bad/good markers.
6. **If live staging is local `dist`, back it up then rsync the verified rollback build.**
   - `cp -a dist dist.backup-bad-shell-<timestamp>` before mutation.
   - `rsync -a --delete <verified-rollback>/dist/ <live-staging>/dist/`.
   - Re-fetch the live URL and probe for regression markers.

## Verification markers from this incident

- Bad shell/content marker: homepage title `Human Design Engine — The Engine Behind Every Chart` with light-theme variables such as `--navy-deep: #FAF7F0`.
- Rollback preview marker: generated Astro homepage with `menuTrigger` and `nav-inner`, and no legacy homepage title.
- Full verifier result: `npm run pwp:verify` passed build, visual, a11y, flows, lighthouse, and link checks after rollback.

## Pitfalls

- Do not assume Cloudflare preview freshness means the human-facing staging hostname changed. Check the actual hostname.
- Do not destroy the bad state before preserving it; back up runtime `dist` and leave the bad branch/commits intact.
- Do not stop at a PR if Michael is reporting a live staging outage. If the safe path is obvious and reversible, restore the live staging runtime from a verified build.
- Do not claim a rollback is complete until the deployed/live URL is fetched and checked for the specific bad markers Michael reported.
