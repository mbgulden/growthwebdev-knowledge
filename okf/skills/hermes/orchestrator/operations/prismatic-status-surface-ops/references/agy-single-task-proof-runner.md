# AGY Single-Task Proof Runner

Session learning from proving the AGY canary after assigned-agent resolver/wake behavior was accepted.

## Trigger

Use this when assigned-agent dispatch recovery is blocked only by `AGY_SINGLE_TASK_PROOF_OK`, especially for the approved canary `GRO-3837`.

Do **not** expand resolver/wake work in this phase. The next slice is one real AGY canary task and proof readback.

## Current AGY CLI shape

The installed AGY CLI supports the non-interactive shape:

```text
agy --print <prompt> --print-timeout <duration> --model "Gemini 3.5 Flash (High)" --log-file <path>
```

Do not use the legacy unsupported dispatcher shape:

```text
agy --headless --issue ...   # unsupported for this installed CLI
```

## Guardrails

- Hard-code or otherwise enforce the single allowed issue when running a canary, e.g. `ALLOWED_IDENTIFIER = "GRO-3837"`.
- Refuse every other issue before calling AGY.
- Query Linear first and require the issue resolves back to the exact allowed identifier.
- Require expected labels such as `agent:agy` and `dispatch:ready` before launch.
- Capture pre-run and post-run `/tmp/issue-batches` snapshots so the proof can say whether the runner created unrelated batch files.
- If AGY does not expose `actual_input` / `actual_output` token counters, acceptable equivalent proof is:
  - `prompt_length > 0`
  - `task_payload_bytes > 0`
  - `result_text_bytes > 0`
  - result artifact exists
  - proof artifact exists
  - live Linear comment exists
  - live Linear state update exists
  - proof no unrelated task/batch launch occurred

## Runner pattern

A durable runner can live at `scripts/verify-agy-single-task-proof.py` and should:

1. Fetch the allowed Linear issue by identifier.
2. Build and persist a task payload JSON.
3. Build and persist the exact prompt.
4. Run `agy --print` with the selected model and a log file path.
5. Write `RESULT.md`, `proof.json`, `agy.log`, `task_payload.json`, and `prompt.txt` to a timestamped artifact directory.
6. Require non-empty result text and a `DONE: <identifier>` marker somewhere in the result artifact.
7. Post a Linear proof comment with the accepted fields.
8. Move the issue to an explicit review state such as `In Review` after artifact/comment proof succeeds.
9. Print `AGY_SINGLE_TASK_PROOF_OK` only after artifact and Linear writeback succeed.

Example proof output shape:

```json
{
  "AD_HOC_VERIFICATION": "PASS",
  "marker": "AGY_SINGLE_TASK_PROOF_OK",
  "identifier": "GRO-3837",
  "model": "Gemini 3.5 Flash (High)",
  "command_shape": ["agy", "--print", "<prompt>", "--print-timeout", "20m0s", "--model", "Gemini 3.5 Flash (High)", "--log-file", ".../agy.log"],
  "prompt_length": 2037,
  "task_payload_bytes": 1811,
  "result_text_bytes": 8969,
  "result_artifact_exists": true,
  "linear_comment_id": "...",
  "linear_state_update_ok": true,
  "new_issue_batch_files": [],
  "no_other_tasks_launched": true
}
```

## Post-run readback verifier

After running the real canary, run a separate `/tmp/hermes-verify-*` readback verifier that does **not** launch AGY again. It should verify:

- `python3 -m py_compile scripts/verify-agy-single-task-proof.py`
- the runner is merged/readable from `origin/deploy-fresh` if committed;
- runner contains hard guard (`ALLOWED_IDENTIFIER = "GRO-3837"`) and `"--print"` markers;
- `proof.json` has `marker=AGY_SINGLE_TASK_PROOF_OK` and `identifier=GRO-3837`;
- `prompt_length`, `task_payload_bytes`, and `result_text_bytes` are all greater than zero;
- artifact paths exist;
- `RESULT.md` contains `DONE: GRO-3837`;
- live Linear issue is the same identifier and has the proof comment;
- live Linear state is the expected review state;
- no new issue-batch files were created by the runner.

If a stale guard flags the prior temp verifier path, include that old path in `changed_paths_checked`, assert it no longer exists, and clean up the new verifier.

## Reporting boundaries

Only after this proof passes may you claim:

```text
AGY_SINGLE_TASK_PROOF_OK
```

If assigned-agent behavior markers were already proven, you may then claim:

```text
ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
```

If the queue/dashboard/drain/preflight chain was also already accepted, you may claim:

```text
DASHBOARD_DISPATCH_INGESTION_READY_OK
```

Always label the result as ad hoc targeted recovery proof, not canonical full suite green.

## Pitfalls

- Do not rerun/expand resolver/wake work after the user accepts those markers.
- Do not launch AGY if the runner cannot capture either token counters or the accepted equivalent proof fields.
- Do not merge the AGY task-output PR as part of the canary proof unless explicitly asked; report it as the canary's output artifact/PR.
- If AGY returns an action transcript before the final answer, the proof can still be valid if byte counts are non-zero and `DONE: <identifier>` appears in the artifact, but future hardening should prefer requiring the first substantive result line to be the DONE marker.
