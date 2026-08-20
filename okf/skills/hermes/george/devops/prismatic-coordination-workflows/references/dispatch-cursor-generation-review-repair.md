# Dispatch cursor generation review/repair pattern

Session-derived pattern for reviewing AGY-produced dispatch consumer cursor-generation repairs under supervised cap 1.

## Trigger

Use this when a producer modifies dispatch consumer cursor/generation logic, repair/inspect CLI behavior, or filesystem-bus consumption safety.

## Review lessons

1. **Green producer tests are not enough.** Preserve the exact candidate commit/tree, then reproduce runtime semantics against the actual loop ordering.
2. **Probe same-path database replacement.** A consumer that validates DB generation only once before a long/infinite loop can still spawn work from a later atomically replaced DB at the same path before rejecting the generation mismatch.
3. **Inspect must be read-only.** `--inspect` and similar diagnostic paths must not create schema, metadata, cursor files, generation rows, or repair state through helper fallbacks. Use read-only URI/path probes and assert filesystem/DB identity does not change.
4. **Repair dry-runs must be deterministic.** Run the dry-run twice against the same fixture and compare normalized output/state. Non-deterministic plans are a repair verdict even if they do not mutate production.
5. **Reject invalid repair targets up front.** Negative rowids, non-integer targets, ahead-of-bus targets, generation mismatches, and stale DB identity must fail closed before cursor/state mutation.
6. **If producer exits after committing but before final packet, treat the commit as an untrusted candidate snapshot.** Review exact paths, hash-bind the candidate, run producer-required checks, then perform adversarial semantic reproductions before accepting or issuing repair.
7. **Relaunch same-task repairs without raising cap.** If a launch fails before edits due to an unsupported model option, verify the worktree remains exact/clean, remove only local generated artifacts, then retry the same hashed repair prompt without the unsupported option. Record the failed attempt as pre-edit, not as candidate evidence.

## Proof packet fields

```text
TASK=<exact task id>
BASE=<base sha>
CANDIDATE_HEAD=<candidate sha>
CANDIDATE_TREE=<tree sha>
CHANGED_PATHS=<exact allowlist>
PRODUCER_STATUS=<completed|timeout_after_commit|failed_before_edits>
FOCUSED_TESTS=<result/log>
CANONICAL_TESTS=<result/log>
SEMANTIC_REPRO=<runtime-replacement|inspect-readonly|dry-run-determinism|invalid-target>
VERDICT=<CLEAN|REPAIR|BLOCKED>
REPAIR_CONTRACT=<path + sha256 when applicable>
CAP=<must remain 1>
NOT_CLAIMING=<no live DB/cursor mutation, no dispatch resume, no PR/merge/deploy>
```

## Boundaries

- Do not inspect partial producer files while a producer is still live.
- Do not trust `RESULT.md`, self-review, or green focused tests as completion authority.
- Do not advance to another issue or scale producers while the exact candidate is `REPAIR`.
- Keep live bus DB/cursor, Linear, services, GitHub PRs, deploy/restart, and generic dispatch paused unless separately authorized.
