## OKF / North Star positioning audits

When Michael asks to turn Prismatic positioning language into an OKF audit, North Star audit, README doctrine, or product-thesis alignment report, treat it as a **product doctrine alignment audit**, not generic copywriting. Compare the requested language against `docs/north-star.md`, `docs/okf-evidence-map.md`, and the current runway handoff, then make the next proof gate explicit.

Preferred thesis language from the 2026-07-19 session:

```text
Prismatic is an evidence-first work orchestration layer for AI agents, plugins, and operators.
Prismatic makes AI agent work auditable and safe to integrate.
Prismatic is a task-manager-agnostic control plane that turns agent output into verified work packets, artifacts, and promotion decisions.
```

When useful, upgrade the OKF frame from `Objective → Key Result → Function → Evidence` to:

```text
Objective → Key Result → Function → Evidence → Promotion Decision
```

Promotion decisions include `promote`, `open_or_update_pr`, `needs_approval`, `blocked`, `superseded`, `clean_rebuild`, `manual_review`, and `reject`. This connects North Star doctrine directly to implementation gates such as `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK` without overclaiming auto-merge or production readiness. For the reusable report structure, see `references/okf-north-star-positioning-audit-2026-07-19.md`.

## Rubric-to-10/10 AGY Linear planning

When Michael asks to create epics/tasks so AGY can drive every rubric item to 10/10, treat it as a **scorecard architecture + execution tree** task, not a flat backlog dump.

Use the canonical PE docs as the rubric source before creating Linear work:

- `docs/north-star.md` — public launch proof table, plugin ecosystem maturity ladder, media/business readiness checklists, Golden Flow sequence.
- `docs/dashboard-primary-touchpoint.md` — dashboard-first command surface expectations.
- `docs/okf-evidence-map.md` — Objective → Key Result → Function → Evidence mapping.
- `docs/public-launch.md`, `docs/pwp-reference-lifecycle.md`, and `docs/prismatic-plugin-architecture.md` for concrete proof surfaces.


Recommended epic shape:

1. **Scorecard baseline + evidence ledger** — inventory every rubric item, define 10/10 scoring rules, run current baseline, and create a reusable closure ledger.
2. **Public local launch path** — clean-clone quickstart, public launch smoke coverage, public security/release readiness.
3. **Dashboard-primary command surface** — UI/API coverage gap audit, visual/UX proof pack, dashboard-backed smoke/readiness reports.
4. **Media plugin structured governance** — media blueprint governance schema, validation smoke, asset provenance/approval contract.
5. **Business plugin blueprint pack** — class taxonomy/risk model plus `seo-ops`, `booking-ops`, and `business-intelligence` blueprint readiness.
6. **Dashboard-visible Golden Flow** — current-state trace, dashboard event model, acceptance demo plan.

Linear creation pattern:

- Use the active Prismatic Engine project when available, and label every item with `agent:agy`, `dispatch:ready`, `prismatic-engine`, `plugins`, and a pipeline label (`pipeline:research-strategy`, `pipeline:backend-api`, or `pipeline:visual-design`).
- Add `epic` only to parent epic issues; children should use `parentId` pointing at the epic.
- Put the AGY operating instructions in every description: repo path, source-of-truth docs, “10/10 requires evidence,” PR expectation when implementation is needed, and no completion without real command/API/dashboard/docs proof.
- Verify Linear mutations by checking `success: true` and then re-querying the created issue identifiers, parents, states, project, and labels. Do not rely only on the mutation response.
- In the final report, link every Linear identifier using the Prismatic task URL pattern and recommend the first AGY sequence: inventory rubric → run baseline scores → create closure ledger.

### OKF trust doctrine and promotion-decision framing

When Michael asks for Prismatic OKF/North Star/audit docs, or for Kai/Fred/AGY prompts that explain why a slice matters, embed the product doctrine directly instead of treating it as background prose:

```text
AI agent output is becoming cheap, but trustworthy AI work is still expensive.
Claude Code writes work.
Hermes runs agents/tools/plugins.
Prismatic governs work.
```

Use the expanded OKF shape:


```text
Objective → Key Result → Function → Evidence → Promotion Decision
```

The point is not to trust only an adversarial review agent, chat transcript, or model self-report. A successful Prismatic slice should build cumulative trust through packet validation, scope checks, logs, artifacts, provenance, policy decisions, review state, dashboard/API visibility, and a promotion decision such as `promote`, `open_or_update_pr`, `needs_approval`, `blocked`, `superseded`, `clean_rebuild`, `manual_review`, or `reject`.

For next-slice prompts, include a small OKF table:

| OKF field | What to specify |
|---|---|
| Objective | What trusted/operator-decisionable outcome this slice serves. |
| Key Result | The concrete proof condition, marker, route/test state, or CI result. |
| Function | The API/CLI/dashboard/workflow being exercised. |
| Evidence | Commands, logs, markers, artifacts, route probes, CI, browser proof where relevant. |
| Promotion Decision | The allowed outcome and side-effect boundary. |

Reference: `references/okf-trust-doctrine-and-pr329-kai-prompt-2026-07-19.md`.

### Structured audit coverage supplements

After creating the first rubric-to-10/10 task tree, do a second pass against the originating audit before claiming coverage is complete. Broad epics can miss specific audit surfaces. Look explicitly for these common misses and create supplemental AGY-routed Linear work when present:

- **Plugin productization / graduation:** new-plugin acceptance checklist, blueprint-to-live promotion path, second reference plugin beyond PWP, external MCP/auth reference path.
- **Domain policy explainability:** media and business policy preset packs, policy simulation matrix, approval context payloads.
- **Hosted/public hardening:** optional Gateway auth, deployment-hardening guide, state directory/persistence guide, audit pagination/filtering/retention/export, optional DB backend path, stale path/branch cleanup.
- **Dashboard operator polish:** plugin/status/risk filters, deep-linkable job/artifact detail routes, copy-curl/replay-safe operator actions.
- **Artifact lineage:** media prompt/model/rights/variants; business PII/external IDs/retention/actor chain.
- **Architecture visibility:** advertise business plugin classes in architecture surfaces and add a business plugin developer quickstart.
- **Golden Flow drift:** explicitly check original Golden Flow v0 acceptance steps against current dashboard/plugin public-launch milestones.


Treat the answer to “do these tasks really cover the whole audit?” as a verification task: re-read the audit, map findings → existing issues, then create missing tasks. Include a dedicated coverage-matrix task so future agents can prove no audit finding was orphaned.

### Post-pass cohesive app surface integration

After all rubric and supplemental audit tasks are substantially complete, add a **post-pass integration epic** rather than stopping at section-level 10/10s. The integration epic should wire completed areas into one coherent app surface:

```text
install/run → dashboard home/readiness → plugin catalog → governance/policy → create/start job → approval → artifact/provenance → audit history → export/publish → disconnect safely → evidence/report
```

Recommended post-pass child tasks:

1. Final cross-epic gap matrix and closure ledger.
2. Unified dashboard information architecture.
3. Unified app state and event contract.
4. End-to-end cohesive app demo path.
5. Cohesive app surface smoke script, e.g. marker `COHESIVE_APP_SURFACE_OK`.
6. No-orphan API/UI/docs/test audit.
7. Unified public onboarding journey.
8. Dashboard readiness command center.
9. Unified visual proof and UX QA pack.
10. Release gate for cohesive app surface.
11. Final operator handoff and maintenance playbook.

The purpose is to ensure there are no orphan APIs, dashboard dead-ends, shell-only critical paths, docs/smoke drift, or task clusters that are individually good but fail to compose into a usable product. This is the “make the whole app float” pass.

### RC1 Portable App Readiness release-candidate loop

After the cohesive app surface integration pass, the next layer is not another open-ended audit. Use a **release-candidate loop** with an explicit endpoint: ship a portable developer preview.


Canonical sequence:

```text
cohesive app surface
→ portable app readiness audit
→ blocker fixes
→ one-command readiness proof
→ versioned developer preview
→ cross-platform hardening
→ plugin SDK/reference ecosystem
→ hosted/team-ready hardening
→ stable local-first platform
```

Recommended RC1 epics:

1. **Portable App Readiness Audit** — freeze RC scope, define G1-G10 rubric, implement `scripts/portable_app_readiness_audit.py`, run clean-install/dashboard/state/security/docs/release audits, and publish scorecard/findings.
2. **RC1 Blocker Fixes** — convert audit findings to fix issues, fix P0 install/security/dashboard/plugin blockers, explicitly resolve/defer P1s, then rerun audit until `P0=0` and thresholds pass.
3. **Cross-OS Install & State Portability** — define OS support tiers, audit paths/env/state/shell assumptions, prove Linux, plan/prove macOS and Windows/WSL, and prove backup/restore/move-to-new-machine state portability.
4. **Dashboard-First Usability Hardening** — first-run readiness/home, guided plugin lifecycle, useful error/recovery states, approval/risk explanation, mobile/tablet audit, and browser console/visual proof pack.
5. **Release Proof & Versioned Developer Preview** — one-command RC readiness proof, version/tag naming, build/package artifact proof, release notes/known limitations, tag/cut checklist, and post-RC roadmap.

Portable App Readiness rubric gates:

| Gate | RC1 minimum | 10/10 target |
|---|---:|---:|
| G1 Fresh install / bootstrap | 9 | 10 |
| G2 OS portability | 8 | 10 |
| G3 Dashboard-first operation | 8 | 10 |

| G4 Plugin lifecycle | 9 | 10 |
| G5 Policy / governance | 9 | 10 |
| G6 State / data portability | 8 | 10 |
| G7 Security / secrets / hosted-hardening boundaries | 9 | 10 |
| G8 Docs / onboarding | 9 | 10 |
| G9 Release/test proof | 9 | 10 |
| G10 Maintenance / upgrade path | 8 | 10 |

Finding classes:

- `P0 blocker` — prevents install, safety, core lifecycle, dashboard-first proof, or data integrity; must fix before RC1.
- `P1 release gap` — hurts public usability/portability but workaround exists; fix or explicitly defer for developer preview.
- `P2 polish` — useful but not release-blocking.
- `P3 future` — roadmap.
- `won't-fix` — intentionally out of scope with written reason.

Expected proof marker for the loop should be something like:

```text
PORTABLE_APP_READINESS_OK
```

Do not let this become “audit then fix everything forever.” Freeze RC scope, classify findings, fix blockers, rerun proof, cut a named developer-preview release, then move the remaining work into the next maturity stage.
