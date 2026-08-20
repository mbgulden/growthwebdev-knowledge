# Platform Gap Audit Pattern (2026-07-26)

When Michael asks "what gaps do you see?" (or any variant — "are we missing anything?", "what else is broken?", "would 3-5 agents know how to do this?"), the right move is an **active audit against the live filesystem + Linear state**, not a brainstorm.

## The pattern (5 phases)

### Phase 1 — Surface inventory

Read the actual source. Categorize by surface:

- **Cron / scheduler** — `prismatic/native_crons.py`, `core_crons.py`
- **Dispatch / routing** — `prismatic/dispatcher.py`, `lane_contracts.py`, `capability_router.py`, `label_debt.py`
- **Agent harness** — `prismatic/agents/`, `harnesses/`, `supervisor/`
- **Linear integration** — `prismatic/providers/tasks/linear.py`, `linear/`
- **Gateway / IPC / event bus** — `prismatic/gateway/`
- **Storage / state dbs** — `prismatic/dedup.py`, `ingestion_queue.py`, `state_machine.py`, `prismatic_state/*`
- **Plugin / skill** — `prismatic/plugin_*.py`, `prismatic/skills/`
- **Quality / gates** — `prismatic/quality/`, `guardrails.py`
- **Sandbox / security** — `prismatic/sandbox/`, `plugins/sandbox_pod_manager.py`
- **Observability / telemetry** — `prismatic/observability/`, `vertex_telemetry.py`, `run_records.py`
- **API / web** — `prismatic/api/`
- **CLI / admin** — `prismatic/admin.py`, `prismatic-engine` entrypoint

For each category, tag every relevant module: **exists / partial / absent / has-spec-but-no-impl**.

### Phase 2 — Tiered classification

Classify each finding:

| Tier | Definition | Example |
|---|---|---|
| **T1 — Genuinely broken or stub-by-design** | A file declares "STUB" in the docstring, or a feature is silently ignored | `SwarmLockManager.acquire()` returns True without doing anything |
| **T2 — Operationally fragile** | Works in the happy path but breaks under common conditions | Zero crons have ever fired (`last_run_at: None` for every entry) |
| **T3 — Missing product surface** | No code path exists; users have to work around it | No operator cron dashboard |
| **T4 — Meta / cross-cutting** | Documentation, retention, skill-bundling — not blocking | No OKF retention policy |

Each finding gets **file-path + line-number evidence**. Findings without evidence don't ship.

### Phase 3 — Stakeholder split

If the plan needs different reviewers, split the OKF docs by audience (not by topic):

- **Foundational doc** — for the stability reviewer (e.g., George). Lists primitives that must land before anything else. Ends with explicit "Decisions needed from <reviewer>" questions.
- **Cross-cutting doc** — for the operator (Michael). Lists parallel work + tasks blocked on first-wave epics.
- **Audit doc** — the index of record. Full inventory + tiered findings + cross-references to the other two docs.

One giant doc is the mistake. Different stakeholders won't read past their section, and the doc gets approved in pieces without anyone seeing the whole.

### Phase 4 — Verify before claiming done

After writing the audit doc + the two split docs, run the OKF verifier. If a finding has no evidence, **don't include it**. If a finding has evidence but no severity, classify it. If the audit would change the user's decision, **say so explicitly** at the top of the doc.

### Phase 5 — Decision-pause discipline

Make exactly **one** decision-pause after the audit is written. The user reviews the docs and answers the questions in §8 of the foundational doc. Then Linear mutations happen in one batched run. Don't pause between audit docs and Linear creation — one approval covers both.

## What the audit must NOT be

- **A brainstorm.** If you can't point to a file path + line number, the finding is speculation, not a gap.
- **A memory recall.** "I think there's a codex lane gap" without reading `lane_contracts.py` is not an audit.
- **A defense.** When Michael asks "is this enough?", treat it as a request to enumerate missing pieces by category, not as an invitation to claim completeness.
- **A plan dump.** The audit is the input to the next plan-mode iteration, not a substitute for it.

## Failure modes already observed

- **Memory-only answer.** I told Michael "G1..G10 gaps exist" without reading the actual code. The first-wave audit caught G1–G9 accurately because I read the source. The third-wave audit caught T1-1 (SwarmLockManager stub) by reading `core/locking.py:8-12` — a finding I would have missed from memory.
- **Defensive answer.** When asked "is this enough?", I defended the build-out instead of auditing for missing pieces. The right move is always: re-read the build-out against the question, list gaps by category, patch.
- **One giant doc.** I produced a 13-finding audit with mixed audiences (George for foundational, Michael for ops, nobody for meta). Splitting by audience produced a cleaner doc and a faster review cycle.
- **Verifying in memory.** "Looks done" is not verification. Run the verifier; if the verifier fails, fix the right layer (often the verifier, not the doc).

## Pair with these skills

- `linear-handoff-build-out` — produces the OKF + Linear tree the audit findings feed into.
- `linear-handoff-build-out/references/platform-gap-audit.md` — pre-feature dependency closure; this file is its sibling for *triggered* gap audits.
- `okf-documentation-ops` §21, §22, §23 — the umbrella principles.