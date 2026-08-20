# GRO-4001 OG/social redispatch refresh pattern

Session: 2026-07-19 Ned cron redispatch of an already-implemented HD Platform SEO/static task.

## Trigger

A task is redispatched from `Backlog` with `dispatch:ready`, but Linear comments and GitHub already show an implementation branch/PR and prior finalization evidence. For GRO-4001:

- Branch/commit existed: `ned/GRO-4001` at `6f9f6fd`.
- PR existed: `mbgulden/hd-platform#34`.
- Linear had prior finalizer/evidence comments, but had drifted back to `Backlog` and still had `dispatch:ready`.
- Shared `/home/ubuntu/work/hd-platform` checkout was dirty on an unrelated branch, so direct checkout would have risked another agent's work.

## Safe refresh sequence

1. Read the task skeleton and issue details including comments.
2. Verify prior completion signals: branch, PR, commit, comments, and current PR checks.
3. Acquire locks for the branch diff files if using finalize, but do not touch the dirty primary checkout.
4. Create a clean detached worktree from the remote task branch, e.g.:

   ```bash
   git -C /home/ubuntu/work/hd-platform worktree add --detach /tmp/hd-platform-gro4001-refresh-<ts> origin/ned/GRO-4001
   ```

5. Run fresh local verification in that clean worktree:
   - `npm ci`
   - `npm run build`
   - targeted ad-hoc generated-HTML verifier for the durable SEO contract.
6. Run finalize with absolute script path and explicit environment:

   ```bash
   export HOME=/home/ubuntu
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro4001-refresh-<ts> \
   FINALIZE_LOCK_FILES='docs/social-image-strategy.md src/layouts/Layout.astro ...' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4001 ned/GRO-4001 ned
   ```

7. Re-query Linear after finalize. If state is `In Review` but `dispatch:ready` remains, remove only the stale dispatch label with `issueUpdate(labelIds=[...without dispatch:ready...])` and post a concise evidence-refresh comment.
8. Query `comments(first:50)` and sort by `createdAt` to verify the new comment; `comments(last:N)` ordering can be surprising and may omit the newest comments.
9. Unlock leftovers with the same simple-owner shape used to acquire them (`swarm.js unlock <path> ned`) if finalize's repo-qualified unlock transcript leaves locks behind.
10. Remove the temp worktree and update `/tmp/issue-batches/<ISSUE>_RESULT.md`.
11. If the only remaining blocker is an external CI integration mismatch already captured in PR checks, return `[SILENT]` after local/Linear evidence is refreshed.

## Verification contract used

For a site-wide OG/social image strategy, local build success is not enough. Add a generated-HTML verifier that checks representative built pages for:

- `og:image`
- `og:image:secure_url`
- `og:image:alt`
- `twitter:image`
- `twitter:card` = `summary_large_image`
- absolute production image URL

## Caveat

For HD Platform, `Cloudflare Pages` can pass while `Workers Builds: hd-platform` fails due to the known Pages-vs-Workers integration mismatch. Keep Linear `In Review`/partial, not Done/green, until live/social proof or CI is actually green.
