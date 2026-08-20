# Blocker Closeout Pattern — Linear + PR + Ad-hoc Verification — 2026-07-09

## Context

Michael asked to stop items like GRO-3304 and GRO-3366 from surfacing as blockers. Live Linear showed one item already Done and another still In Progress with blocker labels. The fix required both real implementation/merge evidence and tracker cleanup.

## Durable Pattern

When a blocker keeps resurfacing, do not trust digest text or local scratch state. Close the loop in this order:

1. **Live Linear read first**
   - Query the exact issue identifiers.
   - Record current state, labels, parent/child relationships, and acceptance criteria.
   - If the issue is already completed, remove it from local commitment/digest sources rather than rebuilding work.

2. **Implement only the missing acceptance slice**
   - Use the smallest code/docs change that satisfies the issue’s explicit acceptance criteria.
   - Keep broad legacy lint failures out of scope unless they block the targeted change.

3. **Targeted verification + ad-hoc verifier**
   - Run focused tests/lint for changed surfaces.
   - Create a temporary verifier with an OS-safe `/tmp/hermes-verify-*` filename using `tempfile`/`mktemp`.
   - Verify behavior at runtime, not just imports.
   - Clean the temp script/artifacts and explicitly report cleanup.
   - Label this **ad-hoc targeted verification**, not canonical/full-suite green.

4. **Publish from a clean worktree if push fails**
   - If GitHub rejects a push with missing-object/unpack errors, create a clean worktree from `origin/main`, cherry-pick/apply the intended commit, rerun targeted verification there, then push the clean branch.
   - Resolve conflicts by preserving upstream additions and layering only the intended change.

5. **PR body quoting safety**
   - Avoid passing Markdown containing backticks directly inside a shell-quoted `gh pr create --body "..."`; command substitution can execute snippets.
   - Safer pattern: write the PR body to `/tmp/hermes-pr-*.md`, create/edit with `--body-file`, then remove the file.
   - If `gh pr edit` fails due Projects Classic GraphQL deprecation, use `gh api graphql` `updatePullRequest` with the PR node ID.

6. **Tracker cleanup after merge**
   - Merge only after PR checks are clean or the blocker owner accepts the explicit evidence scope.
   - Post evidence comments to the exact Linear issues.
   - Move only the exact evidenced issues to Done.
   - Remove stale blocker-routing labels such as `dispatch:ready`, `agent:peer-review`, or `agent:needs-human-review` when they no longer reflect reality.

## Evidence Shape to Report

```text
PR: <url>
Merge commit: <sha>
Linear: GRO-xxxx Done, blocker labels removed
Focused lint: PASS
Focused tests: PASS
Ad-hoc runtime verifier: PASS, /tmp/hermes-verify-* cleaned
Scope: targeted/ad-hoc verification, not full-suite green
Known repo-level warnings: <if any, clearly marked pre-existing/non-blocking>
```

## Pitfalls

- Do not call a Done Linear issue a blocker just because an old digest listed it.
- Do not leave `dispatch:ready` / review labels on completed issues; they are routing signals and will keep resurfacing.
- Do not let shell quoting execute Markdown backticks when creating PR bodies.
- Do not claim verification if a system nudge says changed paths are still unverified; rerun a `/tmp/hermes-verify-*` script and clean it.
