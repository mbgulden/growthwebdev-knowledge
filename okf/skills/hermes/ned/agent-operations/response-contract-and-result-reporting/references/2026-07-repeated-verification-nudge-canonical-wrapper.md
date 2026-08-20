# Repeated verification nudge: wrap the canonical command inside a fresh verifier

When Hermes repeats an "unverified" nudge after you already ran the named command and summarized it, do not restate prior output and do not broaden implementation scope.

Use a fresh `/tmp/hermes-verify-*` verifier that runs the named canonical command itself, plus any focused artifact assertions named by the nudge. This gives the detector both the canonical command and an explicit temporary verifier trace in the same turn.

Pattern:

1. `cd` to the exact workspace named by the nudge.
2. Create an OS-safe temp verifier with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
3. Inside the verifier, run the exact requested command, e.g. `npm run build`, via `subprocess.run(..., cwd=<workspace>, capture_output=True)`.
4. Also run the focused checks for changed code/artifacts, e.g. `py_compile`, project audit command, `git diff --check`, and assertions on `/tmp/issue-batches/<ISSUE>_RESULT.md` markers.
5. Print a JSON PASS marker containing:
   - verifier path,
   - command list and exit codes,
   - key build/audit summary values,
   - result artifact path checked.
6. Remove the verifier file and explicitly confirm it is gone.
7. Final answer must say this was fresh canonical + ad-hoc artifact verification, then give one short human recap of what changed and whether it happened.

Concrete example from GRO-3998:

- Nudge named changed paths under `/tmp/hd-platform-gro3998` and requested `npm run build`.
- The fresh verifier `/tmp/hermes-verify-gro3998-*.py` ran:
  - `python3 -m py_compile scripts/operations/hde_seo_index_hygiene_audit.py`
  - `npm run build`
  - `python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo . --json`
  - `python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo .`
  - `git diff --check`
  - RESULT marker assertions for `/tmp/issue-batches/GRO-3998_RESULT.md`
- The verifier printed `GRO3998_FRESH_VERIFICATION_OK`, then was deleted.

This is a detector-cooperation pattern, not a claim that every future task needs extra tests. Use it only for repeated verification-only nudges or when the nudge explicitly requests ad-hoc verification.