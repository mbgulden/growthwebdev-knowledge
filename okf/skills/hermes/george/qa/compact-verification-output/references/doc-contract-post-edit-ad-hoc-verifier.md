# Documentation-contract post-edit ad-hoc verifier pattern

Use when a Prismatic slice edits a normative Markdown contract plus out-of-repo recovery/proof receipts, and Hermes repeats: "No canonical test/lint/build command was detected."

## Durable lesson

For documentation-only contract work, a valid closeout is not suite green. It is an ad-hoc, exact-head verifier that binds the Markdown contract, receipt artifact, and review boundary.

The verifier should be created under `/tmp` via Python `tempfile.NamedTemporaryFile(...)` or `tempfile.mkstemp(...)` with a `hermes-verify-` filename prefix. Shell `mktemp` may create a safe path, but if the warning explicitly asks for an OS-safe `tempfile` path, use Python tempfile first.

## Minimum assertions

1. Exact repo head and tree match the candidate under review.
2. Worktree is clean, or the only dirty paths are intentionally out-of-repo artifacts named in the detector warning.
3. `git diff --name-only <base> HEAD` equals the expected Markdown contract path(s).
4. `git diff --check <base> HEAD` passes.
5. Contract text contains the behavior markers that changed, not just generic prose.
6. If a recovery/proof receipt changed, read it back and assert:
   - candidate commit/tree;
   - log path and digest;
   - `AD_HOC_OR_CANONICAL=ad-hoc ...`;
   - explicit non-claims / independent-review gate.
7. Print the verifier temp path, compile result, execution result, log/digest if used, and cleanup status.

## Reporting shape

```text
TEMPFILE=/tmp/hermes-verify-<random>.py
COMMAND=python3 -m py_compile <tempfile>
RESULT=PASS

COMMAND=python3 <tempfile>
RESULT=PASS

AD_HOC_OR_CANONICAL=ad-hoc documentation-contract verification
TEMPFILE_CLEANED=true
NOT_CLAIMING=canonical suite green, runtime implementation proof, deployment, merge, or independent acceptance
```

## Pitfall from GRO-4345

Do not answer a repeated guard warning by pointing back to the previous receipt only. Run one fresh same-turn tempfile verifier that is visible in tool output. If the warning repeats after that compliant run, report detector non-recognition and preserve the evidence boundary instead of looping indefinitely.
