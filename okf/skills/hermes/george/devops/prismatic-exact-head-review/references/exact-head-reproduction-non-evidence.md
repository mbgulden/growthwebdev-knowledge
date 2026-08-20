# Exact-head reproduction: setup/verifier failures are non-evidence

Use this reference when reviewing a completed Prismatic producer at an exact candidate head and local reproduction initially fails for reasons outside the candidate.

## Session pattern captured

A producer completed cleanly at an exact commit/tree and the acceptance contract required targeted exact-head reproduction, not canonical suite green. Two local reproductions initially failed before the final clean proof:

1. **Wrong tool binding** — the verifier trusted a named interpreter from the producer narrative instead of proving the executable actually had the required test/lint tools.
2. **Verifier-location error** — product commands were green, but the disposable semantic verifier looked for an invariant in the wrong allowlisted source file.

Both were preserved as artifacts but explicitly excluded from acceptance evidence. The final proof restarted from a fresh `.git`-free archive after each verifier/setup correction.

## Durable rule

When exact-head reproduction fails because of verifier setup, wrong toolchain binding, quoting, API mismatch, or wrong source-location assumptions:

1. Classify the report as `SETUP_FAILED` or `VERIFIER_FAILED`, not `CANDIDATE_FAILED`, unless product behavior actually failed.
2. Preserve the failed report path/hash as non-evidence.
3. Fix only the verifier/tool binding, not the candidate.
4. Restart the complete proof from a new disposable archive instead of resuming partial output.
5. In the review packet, list successful evidence separately from non-evidence reports.
6. Keep the shared worktree read-only/clean and label the result `AD_HOC_OR_CANONICAL=ad-hoc targeted exact-head contract suite` unless the canonical full suite really ran.

## Packet fields to include

```text
SUCCESSFUL_REPRODUCTION=<path>
SUCCESSFUL_REPRODUCTION_SUMS_SHA256=<sha>
REPRODUCTION=<pytest/lint/compile/verifier/diff summary>
NON_EVIDENCE_REPORTS=<timestamp_reason;...>
AD_HOC_OR_CANONICAL=ad-hoc targeted exact-head contract suite
NOT_CLAIMING=canonical full-suite green
```
