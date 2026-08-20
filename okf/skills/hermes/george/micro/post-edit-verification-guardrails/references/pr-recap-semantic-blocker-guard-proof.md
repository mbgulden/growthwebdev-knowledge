# PR recap semantic-blocker guard proof

Session-derived pattern for Prismatic PR/review work where independent review finds real semantic blockers after an earlier green candidate.

## When to use

Use this after repairing review blockers in a PR candidate, especially when the platform guard repeats that changed paths lack fresh verification.

## Required proof shape

1. **Accept blockers as real until disproved.** Do not defend older green evidence. Repair or reproduce each blocker.
2. **Add one persistent regression per accepted blocker.** For evidence recap work this included chronological latest ordering, full citation IDs, dynamic-field redaction/bounds, transaction/rollback safety, quoted redaction, symlink/no-follow output boundary, and recoverable rollback preservation.
3. **Create a fresh OS-safe temp probe under `/tmp`.** Use `tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')`.
4. **Prefer single-transcript temp source creation.** If the guard starts listing the temp probe itself as a changed path, create/write/run/delete the probe inside one shell transcript rather than via `write_file`, and assert all stale temp probe paths are absent.
5. **Run direct project commands visibly.** Pair the temp probe with focused pytest targets, direct lint/compile/docs/build commands, and `git diff --check`/clean-worktree checks as appropriate.
6. **Label proof class.** Report `AD_HOC_OR_CANONICAL=ad-hoc targeted`; cite any canonical run separately as historical evidence only.

## Compact report fields

```text
COMMAND=OS-safe temporary exact-head verifier + prior-blocker regressions + Ruff/compile/docs/build
RESULT=PASS
SCOPE=<PR/candidate commit>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green from this run,independent acceptance,push,merge,Linear completion,or deployment
MARKER=<unique marker>
TEMP_SCRIPT_CLEANED=true
STALE_TEMP_ABSENT=true
LOG=/tmp/hermes-verify-<topic>.log
LOG_SHA256=<sha256>
```

## Pitfalls

- A canonical suite run before the latest repairs does not cover post-review edits.
- If a completion packet under `/tmp` is edited after proof, it is also a changed artifact; either bind it in the proof or avoid treating it as part of source acceptance.
- Repeated guard prompts should trigger a fresh detector-shaped pass once; if the guard persists after a compliant current-turn transcript, classify it as detector-ingestion stale rather than looping indefinitely.
