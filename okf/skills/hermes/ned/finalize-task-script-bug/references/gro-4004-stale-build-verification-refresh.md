# GRO-4004 stale build verification refresh

Session pattern: after a task was finalized and summarized, the verification detector rejected the evidence as `unverified`/`stale` even though a prior `npm run build` had passed. The correct recovery was to rerun the exact canonical command requested by the detector from the task worktree and report the fresh output, not argue from the previous run.

## Durable lesson

When a post-response verifier asks for fresh evidence:

1. Rerun the exact requested command from the changed worktree (`npm run build` in this case).
2. If the first run fails because dependencies are absent in a fresh worktree (`astro: not found`), install dependencies (`npm install`) and rerun before declaring a code blocker.
3. Treat the rerun output as the authoritative evidence, even when it duplicates a previous passing run.
4. If only local result/evidence files change after finalization, update the result file and Linear evidence comment; do not create an unnecessary code commit when the tracked task branch remains clean.
5. Final reply should summarize the fresh pass with concrete counts from the latest output.

## Concrete passing evidence shape

For the HD Platform Astro build, a healthy run looked like:

```text
npm run build: PASS
Astro built 10 page(s)
postbuild route-complete preserved legacy files, generated sitemap routes and redirects, normalized built HTML files, and skipped known directory collisions.
```

The important point is not those exact counts; it is that the build and postbuild both completed in the latest run.