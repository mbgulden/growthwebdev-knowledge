# Verifier freshness after RESULT/local evidence writes

When a cron task writes or refreshes local evidence after running the canonical verifier, the supervising verifier may treat the prior build/test output as stale. This can happen even when the post-verification write is outside the repo, such as `/tmp/issue-batches/<ISSUE>_RESULT.md`.

## Pattern

1. Run the normal canonical verification command after code/doc edits, e.g. `npm run build` for HD Platform.
2. Finalize, push, query Linear/PR/locks.
3. If you then write or update local evidence (`*_RESULT.md`, audit JSON/MD, verifier summaries), rerun the canonical verification command from the clean task worktree before final response.
4. Report the fresh post-write command and output summary. Do not rely on the earlier successful command; the detector keys on freshness after the last write.

## Concrete trigger

A GRO-3992 redispatch refresh updated docs, ran `npm run build`, finalized/pushed, then refreshed `/tmp/issue-batches/GRO-3992_RESULT.md`. The system marked verification stale because the RESULT write happened after the build. Rerunning `cd /tmp/hd-platform-gro3992-cron-refresh && npm run build` produced fresh passing evidence: Astro built 10 pages and route-complete preserved 228 legacy files, generated 171 sitemap routes, 529 redirects, 297 redirect pages, synced 4 aliases, and normalized 79 built HTML files.

## Rule of thumb

If the last operation was a write, the next operation should usually be the relevant verifier before claiming completion. Servers remain unimpressed by chronology excuses.