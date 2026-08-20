# Linear Markdown Normalization + Bounded Recovery

Use this when an explicitly authorized Prismatic Linear writer fails a byte-exact postcondition after updating an issue description.

## Durable behavior

Linear can canonicalize Markdown list markers in stored descriptions:

```text
submitted: - list item
stored:    * list item
```

This can create a byte-exact mismatch even when the live semantic payload is the intended packet text. Preserve fail-closed behavior: the writer should stop, write a failed receipt, and require bounded recovery/review rather than silently accepting broad equivalence.

## Required recovery sequence

1. Preserve the failed receipt and exact writer SHA.
2. Snapshot the current live state for every owned target issue plus any parent/root projection issue.
3. Classify current state precisely:
   - protective/quarantine labels already applied,
   - packet-created issue absent/present,
   - packet-created relations absent/present,
   - residual fields still mutated,
   - projection-only drift caused by residual parent title/description.
4. Diff packet text vs Linear-stored text character-by-character. Only treat it as normalization if the exact difference is known and bounded, e.g. `\n- ` to `\n* ` at a counted set of locations.
5. Prepare a one-purpose recovery script that hard-guards the exact residual state, including normalized stored text, before any mutation.
6. Restore only the baseline residual field(s), then re-read and verify:
   - all owned issue content/state/parent/topology,
   - labels intentionally retained for quarantine/protection,
   - root/parent child projections,
   - zero packet relations and absent packet-created issue,
   - receipt hash/source binding.
7. Run dry-run first, request independent exact-SHA `CLEAN`, then ask for explicit mutation authorization if needed.

## Implementation notes

- Keep normalization local to the exact residual guard; do not weaken the main writer's verification globally.
- If timestamps are the only unavoidable drift after failed mutation/rollback, compare stable fields with `check_updated=False` or equivalent and state that boundary explicitly.
- Do not retry the failed writer unchanged. Inspect and classify drift first.
- Do not claim rollback complete while child/parent projections still reflect residual title/description content.
- Treat Linear read-after-write behavior as eventually consistent: a failed immediate post-update check can still leave the submitted content visible on a later read. Before classifying a second/third retry failure, re-read the live issue and compare the stored content against the packet canonical form. If it now matches, classify it as an owned residual caused by convergence timing, not as a new Markdown transform.
- Recovery scripts for convergence-timing residuals should write a durable intent per target, mutate one target at a time, then run a bounded polling loop that verifies the entire owned graph/root projection after each operation. Only mark `PASS_RECONCILED` when the full expected global state is observed within the reviewed bound; otherwise fail closed with the receipt preserved.

## Repeated safe failures and multi-target residual recovery

If a recovery-mode retry fails after earlier successful recoveries, do not keep launching the packet or flatten the incident into one broad rollback. Build the next recovery from the *latest failed receipt* and its hash-bound private before snapshot:

1. Verify the source failure receipt SHA and that its `preflight.before_snapshot_sha256` matches the private snapshot file.
2. Run a fresh residual probe against the live source of truth: list residual fields, parent/root projection drift, quarantine labels, packet-created issue absence, and relation absence.
3. Pin the live residual title/description hashes for every mutated target before any recovery mutation. This prevents the recovery from overwriting unrelated human edits made after the failure.
4. Restore targets in dependency-safe order. For parent title/description residuals, restore child/root projections in the expected model and verify them after each write.
5. Use a full-graph guard, not a target-only guard: every owned issue, parent pointer, child projection, quarantine label set, relation absence, and packet-created issue absence must be checked before and after.
6. Require dry-run `PASS`, exact recovery-script SHA, exact source receipt SHA, exact before snapshot SHA, and independent `CLEAN` before asking Michael for the next mutation authorization.

## Retrying from a quarantined post-recovery state

If the first live writer fails safely, bounded recovery returns the hierarchy to a quarantined/recovered state, and Michael later wants to retry the original packet, do **not** treat the original before-guard export as sufficient authority. The live state may intentionally differ from the pre-write baseline because dispatch labels were removed, agent labels were added, timestamps changed, or rollback protection was retained.

Use a separate retry-baseline contract:

1. Freeze the exact post-recovery live snapshot for every owned issue plus read-only parent/root projections in a private mode-600 artifact.
2. Hash-bind that retry baseline in the writer CLI/API (`--retry-baseline-sha` or equivalent) and receipt.
3. Hash-bind the source recovery receipt and require it to be `PASS` with the expected proof facts: exact owned issue count, zero packet-created relations, packet-created issue absent, and any quarantine/protection labels intentionally retained.
4. On retry preflight, compare live snapshots to the retry baseline including immutable IDs/identifiers and `updatedAt` unless a timestamp boundary is explicitly reviewed.
5. Bind deterministic IDs for any packet-created issue and relation ledger; fail closed if any are already occupied.
6. Preserve the original frozen packet and raw submitted Markdown; use a narrow canonicalizer only for Linear's known stored representation, such as line-start unordered-list marker normalization (`- ` stored as `* `), when computing expected postconditions.
7. Keep dispatch restoration out of recovery/retry unless a separate authorization explicitly allows it.
8. Run retry mode as live dry-run first, then get independent exact-writer-SHA review before asking for recovery-mode execution authorization.

This retry baseline is not a new source of product truth; it is a bounded authority bridge from the verified recovered state back into the still-frozen approved packet.

## Compact proof block

```text
FAILED_RECEIPT=<path>
FAILED_WRITER_SHA=<sha256>
CURRENT_RESIDUAL=<issue/field/projection list>
NORMALIZATION=<exact transform + count>
RECOVERY_SCRIPT_SHA=<sha256>
DRY_RUN_RECEIPT=<path>
LINEAR_MUTATED_BY_DRY_RUN=false
REVIEW=<independent review id>
BOUNDARY=not public mutation until CLEAN review and explicit authorization
```
