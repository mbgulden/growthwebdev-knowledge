# AOT PR Runway: Safe Successors and Credential Shadowing (2026-07-23)

## When an old PR is stale, conflicted, or method-invalid

1. Review the PR against current `main`; do not merge just because its original CI was green.
2. Use a clean worktree from `origin/main` and compare conflicts/overlap before choosing disposition.
3. If the desired outcome is valid but the implementation violates the HTML bulk-edit rule (for example regex discovery/rewrite), create a **successor PR** from current `main` rather than rebasing the old branch.
4. Preserve the bounded source map/acceptance criteria, but rebuild discovery with `HTMLParser`; retain non-empty existing `alt` text and change only approved empty/missing values.
5. Prove exact behavior with a fresh `/tmp/hermes-verify-*` verifier: parser implementation marker, targeted content count, no blank target values, idempotent second dry/check run, and `git diff --check`.
6. Merge only after all PR checks pass, wait for Pages propagation, and verify a real production content marker.
7. Close the predecessor as superseded only after successor merge/deploy; leave an evidence comment. If a current-main inspection shows zero desired visible changes, close the conflicted predecessor as no-longer-actionable rather than forcing an empty rebase.

## GitHub credential-health pitfall

A valid `GITHUB_PAT_KEY` or GitHub CLI host token can coexist with an expired `GH_TOKEN`; GitHub CLI prioritizes `GH_TOKEN`, producing false-looking auth failures. Before declaring GitHub blocked, test candidates without printing secrets and run GitHub commands in a process environment that removes stale `GH_TOKEN`/`GITHUB_TOKEN` and sets `GH_TOKEN` from the validated credential. Never copy credentials into logs, PR bodies, or chat.

## Useful verification boundaries

Focused parser/verifier checks are **ad-hoc targeted**, not a canonical suite or production proof. State those boundaries explicitly. Production proof requires the live apex or Pages mirror to return a specific shipped marker after deployment.