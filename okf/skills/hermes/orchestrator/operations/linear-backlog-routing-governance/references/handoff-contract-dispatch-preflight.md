# Handoff Contract Dispatch Preflight Pattern

Use this reference when a Linear/Prismatic runway task asks to turn a handoff contract, schema, or CLI validator into the first runtime dispatch gate.

## Proven shape

1. Keep the validator reusable.
   - Put shared schema + semantic validation in a module such as `prismatic/handoff_contracts.py`.
   - Keep `scripts/validate_handoff_contract.py` as a thin CLI wrapper over the shared module.
   - Update schema tests to import the shared validator so CLI/runtime behavior cannot drift.

2. Wire the smallest launch-boundary preflight.
   - Prefer the existing assigned-agent dispatch/preflight seam.
   - If no clean standalone seam exists, hook immediately before `launcher(...)` in the dispatcher and keep the helper small (`handoff_dispatch_preflight(...)`).
   - Only activate when a payload explicitly carries `handoff_packet`, `handoff_contract`, or `handoff`; do not change ordinary dispatch behavior.

3. Fail closed with reviewable states.
   - Valid packet: allow existing dispatch path.
   - Missing result/durable output: block before launch.
   - Out-of-lane changed path: block before launch.
   - Production claim without proof: block before launch.
   - Empty/ambiguous target agent: `needs_manual_review`, no agent launched.
   - Record concise reason/errors in local metadata or Linear comment path so dashboard/Linear follow-up can explain why no launch happened.

4. Keep AGY completed-work integration separate.
   - The dispatch preflight primitive must land before `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`.
   - Do not start broader completed-work classification in the preflight slice.
   - Next slice may reuse the same validator/preflight contract to classify AGY completed work as merge-ready, needs clean rebuild, blocked, superseded, or manual-review.

## Verification shape

Use a `/tmp/hermes-verify-*` script and put long output in `/tmp/fred-gro-549-preflight-verify.log` or the issue-specific equivalent.

Minimum focused command shape:

```text
python3 -m pytest tests/test_handoff_contract_schema.py tests/test_handoff_contract_cli.py tests/test_handoff_contract_preflight.py -q
```

Also run direct CLI fixture sanity if not covered by tests:

```text
python3 scripts/validate_handoff_contract.py tests/fixtures/handoff-contracts/pass.json                    # exit 0
python3 scripts/validate_handoff_contract.py tests/fixtures/handoff-contracts/missing-result.json          # nonzero
python3 scripts/validate_handoff_contract.py tests/fixtures/handoff-contracts/out-of-lane.json             # nonzero
python3 scripts/validate_handoff_contract.py tests/fixtures/handoff-contracts/production-proof-missing.json # nonzero
python3 scripts/validate_handoff_contract.py tests/fixtures/handoff-contracts/ambiguous-target-agent.json  # nonzero
```

Compact proof block should be plain text:

```text
COMMAND=<exact focused pytest command>
RESULT=PASS
LOG=/tmp/<agent>-<issue>-preflight-verify.log
SCOPE=handoff contract validator wired into assigned-agent dispatcher preflight
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=full_dispatcher_recovery,agy_completed_work_integration_gate,auto_merge,canonical_full_suite_green
MARKER=HANDOFF_CONTRACT_DISPATCH_PREFLIGHT_OK
cleanup=PASS
```

## Detector pitfall

If the workspace verifier complains about stale evidence for one changed docs path, rerun a docs-scoped `/tmp/hermes-verify-*` proof against that exact path and include the focused pytest command. Emit both `MARKER=` and, if the latch repeats, `marker=`. Do not paste logs; return only the compact block.

## PR / Linear closeout

- If the original PR is still open and scope is a small continuation, update that PR rather than opening a second one.
- Update the PR body with scope, files, focused verification, marker, and explicit non-claims.
- Write back to the Linear issue with PR URL, commit, marker, CI status, and non-claims.
- Do not merge unless repo policy explicitly allows Fred to merge the PR.