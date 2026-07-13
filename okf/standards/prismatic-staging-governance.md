---
type: Standard
title: Prismatic staging governance
description: Standard for staging branch promotion, governor-only pushes, and repo-local hook precedence across Prismatic workspaces.
resource: okf/standards/prismatic-staging-governance.md
tags: [standard, prismatic-engine, governance, staging, git-hooks, fred]
timestamp: 2026-07-13T20:00:00Z
linear_issue: GRO-3792
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-staging-governance.md
last_verified: 2026-07-13
verified_by: fred
status: current
---

# Prismatic staging governance

## Standard

Protected staging branches are promotion lanes, not worker branches. A staging
branch does not need to match a worker prefix such as `feature/`, `ned/`,
`content/`, or `research/`. It must instead be governed by an explicit
staging-governor rule.

```yaml
staging:
  governor: "fred"
  branch: "staging"
```

## Required hook behavior

A compliant pre-push hook must evaluate staging-governor permission **before**
normal branch-prefix validation.

| Push target | Required behavior |
|---|---|
| `refs/heads/staging` from local branch `staging` | Allow only configured governor, currently `fred`. |
| `refs/heads/staging` from any non-governor worker branch | Block with an explicit `Only fred ... can push to staging` message. |
| `refs/heads/main` | Always block; production is manual-only. |
| Worker branches | Continue normal prefix and lane validation. |

## Hook precedence rule

Repo-local hooks must win over stale profile/global hooks for governed repos.
Set local hook precedence explicitly when needed:

```bash
git config --local core.hooksPath .git/hooks
```

Incident that created this rule: HDE inherited a stale global hook from Ned's
profile (`/home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push`). Git ignored
HDE's fixed `.git/hooks/pre-push` until the local `core.hooksPath` was set.

## Verification pattern

Use a focused `/tmp/hermes-verify-*` script that checks:

1. hook compiles,
2. tracked hook and installed `.git/hooks/pre-push` have identical hashes,
3. repo-local `core.hooksPath` is `.git/hooks`,
4. non-empty Fred staging push is allowed,
5. no-op Fred staging push is allowed,
6. Ned/non-governor staging push is blocked,
7. direct `main` push is blocked,
8. remote readback matches local `HEAD` after real push.

## HDE reference implementation

| File | Commit |
|---|---|
| `PRISMATIC_ENGINE.yaml` | `1083287` |
| `scripts/prismatic-pre-push-hook.py` | `1083287` |
| Installed hook | `.git/hooks/pre-push`, hash matched tracked script during verification |

## Anti-patterns

- Do not force-push or bypass hooks to promote staging.
- Do not treat a staging branch as a normal worker branch prefix problem.
- Do not rely on global `core.hooksPath` in repos with repo-specific governance.
- Do not update the tracked hook without reinstalling/verifying the active hook.
