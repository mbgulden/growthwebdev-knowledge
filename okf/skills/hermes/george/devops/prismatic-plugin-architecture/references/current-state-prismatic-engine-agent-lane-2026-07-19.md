# Prismatic Engine current state — agent lane / George handoff (2026-07-19)

Purpose: keep George from needing Kai/Michael to re-prompt the same Prismatic Engine context. This is a durable handoff reference for George's `prismatic-plugin-architecture` skill.

## Current repo/runtime snapshot

- Primary repo checkout for the active Kai work: `/home/ubuntu/work/prismatic-pwp-ubersuggest-auth`.
- Runtime gateway worktree: `/home/ubuntu/.prismatic/runtime/prismatic-engine`.
- Runtime service: `prismatic-gateway.service`, port `9000`, working directory `/home/ubuntu/.prismatic/runtime/prismatic-engine`.
- Runtime HEAD as of this handoff: `4f554ae` / PR #328, `Add one-agent verified PR dry-run bridge`.
- `origin/main` as of this handoff: `4f554ae`.
- Active Kai branch/PR as of this handoff: PR #329, `feature/agy-completed-work-packet-classification-readmodel`, head `6861e9ee`, merge state `CLEAN`, CI green across py3.10/3.11/3.12/3.13 plus build package.

## What is already landed on main/runtime

Recent merged stack:

1. PR #316 — Prompt 4 assigned-agent integration lane.
2. PR #317 — Prompt 5.2 completed-work PR candidate lifecycle.
3. PR #318 — Prompt 5.3 operator-approved PR creation dry run.
4. PR #319 — Prompt 5.4 real PR approval gate.
5. PR #320 — Prompt 5.5 approved real PR executor gate.
6. PR #321 — Prompt 6 executor audit canary dry-run lane.
7. PR #322 — Prompt 7 executor API audit writeback.
8. PR #323 — AGY CLI context work packets.
9. PR #325 — Jules CLI session context packs.
10. PR #326 — completed-work log ingestion bridge.
11. PR #327 — one-agent dashboard + Linear dry-run bridge.
12. PR #328 — one-agent verified PR dry-run bridge.

The live runtime proves the dry-run bridge surfaces are available with these local GET routes:

```text
GET http://127.0.0.1:9000/health -> 200
GET http://127.0.0.1:9000/api/agy/completed-work -> 200, marker AGY_COMPLETED_WORK_INGESTION_OK, count 9 at handoff
GET http://127.0.0.1:9000/api/agy/completed-work/dashboard-linear-dry-run/latest -> 200, marker ONE_AGENT_COMPLETED_WORK_TO_DASHBOARD_LINEAR_DRY_RUN_OK
GET http://127.0.0.1:9000/api/agy/completed-work/verified-pr-dry-run/latest -> 200, marker ONE_AGENT_COMPLETED_WORK_TO_VERIFIED_PR_DRY_RUN_OK
GET http://127.0.0.1:9000/api/gateway/signals -> 200, signal stream currently has AGY work-result packets
GET http://127.0.0.1:9000/api/webhooks/queue -> 200, shows dispatched queue rows such as GRO-3954
```

Use the exact `/latest` dry-run routes above; `/api/agy/latest-completed-work`, `/api/agy/completed-work/dashboard-linear-dry-run`, `/api/agy/completed-work/verified-pr-dry-run`, and `/api/gateway/webhooks/queue/stats` returned 404 in Kai's probe, so do not use those as proof routes unless later code adds them.

## Active open PRs to understand

- PR #329 — `Add AGY packet classification read model`: current active good PR. Adds packet-level classifications: `packet_valid`, `packet_blocked`, `packet_failed`, `packet_malformed`, `packet_missing`, and `needs_manual_review`; exposes `packet_classification` / `normalized_record`; preserves original raw-packet validation before defaults. Local Kai guard verification passed: `tests/test_agy_completed_work.py` = 22 passed; ruff check/format pass; marker `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`. CI is green and merge state is clean.
- PR #324 — `GRO-3969: Document AGY overnight readiness guard design`: clean docs PR, but not the immediate golden path unless Michael directs.
- PR #315 — raw agent output repair queue: open but dirty/stale against current main; inspect before merging.
- PR #301 — older AGY overnight readiness guard: now dirty/stale versus the much newer PR #316-#328 stack; reconcile before acting.
- PR #293 — older AGY autopilot result packet contract: dirty/stale; do not treat as current source of truth.
- PR #282, #249, #250 are older/open context; do not merge without scope review.

## Linear roadmap state

The Agent Output Resilience roadmap was materialized in Linear and verified in `/tmp/agent-output-resilience-linear-created.json`:

```text
verified.expected_titles=22
verified.found_titles=22
verified.missing=[]
verified.parent_fail=[]
```

Key issue identifiers:

- Epic 1: GRO-3949 — Canonical Agent Output Contract.
  - GRO-3950 — Define canonical completed-work packet v1.
  - GRO-3951 — Add agent dialect normalizers.
  - GRO-3952 — Preserve raw agent output before normalization.
- Epic 2: GRO-3953 — Invalid Packet Repair and Rerun Lane.
  - GRO-3954 — Invalid packet queue + repair hints.
  - GRO-3955 — One controlled rerun policy.
- Epic 3: GRO-3956 — Agent Skill Packs for Best Output.
  - GRO-3957 — Shared Prismatic completed-work skill.
  - GRO-3958 — AGY skill pack.
  - GRO-3959 — Fred skill pack.
  - GRO-3960 — George skill pack.
- Epic 4: GRO-3961 — Multi-Agent Completed-Work Lane.
  - GRO-3962 — Agent registry for output dialects and permissions.
  - GRO-3963 — Per-agent preflight and packet validation.
  - GRO-3964 — Multi-agent dashboard output view.
- Epic 5: GRO-3965 — One-Task Autopilot Recovery Loop.
  - GRO-3966 — Fix AGY packet normalization and rerun one-task dry run.
  - GRO-3967 — One-task dry run recovery matrix.
- Epic 6: GRO-3968 — Limited Overnight Readiness Guard.
  - GRO-3969 — Overnight readiness guard design.
  - GRO-3970 — Limited overnight dry run, no auto-merge.

George's natural ownership lane: verify dashboard/API/writeback/operator-state, especially GRO-3960, GRO-3964, GRO-3967, and any live dashboard/route proof after Fred/AGY implementation.

## Direction / golden path from here

Do not re-open old prompts unless Michael specifically asks. The true next runway is:

1. Merge PR #329 only after head/CI/mergeability checks remain green.
2. Sync local `main` and runtime deliberately to the merged commit.
3. Restart gateway and smoke local runtime routes.
4. Prove packet-classification read model at runtime without posting unsafe production demo junk.
5. Continue the one-agent lane from the live dry-run bridge toward dashboard/operator verification:
   - completed work -> dashboard/Linear dry-run -> verified PR dry-run -> George dashboard/API verification -> then only later controlled limited AGY dry-run.
6. Keep PR creation, Linear writeback, auto-merge, bulk dispatch, and production deploy side effects disabled unless Michael explicitly authorizes them.

## George operating guidance

George should act as the verification/integration guardian, not as a hype bot:

- Reconcile live state before acting: check `origin/main`, current PRs, runtime HEAD, service port, route table, and API responses.
- Prefer local GET/TestClient/dashboard proof before claiming runtime readiness.
- If a marker appears only inside a prompt/template, ignore it. Require exact proof lines such as `RESULT=PASS` plus `MARKER=..._OK`.
- For dashboard claims, check real routes and markers; browser/console/visual proof is preferred when the claim is UI readiness.
- For completed-work claims, distinguish dry-run plans from real side effects. Side-effect fields must stay false unless Michael gave explicit approval.
- For stale open PRs (#301/#293/#315), reconcile against current main and newer merged PRs before recommending merge.
- Use compact proof packets:

```text
COMMAND=<exact command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<what was verified>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<explicit boundaries>
MARKER=<marker>
```

## Non-claims at handoff

This handoff does **not** claim:

- broad overnight AGY autopilot is active;
- bulk Linear task processing is safe;
- auto-merge is enabled;
- real GitHub PR creation is enabled by default;
- real Linear writeback is enabled by default;
- production deployment is being performed by the agent lane;
- every stale open PR is mergeable or useful.

Current honest state: the foundation and one-agent dry-run bridges are now strong; the next useful George role is verifying the operator/dashboard/API state around the packet-classification merge and the dry-run bridge, while keeping real side effects guarded.
