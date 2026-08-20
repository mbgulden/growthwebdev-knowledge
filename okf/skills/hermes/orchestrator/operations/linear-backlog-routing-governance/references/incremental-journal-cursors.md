# Incremental Journal Collector Cursor Pattern

Use this when converting a repeated scan-and-resummarize journal collector into an evidence-bounded incremental collector.

## Cursor contract per source

Persist a record keyed by a stable source path containing:

- device/inode identity;
- byte offset and cumulative record position;
- hash of newly read content;
- collection window (`observed_at`, start/end offset);
- parse outcome (`accepted`, `empty`, or `quarantined`);
- rotation indicator; and
- a trailing-window anchor hash (for example, the final 4 KiB ending at the stored offset).

## Rotation safety

Do not consider `size >= old_offset` sufficient proof of append-only continuity. A process can truncate and rewrite a file on the **same inode**, growing past the old offset before the next poll. Before seeking to the old offset, hash the current bytes ending at that offset and compare them to the stored anchor. On mismatch, reset to offset zero and mark the source rotated.

## Event correctness

- Build stable idempotency keys from canonical signal content, excluding observation timestamps.
- Deduplicate before rendering a recap or appending to the event index.
- Keep untimestamped or malformed operational lines in a separate, redacted quarantine store; never promote them into current health/recaps.
- A no-new-input rerun must accept zero events and avoid appending a duplicate recap.

## Minimum focused tests

1. initial read, append-only read, and no-new-byte rerun;
2. truncate/replace rotation with a smaller file;
3. same-inode truncate/rewrite that grows beyond the former offset;
4. repeat signal dedupe using stable key;
5. malformed operational line quarantined, not normalized; and
6. a rerun of the snapshot accepts zero events.

## Verification boundary

Use a fresh `/tmp/hermes-verify-*` script created through `tempfile`, run pycompile + focused tests + lint, and explicitly call the result **ad hoc targeted verification**. CI and a live runtime install remain separate proof classes.
