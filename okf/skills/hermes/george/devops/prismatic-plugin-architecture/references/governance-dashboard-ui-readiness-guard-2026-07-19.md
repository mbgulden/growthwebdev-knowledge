# Governance dashboard UI readiness guard — 2026-07-19

Use this note when Michael asks to make Prismatic governance dashboard UI complete, tested, portable, or durable after the agent-governance/autopacer bridge is already running.

## Durable lesson

Do not treat a completed safe-mode backlog or a green monitor percent as dashboard production readiness. A governance dashboard claim needs immediate UI/API/browser proof and then explicit backlog gates for any missing production-readiness work.

## Good response pattern

1. **Load the Prismatic dashboard/governance skill context** and preserve the existing canonical dashboard shell. Do not replace the dashboard with a new mini/fallback UI.
2. **Check active lane state** before adding work. If Kai/Fred already have active tasks, extend the backlog but do not bulk-dispatch; let the autopacer advance after current results/audits.
3. **Run immediate readiness probes** before reporting:
   - local `/` and `/dashboard` route probes;
   - public `/` and `/dashboard` route probes where configured;
   - governance/agent status API route probes;
   - `scripts/dashboard_visual_qa.py`;
   - public/release smoke with correct repo import context when needed;
   - focused dashboard/API pytest;
   - inline dashboard JS extraction + `node --check`;
   - browser render/DOM/console snapshot.
4. **Classify honestly**:
   - `PASS` for surfaces actually proven;
   - `PARTIAL` when UI is live/testable but not merged/deployed/browser-mobile/source-readback/rollback proven;
   - `BLOCKED` when local/public route or core UI/API tests fail.
5. **Add explicit next backlog gates** instead of vague “keep improving dashboard” tasks:
   - `GOVERNANCE_DASHBOARD_UI_API_CONTRACT_OK` — API/read-model contract for lane state, task detail, proof links, audit events, approval gates, side-effect policy, durability status, portability/readiness fields, and source labels.
   - `GOVERNANCE_DASHBOARD_UI_COMPLETION_AUDIT_OK` — UI inventory and gap closure; no mock/sample/no-op truth presented as live.
   - `GOVERNANCE_DASHBOARD_PORTABLE_DURABLE_VISUAL_QA_OK` — local/public/browser/mobile/console/source-readback/rollback proof; production CDN fragility removed or explicitly classified.
6. **Update the human monitor denominator/sections** after adding new gates so it does not keep reporting 100% against the old backlog.
7. **Write a small guard report** under the bus audit/report area with evidence, blockers, checklist, and compact proof packet.

## Evidence shape that worked

```text
LOCAL_ROOT=/ -> 200 OK
LOCAL_DASHBOARD=/dashboard -> 200 OK
PUBLIC_ROOT=https://.../ -> 200 OK
PUBLIC_DASHBOARD=https://.../dashboard -> 200 OK
AGENT_GOVERNANCE_API_LOCAL=/api/gateway/agents/governance-status -> 200 OK
AGENT_GOVERNANCE_API_PUBLIC=/api/gateway/agents/governance-status -> 200 OK
DASHBOARD_VISUAL_QA=PASS
PUBLIC_LAUNCH_SMOKE=PASS
RELEASE_SMOKE=PASS
FOCUSED_TESTS=PASS
DASHBOARD_JS_NODE_CHECK=PASS
BROWSER_RENDER=PASS nonblank dashboard
BROWSER_CONSOLE=PARTIAL if warnings remain, e.g. Tailwind CDN production warning
```

## Common blockers / non-claims

- Dirty feature branch is not production durability.
- Browser console with `cdn.tailwindcss.com should not be used in production` is a portability/durability warning until removed, bundled, or explicitly accepted as a non-production limitation.
- Static visual QA is not full browser/mobile screenshot proof.
- Local route proof is not public proof; public proof is not merge/deploy/rollback proof.
- `100%` in a monitor only means the current backlog denominator, not product completeness.

## Compact proof marker

Use a marker like:

```text
MARKER=GOVERNANCE_DASHBOARD_UI_READINESS_GUARD_OK
RESULT=PARTIAL
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=complete production-ready dashboard, merge, deploy, PR creation, production restart, canonical full-suite green, full mobile screenshot pack
```
