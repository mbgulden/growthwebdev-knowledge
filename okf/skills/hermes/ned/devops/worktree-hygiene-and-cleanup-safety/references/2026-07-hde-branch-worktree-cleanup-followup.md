# HDE branch/worktree cleanup follow-up — 2026-07

Use this as the branch-cleanup companion to the HDE workspace cleanup pattern.

## Pattern

1. Inventory before mutation:
   - `git status --short --branch`
   - `git worktree list --porcelain`
   - local branches with upstream/date/subject
   - remote branches merged to the intended base
2. Remove only clean worktrees whose branch is already pushed/merged and whose status is clean.
3. For merged branch cleanup:
   - dry-run remote branch deletion first (`git push --dry-run origin --delete ...`)
   - delete local branches only if `merge-base --is-ancestor` proves they are merged into the intended base (`origin/deploy-fresh` or `origin/main`)
   - delete remote review branches only when the user explicitly asked to clean branches, the PR/branch is already merged, and the dry-run proves the exact deletion set
4. Preserve dirty or unmerged branches. A current branch with one tracked modification is not trash; report it as preserved/manual-review.
5. Archive generated proof artifacts and runtime backups outside the live checkout rather than deleting them silently.
6. Verify after cleanup:
   - worktree list shows only intended canonical worktrees
   - removed temp path no longer exists
   - staging/runtime checkout is clean
   - remote branch checks return gone for deleted branch names
   - archive/manifest path exists

## Pitfalls

- Do not delete older Ned branches merely because they are old. If not mechanically merged, keep them.
- Do not clean a current dirty feature branch while doing branch/worktree hygiene; name the remaining dirty path instead.
- Do not leave staging runtime `dist.backup-*` directories in the live checkout after they have served their rollback purpose; archive them with a manifest.
