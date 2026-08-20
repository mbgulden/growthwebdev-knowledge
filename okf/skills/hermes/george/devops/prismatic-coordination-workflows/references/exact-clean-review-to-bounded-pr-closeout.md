# Exact CLEAN review to bounded PR closeout

Use when a Prismatic assigned-agent candidate has already survived same-task repairs and receives an independent exact-head `CLEAN/PASS`.

## Pattern

1. Treat `CLEAN/PASS` as permission to open a bounded PR only when the governing prompt/policy already allowed `PR if CLEAN`.
2. Before push/PR, reassert local immutability:
   - `git rev-parse HEAD` equals the reviewed commit.
   - `git rev-parse HEAD^{tree}` equals the reviewed tree.
   - merge-base is the expected base.
   - tracked status is clean.
   - diff path count and path list match the contract.
3. Fetch/prune and identify the remote default/base branch from `git remote show origin`; do not guess the base.
4. Check there is no existing PR for the branch before creating one.
5. Write the PR body to a temporary Markdown file and use `gh pr create --body-file`; remove the temp file afterward. This avoids shell quoting/body mangling and keeps secrets out of chat.
6. After PR creation, verify the remote PR, not just local git:
   - PR number/url/state/draft/base/head/ref OID.
   - remote head SHA equals the independently accepted head.
   - file list/count equals the one-path contract.
   - mergeability if GitHub reports it.
   - tracked local status remains clean; separate expected untracked task-control files from PR contents.
7. Only after remote verification, update durable handoff/control state from `review_pending` to `PR_OPEN_AWAITING_SEPARATE_MERGE_AUTHORIZATION`.
8. Run a final `/tmp/hermes-verify-*` ad-hoc verifier after the handoff edit that binds local head/tree, PR remote metadata, handoff markers, health/readback if relevant, and explicit non-claims.

## Required boundaries

Opening the PR does **not** claim merge, deploy, Linear write, cron/timer mutation, production runtime enforcement, or canonical suite green unless those exact actions/proofs also happened.

Suggested final packet fields:

```text
PR=<number/url>
REMOTE_HEAD=<accepted sha>
REMOTE_FILE_COUNT=<n>
TRACKED_STATUS_CLEAN=true
AD_HOC_OR_CANONICAL=ad-hoc targeted post-PR verification
NOT_CLAIMING=canonical suite green, merge, deployment, Linear write, cron/timer mutation, or live schema migration
MARKER=<slice>_PR_OPEN_VERIFIED
```
