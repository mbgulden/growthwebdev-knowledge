# Ned Branch Triage — Linear Setup Transcript (2026-08-04)

Worked example of the **blocking-chain + umbrella pattern** for a resume-safe multi-step workstream.

## Context

Michael asked: "What do we do with all the 'Ned' branches and work trees? Make a plan... How do we find out if we even want these Ned branches?"

Michael asked: "What do we do with all the 'Ned' branches and work trees? Make a plan... How do we find out if we even want these Ned branches?"

After scoping (solo authority, newest-first with breakage-check promotion, Linear-linkage primary signal, single-threaded), I produced an 8-step plan, then Michael asked: **"Make a linear task series for Ned to follow so that it's all ready to be worked on and we can start and stop if we need to or if you get interrupted."** That last clause — *start and stop if we need to* — is the trigger for the umbrella pattern. A plain epic+children layout doesn't guarantee resume safety; only a chain with a manifest-as-source-of-truth does.

## Scope correction: the "5 repos" claim was wrong from creation

The system-reminder handoff at session start said the live scope was 5 repos. The on-disk `state/current.json` and the live filesystem (`reports/discovery/ned-branches-2026-07-31/` with 2,060 refs across 32 repos) both disagreed — actual scope was **32 repos under `/home/ubuntu/work`**, with the 5-repo prismatic-engine family as a subset.

**Both the umbrella description and GRO-4463's description were created with "5 repos" before I detected the staleness.** I corrected them on the spot: one `issueUpdate` rewriting GRO-4463's description to "Scope corrected: 32 repos under /home/ubuntu/work, not 5. Re-run scan against existing 2026-07-31 packet (326 active + 1,398 closed-task refs), verify, fill gaps, output state/triage/raw-branches.json." plus a posted comment naming the source of the staleness and the real scope. The 255-char description limit forced brevity but the comment carries the full audit trail.

**Lesson: detect scope mismatches before any child work begins, and correct the Linear issue descriptions immediately.** See the "scope-correction must propagate to Linear" pitfall in SKILL.md for the recipe. Future agents who read GRO-4463's description first will now see the correct scope.

## What I built

- **Project**: `Ned Branch Triage & Merge` (state: planned)
- **1 umbrella**: GRO-4462 — "Triage & merge all Ned branches across 5 repos" *(note: description says "5 repos" but the actual scope is 32; this is documented in the comment thread on GRO-4463)*
- **8 children in execution order** (all descriptions were scope-corrected):
  - GRO-4463 — Enumerate ned/* branches + worktrees (across 32 repos; corrected from "5")
  - GRO-4464 — Pull per-branch metadata: Linear linkage, diff size, issue state
  - GRO-4465 — Filter: drop no-linkage + no-work branches
  - GRO-4466 — Sort survivors newest-first, apply promotion rule
  - GRO-4467 — Write final triage manifest with merge order
  - GRO-4468 — Process top branch: rebase, open PR, record URL
  - GRO-4469 — After each merge, re-run breakage check on remaining queue
  - GRO-4470 — Worktree cleanup: remove merged/dropped worktrees, document kept ones
- **15 blocking relations**: 7 in chain (each step blocks the next), 8 from children to umbrella

## Auth + setup gotchas hit

- `LINEAR_API_KEY` was unset in env; `/tmp/lkey.txt` had it. Previous scripts in `/tmp/linear_*.py` confirmed the pattern (raw key, no Bearer).
- First auth attempt with `Bearer ` prefix returned `HTTPError 400` (not 401). Body literally said: *"It looks like you're trying to use an API key as a Bearer token. Remove the Bearer prefix."* Fixed in one line.
- `Project` GraphQL type has no `key` field. Trying to select `key` returned `GRAPHQL_VALIDATION_FAILED: Cannot query field "key" on type "Project"`.
- `projectCreate` rejected descriptions over 255 chars with `Argument Validation Error` naming the property and the exact constraint. Shortened the description.
- No existing "Ned branches" project; created a new one rather than dumping 9 tasks into the team backlog.

## The mistake-and-fix on `blocks` direction

I created 15 `blocks` relations with `issueId = blocker, relatedIssueId = blocked`, thinking that meant "blocker blocks blocked". After verification, the direction was backwards: querying GRO-4463 showed `blocked-by: [GRO-4464]` — i.e. 4464 (the later step) was blocking 4463 (the earlier step). The chain enforced the *reverse* order.

Fixed by deleting all 15 relations and recreating with the parameters swapped: `issueId = later (the one that must wait), relatedIssueId = earlier (the blocker)`. After the swap, the verification read correctly:
- `GRO-4463: blocks=[GRO-4462, GRO-4464], blocked-by=[]`
- `GRO-4464: blocks=[GRO-4462, GRO-4465], blocked-by=[GRO-4463]`
- ...
- `UMBRELLA GRO-4462: blocks=[], blocked-by=[all 8 children]`

To delete, I queried all issues in the batch, collected `relations.nodes[].id` for type=blocks (15 of them), then `issueRelationDelete(id: <relation_uuid>)` per ID. Sleep 0.2s between deletes to stay under rate limits.

## Verification recipe

After any blocking-chain build, run this verification to confirm the direction is correct:

```graphql
query($id: String!) {
  issue(id: "<first_child_id>") {
    relations { nodes { type relatedIssue { identifier } } }
    inverseRelations { nodes { type issue { identifier } } }
  }
}
```

For the FIRST child in the chain, expect:
- `relations` (what it blocks) — empty
- `inverseRelations` (what blocks it) — empty

For the LAST child, expect:
- `relations` — `[<umbrella_id>]`
- `inverseRelations` — `[<previous_child_id>]`

For the UMBRELLA, expect:
- `relations` — empty
- `inverseRelations` — `[<all_children_ids>]`

If any of these is inverted, the direction is wrong. Delete and recreate.

## What made this resume-safe

Two things working together:

1. **Linear's chain enforcement** means the next session literally cannot start step N+1 until step N is marked Done. So there's no ambiguity about "what's next?" — it's whatever the first non-Done child is.
2. **The manifest file** (`state/triage/ned-branches.md`, created in step 5) holds every decision, PR URL, and rationale. The next session reads the manifest to know *context* (which branches exist, what was decided) and reads Linear to know *position* (which step is open).

Neither alone is sufficient. Linear's chain without the manifest means you know the step but not the prior decisions. The manifest without the chain means you know the context but not which step is next.

## Total cost

- 1 `projectCreate` mutation
- 9 `issueCreate` mutations
- 15 `issueRelationCreate` mutations (after the failed first batch)
- ~5 verification queries
- Total: ~30 API calls, ~25 seconds elapsed