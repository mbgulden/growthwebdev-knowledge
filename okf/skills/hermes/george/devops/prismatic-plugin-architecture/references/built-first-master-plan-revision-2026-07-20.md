# Built-first Prismatic master-plan revision — 2026-07-20

## Trigger

Michael challenged a Prismatic master plan that was directionally right but still framed too much as greenfield building. His correction: base the master plan on what has already been built, use as much as possible, optimize/build on top, and surgically remove only what does not fit the new plan.

## Durable lesson

For Prismatic architecture, dashboard, control-center, plugin, assigned-agent, and production-readiness planning, use a **built-first** planning model:

```text
inventory what exists
→ preserve every useful implementation and proof contract
→ identify whether the problem is source, integration, deployment, UI, or proof
→ reconnect existing surfaces
→ harden unsafe boundaries
→ complete missing lifecycle steps
→ generalize narrow/hardcoded implementations
→ retire only proven duplicate/dead/misleading surfaces
```

Do not start from “build auth / build dashboard / build completed-work / build backup” when Prismatic already has partial implementations. Rephrase as “wire existing auth,” “reconnect existing dashboard adapters,” “generalize existing completed-work spine,” or “complete existing backup with restore/drill.”

## Disposition vocabulary

Use one disposition per asset:

| Disposition | Meaning |
|---|---|
| KEEP | Canonical foundation; do not rewrite. |
| RECONNECT | Implementation exists but live dashboard/proxy/runtime is not using it correctly. |
| HARDEN | Implementation works but has security, durability, concurrency, truth-boundary, or operational gaps. |
| COMPLETE | Preserve the contract and add missing lifecycle/UI/receipt/restore/proof steps. |
| GENERALIZE | Preserve useful logic but remove hardcoded issue/agent/single-environment assumptions. |
| REPLACE SURGICALLY | Swap a narrow adapter/label/dependency without replacing the surrounding system. |
| RETIRE AFTER PROOF | Remove only after usage search, parity, migration/readback, compatibility period, and rollback path. |

## Assets to treat as built foundations before proposing replacement

- Dashboard: canonical Hub shell in `prismatic/gateway/templates/dashboard.html`, existing tab adapters/components, Workspace deep links, plugin/PWP/queue/merge/signal/cron/resource/foundation surfaces.
- Plugins: `prismatic/interface/plugin.py`, `prismatic/core/registry.py`, `prismatic/plugin_architecture.py`, `plugin_jobs.py`, `plugin_artifacts.py`, `plugin_policy.py`, `/api/plugins/*`, PWP reference lifecycle, and `scripts/app_surface_golden_demo.py`.
- Assigned-agent/completed-work: dispatcher/router/preflight pieces, durable ingestion queue, `completed_work_gate.py`, `agent_packet_normalizer.py`, `agy_completed_work.py`, `agent_raw_output_queue.py`, `scripts/ingest_agy_result.py`, `scripts/assigned_agent_result_writeback.py`, promotion/approval ledgers, merge backlog, and worktree janitor.
- Operations/release: native crons/schedules, locks, journal, doctor, `backup.py`, release/public/security/distribution smokes, dashboard visual QA, EventBus/`/ws`, sandbox/runtime helpers.
- Security: existing bearer auth helpers, gateway security helpers, webhook HMAC code, CORS/redaction/security readiness tests.

Presence in source means “built or partially built,” not automatically production-ready. Classify each as KEEP/RECONNECT/HARDEN/COMPLETE/GENERALIZE/REPLACE/RETIRE.

## First task before implementation

When converting a broad audit/model report into a master plan, the first executable task should be a preservation/source map, not new implementation:

```text
BUILT_ASSET_PRESERVATION_MAP_OK
```

Required map:

1. Dashboard tab → JS fetch → API route → backend module → state → tests.
2. Agent event → queue → resolver → launch → packet → result/writeback.
3. Plugin catalog → policy → job → approval → artifact → export.
4. Service/timer → executable → checkout/SHA → state.
5. Dev/runtime/main/open-PR/worktree reuse buckets.
6. Disposition for every relevant asset.
7. Preservation bundle paths and hashes.
8. Exact first security/runtime PR boundaries.

## Required prompt/report packet additions

For Fred/Kai/AGY/Jules/George implementation prompts and review packets, require these fields when plan touches existing Prismatic systems:

```text
EXISTING_ASSETS_REUSED=
EXISTING_CONTRACTS_PRESERVED=
SURGICAL_CHANGES=
CANDIDATES_RETIRED=
CALLER_USAGE_SEARCH=
STATE_MIGRATION=
ROLLBACK_PATH=
```

If a packet lists only new files without reusable-asset evidence, reject or ask for proof that no reusable implementation existed.

## Surgical retirement rule

No component is deleted because it is ugly, duplicated, old, or currently broken. Removal requires:

```text
caller/state/test/docs/service/dashboard usage search
→ classification
→ preservation bundle
→ named replacement/canonical contract
→ parity tests and migration/readback
→ one-caller-at-a-time migration
→ targeted + runtime/public/browser proof as applicable
→ compatibility/usage quiet period
→ delete only obsolete leaf
→ rollback path
```

Candidates from the 2026-07-20 revision were the live webhook simulator, accepted-noop controls, misleading sync buttons, Tailwind CDN dependency, hardcoded GRO paths, duplicate aliases/layers, generated cache, and speculative model-report docs — all candidates, not immediate deletion authorization.

## Verification pattern for plan artifacts

After writing a Prismatic master plan or cheat sheet, run a small `/tmp/hermes-verify-*` script that checks:

- file exists, size/line count/hash;
- required headings and markers;
- required existing asset paths in the repo;
- source-grounded claim needles such as important markers/routes;
- basic secret/token/private-key pattern absence;
- cleanup of the temp verifier.

Report as ad-hoc targeted verification, not canonical suite green.

## Good marker

```text
PRISMATIC_BUILT_FIRST_MASTER_PLAN_OK
```
