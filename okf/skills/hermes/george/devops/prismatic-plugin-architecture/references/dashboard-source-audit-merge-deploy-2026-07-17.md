# Dashboard source-audit digest + merge/deploy closure pattern — 2026-07-17

Session lesson from Prismatic dashboard reconnect work.

## User-facing report shape

A comprehensive branch/repo/worktree audit can be too large to be useful. When Michael says a report is a “huge blob,” do not defend it or add more bulk. Produce a small execution packet first, with the full audit as appendix/reference.

Recommended pair:

1. **Full audit artifact** — exhaustive source list, ranked rubric, branch/file evidence.
2. **Fred cheat sheet** — 1–2 pages / ~100 lines:
   - do-first sequence
   - A/B/C/D buckets
   - exact source paths
   - first files to inspect
   - exact commands
   - red flags
   - pointer back to the full audit

A/B/C/D source buckets used successfully:

- **A** — inspect first / likely dashboard preservation value.
- **B** — governance/workflow source to mine after shell is mapped.
- **C** — runtime/canonical comparison anchor; diff against, do not blindly overwrite.
- **D** — archive/cleanup fallback only.

## Dashboard source-audit closeout pattern

When Fred reports a source-audit PR:

1. Verify PR metadata and CI with GitHub.
2. Fetch the PR ref and inspect changed files.
3. Verify doc-only claims when applicable.
4. Verify anchor equality with byte comparisons for key files, e.g.:
   - `prismatic/gateway/templates/dashboard.html`
   - `prismatic/gateway/server.py`
5. Verify candidate source paths/files exist.
6. Use a fresh `/tmp/hermes-verify-*` script and remove it afterward.
7. Report as ad-hoc targeted verification, not canonical suite green.

## Merge/deploy closure pattern for dashboard PRs

When Michael explicitly asks to merge/deploy:

1. Re-check PR state, mergeability, changed files, and CI before merging.
2. Merge in dependency order. If PR B depends on PR A’s docs/branch state, merge A first.
3. If `gh pr merge --delete-branch` fails because a local branch is checked out in another worktree, verify whether the PR actually merged before retrying. GitHub may have merged but failed local branch deletion.
4. If the next PR becomes temporarily unmergeable because main advanced, update the PR branch from `origin/main`, rerun targeted verification, push, then merge.
5. If Git push over HTTPS cannot read credentials, run `gh auth setup-git` and retry rather than switching remotes blindly.
6. Deploy by updating the durable runtime checkout, not the mutable dev checkout:
   - `cd /home/ubuntu/.prismatic/runtime/prismatic-engine`
   - `git fetch origin --quiet`
   - `git reset --hard origin/main`
   - run targeted compile/smoke checks
   - restart services intentionally
7. Verify local routes before public routes.
8. Browser-click the relevant dashboard tab for operator proof, and check console errors.
9. If a service restart fails due to an auxiliary path, fix the durable service dependency path/symlink and re-run service status; do not claim deploy until services are active.

## Proof packet used successfully

```text
COMMAND=runtime checkout update + service restart + local/public route proof + browser proof
RESULT=PASS
LOG=/tmp/<agent>-postdeploy.log
SCOPE=merged main commit, runtime checkout, gateway/dispatcher services, dashboard/resources routes
AD_HOC_OR_CANONICAL=ad-hoc targeted production deploy proof
NOT_CLAIMING=canonical full-suite green, public POST mutation proof
MARKER=<FEATURE>_DEPLOYED_OK
```

## Next-prompt pattern after dashboard runway closes

After dashboard reconnect/source-map/resources slices are merged and deployed, do not keep sending Fred into dashboard source mining by inertia. Move to the next named workflow gap if no dashboard blocker remains. In this session the correct next prompt was `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`, explicitly bounded as:

```text
AGY completed work
→ validate handoff/result packet
→ lane/scope check
→ proof check
→ classify merge-ready / clean-rebuild / blocked / superseded / manual-review
→ expose status in dashboard/API/Linear
→ do not auto-merge yet
```
