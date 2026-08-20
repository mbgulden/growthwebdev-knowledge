# AOT PR + Linear Runway Reconciliation — 2026-07-11

Use this reference when Michael asks to “check outstanding tasks/PRs,” “resolve or reassign everything,” or clear the AOT runway.

## Durable lessons

1. **Reconcile GitHub before Linear.**
   - Check both public deploy repo and private business repo for open PRs.
   - If a PR is clean/mergeable with passing checks and low risk, merge it first, then verify the artifact on `origin/main` before closing the related Linear issue.
   - After merge, re-run `gh pr list` for both repos and report zero/open count explicitly.

2. **Close stale Linear only with live evidence.**
   - DNS/custom-domain tasks can be closed when apex returns 200, `www` redirects to apex then 200, and the mirror returns 200.
   - Superseded pre-launch issues should be canceled, not left in Todo, when their own description says they are archived/superseded.
   - Add a Linear comment with exact evidence before moving state.

3. **Route work by labels if app-user assignment is blocked.**
   - Linear app users may reject assignment with `App user not valid` / missing scope.
   - Do not treat that as a blocker: add lane labels instead (`agent:kai`, `agent:codex`, `agent:kai-content`, `agent:fred`, `agent:agy`, etc.) and leave a comment saying it is agent-routed.
   - For human content ownership, assign to Ella when appropriate; for Michael-owned backlog items that are not truly waiting on him, remove Michael and route via labels.

4. **Define “resolved or reassigned” as zero ambiguous items, not zero backlog.**
   - Real AOT backlog can remain open.
   - The cleanup target is:
     - no open PRs needing action,
     - no stale/superseded tasks still pretending to be active,
     - no unassigned/unlabeled ambiguous items,
     - all remaining tasks routed by lane.

5. **Clean workspace hygiene before reporting.**
   - If the main repo/worktree is on a stale branch or has a dirty generated audit/report, preserve a copy under `/tmp` if potentially useful, restore the dirty file, switch/pull to current `main`, and verify `git status --short --branch` is clean.
   - Do not leave a task report saying the runway is clear while the primary repo remains dirty or on a gone branch.

## Recommended live checks

```bash
# PR runway
gh pr list --repo mbgulden/active-oahu-tours-mirror --state open --json number,title,url --limit 100
gh pr list --repo mbgulden/active-oahu-business --state open --json number,title,url --limit 100

# Production / canonical redirects / mirror
curl -sS -I https://activeoahutours.com/ | sed -n '1,12p'
curl -sS -I -L https://www.activeoahutours.com/ | sed -n '1,16p'
curl -sS -I https://active-oahu-tours-mirror.pages.dev/ | sed -n '1,12p'

# Workspace hygiene
git status --short --branch
```

## Linear routing matrix used

| Lane | Typical labels / owner | Examples |
|---|---|---|
| Kai/Codex implementation | `agent:kai`, `agent:codex`, `agent:kai-css`, `agent:kai-js` | Lighthouse cycles, CTA implementation, broken-reference triage, headers/nav/accessibility |
| Ella/Kai content | Ella assignment + `agent:kai-content`, `agent:agy`, `dispatch:ready` | Interviews, content audit, content clusters, outreach copy |
| Fred/Ops/security | `agent:fred`, sometimes `agent:needs-human-review` | WAF review, CSP enforcement, DNS/governance, SOPs, store/infra automation |
| AGY/research monitor | `agent:agy`, `agent:needs-human-review` | Competitor monitoring or research that requires judgement before implementation |

## Reporting pattern

Lead with runway state:

- open PR count by repo,
- tasks closed/canceled,
- remaining open count,
- whether ambiguous/unrouted count is zero,
- live site status,
- repo hygiene state.

Then identify the next golden-path item, usually the highest-value unblocked implementation task, not a long undifferentiated backlog dump.
