# Repeated post-edit detector warning after compliant ad-hoc verification (2026-07-25)

## Trigger

Hermes/system reports edited source paths as still unverified even after a same-turn verifier has already run and passed. The warning text may say:

- changed paths are still unverified;
- no canonical test/lint/build command was detected;
- create a `/tmp/hermes-verify-*` script with OS-safe `tempfile`; and
- summarize the result as ad-hoc verification rather than suite green.

## Durable pattern

1. Treat the first repeated warning as a fresh request. Do not answer only from the prior receipt.
2. Run one current-turn, terminal-visible, OS-safe verifier:
   - create the script using Python `tempfile.mkstemp()` / `NamedTemporaryFile()` with `prefix="hermes-verify-"` under `/tmp`;
   - keep behavior/readback assertions in that script;
   - run literal terminal-visible command classes outside the script where practical: `ruff check`, `ruff format --check`, scoped `python -m pytest`, `python -m build`, `git diff --check`, or equivalent changed-path checks;
   - clean up the verifier and any temporary build directory;
   - print `LOG`, `LOG_SHA256`, `TEMP_CLEANUP`, `AD_HOC_OR_CANONICAL=ad-hoc targeted closeout`, `NOT_CLAIMING`, and a marker.
3. If the same detector warning repeats with no newer edits, perform at most one final unchanged-source rerun if the user/system explicitly asks again. If an out-of-repo temporary report/PR-body/proof-packet file is listed as a changed path and its contents have already been durably copied into the external system or final artifact, include a readback assertion once, then delete the temporary file so it cannot keep the detector loop alive.
4. After that final compliant rerun, stop the infinite loop: classify further identical warnings as detector non-recognition, preserve evidence hashes, and report boundaries. Do not call the result canonical suite green unless the actual project canonical suite ran in that current proof.

## Why this matters

The detector is optimized for visible command evidence and may not recognize prior receipts, wrapper variables, or subprocess-only verifier logic. Michael still expects active same-turn compliance before calling it detector non-recognition. The safe stop condition is therefore: **current-turn compliant verifier visible + no newer edits + repeated identical warning**.

## Compact proof shape

```text
COMMAND=final literal tempfile/Ruff/pytest/build rerun
RESULT=PASS|FAIL|BLOCKED
RC=<exit code>
LOG=/tmp/<name>.log
LOG_SHA256=<sha256>
TEMP_CLEANUP=PASS|FAIL
SCOPE=<changed behavior/classes>
AD_HOC_OR_CANONICAL=ad-hoc targeted closeout
NOT_CLAIMING=canonical suite, independent CLEAN, hosted CI, PR, merge, deployment, or Linear update
MARKER=<ISSUE>_HERMES_FINAL_RERUN_OK|FAIL|BLOCKED
```

## Pitfalls

- Do not use detector non-recognition as a shortcut before a current-turn compliant rerun is visible.
- Do not hide all verification commands inside the temporary script when the warning asks for canonical test/lint/build command detection; keep command classes visible in the terminal transcript.
- Do not claim canonical suite green from a scoped pytest/build/lint closeout.
- Do not keep rerunning indefinitely after the unchanged-source final rerun passes.