# Stability Course-Correction Prompt Pattern

Use this reference when Michael asks to quantify Prismatic state and provide a course-correction plan/prompt.

## Trigger

Michael asks variants of:

- “where are we at?”
- “quantify Prismatic Engine”
- “if course correction is needed, give me a plan/prompt”
- “are we stable / production grade / ready to scale?”

## Required posture

Do not answer from the handoff alone. Perform or request a compact live readback, then convert the result into a decision-ready correction prompt. Prefer a downloadable `.md` prompt when the plan has multiple phases or must be handed to another lane.

## Assessment shape

Report maturity as separate tracks, not one blended optimism score:

| Track | Meaning |
|---|---|
| Operator-supervised stability | Can George safely run bounded work with exact-artifact review? |
| Autonomous production operation | Can producers verify/promote/recover without manual correction? |
| Runtime convergence | Are gateway, consumer, supervisor/profile scripts, runtime checkout, and current main on known compatible immutable SHAs? |
| Portability/distribution readiness | Can a fresh environment install, boot, exercise dashboard/API/dispatch, back up, and roll back? |
| Dashboard/operator visibility | Is the live dashboard truthful, rendered, and free of mock/unlabeled/runtime-stale claims? |

Use judgment ranges only when they are clearly labelled as judgment. Keep proof immediately next to the score.

## Live readback minimum

Before judging, gather enough direct evidence to avoid stale handoff optimism:

1. Current `origin/main`, local runtime branch/head/dirty state, and open PR head/checks/mergeability.
2. Gateway `/`, `/dashboard`, health, and key API status.
3. Runtime topology: gateway release SHA, consumer release SHA, supervisor/profile-script source, current main/release SHA.
4. Active producers/processes, stage/cap, generic dispatch pause/resume state.
5. Handoff/control-state claims, explicitly comparing them against direct process/GitHub/runtime proof.
6. Current distribution/readiness/portability blocker classification.

If handoff/control JSON says a producer is active but process/GitHub evidence says the work has become a PR or exited, classify it as **coordination-state drift**. Repair the state before claiming completion or launching another producer.

## Course-correction prompt phases

A durable correction prompt should usually include these gates:

1. **Independent exact-head PR review** — verify base/head/tree, changed-path scope, diff behavior, focused/canonical/release/build/wheel/real-smoke proof, and refreshed exact-head GitHub CI. Verdict is only `CLEAN` or `REPAIR`.
2. **Merge/release boundary** — only after `CLEAN` + exact-head CI; read back GitHub merge SHA; build standalone immutable release with no alternates or mutable checkout dependency; run post-merge proof from that release.
3. **Coordination-state reconciliation** — update handoff/control truth so stale active-producer claims, contradictory labels, and old PR states do not drive launches.
4. **Runtime convergence audit** — gateway/consumer/supervisor/current-main parity, with split topology reported as `PARTIAL` until intentionally resolved.
5. **Dashboard truth** — rendered desktop/mobile proof, browser console, API truth, static asset dependency, and real-vs-mock labelling.
6. **Portability drill** — fresh-host/container install, boot, dashboard/API, exact dry-run dispatch canary, backup, rollback, cleanup. Wheel install alone is not clean-room portability.
7. **Cap decision** — cap increase only after repeated clean cap-1 cycles, converged runtime, and clean-room proof; never from one PR or CI green alone.

## Stop conditions to include

Stop and report `BLOCKED` if:

- PR head changes after evidence collection;
- changed-path scope expands unexpectedly;
- independent review returns `REPAIR`;
- GitHub CI is incomplete/failing;
- verifier crashes;
- runtime source cannot be bound to immutable SHAs;
- the next side effect requires deploy/restart, Linear mutation, generic dispatch, cap increase, or secret/provider action not explicitly authorized.

## Compact proof packet

```text
STATUS=<PASS|PARTIAL|BLOCKED>
VERDICT=<CLEAN|REPAIR|NOT_REVIEWED>
BASE_SHA=<sha>
HEAD_SHA=<sha>
TREE_SHA=<sha>
MERGE_SHA=<sha-or-NOT_MERGED>
CHANGED_PATHS=<exact list>
COMMAND=<exact command or grouped summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<absolute path>
LOG_SHA256=<sha256>
SCOPE=<scope>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|GitHub CI|production proof|browser proof|canonical suite>
RUNTIME_PARITY=<unified|split + exact SHAs>
DISTRIBUTION_VERDICT=<PUBLISHABLE|NOT_PUBLISHABLE|BLOCKED>
GENERIC_DISPATCH=<PAUSED|RESUMED>
CAP=<n>
ACTIVE_PRODUCERS=<n>
NOT_CLAIMING=<non-claims>
NEXT_GATE=<one exact next action>
MARKER=<course-correction-marker>
```

## Common overclaim traps

- Dashboard HTTP 200 is not production-grade autonomy.
- CI green is not deployment or runtime parity proof.
- An immutable wheel is not clean-room portability.
- A real readiness failure after the verifier runs is `NOT_PUBLISHABLE`, not a verifier failure.
- A verifier crash is `BLOCKED`, not a readiness verdict.
- Stale control-state “active producer” fields are coordination debt, not proof that work is still running.
