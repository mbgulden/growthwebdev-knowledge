# OKF SSOT + Agent Memory Reconciliation Pattern (2026-07)

Use when Michael asks to make OKF a single source of truth across stray branches/worktrees, especially after a narrow OKF standard was created in a temporary worktree.

## Core pattern

1. **Pick one canonical family first.** Start with the named family, not the whole OKF universe. In this session that was `okf/standards/agent-memory-governance.md`.
2. **Treat `origin/main` as canonical.** Dirty local hub checkouts and old PR branches are source candidates, not truth.
3. **Verify PR scope before merge.** Read PR files/commits and confirm the PR contains only the intended canonical files.
4. **Merge narrow family to `origin/main`.** After merge, verify with `git show origin/main:<path>` rather than trusting a local dirty checkout.
5. **Clean only temp artifacts created for the merged family.** It is safe to remove a temporary worktree/branch created in-session after remote readback proves the content is on `origin/main`. Do not clean unrelated branches/worktrees.
6. **Create a durable SSOT control report.** Land an OKF report that records canonical source, merged PRs, cleanup policy, remaining refs, and the next family.
7. **Inventory all remaining sources.** Generate a manifest of local/remote branches, worktrees, open PRs, and dirty/untracked OKF paths. Classify, but do not delete.
8. **For dirty primary worktrees, create a source manifest before promotion.** Classify each path as `promote`, `archive`, `duplicate`, `unsafe/private`, or `noise`; then promote selected docs through a clean worktree from `origin/main`.

## Safety boundaries

- `cleanup_executed: false` until content has been promoted/archived/queued and Michael approves cleanup.
- Never bulk-merge a dirty OKF branch that mixes reports, plugin mirrors, artifacts, indexes, and transient files.
- Old PRs with conflicts are extraction sources; use `git show`/diffs rather than checking them out over canonical trees.
- External PDFs/emails are source candidates. Extract and classify them, but do not publish raw headers/recipient addresses or private details in public OKF.

## Good verification packet

Use a focused `/tmp/hermes-verify-*` script that checks:

- canonical docs exist on `origin/main` using `git show origin/main:<path>`;
- indexes link to the canonical docs;
- PRs are merged and merge commits exist;
- temp worktrees/branches created during the run are absent;
- cleanup manifests explicitly say `cleanup_executed: false` for unrelated refs;
- verifier cleaned itself up.

Report as ad hoc targeted OKF verification only, not full docs-suite green.

## Artifacts from the originating session

- Agent Memory standard: `okf/standards/agent-memory-governance.md`
- SSOT report: `okf/reports/okf-ssot-reconciliation-2026-07-18.md`
- Source map examples: `/tmp/okf-ssot-full-inventory.json`, `/tmp/okf-hde-cron-source-manifest.json`
