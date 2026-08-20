# Production Governance Readiness Audit Pattern — 2026-07-19

## Trigger

Use this when Michael asks whether Prismatic governance, agent orchestration, filesystem bus/autopacer work, dashboard governance, or OKF/North-Star work is **actually integrated, live, and 100% production ready**.

## Key lesson

Do not equate a live host-level bridge with production-ready Prismatic Engine governance.

The filesystem agent bus/autopacer can be live and useful while still failing the highest Prismatic standard because it is outside PE Core, outside the durable dashboard/API source of truth, and lacks clean PR/merge/deploy/browser/rollback proof.

Use this distinction:

```text
Live interim governance bridge: can be PASS
Production-grade Prismatic governance: may still be BLOCKED
```

## Source standards to compare

Always compare against these repo docs, not just recent chat claims:

- `docs/north-star.md`
  - public local-launch / developer preview
  - dashboard is intended primary touchpoint
  - Telegram/headless is bridge/notification
  - public claims need code, docs, tests, API/CLI/dashboard proof, real verification output
- `docs/okf-evidence-map.md`
  - Objective → Key Result → Function → Evidence
  - dashboard-ready workflows show objective, status, run/preview/approve action, evidence links, audit history, fallback CLI/API command
- `research/rubric-inventory-matrix.md`
  - 9–10 = production-grade, implemented, automated end-to-end, documented, and verified under CLI/API/dashboard proof
  - 5–6 = partial local/script/API path without full Gateway/dashboard/operator integration
- `docs/prismatic-production-durability-standard.md`
  - clean production-safe branch/worktree
  - local route/API/browser proof
  - path-safety/security proof
  - intentional deploy/restart/reload
  - public/authenticated proof
  - screenshot/browser/console proof
  - durable runtime source readback
  - rollback packet

## Audit method

Run a live source-and-runtime audit before answering:

1. Repo and runtime source state:
   - `/home/ubuntu/work/prismatic-engine` branch/HEAD/dirty status
   - `/home/ubuntu/.prismatic/runtime/prismatic-engine` branch/HEAD/dirty status
   - `systemctl show prismatic-gateway.service -p ExecStart -p WorkingDirectory -p ActiveState -p SubState`
2. Service/timer state:
   - `prismatic-gateway.service`
   - Hermes Kai/Fred/George gateways
   - bus timers
   - governance autopacer timer
3. Local API/dashboard proof:
   - `/health`
   - `/dashboard`
   - plugin governance APIs (`/api/plugins/catalog`, `/governance`, `/jobs`, `/artifacts`, `/audit-events`, `/api/pwp/status`)
   - agent/bus or queue APIs if present
4. Public/browser proof if production readiness is being claimed:
   - public `/dashboard` status
   - authenticated/browser screenshot or DOM proof
   - console review for fatal JS errors
5. Smoke commands when relevant:
   - `python scripts/public_launch_smoke.py`
   - `python scripts/public_security_readiness_audit.py`
   - `python scripts/release_smoke.py`
6. Agent governance bridge state:
   - bus inbox/claimed/outbox/audits/archive/failed counts
   - George audit artifacts
   - repo marker presence for claimed production markers
7. 10/10 rubric closure:
   - check whether the rubric baseline/evidence ledger still contains TBD/gap rows
   - do not accept “100%” if closure ledger is absent or P0s remain

## Scoring and verdict

Use a gate scorecard, not a yes/no vibe check.

Recommended gates:

| Gate | What it tests |
|---|---|
| Public local launch / developer preview | public smoke and local first-user path |
| Security readiness / local-first boundaries | public security audit and documented remote-hosted caveats |
| Release smoke / package coherence | release smoke and packaging readiness |
| Local dashboard/API governance surfaces | dashboard and governance APIs respond locally |
| Filesystem bus/autopacer live operation | host-level bridge is active and producing audit artifacts |
| PE Core integration of agent governance | bus/state/control is first-class PE Core/dashboard/API, not just `/home/ubuntu/prismatic-agent-bus` |
| Assigned-agent durable dispatch/writeback | event → resolver → preflight → exact wake → result/blocker writeback |
| Production durability standard | clean PR/deploy/runtime/public/browser/rollback proof |
| Public/authenticated dashboard proof | actual public/dashboard browser proof |
| 10/10 rubric closure ledger | baseline scores, evidence, follow-up tasks for <=8, closure proof |

Classification:

```text
PASS = live and production-standard evidence exists
PARTIAL = useful implementation exists but a proof/integration layer is missing
BLOCKED = P0 standard gap prevents production-ready claim
```

Typical P0 blockers for a host-level bridge:

- PE Core integration missing: bridge is outside repo/runtime Core and dashboard/API source of truth.
- Assigned-agent durable dispatch/writeback missing.
- Production durability packet missing: no clean PR/merge/deploy/browser/rollback proof.
- 10/10 rubric closure ledger missing or still TBD.

## Reporting pattern

Lead with the answer Michael needs:

```text
Status: BLOCKED — not 100% production-ready governance
Score: <x>/10
Live interim bridge: yes/no
Production Prismatic governance: yes/no
```

Then provide:

1. compact proof packet;
2. direct answer;
3. downloadable full audit report;
4. downloadable short digest;
5. what is live;
6. what blocks production ready;
7. required closeout path to 100%.

For large audits, write both:

```text
/home/ubuntu/prismatic-agent-bus/audits/PRODUCTION_GOVERNANCE_AUDIT_<date>.md
/home/ubuntu/prismatic-agent-bus/audits/PRODUCTION_GOVERNANCE_AUDIT_DIGEST_<date>.md
```

Verify report artifacts with a temporary `/tmp/hermes-verify-*` script and include cleanup proof.

## Important boundary language

Use this exact distinction when true:

```text
The governance bridge is live and useful, but it is not 100% production-ready Prismatic Engine governance.
It is a live safe-mode/interim control plane until it is integrated into PE Core/dashboard/API and proven through the production durability ladder.
```

Do not sugarcoat “100% production ready” if any P0 remains.
