# Prismatic North Star reset prompt pattern

Use this reference when Michael asks to “get Prismatic back on track,” asks for the North Star, or wants a new prompt/document to realign George/Fred/Ned/AGY/Jules around supervised self-build.

## Trigger

- User asks for a reset/course-correction prompt, North Star prompt, or Markdown/Telegram handoff document.
- Current Prismatic state has multiple drifting lanes: Engine PR/review, dashboard/runtime, dispatch/cursor, AGY/Jules capacity, PWP/Ned sequencing, or stale handoff/control records.

## Required live readback before writing

Before producing the reset prompt, do a compact direct-source readback and treat handoff/dashboard/tracker summaries as secondary:

1. `origin/main` SHA/tree for the relevant Engine repo.
2. Active PR(s): state, exact head SHA, changed paths, mergeability, hosted CI conclusions, and whether any prior review is invalidated by a new head.
3. Gateway/dashboard route health and the actual bound port being used.
4. Runtime topology: gateway/consumer/supervisor PIDs, release/checkouts/import paths, active producer count, and whether generic dispatch is paused.
5. Bus/cursor identity and any “cursor ahead of DB” or generation mismatch condition when relevant.
6. Independent repo owner lanes, especially PWP/Ned: re-read current PR/merge state and do not commandeer owner work.

## Prompt structure

The reset prompt should be durable and phase-ordered:

1. **Mission / North Star** — lead with `Don’t trust, Verify`: one exact task, one producer, preserved candidate, independent exact-artifact review, exact-head CI, George merge verdict, immutable merge-SHA release proof, then next admission.
2. **Live reset point** — list direct-source evidence with SHAs/heads/routes/cap/dispatch/runtime non-claims. Mark stale prior reviews invalidated by new heads.
3. **Authority boundaries** — allowed read/review/repair/merge-release actions versus separate explicit authorization gates: production deploy/restart, cursor/bus mutation, Linear writes, generic dispatch resume, cap increase, bulk dispatch, credentials/provider changes, PR close/delete, and dashboard replacement.
4. **Stop-the-line rules** — stale evidence, head changes, widened paths, completion before persistence, runtime/cursor contradictions, mock dashboard truth, or unauthorized side effects.
5. **Phase 0** — freeze intake and bind the truth plane with read-only live inspection.
6. **Phase 1** — close the single active Engine slice first, including exact blockers and adversarial probes. Green CI is necessary but not sufficient.
7. **Phase 2** — reconcile handoff/control/queue records before admitting another producer.
8. **Later phases** — runtime/dispatch foundation, completed-work integration marker, dashboard preservation, and cap promotion gates.
9. **Required outputs** — exact-head review packet, verbose logs/digests, George merge-judge verdict, merge-SHA release receipt if merged, reconciled durable state, and one next task `QUEUED_NOT_DISPATCHED` until cap is free.

## Report/file delivery pattern

- Save the reset prompt as a Markdown artifact under the George profile reports directory, then read back key sections and compute `sha256sum`/line count.
- In Telegram, deliver it with `MEDIA:/absolute/path/to/file.md` and a compact proof packet.
- Do not claim that creating the prompt completed review, merge, deploy, runtime parity, cursor repair, cap increase, or autonomous production readiness.

## Compact receipt template

```text
STATUS=PARTIAL
VERDICT=NOT_REVIEWED
TASK=Prismatic North Star reset / controlled self-build runway
BASE_SHA=<repo-main-sha>
HEAD_SHA=<active-pr-head-or-N/A>
CHANGED_PATHS=<active-pr-paths-or-N/A>
COMMAND=live GitHub/Gateway/process readback + Markdown readback + sha256sum
RESULT=PASS
LOG=<absolute-md-path>
LOG_SHA256=<sha256>
SCOPE=North Star reset prompt and current runway boundaries
AD_HOC_OR_CANONICAL=ad-hoc targeted live readback
GENERIC_DISPATCH=PAUSED
CAP=1
NOT_CLAIMING=exact-head clean review, merge, deployment, runtime parity, dispatch readiness, cursor repair, cap increase, or autonomous production readiness
MARKER=PRISMATIC_NORTH_STAR_RESET_<date>
```
