# Verification nudges need human outcome recap — 2026-07-16

## Trigger

Michael corrected the agent after repeated platform verification nudges produced responses like “created verifier, ran verifier, removed verifier, checks passed” without explaining in human language what actually changed or whether the intended outcome happened.

## Durable lesson

For verification-only system nudges, still run the requested fresh `/tmp/hermes-verify-*` script or named canonical command. But the final answer must include both:

1. **Fresh verification evidence** — verifier path, cleanup, scoped checks, and “ad-hoc not suite green.”
2. **Human result recap** — one or two plain-English sentences saying what changed and whether the user-facing/system-facing outcome actually happened.

## Good shape

```md
✅ Fresh ad-hoc verification passed.

Human result: the staging checkpoint commit exists and was pushed; the orchestrator now provisions from the repo-local guest template. The coach dashboard shell is live, coach data APIs remain gated, and the report PDF follow-up still returns media metadata.

Verifier: `/tmp/hermes-verify-abc123.py` created, run, and removed.
Checks: compile, nginx -t, dashboard 200, API 401, report auth 200, PDF metadata, secret scan.
Scope: focused ad-hoc verification, not full suite green.
```

## Bad shape

```md
✅ Fresh ad-hoc verification passed.
Verifier removed.
Checks passed.
```

Accurate, but operationally unhelpful. Michael should not have to infer whether the actual thing happened from CI-style mechanics.
