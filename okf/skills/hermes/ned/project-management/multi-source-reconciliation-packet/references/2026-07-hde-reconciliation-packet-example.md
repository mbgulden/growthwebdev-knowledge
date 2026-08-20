---
type: Reference
title: HDE Reconciliation Packet — worked example
description: Concrete packet generated for Human Design Engine on 2026-07-27. Use as a worked template when applying multi-source-reconciliation-packet to other projects.
timestamp: 2026-07-27T20:55:00Z
source_session: ned / 2026-07-27
related_linear: GRO-4343
---

# HDE Reconciliation Packet — 2026-07-27 (worked example)

## Context

Human Design Engine project. Canonical repo is `mbgulden/hd-platform` checked out at `/home/ubuntu/work/hd-platform`. Staging runtime is `/home/ubuntu/work/hd-platform-staging` (separate clone, remote points to local canonical). Chart engine is `mbgulden/OpenHumanDesignMCP`.

Michael asked "where are we at" without a clear answer. Inspection showed:

- Canonical checkout dirty: 107 entries (60 M, 47 ??).
- Staging checkout dirty: 20 entries.
- Open PRs against hd-platform: 28.
- Local-only branches (not on origin): 21 across three repos.
- Linear issues in HD Engine Core: 40; some marked Done while required children still Todo.

Production site (`humandesignengine.com`), staging (`staging.humandesignengine.com`), API, payment, reports, tunnel, orchestrator, router, and 11 guest containers all healthy. The drift was not an outage — it was a planning/deployment state.

## What the packet captured

127 dirty entries classified into:

| Disposition | Count |
|---|---:|
| `promote-pending-source` | 91 |
| `promote-pending-content` | 11 |
| `runtime-only` | 10 |
| `sensitive-review` | 3 |
| `archive` | 7 |
| `unclassified` | 2 |

Key sensitive paths identified:

- `production_database.db\n` (hd-platform, untracked)
- `.runtime/` (both hd-platform and hd-platform-staging, untracked)
- `dist.backup-bad-old-shell-20260718T093141Z/` (hd-platform-staging)
- `dist.backup-pre-price-copy-20260718T165249Z/` (hd-platform-staging)

21 local-only branches catalogued with SHA, date, last commit, and disposition. Eight were `promote-pending`, eleven were `superseded`/`archive`.

28 open PRs mapped to Linear via `re.search(r'GRO-(\d+)', title)`. Disposition table included `merge`, `close`, `sequence`, `hold`. PR #47 (daily nervous-system loop, GRO-4011) was the keystone — already merged to deploy-fresh per recent history but still open.

51 Linear issues pulled with state, project, parent, labels, and assignee. Notable drift signals:

- GRO-4004 Done, but child GRO-4009 evidence says "production report delivery is not green".
- GRO-4010 Done, but children GRO-4012, GRO-4013, GRO-4015 incomplete.
- GRO-3992 Done, but children GRO-3995, GRO-3996 Backlog.

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Packet doc | `hd-platform/docs/operations/_reconciliation/hde-reconciliation-packet-2026-07-27.md` | untracked |
| Path snapshot | `hd-platform/docs/operations/_reconciliation/hde-dirty-snapshot-2026-07-27.json` | untracked |
| Linear parent | `GRO-4343` | Todo, awaiting sign-off |
| Raw snapshots | `/tmp/hde_dirty_paths.json`, `hde_branches.json`, `hde_prs.json`, `hde_linear.json`, `hde_dirty_classified.json` | runtime, ephemeral |

## Linear parent issue

```
title: [HDE-RECONCILE] Non-destructive reconciliation packet before any production change
state: Todo (unstarted)
project: HD Engine Core
labels: agent:ned, epic, requires:human-approval, dispatch:ready
```

Comment posted with snapshot totals and explicit "no production change permitted until this issue is moved out of Todo".

## Verifications run

- `git status --short --branch` before: 107. After: 109 (added 2 untracked files; no tracked diff).
- Linear API call to `commentCreate` succeeded only after switching from `issueId`+`body` direct args to `input: {issueId, body}` wrapper.
- GitHub PR list endpoint (`/pulls?state=open`) returned 28 — packet reports 28.
- `git branch -r --contains <branch>` produced `True/False` for each branch; `on_origin=False` set matched the count.

## Sign-off checklist in the packet

1. Sensitive-artifact plan: confirm `production_database.db\n`, `.runtime/`, `dist.backup-*` scope.
2. Branch-ownership: name the production release branch (`main`, `deploy-fresh`, other) and staging branch.
3. Linear parent-reopen policy: reopen GRO-4004 / GRO-4010 / GRO-3992 vs. accept-Done-with-supersede.
4. PR closure authority: blanket vs. per-PR.

## Production-readiness gate (in packet)

Seven explicit checks. No production deploy until all are ticked:

- Packet reviewed by Michael.
- Sensitive paths quarantined.
- `feature/gro-3999` rebased onto the agreed release branch.
- 28 open PRs dispositioned.
- 51 Linear issues state-consistent.
- Fresh HDE green report from staging.
- End-to-end user journey provable on staging.

## Lessons learned

- **Keep the packet untracked.** Writing into `docs/operations/_reconciliation/` (a fresh subdir) avoided adding to the existing 107-entry dirty diff while still being adjacent to canonical documentation.
- **Cross-source drift compounds.** A parent Done + child Todo + open PR + dirty tree is a single coherent signal, not four separate anomalies. The packet makes them a single artifact for Michael.
- **Sensitive paths cluster.** `production_database.db\n`, `.runtime/`, `dist.backup-*` are typically co-located with ops directories because that's where the orchestration scripts run. Grep the same set of regex patterns in one pass.
- **Worktree porcelain is text.** The first script's `json.loads()` blew up; the parser must split on `\n` and walk 3-line blocks.
- **`commentCreate` needs the `input` wrapper.** GraphQL mutation signature is `mutation($input: CommentCreateInput!)` not `mutation($id:String!,$body:String!)`. This caught me once.

## Reuse for other projects

Same pattern, swap identifiers:

- BeyondSaaS: `beyondsaas-site` repo, `BeyondSaaS` Linear project.
- Sentinel ITAD: future canonical repo, `Sentinel ITAD` Linear project (when created).
- Anything with >50 dirty entries or >5 stale PRs: run the workflow as written.

The packet doc template (six dispositions, four sign-off items, seven production-readiness gates) is portable. The regex classifiers should be tuned per-project, but the structure stays the same.