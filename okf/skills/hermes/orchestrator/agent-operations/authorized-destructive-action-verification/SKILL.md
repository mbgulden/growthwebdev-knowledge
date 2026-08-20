---
name: authorized-destructive-action-verification
description: Operator authorization to perform a destructive action (merge to main, force-push, deploy, large rollback) is necessary but not sufficient — the agent must still verify the actual scope matches the authorization before executing. "I authorize you to merge PR #382 if you don't make a mess" authorizes 4 commits; if the PR sits on 351 commits of divergent history, the authorization does not extend to those 351 commits. Preflight scope verification is mandatory even after explicit confirmation. Use when Michael (or any operator) says "go ahead, merge/delete/deploy X" and the action is reversible only by manual intervention. Also use when a prior protocol names a lane-owner (e.g., George, Ned) as the gatekeeper — in that case, surface the hold to the lane-owner via Linear comment, not back to the operator.
---

# authorized-destructive-action-verification

## The rule

When the operator authorizes a destructive, hard-to-reverse action — even with explicit "go ahead" / "if you don't make a mess" / "yes, do it" — the agent MUST run a scope-verification preflight BEFORE executing. The preflight answers one question:

> **Does the actual scope of the action match the scope the operator authorized?**

If yes → execute.
If no → hold, surface the gap, and ask the operator to confirm the larger scope (or amend the action).

The operator's authorization is for a SCOPE, not for the agent's good faith. "Don't make a mess" is a constraint on the scope, not a transfer of responsibility.

## The class of action this covers

Any irreversible or hard-to-reverse mutation:

- **Merge to main / deploy-fresh** (the canonical case)
- **Force-push to a shared branch**
- **Delete of multiple refs / namespaces**
- **Large rollback / revert of merged work**
- **Reset / cleanup of runtime state databases** (state.db, event_bus.db)
- **Any action where the operator's authorization phrase implies a bounded scope but the action's actual scope is broader**

For local-only / easily-reversible actions (commit on a feature branch, edit a draft file, move a worktree to /tmp) the rule does not apply — just execute.

## The preflight scope-verification recipe

Before executing the authorized action:

1. **Identify the authorized scope.** Quote the operator's words back: "Authorized: 'merge PR #382 if you don't make a mess.'" The authorized scope is "PR #382" + "the constraint not making a mess."

2. **Identify the actual scope.** Compute it independently of the authorized framing. Examples:
   - For a PR merge: `git diff <pr-base>..HEAD --stat` (just the PR's commits) AND `git diff origin/main..HEAD --stat` (cumulative divergence). Compare the two.
   - For a delete: list every ref / branch / worktree / file that would be removed.
   - For a deploy: list every artifact, config, and downstream consumer that would change.

3. **Compare scopes.** If actual scope = authorized scope (or actual is a strict subset), execute. If actual scope > authorized scope, hold.

4. **Diagnose pre-existing rot separately.** If the action targets a branch with pre-existing CI failures / lint errors / debt, separate that from what the action adds. Use:
   - `git diff origin/main..HEAD -- <file>` to see if the failure existed before the PR
   - `gh api repos/<owner>/<repo>/commits/<base-sha>/check-runs` for the base commit's CI status
   - The rule: "PR introduces X failures" is a different claim from "target branch has X failures." The first blocks; the second does not.

5. **Surface scope mismatch honestly.** If actual > authorized, do NOT silently execute the larger scope. Report:
   - Authorized scope (1 line, quoted)
   - Actual scope (1 line, computed)
   - The gap (1 line, why it diverged)
   - Three options: (a) escalate to the broader authority, (b) shrink the action to the authorized scope, (c) punt.

## Anti-patterns

- **"Operator said yes, so I executed"** — authorization without scope verification. The operator may have assumed a bounded scope that does not exist.
- **"I figured since they authorized the merge, they authorized whatever I found under the hood"** — the operator authorized "the merge," not "any merge that produces this commit."
- **"The PR was open and mergeable so I merged it"** — GitHub's `mergeable: MERGEABLE` is a permission, not a scope check.
- **"CI was failing anyway, so what I added doesn't matter"** — the action adds to the failure surface even if the underlying rot is pre-existing. The action is still attributable.
- **Stopping the preflight to ask "is this scope OK?"** — that IS the question. Compute first, then ask with the computed scope.

## What to do when scope doesn't match

Don't freeze. Don't refuse. Don't execute. **Hold and surface.**

The hold message should contain:
- The verified green lights (what passed)
- The verified red flag (what's bigger than expected)
- Three concrete unblock options, each one line
- No "should I do this?" question — the operator's prior "yes" does not transfer

The operator will pick (a), (b), (c), or (d). Move on their answer.

## Where to route the hold-ask

The default is the operator, but **a prior containment protocol may name a different authority** (e.g., "Only George YES may authorize merge"). In that case:

- **Operator authorized the action** → if a downstream gate is named, surface to the gatekeeper (lane-owner), NOT the operator. The operator's authorization is upstream; the gate is downstream.
- **No named gate** → route to the operator with computed scope.
- **Both** → surface to both: the lane-owner for the protocol gate, the operator for the implicit re-authorization.

When surfacing to a lane-owner (not the operator), post the ask as a Linear comment on the PR's tracking issue with `@displayname` mention, evidence package, and 3-4 explicit decision axes. The recipe is in `references/pr-merge-scope-recipe.md` ("The lane-owner YES request pattern"). Verify the comment landed by fetching `comments(last: N)` — `linear_comment()` returning `True` is necessary but not sufficient.

Chat replies to the lane-owner don't satisfy the protocol gate; the gate is on the Linear comment chain. If the lane-owner doesn't see the request, the hold becomes indefinite — that's why the verification step matters.

## Verification

Every authorized-destructive action has:
- A preflight scope record (even a single-line echo in the response)
- A scope-comparison report (authorized vs actual)
- Either: a clean execution (scopes matched) or a hold + option list (scopes didn't match)
- A counter bump for the preflight, regardless of whether execution happened

The counter bump on a hold is non-negotiable: the preflight is bounded work that earned its increment.

## Related gates (do not duplicate)

- **outbound-action-gate** — covers send / publish / record. Merge is NOT outbound (it's an internal mutation).
- **branch-deletion-approval** — covers branch / worktree / ref deletion. Merge is NOT deletion.
- **directive-then-execute** — covers execution shape for non-unsafe directives. Adds the "if unsafe, gate + confirm" exception that this skill extends.

This skill fills the gap between `directive-then-execute` (execute when safe) and the destruction-specific gates (delete, send). It's the umbrella for "the operator authorized it, but the action's actual scope is bigger than the authorization — what now?"