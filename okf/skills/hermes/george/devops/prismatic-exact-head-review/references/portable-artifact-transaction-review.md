# Portable artifact transaction review

Use this reference when exact-head review covers code that writes paired or multi-file artifacts (recap + manifest, receipt + index, checkpoint + metadata) under a configured output directory.

## Failure modes caught in PR #382-style review

- **Chronology drift:** "latest" output must sort accepted events by normalized UTC timestamp, not by input/file iteration order.
- **Ambiguous citation IDs:** shortened IDs can collide or become untraceable in manifests; externally referenced citations should be full deterministic IDs unless the contract explicitly defines collision handling.
- **Partial redaction/bounding:** rendering only the body through a redactor is insufficient. Every dynamic rendered field (title, source, status, names, scheduler labels, quoted config values) needs redaction and length bounds.
- **Non-atomic paired output:** writing the main artifact and manifest independently can leave mixed old/new pairs. Stage the pair together and replace both as one transaction, with rollback/recovery semantics documented and tested.
- **Symlinked output directory escape:** a user-controlled `recaps`/artifact directory symlink can redirect writes outside the journal root. Open the real output directory with no-follow semantics and bind all operations through that descriptor.
- **Linux-only descriptor paths:** `/proc/self/fd/<n>` is not portable to macOS even if it is safe on Linux. Prefer descriptor-relative operations (`dir_fd` parameters, relative names, `os.replace`/`os.rename` where supported) instead of path strings through `/proc`.
- **FD leak/ownership gaps:** failure-injection tests must account for close/cleanup paths and preserve recoverable backups if rollback itself fails.

## Review recipe

1. Bind exact `HEAD`/tree and changed paths before review.
2. Trace the real writer path, not only helper functions, from input selection to artifact bytes.
3. Add or require one regression per semantic blocker:
   - UTC chronological latest ordering;
   - full/normalized citation IDs;
   - redaction and bounds across every dynamic rendered field;
   - rollback-safe paired replacement;
   - symlinked output directory rejection;
   - descriptor-relative operations with no `/proc` dependency.
4. Run focused artifact tests plus lint/compile/build; label post-edit detector proofs as `ad-hoc targeted` unless the full canonical suite also ran.
5. Freeze the new commit as a fresh candidate; prior independent `CLEAN/PASS` does not carry forward after semantic repair commits.

## Proof boundary

A clean result proves the reviewed artifact writer behavior at the named exact head. It does **not** prove production deployment, future writer paths not covered by tests, or GitHub CI execution unless those layers are separately run and bound.
