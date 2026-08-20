# Post-edit guard for packet-classification read models — 2026-07-19

Use this when Hermes repeatedly reports changed-path verification as unverified after a parser/classifier/read-model edit.

## Pattern

1. Create a real temp script with `tempfile.NamedTemporaryFile(prefix='hermes-verify-', dir='/tmp', delete=False)`.
2. Run it with the project venv/interpreter.
3. Insert the edited repo root at `sys.path[0]` before importing project code.
4. Scope assertions to the exact changed paths named by the guard.
5. Include behavior assertions, not just test commands.
6. Remove the temp script and append `cleanup=PASS verifier_removed=<path>` to the log.

## Behavior assertions for packet classifiers

For a completed-work packet classifier/read model, assert all of these if relevant:

- `packet_valid`
- `packet_blocked`
- `packet_failed`
- `packet_malformed`
- `packet_missing`
- `needs_manual_review`
- token-like summary redaction
- persisted record readback
- row/read-model exposure
- non-side-effect fields remain false

## Reporting

Use compact output only:

```text
COMMAND=/path/to/python /tmp/hermes-verify-*.py
RESULT=PASS
LOG=/tmp/<name>.log
SCOPE=exact guard-listed paths plus behavior assertions
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green,production deploy,auto-merge,live bulk dispatch,real Linear writeback,real GitHub PR creation
MARKER=<target marker>
cleanup=PASS verifier_removed=/tmp/hermes-verify-...
```

If the detector repeats after a passing proof, rerun a **new** temp verifier and report only the fresh proof. Do not argue with the detector or repost stale evidence.
