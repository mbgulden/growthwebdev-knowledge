# Controlled Two-Task AGY Stage After Canary

Use this reference when dispatch recovery/canary proof has passed and Michael asks to open the next AGY stage.

## Durable pattern

1. Treat canary dispatch proof and canary output quality as separate gates.
2. Do not open the next stage until the canary output PR/artifact is reviewed, fixed if needed, merged/accepted, and the Linear issue is closed with evidence.
3. When the next stage is approved, launch only the named issues — not the backlog and not every `dispatch:ready` item.
4. Before launch, live-read Linear for the named issues. Clear only stale abandoned-run blockers that directly prevent the approved stage, for example:
   - remove `agent:needs-human-review` only when it is stale from an abandoned run and not a real Michael blocker
   - remove `dispatch:paused` only for the approved issues
   - preserve or add `agent:agy` + `dispatch:ready`
5. Use a guarded runner that hard-fails unless the issue set is exactly the approved set. For `GRO-3838` + `GRO-3839`, assert `set(issues) == {'GRO-3838','GRO-3839'}` and run one `agy --print` per issue.
6. Capture per-issue artifacts:
   - `task_payload.json`
   - `prompt.txt`
   - `RESULT.md`
   - `proof.json`
   - `agy.log`
   - Linear proof comment ID
7. Move outputs to `In Review`, not `Done`, unless the resulting PR/artifact has been reviewed and accepted.
8. If AGY opens a PR, review it normally. Do not merge solely because dispatch succeeded.
9. If AGY hits lane governance, report the exact lane blocker and route to the allowed owner lane; do not bypass hooks.

## Required guardrails

- No bulk redispatch.
- No third issue launch.
- Preserve assigned-agent wake semantics: Kai -> Kai, Fred -> Fred, AGY -> AGY, unknown/ambiguous -> manual review.
- No uncontrolled Ned expansion.
- No completion without result evidence.
- Use the exact boundary language: `Recovery proof is ad-hoc targeted, not canonical full suite green.`

## Final verification shape

Run a fresh `/tmp/hermes-verify-*` readback that proves:

- `issues_attempted` equals the approved set exactly.
- Each issue has return code 0 and `DONE: ISSUE` marker in its result artifact.
- Linear state/comment readback exists for each issue.
- No stale blocker labels remain unless intentionally preserved.
- No active AGY stage process remains.
- Any PR opened by AGY is still review-gated unless accepted by a separate output review.
- Cleanup removed temp verifier files.

## Reporting markers

- Launch/readback complete but output still needs review: `CONTROLLED_AGY_STAGE_<ISSUES>_COMPLETE_FOR_REVIEW`.
- Do not claim `<ISSUE>_OUTPUT_REVIEW_OK` until PR/artifact review passes.
