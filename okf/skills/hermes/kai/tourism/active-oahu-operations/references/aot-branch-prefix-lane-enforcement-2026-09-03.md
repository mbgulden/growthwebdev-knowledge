# AOT branch-prefix lane enforcement (verified 2026-09-03)

Session 20260903_063545_424590be — post-unify marker fix in `active-oahu-tours-mirror`.
Resolves the pre-boundary confusion about who may push ROOT governance files.

## What actually enforces lanes
- The real pre-push validator is `scripts/prismatic-pre-push-hook.py` (278 lines), installed as a **local symlink** at `.git/hooks/pre-push`. There is no server-side `pe_lane_guard.py` (an earlier claim of one was a hallucination).
- Agent identity is derived from the **branch name prefix** in `PRISMATIC_ENGINE.yaml` (`lanes.owner`) — NOT from `.prismatic-web-governance.json` `owner_paths`.
- `feature/*` branches → Fred identity → `lanes.owner: ["*"]`, `staging_governor: true`.
- Precedence rule (verbatim from the engine): *"more-specific lane wins over '*'"*. Kai's `site/`, `content/`, `active-oahu/`, `okf/`, `scripts/` lanes still bind, but a file in **no** Kai lane (e.g. ROOT `.prismatic-web-governance.json`) falls through to Fred's wildcard.

## Consequences (workflow)
- To edit a protected ROOT file (`.prismatic-web-governance.json` is listed in `protected_paths`), work from a `feature/` unify branch (Fred-lane) — **not** from a `content/` branch. The branch, not the profile name, picks the enforcing identity.
- `require_issue_ref: true` — commit messages must carry a GRO-#### issue ref or the hook rejects.
- Rule 4: non-staging-governor agents cannot push `deploy-fresh`.
- Rule 5: no direct pushes to `main` — main advances by manual merge (Michael) only.

## Case: nav-fix marker fix (2026-09-03)
- Live prod + staging both served `nav-fix.css?v=16`; ROOT governance `required_production_markers` still held `v=10` (line 20).
- Owed path: edit ROOT file → commit on `feature/staging-unify-20260826` (with GRO ref) → push fast-forwards `origin/staging` → CF staging auto-deploy → PR to `main` → manual merge flips watchdog `live-production` to PASS.
- Unify state at the time: HEAD = `origin/staging` = `277b642de`, tree-equal to `origin/main` (`c7f5f509`, 0 conflicts), 5 commits ahead.

## Pitfalls
- Don't infer lane outcome from profile name or from the governance JSON's `owner_paths` alone — read `PRISMATIC_ENGINE.yaml` lanes + the current branch first.
- Watchdog stays `live-production` FAIL until `main` is actually merged; tree-equal staging is not sufficient evidence.
- In this session, multi-line terminal output repeatedly collapsed to a one-line reply (`done`/`ok`); durable evidence came from redirecting output to a `/tmp` file and reading it back. Use that pattern when tool output looks collapsed.
