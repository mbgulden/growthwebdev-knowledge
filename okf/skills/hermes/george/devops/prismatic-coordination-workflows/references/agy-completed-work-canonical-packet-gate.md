# AGY completed-work canonical packet gate lessons

Related recovery reference: `references/agy-terminal-without-result-recovery.md` covers cap-1 producer terminal states with no `RESULT.md`/commit, stable operator recovery packets, ledger verification, handoff updates, and exact-head review before push/merge/deploy.

## Trigger

Use this when reviewing or repairing assigned-agent completed-work ingestion, visible-result writeback, or merge eligibility gates for Prismatic.

## Durable pattern

Completed-work ingestion must treat compact `KEY=value` chat output as operator-visible summary only, not as the authoritative completion transport. The durable gate should parse exactly one fenced JSON object and fail closed before persistence or side effects when the packet is absent, ambiguous, malformed, or missing required provenance.

## Required pre-ingest bindings

Before `AgyCompletedWorkStore.ingest`, comments, status mutation, or visible events:

- Require exactly one fenced JSON object; reject multiple JSON fences even if one looks valid.
- Bind packet identity to the raw durable capture row and launched run: agent, issue identifier, run id, and raw-output identity must match the launch record.
- Require explicit provenance: `source_path`, `source_branch`, `source_commit_sha`, `base_branch`, and `base_commit_sha`.
- Verify `source_path` is canonical, absolute, under the trusted lane, a real nonsymlink git worktree, and that `source_commit_sha` equals that repo `HEAD`.
- Verify `base_branch` resolves and `base_commit_sha` equals that ref; validate source branch syntax with git check-ref-format rather than trusting free text.
- Require nonempty lane-scope arrays, changed-file uniqueness, and equality between touched paths and changed paths when that is the contract.
- Require artifact entries to be nonempty dicts with nonempty paths; reject placeholder objects like `{}`.
- Require nonempty non-claim strings and proof metadata including `ad_hoc_or_canonical`.
- Enforce result/classification consistency: `PASS` must be persisted `merge_ready` and eligible; `BLOCKED` must classify blocked; `FAIL` must classify failed.

## Review adversarial cases

A clean review should explicitly reproduce that these fail closed before persistence and before comments/status/events:

- Compact-only result with no canonical JSON.
- Missing run id, commit SHA, classification, result summary, or verification lane.
- Empty lane scope / empty touched paths.
- Artifact list containing `{}` or an entry with an empty path.
- Two fenced JSON blocks in one transcript.
- Raw durable capture identity mismatch.
- Persisted `PASS` whose store result is rejected or not merge-ready.

## Transaction and replay safety

Keep conflict detection, evidence retention, and insert in one database lock/transaction so losing concurrent packets cannot race in separate evidence writes. Replays should be idempotent only for the exact same durable packet identity; distinct packets with the same completed-work id should retain the winning evidence and reject the loser.

## Test hygiene pitfall

Visible-stream reconciliation tests can cumulatively leak file descriptors through persistence/module state even when each test passes alone. When a later clean-room FD assertion fails only after a visible-stream module, reproduce the ordered pair/prefix and add explicit teardown for dynamically loaded modules, monkeypatched state, and GC. Do not weaken the clean-room FD assertion unless the leak is proven unrelated and independently fixed.

## Proof reporting

Separate proof classes:

```text
AD_HOC_OR_CANONICAL=ad-hoc targeted  # exact adversarial packet/provenance probes
AD_HOC_OR_CANONICAL=canonical suite  # full repository suite only when actually run
NOT_CLAIMING=merge/deploy/producer success until exact-head independent review is CLEAN
```
