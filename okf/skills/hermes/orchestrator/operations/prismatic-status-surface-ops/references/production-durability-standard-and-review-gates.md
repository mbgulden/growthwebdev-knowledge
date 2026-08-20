# Production durability standard and review gates

Use this reference when a Prismatic production-facing route/service/dashboard change is being standardized, reviewed, or fixed after a durability incident.

## Core lesson

The `/workspace-tree` black-page incident is not just a route bug. It exposed a production-standard failure:

```text
production route fixed ≠ code edited
standard installed ≠ /workspace-tree fixed
ad-hoc targeted proof ≠ canonical suite green
```

Production must live from durable, reviewable source and must be proven through local, public/authenticated, browser, and rollback gates before any agent claims it is fixed.

## Required workflow

Every production-facing Prismatic fix must follow:

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

## Durable artifacts now expected in repo

The standard class is represented by these repo artifacts:

- `docs/prismatic-production-durability-standard.md` — canonical standard (`PRODUCTION_DURABILITY_STANDARD_DOC_OK`).
- `docs/agent-production-route-checklist.md` — agent route checklist (`AGENT_PRODUCTION_ROUTE_CHECKLIST_OK`).
- `docs/production-durability-review-gate.md` — PR/review question block (`PRODUCTION_DURABILITY_REVIEW_GATE_OK`).
- `docs/prompts/production-durability-agent-brief.md` — reusable AGY/Fred/Kai/Ned/Jules brief (`PRODUCTION_DURABILITY_AGENT_BRIEF_OK`).
- `docs/production-worktree-durability-migration-plan.md` — production worktree migration plan (`PRODUCTION_WORKTREE_DURABILITY_PLAN_OK`).
- `scripts/verify_production_durability_standard.py` — credential-free verifier (`PRODUCTION_DURABILITY_VERIFIER_OK`).

## Review-gate questions

For any production-facing PR/review, require answers to:

- Does this affect a live route/service/dashboard?
- Where is the production-safe branch/worktree proof?
- Where is local gateway/service proof?
- Where is security/path traversal proof?
- Where is public/authenticated proof?
- Where is screenshot/browser proof?
- What is the rollback path?
- Is this `ad_hoc_targeted`, `canonical_suite_green`, or `skipped_auth_required`?

If the repo lacks a central GitHub PR template, point agents to `docs/production-durability-review-gate.md` and say future templates should import that block.

## Verifier pattern

Use the standard verifier in two modes:

```bash
python3 -m py_compile scripts/verify_production_durability_standard.py prismatic/gateway/server.py
python3 scripts/verify_production_durability_standard.py --route /workspace-tree --local-base http://127.0.0.1:9000
```

Standard mode is credential-free and may report public/auth checks as `skipped_auth_required`.

For real route-fix closeout, enforce local route expectations:

```bash
python3 scripts/verify_production_durability_standard.py \
  --route /workspace-tree \
  --local-base http://127.0.0.1:9000 \
  --require-local \
  --enforce-route
```

A failure in enforce mode is useful evidence, not a verifier failure, when the route has not been fixed yet. Report the exact blockers, e.g. route table missing, local route 404, safe preview missing.

## Production worktree policy

Durability invariant:

```text
live service source != mutable multi-agent development checkout
```

If `prismatic-gateway.service` reads back as:

```text
WorkingDirectory=/home/ubuntu/work/prismatic-engine
```

then production is still using the mutable multi-agent dev checkout. Do not silently leave that risk unnamed. Either implement a dedicated runtime checkout migration safely or document/track a follow-up issue.

Preferred target:

```text
/home/ubuntu/.prismatic/runtime/prismatic-engine
```

Use marker `PRODUCTION_WORKTREE_DURABILITY_OK` only if implemented. Use `PRODUCTION_WORKTREE_DURABILITY_PLAN_OK` if documented/planned.

## Fresh verification proof packets

When the system says verification is stale, produce a compact `/tmp/hermes-verify-*` script. Keep the output small enough that the detector can see:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=...
AD_HOC_VERIFICATION=PASS
changed_paths_checked=[exact paths]
cleanup=PASS removed /tmp/hermes-verify-...
```

Avoid dumping nested child verifier JSON into the final proof. Run child commands but summarize them as compact pass/fail fields so the verification detector does not miss the proof due to truncation.

## Pitfalls

- Do not claim `/workspace-tree` fixed because the standard/verifier shipped.
- Do not claim production fixed from code/static checks alone.
- Do not use `PRODUCTION_WORKTREE_DURABILITY_OK` unless the live service source was actually migrated and read back.
- Do not hide public proof behind localhost proof. If auth blocks it, say `skipped_auth_required` with the exact reason.
- Do not over-scope standard work into a full production platform rewrite; standard/review gate/verifier can ship separately from the route fix and systemd migration.
