---
name: branch-deletion-approval
description: No branch, worktree, or git ref deletion without explicit Michael approval. This is the OKF/Prismatic governance rule. Source manifests before cleanup, durable evidence, clear exits.
---

# branch-deletion-approval

## The rule

Any deletion of:
- A git branch (local or remote).
- A git worktree.
- A git ref (tag, namespace).
- A branch-protection rule.
- A CI/CD pipeline or deploy hook.

Requires Michael's explicit approval **before** the deletion.

## Why this is a hard rule

Branches and refs are durable evidence. The OKF/Prismatic governance requires "source manifests before cleanup" — meaning before anything is deleted, there's a manifest of what existed and where it lives now. A branch deletion without a manifest is a hole in the durable evidence chain.

## The procedure before any deletion

1. **Inventory**: list what would be deleted (branches, refs, worktrees, files).
2. **Manifest**: write a manifest file (`deletion-manifest-<date>.md` or similar) listing each item, where its content lives now (preserved branch? merged to main? backed up to okf/?), and the reason for deletion.
3. **Ask Michael**: present the manifest and the deletion plan.
4. **Wait for approval**: do not delete until Michael says "yes, delete".
5. **Execute the deletion** and update the manifest with the deletion timestamp.

## What this is NOT

- A ban on deletion. Branches and refs can be deleted; the rule is "approval + manifest", not "never delete".
- A ban on cleanup. Old branches should be cleaned up; just with a manifest.

## Anti-patterns

- "The branch was stale so I deleted it." (No manifest, no approval.)
- "The work was merged so the branch is safe to delete." (Merge ≠ deletion; manifest first.)
- "I cleaned up the worktree locally." (Local cleanup of worktrees is the same rule.)

## Verification

Every deletion has a corresponding manifest file and a corresponding approval from Michael. The manifest is durable (in okf/ or pinned) and references what existed and where it lives now.
