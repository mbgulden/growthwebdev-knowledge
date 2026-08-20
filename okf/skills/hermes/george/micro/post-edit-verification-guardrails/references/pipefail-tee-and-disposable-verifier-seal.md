# Pipefail, tee, and disposable verifier final seals

Use this reference when a post-edit guard keeps requesting fresh verification after source/evidence packet edits and the closeout uses a disposable `/tmp/hermes-verify-*` pytest probe plus retained logs.

## Durable lesson

A final verifier can appear green in chat while still returning a masked or incorrect process status if the shell pipes pytest through `tee` without `set -o pipefail`. Always enable pipefail for proof commands that use `tee`, especially when the log is part of the receipt.

```bash
set -o pipefail
source /path/to/project/venv/bin/activate
cd /path/to/worktree
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. pytest -p no:cacheprovider -q /tmp/hermes-verify-<random>.py \
  | tee /tmp/hermes-verify-<topic>.log
```

If the first verifier failure is only a disposable assertion mismatch (for example, the product raises the correct error class but with different wording), classify it as verifier setup failure, patch only the temporary probe, and rerun with `pipefail`. Do not edit source or evidence packets after the final passing rerun unless you will rerun proof again.

## Exact-head acceptance seal pattern

A robust final seal for an accepted local candidate should assert all of these in the temporary pytest probe:

- exact `git rev-parse HEAD` and `HEAD^{tree}`;
- clean `git status --porcelain=v1`;
- SHA-256 of the accepted packet/handoff/current-state artifacts;
- explicit packet keys for no-push/no-merge/no-deploy/no-restart boundaries;
- at least one product behavior assertion that exercises the repaired fail-closed path.

Then run direct project commands outside the temp probe:

```bash
set -o pipefail
pytest -p no:cacheprovider -q <focused-test-files> | tee /tmp/hermes-verify-<topic>-focused.log
ruff check --select E9,F63,F7,F82 <changed-files> | tee /tmp/hermes-verify-<topic>-ruff.log
git diff --check <base> HEAD
test -z "$(git status --porcelain=v1)"
rm -f /tmp/hermes-verify-<random>.py
test ! -e /tmp/hermes-verify-<random>.py
sha256sum /tmp/hermes-verify-<topic>-*.log <accepted-packet>
```

## Pitfalls surfaced by GRO-4407 closeout

- `pytest ... | tee log` without `set -o pipefail` can return success from `tee` even when pytest fails. The rerun must include pipefail.
- Error-message regexes in disposable probes are verifier code, not product truth. Prefer stable substrings from the implemented guard (for example, `not an existing regular file`) or assert only the error class when wording is not the contract.
- Tool displays may visually mask sensitive-looking values such as `PUSH_AUTHORIZED=false` in generated code snippets. If a verifier assertion is critical, read back the temp file or print neutral parsed labels rather than relying on the displayed write preview.
- Retain proof logs but remove disposable temp scripts; include both the log hashes and `TEMP_SCRIPT_CLEANED=true` in the final receipt.

## Reporting boundary

Keep the final packet explicit:

```text
RESULT=PASS
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green,push,PR,merge,release,deploy,restart,Linear mutation
MARKER=<stable_marker>
```
