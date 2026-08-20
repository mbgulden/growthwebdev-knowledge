# Production durability standard and route-fix gates

## When this applies

Use this when a production-facing Prismatic route, dashboard page, gateway endpoint, or public/authenticated operator surface fails, especially if the failure exposes a deeper durability problem rather than a single route bug.

Worked trigger: `/workspace-tree` black page / missing route. The lesson is broader than workspace-tree: production must not depend on a mutable shared development worktree being on the right branch, and no agent should claim a production route is fixed without local gateway proof, public/authenticated proof, path-safety proof, and browser/screenshot proof.

## Standard artifacts now expected

The repository standard is encoded in:

```text
docs/prismatic-production-durability-standard.md
docs/agent-production-route-checklist.md
scripts/verify_production_durability_standard.py
```

Required markers:

```text
PRODUCTION_DURABILITY_STANDARD_DOC_OK
AGENT_PRODUCTION_ROUTE_CHECKLIST_OK
PRODUCTION_DURABILITY_VERIFIER_OK
PRISMATIC_PRODUCTION_DURABILITY_STANDARD_OK
```

## Required production-facing workflow

Every production route fix must follow this ladder:

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

## Verifier usage pattern

For standard/checklist/verifier verification:

```bash
python3 -m py_compile scripts/verify_production_durability_standard.py prismatic/gateway/server.py
python3 scripts/verify_production_durability_standard.py \
  --route /workspace-tree \
  --local-base http://127.0.0.1:9000
```

This standard mode is credential-free. Public/authenticated checks may report:

```text
skipped_auth_required
```

when no authenticated session or public base is supplied.

For an actual production route fix closeout, hard enforcement must be used:

```bash
python3 scripts/verify_production_durability_standard.py \
  --route /workspace-tree \
  --local-base http://127.0.0.1:9000 \
  --require-local \
  --enforce-route
```

In standard mode, reachable local route gaps are `needs_action` warnings so the standard can ship before the first route repair. In enforce mode, those same route gaps are failures.

## Fresh verification discipline

If Hermes reports stale verification after docs/scripts changed, rerun a compact focused verifier under `/tmp` using a tempfile path with prefix:

```text
/tmp/hermes-verify-*.py
```

Keep the final output compact enough for detectors to see:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=<actual compile/verifier command>
AD_HOC_VERIFICATION=PASS
changed_paths_checked=[...]
cleanup=PASS removed /tmp/hermes-verify-*.py
```

Avoid giant nested command outputs in the final JSON; summarize verifier results instead. Large/truncated outputs can make automation think no fresh canonical command was detected even when it ran.

## Proof packet boundary

Always label this as:

```text
ad-hoc targeted standard/route verification — not canonical full suite green
```

Do not claim a route is fixed merely because the standard verifier passes in non-enforce mode. For `/workspace-tree`, enforce mode must pass, public/authenticated route proof must be attached, and browser/screenshot proof must exist before claiming the production route itself is fixed.

## Pitfalls

- Do not patch production-facing routes from a mutable shared worktree and call that durable.
- Do not use local `/health` as proof a user route works.
- Do not treat Cloudflare/auth blocking as public proof; label it `skipped_auth_required` with the exact response.
- Do not let CDN failures blank a critical page shell; require visible fallback/degraded states.
- Do not merge or mark Done from AGY dispatch success alone. Review output scope and evidence first.
- Do not confuse standard-mode verifier OK with route-fix closeout OK; use `--enforce-route --require-local` for route closeout.
