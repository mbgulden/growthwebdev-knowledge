# Ned GRO-3999 — already-implemented PR redispatch refresh

## Trigger

A Linear issue is redispatched with `agent:ned` + `dispatch:ready`, but the comment thread already contains a prior Ned finalization/PR evidence block and the remote branch/PR exists.

Example shape observed on GRO-3999:

- Issue state had drifted back to `Backlog` with `dispatch:ready` still present.
- Prior comments showed PR + implementation evidence.
- `origin/ned/GRO-3999` existed and PR #32 was open.
- No comment indicated out-of-lane/dequeued.

## Safe refresh pattern

1. Read the autonomous task skeleton first.
2. Query Linear including last comments before doing any build work.
3. If prior implementation exists, do not rebuild in the dirty primary worktree. Use a clean detached worktree from the remote branch:
   ```bash
   rm -rf /tmp/hd-platform-gro3999-recheck
   git worktree add --detach /tmp/hd-platform-gro3999-recheck origin/ned/GRO-3999
   ```
4. Verify the existing branch from that worktree. For Astro/HD Engine work, `npm run build` may require a fresh `npm ci` first in a clean worktree; capture the eventual successful command, not the initial missing-dependency failure.
5. Run a deterministic local proof for the issue-specific contract. For sitemap/index-pollution tasks, validate generated `dist/sitemap.xml`, `_redirects`, and generated noindex HTML.
6. Run finalize with absolute script path and explicit env:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro3999-recheck \
   FINALIZE_LOCK_FILES='scripts src public docs' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3999 ned/GRO-3999 ned
   ```
7. Verify Linear state after finalize and remove stale `dispatch:ready` if the redispatch label remains. Leave the issue `In Review`, not Done, when remote checks are still red.
8. After removing `dispatch:ready`, re-query state again. Label cleanup can regress Linear from `In Review` to `In Progress`; if so, explicitly set the state back to the team's `In Review` state and verify a final time. See `references/linear-label-cleanup-state-regression.md`.
9. Re-run `node /home/ubuntu/.antigravity/swarm.js status`; clear simple-shape locks separately if needed.

## Evidence to preserve locally

Write `/tmp/issue-batches/GRO-XXXX_RESULT.md` with:

- remote branch commit verified
- PR URL and remote check state
- local build/proof commands and result
- Linear state/label cleanup
- lock cleanup result

## Issue-specific local proof notes

For GRO-3999, the generated affiliate dashboard file is `dist/affiliates/dashboard.html`, not necessarily `dist/affiliates/dashboard/index.html`. If a noindex verifier fails, inspect generated paths before declaring the proof red. The durable assertion is that the generated dashboard HTML contains `noindex, nofollow` and blocked/private-ish URLs are absent from `dist/sitemap.xml`.

Expected proof shape:

```text
LOCAL_PROOF_PASS
sitemap_url_count=167
blocked_sitemap_entries=0
required_redirects_present=/affiliates /affiliates/signup.html 301,/affiliates.html /affiliates/signup.html 301,/affiliates/ /affiliates/signup.html 301,/landing-index.html / 301
affiliates_html_targets_signup=true
dashboard_noindex_nofollow=true
```

## Pitfalls

`finalize_task.sh` may unlock repo-qualified default lanes (`prismatic-engine`) while any simple/repo-specific locks acquired for verification remain. Always check swarm status and unlock leftovers using the same shape used to acquire them.

Removing stale Linear labels after finalize may unexpectedly alter state. Always verify final state after label cleanup, and reassert `In Review` when checks are still pending/red.
