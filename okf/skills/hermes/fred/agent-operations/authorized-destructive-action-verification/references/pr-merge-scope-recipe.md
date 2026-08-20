# PR-Merge Scope Verification Recipe

Concrete commands and decision logic for verifying that an authorized PR merge matches the operator's authorized scope. Companion to `authorized-destructive-action-verification`.

## The case study (2026-07-31)

Operator authorized: "do the merge if you don't make a mess" (referring to PR #382, `feature/gro-4188-evidence-recaps`).

Pre-execution discovery:
- PR #382 has 4 commits (the visible scope)
- Branch HEAD has 351 commits not in `origin/main`
- `origin/main` has 87 commits not in HEAD (branch divergence)
- Neither branch is an ancestor of the other (`git merge-base --is-ancestor` returns NO both ways)

The "small PR" was sitting on top of a 351-commit divergent branch. Operator's "don't make a mess" authorized 4 commits, not 351.

Result: held, surfaced the gap, three options offered, no execution.

## The recipe (memorize this)

```bash
# Step 1: identify the PR's own commits (the authorized scope)
git diff <pr-base-sha>..HEAD --stat
# Example: git diff d7e21566..c09761ed --stat

# Step 2: identify the cumulative divergence (the actual scope)
git diff origin/main..HEAD --stat

# Step 3: count divergence in both directions
git rev-list --count origin/main..HEAD       # PR not in main
git rev-list --count HEAD..origin/main       # main not in PR

# Step 4: check ancestry — is one branch an ancestor of the other?
git merge-base --is-ancestor origin/main HEAD && echo "main ⊆ HEAD" || echo "main NOT ⊆ HEAD"
git merge-base --is-ancestor HEAD origin/main && echo "HEAD ⊆ main" || echo "HEAD NOT ⊆ main"
# If both NO: branches diverged. Actual scope > PR scope.
```

## Decision matrix

| Authorized scope | Actual scope | Action |
|---|---|---|
| PR commits | PR commits ⊆ main | Execute |
| PR commits | PR commits + divergence | **Hold** — divergence not authorized |
| "Merge X" | X = 1 file, 5 lines | Execute |
| "Merge X" | X = 1 file, 5000 lines | Hold — confirm scope |
| Force-push branch | branch is 1 commit ahead | Execute |
| Force-push branch | branch is 200 commits ahead | Hold |

## Pre-existing CI rot diagnosis (don't conflate with PR scope)

Before concluding a PR "breaks CI," check the base:

```bash
# CI status of the base commit (what the PR inherits)
gh api repos/<owner>/<repo>/commits/<base-sha>/check-runs --jq '.check_runs[] | {name, conclusion, status}'

# Lint on the base branch
git checkout origin/main -- <file>
ruff check <file>
git checkout HEAD -- <file>
```

If the base branch has the same CI failures, the PR is INHERITING rot, not introducing it. Document the inheritance in the hold message — pre-existing rot doesn't block a clean merge, but the operator should know.

## The hold-message template

```
## 🛑 Holding. Authorized scope = X. Actual scope = Y.

Counter <N>/<N>=100%.

### Green lights
| Check | Result |
|---|---|
| <bounded check 1> | PASS |
| <bounded check 2> | PASS |

### Red flag
<one-line: actual scope > authorized scope, here's why>

### Three unblock options
- (a) Escalate to broader authority (George, etc.)
- (b) Shrink the action (squash-merge just the bounded commits)
- (c) Execute despite scope (operator confirms they accept the full scope)
- (d) Punt — keep state, work on something else

Counter <N+1>/<N+1>=100%. Awaiting direction.
```

## Counter discipline under operator pressure

When the operator says "do it," the counter STILL goes up by 1 for the preflight — even if the preflight results in a hold. The preflight is bounded work that earned its increment. The "hold + ask" message is the artifact, not a non-event.

## Related recipes

- For deleting branches/worktrees: `branch-deletion-approval`
- For sending / publishing: `outbound-action-gate`
- For general execution shape: `directive-then-execute`

---

## The lane-owner YES request pattern (extension from the 2026-07-31 case study)

When the hold message points to "escalate to broader authority," the request is rarely verbal — it's posted to Linear so it's auditable and survives session boundaries. Recipe:

1. **Resolve the lane-owner's displayName first** — query `users(first: 20)`, pick the one whose `email` matches the protocol gate. Get both their UUID and `displayName`. The UUID is for explicit reference; the displayName is for `@mention` syntax.
2. **Post the Linear comment on the PR's tracking issue** (e.g., GRO-4188 for PR #382), not on a parent epic or random Linear task. The lane-owner reads the issue thread, not the chat.
3. **Format: `linear_comment(identifier, body)` where body contains**:
   - `@displayname` mention at the top
   - One-line: "requesting YES for `<action>`"
   - **Evidence package** (compact, bulleted): test runs with PASS counts, lint parity, GitHub mergeability state, potential merge commit SHA, PR diff stat
   - **Scope disclosure** (the reason for the hold): e.g., "the 4 PR commits sit on a 351-commit divergent branch; I cannot vouch for those 351 commits"
   - **Three decision axes**, each one line: (a) full merge vs squash, (b) target branch main vs deploy-fresh, (c) acceptable CI baseline
   - Closing: "Standing by until you reply"
4. **Verify the comment landed** — `linear_comment()` returning `True` is necessary but not sufficient. Always follow with `_linear_gql` + `comments(last: N)` to confirm the comment is visible. If using `last: 3` and the issue has 5+ comments, you'll miss yours — size `N` to be safe (use `last: 10`).
5. **Do NOT execute the action** until the lane-owner replies on the Linear thread. Chat replies don't count; the protocol gate is on the Linear comment chain.

**Why this matters**: If the lane-owner doesn't see the request, the hold becomes indefinite. The verification step (item 4) is non-negotiable.

## Pitfalls

- **`git merge-base origin/main HEAD` exiting 1 silently** — exit 1 from merge-base means "no common ancestor," NOT a real failure. It happens when the local repo is stale on `origin/main`, the refs aren't fully fetched, or branches genuinely diverged. The reliable check is `git merge-base --is-ancestor origin/main HEAD && echo "main ⊆ HEAD" || echo "main NOT ⊆ HEAD"` (run both directions). If both say NOT, branches diverged.
- **`linear_comment(identifier, body)` returning `True` doesn't guarantee the comment is visible** — could be budget-throttled, queued, or silently dropped. Always fetch back with `comments(last: N)` and visually confirm. Use `last: 10`, not `last: 3`.
- **Mentioning `@displayName` doesn't notify the user by default** — Linear's `@mention` only renders as a clickable notification if the user is a team member on that workspace and has notification preferences enabled. If the lane-owner's displayName is misspelled or they're outside the team, the mention is plain text. Always verify the UUID first.
- **Asking the operator when the lane-owner is the right authority** — if a previous containment protocol names a specific agent (e.g., "Only George YES may authorize merge"), do NOT route the question to the operator. They authorized the original action; the gate is downstream. Surface to the lane-owner instead.
- **Squash-merging silently** — when scope mismatches and you pick "shrink the action," make sure the operator knows the 351 (or N) commits underneath are erased. Squash is not a no-op. The history belongs to someone.
- **Forgetting pre-existing CI rot** — if `origin/main` itself has CI failures (lint errors, test failures, build skipped), the PR is INHERITING rot, not introducing it. Document the inheritance in the hold message and the eventual merge commit. Pre-existing rot doesn't block a clean merge, but it does mean a post-merge CI red is not attributable to the PR.

## Related references (additions after the 2026-07-31 case study)

- For Linear comment verification pattern: `linear-backlog-routing-governance` (pitfall section on post-edit verifier, "Repeated stale detector" recipe)
- For ad-hoc verifier shape on changed code: `verifier-as-deliverable-discipline`
- For protocol-gated authorizations (George-style): see containment protocol notes that name a specific agent — never route the question back to the operator.