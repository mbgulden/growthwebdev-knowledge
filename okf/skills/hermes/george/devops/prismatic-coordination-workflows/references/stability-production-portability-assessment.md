# Stability / Production-Grade / Portability Assessment

Use this reference when Michael asks how close Prismatic is to stable, production-grade, portable, or ready to build itself.

## Core distinction

Report three separate maturity tracks:

1. **Operator-supervised stability** — can George safely run bounded work with explicit review and containment?
2. **Autonomous production-grade operation** — can producers complete, verify, promote, and recover without false state or manual correction?
3. **Portability** — can a fresh environment install, boot, exercise the dashboard/API/dispatcher, back up, and roll back without Michael-specific paths or mutable checkout dependence?

Do not collapse these into one “stable” label.

## Live proof checklist

Before answering, prefer live evidence over handoff optimism:

- Gateway/API health: `/`, `/dashboard`, and key APIs return HTTP 200 from the configured service.
- Runtime parity: identify gateway, consumer, supervisor/profile-script, immutable release SHA, and current `origin/main`. Split release topology is `PARTIAL`, not unified production parity.
- Producer state: active processes, stage/cap, generic dispatch paused/resumed, exact issue in flight.
- PR state: exact head SHA, CI rollup, mergeability, review condition, merged/unmerged truth.
- Completion containment: false `agent.completed` rows invalidated; Linear labels/status restored; no unauthorized PR/promotion/process side effects.
- Portability gate: wheel install is necessary but insufficient. Run distribution-readiness and, when possible, a fresh-host/container clean-room install/boot/dashboard/canary/backup/rollback proof.

## Reporting pattern

Use ranges or qualitative maturity when no canonical rubric score exists, and label them as judgment ranges:

```text
SUPERVISED_STABILITY=<percent/range + reason>
AUTONOMOUS_PRODUCTION_GRADE=<percent/range + reason>
PORTABILITY=<percent/range + reason>
EVIDENCE=<commands/URLs/PRs/logs/SHA>
BOUNDARY=<non-claims>
NEXT_GATE=<exact slice>
```

Good language:

- “Stable under George supervision, not autonomous production-grade.”
- “Operationally live, but not unified current-main runtime parity.”
- “Wheel install passed; clean-room portability is not established.”
- “A verifier crash is `BLOCKED`, not a portability pass.”

Avoid:

- Calling the dashboard/API healthy state “production-grade” by itself.
- Treating PR CI green as runtime deployment proof.
- Treating one self-build success as permission to raise cap.
- Treating producer self-review or `RESULT.md` text as trusted completion.

## Self-building boundary

When discussing “Prismatic building Prismatic,” frame it as a controlled flywheel:

1. One exact issue at cap 1.
2. Producer output is untrusted until George verifies the exact candidate snapshot.
3. If review finds blockers, repair the same issue before launching the next one.
4. Merge only from exact-head CI + independent review + authorization.
5. Deploy only after separate operational authorization and immutable-release proof.
6. Raise cap only after repeated clean cycles and formal recovery/rollback drills.

Generation speed can increase before autonomous trust does. Verification/promotion is the bottleneck; scale producers only when verification throughput and false-completion containment are proven.