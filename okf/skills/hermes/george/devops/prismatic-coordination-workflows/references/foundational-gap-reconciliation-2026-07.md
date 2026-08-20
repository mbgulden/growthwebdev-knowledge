# Foundational gap reconciliation notes — July 2026

Use as a concrete example when reconciling a broad Fred/agent gap list before Linear restructuring or source changes.

## Durable lessons

- Treat the source agent's evidence boundary as part of the evidence. If a report says "no code was executed," its claims must be rechecked against current source and live read-only state before becoming Linear work.
- Preserve every incoming `.md` unchanged and hash it. If the document cites an upstream audit/report, recover and hash that too; the upstream file can change the meaning of the digest document.
- Do not let stale labels drive task creation. Reframe around current guarantees:
  - "lock manager is a stub" may be stale if a real lock exists; the durable task may be adoption/authority convergence by actual mutation paths.
  - "rate-limit guard is missing" may be stale if the dispatcher already has a circuit; the durable task may be duplicate-path coverage and safe worker deferral semantics.
  - "cron registry never ran" may actually be split-brain production: live crontab runs scripts directly while registry receipts/dependencies remain unwired.
- Avoid creating a second scheduler authority. Prefer one thin system-cron trigger into one canonical PE runner, with receipts/dependency/orphan reconciliation, rather than adding a new daemon beside existing crontab behavior.
- For database retention, never rotate/delete an event router DB wholesale from a gap list. First classify per-table authority and protected evidence classes, dry-run counts, backup/restore proof, reference validation, bounded deletion, and checkpoint/VACUUM policy.
- Retired Hermes/agent profile cleanup is destructive. Inventory, export, hash, migrate active references, and get explicit destructive/cross-profile approval before deletion; do not propose rewriting Git/Linear history to remove old profile names.
- CLI-lane proposals must verify the exact installed CLI syntax before writing prompts/tasks. Codex 0.132.0 accepted `codex -a never exec ...` shape; putting approval flags after `exec` was rejected in this session. Treat CLI syntax as version-bound and re-verify when current facts matter.
- For cross-project dependencies, prefer eventual runtime enforcement, but sequence through canonical dependency identity/schema, cycle/missing/stale validation, audit-only projection, and explicit Linear-write approval before fail-closed enforcement.

## Output shape that worked

Produce a no-mutation downloadable reconciliation packet with:

- source hashes for the provided document and cited upstream audit;
- exact source commit/tree;
- explicit mutation boundary (`linear_mutated=false`, `profile_mutated=false`, `runtime_mutated=false`, `source_mutated=false`);
- per-gap decisions: valid/partial/stale/already implemented/duplicate/blocked;
- reduced task tree mapped into existing parent issues where possible;
- acceptance checks and rollout/rollback gates;
- compact `/tmp/hermes-verify-*` ad-hoc verification log and SHA.
