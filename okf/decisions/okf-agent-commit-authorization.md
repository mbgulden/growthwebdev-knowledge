---
type: Decision
title: OKF Agent Commit Authorization — George Registration
description: Michael authorizes George, Fred, Kai, and Ned to contribute, commit, and push to the OKF hub. Registers george in PRISMATIC_ENGINE.yaml with the george/ branch prefix and full-OKF write lane; main stays manual-merge.
resource: okf/decisions/okf-agent-commit-authorization.md
tags: [decision, prismatic-engine, governance, okf, agents, george]
timestamp: 2026-08-19T03:44:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/decisions/okf-agent-commit-authorization.md
last_verified: 2026-08-19
verified_by: george
status: accepted
---

# OKF Agent Commit Authorization — George Registration

## Context

The 2026-06-23 Prismatic lane-governance install (GRO-2217) registered five
agents in `PRISMATIC_ENGINE.yaml`: `fred`, `kai`, `agy`, `jules`, `ned`.
George (Prismatic helper / workflow guard profile) was missing from the roster,
so any push from a George checkout either failed agent resolution or had to
ride a `feature/` branch that attributes the push to Fred.

On 2026-08-19 Michael explicitly authorized **George, Fred (orchestrator),
Kai, and Ned** to contribute, commit, and push to the OKF
(`mbgulden/growthwebdev-knowledge`). Fred, Kai, and Ned were already
registered; only George required a new entry.

## Decision

- Register `george` in `PRISMATIC_ENGINE.yaml`:
  - role: `Prismatic Helper / Workflow Guard`
  - `branch_prefix: "george/"`
  - lanes `owner`: `["*"]` — George's lane spans the whole OKF (standards,
    decisions, operations, reports, project indexes, root indexes) plus the
    governance config itself, matching his cross-lane review role.
  - `staging_governor: false` — staging governance stays Fred-only.
- **No direct-main push is granted to any agent.** Rule 5 of
  `scripts/prismatic-pre-push-hook.py` (main is production, manual-only) is
  unchanged. "Push to the OKF" means worker-branch push + PR + manual merge.
  For this repo the sanctioned manual step is the PR merge (no deploy-fresh
  involvement for docs-only work).
- The pre-push hook is config-driven (`_determine_agent` +
  `_check_lane_ownership` read `PRISMATIC_ENGINE.yaml` at push time); no hook
  code change is required or made.

## Consequences

**Positive:**

- George's pushes resolve to agent `george` via the `george/` prefix; lane
  validation runs against his own entry instead of failing or misattributing.
- Authorization is recorded in the OKF, so any profile (or a future agent)
  can audit who may commit and what the merge rule is.

**Negative:**

- George's `owner: ["*"]` is broad by design (review role spans lanes); it is
  bounded by the unchanged main-block and lock rules.
- `commit.prefix_format` in the config still shows `[Fred]` as the example;
  the effective convention is `[<agent>] description`, as already used by
  George and Fred commits.

## Alternatives considered

- **Give George a narrow lane subset** (e.g. only `okf/operations/` +
  `okf/standards/`): rejected — George's actual work (index maintenance,
  decision records, governance config edits, cross-category reviews) would
  trip lane violations constantly.
- **Reuse Fred's `feature/` prefix for George**: rejected — misattributes
  agent identity in lock checks and the pre-push report, which is exactly the
  gap that surfaced on 2026-08-19.

## Verification

- Pushed this registration from a `george/` branch; pre-push hook resolved
  agent `george` and validated lane ownership for the changed files (see
  commit history of `PRISMATIC_ENGINE.yaml`).

## Refs

- `PRISMATIC_ENGINE.yaml` (governance config)
- `scripts/prismatic-pre-push-hook.py` (hook; unchanged)
- `okf/standards/prismatic-staging-governance.md` (staging rule; unchanged)
- GRO-2217 (original lane-governance install)
