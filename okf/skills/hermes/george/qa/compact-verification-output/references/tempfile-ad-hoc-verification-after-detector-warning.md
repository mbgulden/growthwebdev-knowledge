# Tempfile-Based Ad-hoc Verification After Detector Warnings

## When this applies

Use this after Hermes reports edited paths as unverified and explicitly asks for a focused temporary verifier under `/tmp` with a `hermes-verify-` filename prefix.

## Required behavior

- Act on the detector request once in the same turn if tools are allowed.
- Create the verifier with Python `tempfile` (`mkstemp` or `NamedTemporaryFile`) instead of a predictable/manual path.
- Run focused checks against the changed behavior and all named changed artifacts, including Markdown handoff/checkpoint/PR-body files when those were edited.
- Print a compact receipt with log path, SHA256, head/tree or artifact digest, cleanup status, and `AD_HOC_OR_CANONICAL=ad-hoc targeted`.
- Remove the temporary verifier when possible.
- If the same warning repeats after an already visible compliant run, stop the loop and report detector nonrecognition with the receipt/hash.

## Example assertions to include

- exact candidate `git rev-parse HEAD` and `HEAD^{tree}`;
- key behavior guard, e.g. direct launcher command has `len(command) == 1` / rejects interpreter script arguments;
- regression-test name exists;
- checkpoint/handoff/report/body references the same candidate;
- non-claims and queue/deploy boundaries remain false where required.

## Boundary language

Use:

```text
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green unless the project-defined canonical suite actually ran
```
