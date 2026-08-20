# Production durability standard — workspace-tree black page lesson (2026-07-15)

## Trigger

Use this reference when any Prismatic-managed project has a production-facing route, dashboard, plugin page, gateway API, or public operator surface that is broken, blank, stale, or inconsistently deployed.

The session trigger was `/workspace-tree` rendering as a black page on `prismatic.growthwebdev.com`. The deeper issue was not only a route bug: production was served from a mutable shared worktree, and the route shell could render empty/black if external scripts failed.

## Core standard

Production must live durably:

```text
live service source != mutable multi-agent development checkout
```

Every production-facing fix should follow:

```text
clean production-safe branch/worktree
→ local gateway/service reproduces the problem
→ patch in reviewed branch, not mutable live checkout
→ local route/API/browser proof passes
→ path safety/security checks pass
→ intentional deploy/restart/reload
→ public/authenticated route proof passes
→ screenshot/browser proof attached
→ production source/worktree remains durable and clean
```

## Required agent instructions

Burn these into Fred/AGY/Kai/Ned/Jules prompts when production is touched:

- fix from a clean production-safe branch/worktree;
- stop relying on the mutable shared worktree for production;
- make user-facing pages robust even if CDN scripts fail;
- preserve path safety and block traversal;
- verify local gateway before public route;
- restart/deploy production intentionally;
- provide screenshot/browser proof;
- distinguish ad-hoc targeted verification from canonical full-suite green.

## Workspace-tree specific audit pattern

Minimum diagnosis:

```bash
curl -sS -D - -o /tmp/workspace-tree.body http://127.0.0.1:9000/workspace-tree
curl -sS -D - -o /tmp/workspaces.body http://127.0.0.1:9000/api/workspaces
curl -sS -D - -o /tmp/preview.body 'http://127.0.0.1:9000/api/workspace-tree/preview?file=prismatic-engine/README.md'
```

Inspect route table from the same source the service uses:

```bash
PYTHONPATH=/path/to/repo:/home/ubuntu/.prismatic/venv_stable/lib/python3.12/site-packages python3 - <<'PY'
import inspect
import prismatic.gateway.server as s
print(inspect.getfile(s))
for r in s.app.routes:
    p = getattr(r, 'path', None)
    if p and ('workspace' in p or 'dashboard' in p or p in ['/', '/health']):
        print(p, sorted(getattr(r, 'methods', []) or []))
PY
```

Check proxy only after local route works. Nginx may already proxy `/workspace-tree` correctly while the gateway route is missing.

## Black-page prevention

Do not ship an empty dark shell that depends on CDN React/Tailwind to render all visible content. Acceptable fixes:

1. best: self-contained no-CDN page using vanilla JS or locally served assets;
2. acceptable: React/plugin shell with visible no-JS/dependency-failure fallback and API health guidance;
3. unacceptable: blank `<main>` that remains black if external scripts, CSP, or plugin globals fail.

## Path safety

Workspace-tree-like APIs must resolve only under configured workspace roots and block traversal. Required checks:

```text
safe repo file preview → 200
../../etc/passwd → 400/403
/api/plugins/.../preview?path=/etc/passwd → 403
```

Never loosen filesystem access to make the UI work.

## Markers

Recommended standard markers:

```text
PRODUCTION_DURABILITY_STANDARD_DOC_OK
AGENT_PRODUCTION_ROUTE_CHECKLIST_OK
PRODUCTION_DURABILITY_VERIFIER_OK
PRODUCTION_DURABILITY_REVIEW_GATE_OK
PRODUCTION_DURABILITY_AGENT_BRIEF_OK
PRODUCTION_WORKTREE_DURABILITY_OK
PRODUCTION_WORKTREE_DURABILITY_PLAN_OK
PRISMATIC_PRODUCTION_DURABILITY_STANDARD_OK
```

Workspace-tree route markers:

```text
WORKSPACE_TREE_BRANCH_SCOPE_OK
WORKSPACE_TREE_REPRO_OK
WORKSPACE_TREE_BLACK_PAGE_GUARD_OK
WORKSPACE_TREE_PATH_SAFETY_OK
WORKSPACE_TREE_DEPLOYED_OK
WORKSPACE_TREE_PRODUCTION_OK
```

## Reporting boundary

Use precise language:

```text
Standard installed ≠ workspace-tree fixed
workspace-tree fixed ≠ all production risks eliminated
focused route verification ≠ full dashboard suite green
```
