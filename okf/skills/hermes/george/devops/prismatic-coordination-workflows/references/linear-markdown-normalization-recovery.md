# Linear Markdown Normalization + Bounded Recovery

Use this when an approved Prismatic Linear packet writer fails a byte-exact postcondition after a Linear update, especially on description fields.

## Durable lesson

Linear may canonicalize Markdown list markers in stored issue descriptions:

```text
submitted: - list item
stored:    * list item
```

A byte-exact writer can correctly fail even when the semantic content is the intended packet content. Do **not** paper over this by loosening all verification. Treat it as a bounded normalization case that must be explicitly proven.

## Recovery pattern

1. Preserve the failed writer receipt and exact script hash.
2. Snapshot every owned issue and any parent/root projections before considering recovery.
3. Identify the exact residual mutation set. Separate:
   - intended quarantine/protective labels already applied,
   - absent packet-created objects/relations,
   - remaining residual fields needing rollback,
   - projection-only effects caused by the residual field.
4. Compare packet text vs stored text character-by-character. If the only delta is known Linear Markdown normalization (`\n- ` -> `\n* `), encode that normalization explicitly in the recovery guard.
5. Build a one-purpose recovery script that:
   - hard-guards the current exact residual state,
   - confirms quarantine labels and absence of packet-created relations/new issue,
   - restores only the residual baseline field(s),
   - re-verifies all owned issues, root/parent projections, labels, topology, and absence conditions,
   - writes a durable receipt with script SHA, source failed receipt SHA, and mutation status.
6. Dry-run the recovery and send it for independent exact-head review before allowing mutation.

## Pitfalls

- Do **not** retry the original writer unchanged after an exact postcondition failure. Inspect drift first.
- Do **not** convert this into broad tolerant comparison. Only normalize the specific proven Linear storage transform for the specific guarded residual.
- Do **not** claim rollback complete while projection rows still show the residual title/description through parent/child snapshots.
- Ignore volatile timestamp drift in recovery comparisons only when content/state/topology/labels are exact and the recovery script explicitly sets `check_updated=False` or equivalent for that purpose.

## Proof packet fields

```text
FAILED_RECEIPT=<path>
FAILED_WRITER_SHA=<sha256>
CURRENT_RESIDUAL=<exact issue/field/projection list>
NORMALIZATION=<exact character transform and count>
RECOVERY_SCRIPT_SHA=<sha256>
DRY_RUN_RECEIPT=<path>
LINEAR_MUTATED_BY_DRY_RUN=false
REVIEW=<delegation/session id>
NOT_CLAIMING=public mutation until independent CLEAN review + explicit authorization
```
