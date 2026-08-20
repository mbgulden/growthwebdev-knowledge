# Agent Memory OKF Lifecycle Pattern (2026-07)

Use when a memory pruning run creates or updates an OKF standard that profile memories will reference.

## Lesson

Do not leave the OKF memory standard only in a temp worktree or open PR. Profile memories may immediately reference the canonical path, so the OKF document must be made durable on `origin/main` before declaring the memory governance layer stable.

## Sequence

1. Create/update the class-level memory skill first if the pruning pattern is reusable.
2. Write or update the OKF standard in a clean worktree from `origin/main`.
3. Verify frontmatter, required sections, and index links with a focused `/tmp/hermes-verify-*` script.
4. Push/open/merge the OKF PR if scope is narrow and clean.
5. Verify with `git show origin/main:<okf-path>` after merge.
6. Remove only the temp worktree/branch created for that merged OKF standard.
7. If broader OKF cleanup remains, create a separate SSOT/source manifest with `cleanup_executed: false` rather than deleting stray refs.

## Memory-specific pitfall

If memories say `OKF: okf/standards/agent-memory-governance.md`, that path must resolve from `origin/main`, not just a dirty local checkout. Otherwise future agents inherit a broken breadcrumb.
