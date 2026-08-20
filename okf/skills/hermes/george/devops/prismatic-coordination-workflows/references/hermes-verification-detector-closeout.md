# Hermes Verification Detector Closeout Pattern

Use when Hermes reports edited paths as `unverified` after a Prismatic coordination/code turn, especially when it asks for an OS-safe temporary verifier under `/tmp` with a `hermes-verify-` prefix.

## Durable lesson

The guard may not recognize previously emitted receipts unless the closeout has a fresh, direct terminal-visible pattern. Do not argue first. If the system/user explicitly asks for a `/tmp` `hermes-verify-` tempfile closeout, comply immediately even when prior focused/canonical/CI receipts exist; those older receipts are not a substitute for the requested detector-shaped proof. Only call it a detector false negative after running the requested closeout in the current warning cycle and capturing log/digest/cleanup evidence.

## Immediate response rule

When a warning says “No canonical test/lint/build command was detected” and requests a focused temporary verifier:

- Do **not** answer with a summary of earlier proof as the first response.
- Do **not** refuse because the detector appears wrong.
- Run the requested OS-safe temporary script plus focused visible commands in the same turn.
- If the script cannot be run, name the concrete blocker. If it runs and the warning repeats, then report detector ingestion failure with the fresh closeout packet.

When a warning explicitly names a canonical command such as `pytest`:

- Run that visible command directly from the affected workspace in the same response, even if an earlier custom verifier already invoked equivalent checks.
- Capture the real output to a log with `tee`, preserve the exit code, and include exact `HEAD`, `TREE`, and worktree cleanliness if the command passes.
- If the same warning repeats with no intervening file edits after the visible passing command, do **not** run a second identical `pytest` loop. Read back the log contents/digest and edited-file mtimes, then report the concrete blocker as detector ingestion/recognition failure.

## Pattern

1. Create the verifier with Python `tempfile.NamedTemporaryFile(...)` using:
   - `dir='/tmp'`
   - `prefix='hermes-verify-...'`
   - `suffix='.py'`
   - `delete=False`
2. Store the generated path in a small `/tmp/hermes-verify-*.path` helper file if a later shell command needs to read it.
3. The temporary script should assert changed behavior and artifact identity, not just print static text:
   - exact `git rev-parse HEAD` and parent/base SHA when applicable;
   - exact changed-path set;
   - import/construct/round-trip behavior for the changed module;
   - expected fail-closed behavior such as premature promotion rejection;
   - cross-artifact consistency when the edit spans product code plus George state, e.g. control-state JSON candidate head, handoff status, and PR-body boundary markers all reference the same exact head;
   - PR body or handoff markers only with the exact current headings/strings.
4. Run the verifier from the affected workspace with `PYTHONPATH="$PWD"` when testing source-checkout code.
5. In the same shell closeout, run direct focused checks that the detector can see, for example:
   - `python3 -m pytest -q <focused test file>`
   - `uvx ruff check <changed files>`
   - `uvx ruff format --check <changed files>`
   - package build command if packaging changed or was part of the slice
   - `git diff --check <base>..<head>`
6. Remove the generated temporary verifier and path helper when possible, and report cleanup status.
7. If the guard repeats after `python3 /tmp/hermes-verify-...py`, create a second OS-safe tempfile with a shebang, `chmod 700`, and invoke the literal `/tmp/hermes-verify-...py` path directly. This direct-executable shape can satisfy detectors that do not recognize interpreter-plus-script execution. Keep the same changed-behavior assertions, clean it up, and label it ad-hoc targeted.
8. Summarize as ad-hoc targeted verification unless a full canonical suite was freshly run in that detector closeout.

## PR/state closeout addendum

When the edited-path set mixes product code, George durable handoff/control files, and a temporary PR body under `/tmp`, make the verifier bind all three layers rather than only rerunning product behavior:

- product workspace: exact `HEAD`, clean worktree, changed-path allowlist, and focused behavior under `PYTHONPATH="$PWD"`;
- durable George records: control-state JSON active task, exact candidate head/tree/PR/check/review fields, handoff status token, and next-action boundary;
- PR evidence file: exact head, CI/review state, proof counts, and non-claim/authorization boundary in the current PR body path;
- detector receipt: a unique marker for the state-closeout layer, log digest, cleanup status, and explicit `ad-hoc targeted` scope.

If a product-behavior verifier already passed before the record edits, add this separate state/PR consistency verifier after the final handoff/control-file patch. That avoids re-running broad suites just to prove record edits while still satisfying the guard's request for changed-path-aware proof.

## Pitfalls

- If the verifier fails, inspect its traceback before changing product code. A literal assertion mismatch in the verifier (for example expecting `GITHUB CI` when the PR body says `## Review and CI`) is verifier debt, not product failure.
- Match artifact assertions to each artifact’s actual binding semantics. A task contract may be bound by its own SHA-256 and intentionally *not* contain the latest candidate head; proof packets, PR bodies, handoffs, and control JSON are the right places to assert current head/tree text. If the detector verifier expects head text in a hash-bound contract and fails, fix the verifier, not the product.
- When the guard specifically says “No canonical test/lint/build command was detected,” include visible focused commands in the detector closeout, not only custom Python behavior assertions. Prefer a temp verifier that calls `python3 -m pytest -q <focused test file>`, Ruff check, and Ruff format-check for the changed paths, then binds coordination artifacts. This is still ad-hoc focused evidence unless the full canonical suite is rerun.
- After a successful detector closeout, do not edit handoff/control/proof files again in the same turn; any subsequent write can make the guard correctly treat the prior verifier as stale.
- Do not turn a repeated detector complaint into a canonical-suite claim. Keep `AD_HOC_OR_CANONICAL=ad-hoc targeted detector closeout` unless the canonical command was actually rerun.
- If the detector repeats after a valid closeout, report the concrete blocker and include the exact log path, SHA256, cleanup status, and marker rather than looping indefinitely.
- Treat “no file edits after the last passing closeout” as the loop-break test. If the changed-path list is unchanged and the previous `/tmp/hermes-verify-*` receipt already ran after the final product/state/proof write, do **not** create another near-identical verifier just because the warning reappeared; report `BLOCKED — detector ingestion false negative` or “verification guard discrepancy” with the latest receipt.
- Do not perform a third identical verifier run solely to appease repeated post-closeout warnings. After one product-behavior closeout and one final state/PR consistency closeout both pass and clean up, the correct outcome is `BLOCKED — detector ingestion false negative` with receipts, not a loop of redundant writes/tests.

## Compact packet

```text
RESULT=<PASS|FAIL|BLOCKED>
RC=<exit code>
LOG=<path>
SHA256=<log digest>
VERIFIER_CLEANUP=<PASS|FAIL>
AD_HOC_OR_CANONICAL=ad-hoc targeted detector closeout
MARKER=<specific marker printed by verifier>
```
