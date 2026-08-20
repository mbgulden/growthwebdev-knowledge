# Worktree Preservation and Cleanup Safety

Use this contract for every Prismatic worktree audit, janitor, archive, or cleanup action.

> Work is disposable only when Git evidence mechanically proves it is safe to remove. Ambiguity means preserve and review.

## Automatic-removal gates

Automatic removal is permitted only when every gate passes:

1. The path is not the canonical checkout or durable runtime checkout.
2. There are no unmerged or conflicted paths.
3. `git status --short` is clean.
4. The worktree head is already an ancestor of the configured merged base.
5. The worktree exceeds the explicit stale threshold.
6. A pre-mutation manifest names the exact path, head, base, classification, and reasons.
7. No active producer, supervisor, process, or open file owns the path.
8. No retained verification receipt, task lease, or deployment binds to that checkout.

If any gate fails, classify the worktree as `keep` or `manual-review`; never downgrade uncertainty into deletion.

## Dirty-work policy

Dirty work must be protected by implementation, not prompt convention:

- Never clean/reset before inventory.
- Never use `git add .` for checkpointing.
- Inspect tracked changes and untracked sizes.
- Exclude secret-bearing backups, runtime state, caches, and generated output.
- Stage only intentional paths.
- Run staged whitespace and secret scans.
- Checkpoint on an agent-owned branch.
- If lane policy blocks a push, preserve a local Git bundle and report the blocked paths rather than forcing publication.
- Cron and ordinary `--apply` modes must never delete dirty work.
- Destructive dirty cleanup requires a second explicit exact confirmation token from a generated manifest and archival first.

## Manifest contract

Every cleanup manifest must include:

- repository and configured base;
- creation timestamp and dry-run/apply mode;
- exact remove candidates;
- exact preserved/manual-review entries;
- branch/head/tree identities;
- dirty/conflict state;
- active process/lease/receipt/deployment ownership;
- safety class and reasons;
- any explicit destructive confirmation token.

Useful but under-proven work receives `preserve-needs-proof`/`proof_gaps`, never a delete signal.

## Verification

Before and after mutation, verify:

1. complete worktree inventory;
2. branch reachability and merge ancestry;
3. protected canonical/runtime paths;
4. active process ownership;
5. manifest-to-action equality;
6. remaining worktrees;
7. archived bundles/manifests are readable.

Cleanup is not complete until the post-action inventory and preserved evidence are read back.
