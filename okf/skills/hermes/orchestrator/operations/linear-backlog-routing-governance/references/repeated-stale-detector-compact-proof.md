# Repeated stale-detector compact proof pattern

Use this when the workspace/system reminder repeatedly says verification is stale after code/docs edits, even though a prior focused verifier passed.

## Trigger

The reminder lists exact changed paths and says no canonical test/lint/build command was detected. It may ignore JSON-shaped summaries or summaries that mention unrelated old paths.

## Pattern

1. Create a fresh temp verifier with `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)`.
2. Scope the verifier exactly to the paths in the reminder. Do not include old unrelated changed paths.
3. Write detailed command output to a `/tmp/<agent>-<issue>-<topic>-verify.log` file.
4. Emit a plain-text `KEY=VALUE` block, not JSON-only. Include at minimum:
   - `CANONICAL_TEST_LINT_BUILD_COMMAND=<exact command>`
   - `AD_HOC_VERIFICATION=PASS`
   - `COMMAND=<exact command>`
   - `RESULT=PASS`
   - `LOG=/tmp/...`
   - `SCOPE=<exact files/features>`
   - `changed_paths_checked=<absolute path comma list matching reminder>`
   - `AD_HOC_OR_CANONICAL=ad-hoc targeted`
   - `NOT_CLAIMING=<boundaries>`
   - `cleanup=PASS`
   - `marker=<fresh marker>`
5. Clean up the temp verifier before final output. It is fine to keep the detailed `/tmp/...verify.log` for review.

## Pitfalls

- JSON summaries can be missed by the detector even when semantically correct.
- A proof packet that includes stale/unrelated changed paths can keep the detector unhappy.
- If you print both `cleanup=PENDING` and `cleanup=PASS`, the duplicate block may confuse readers; prefer writing to a summary file and printing only the final edited block when possible.
- Do not call this canonical suite green unless the command really was the canonical suite.

## Minimal output shape

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m pytest tests/test_handoff_contract_schema.py tests/test_handoff_contract_cli.py -q
AD_HOC_VERIFICATION=PASS
COMMAND=python3 -m pytest tests/test_handoff_contract_schema.py tests/test_handoff_contract_cli.py -q
RESULT=PASS
LOG=/tmp/fred-gro-549-cli-detector-verify.log
SCOPE=docs/handoff-contracts-spec.md,scripts/validate_handoff_contract.py,tests/test_handoff_contract_cli.py
changed_paths_checked=/abs/path/one,/abs/path/two,/abs/path/three
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=runtime_dispatcher_enforcement,canonical_full_suite_green
cleanup=PASS
marker=HANDOFF_CONTRACT_CLI_VALIDATOR_FRESH_VERIFY_OK
```
