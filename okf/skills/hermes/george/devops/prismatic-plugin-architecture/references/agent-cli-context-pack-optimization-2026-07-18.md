# Agent CLI Context-Pack Optimization — AGY and Jules

Session date: 2026-07-18

## Class lesson

For assigned-agent CLI dispatch, the durable optimization is not “more memory inside the model.” It is:

```text
small launch prompt
+ durable context-pack files
+ exact completed-work/proof packet contract
+ CLI-specific launch/capture/reconcile wrapper
+ conservative BLOCKED fallback when output is malformed or missing
```

This preserves context, makes outputs normalizable, and avoids giant chat/log blobs.

## Fred's completed-work skill-pack layer

Fred's useful direction was `AGENT_COMPLETED_WORK_SKILL_PACKS_OK`: shared and agent-specific completed-work skill packs with compact proof packet/non-claim discipline. Treat this as a handoff/output contract layer, not proof that every live agent profile has new memory installed.

Primary contract shape:

```text
agent/source_path/changed_files/proof/artifacts/non_claims/marker
COMMAND/RESULT/LOG/SCOPE/AD_HOC_OR_CANONICAL/NOT_CLAIMING/MARKER
```

## AGY CLI pattern

Installed AGY CLI supports useful non-interactive dispatch flags:

```text
agy --print <prompt>
agy --log-file <path>
agy --print-timeout <duration>
agy --add-dir <path>
agy --project <id>
agy --conversation <id>
agy --agent <agent>
agy --model <model>
```

Recommended AGY dispatch pattern:

1. Generate a bounded context pack under a durable run directory, e.g.:
   - `CONTEXT_PACK.md`
   - `PACKET_CONTRACT.md`
   - `ACCEPTANCE.md`
2. Launch with a small prompt that tells AGY to read the context pack and finish with exact compact packet lines.
3. Use `--add-dir` narrowly: repo/worktree plus the run-context directory only.
4. Use `--log-file` and/or an output-capture wrapper so stdout/stderr and final packet are reconciler-readable.
5. Preflight configured model names with a tiny canary before bulk dispatch.
6. If AGY exits without exact `RESULT=` and `MARKER=` lines, append/report `RESULT=BLOCKED` with a concrete blocker rather than treating silence as work evidence.

Suggested marker: `AGY_CLI_CONTEXT_PACK_OK`.

## Jules CLI pattern

Installed Jules CLI is async/session based. The observed CLI help shape was:

```text
jules new "<task>"
jules new --repo owner/repo "<task>"
jules new --parallel 1-5 "<task>"
jules remote list --session
jules remote pull --session <id>
jules teleport <id>
```

Do not assume Jules supports AGY-style flags such as `--print`, `--log-file`, `--model`, `--add-dir`, `--issue`, or `--task` unless live help proves it. If existing dispatcher code uses `jules --issue ... --task ...`, inspect and repair it against the installed CLI surface before relying on Jules dispatch.

Recommended Jules dispatch pattern:

1. Use Jules for bounded review/test/QA tasks unless explicitly assigned broader implementation.
2. Launch with `jules new --repo mbgulden/prismatic-engine "<compact task prompt>"` or run from the repo cwd with `jules new "<compact task prompt>"`.
3. Include repo, branch/base, exact files, acceptance criteria, and required output packet format in the prompt/context pack.
4. Persist the remote Jules session ID/handle in launch records.
5. Reconcile later via `jules remote list --session` / `jules remote pull --session <id>` and normalize pulled output into the same completed-work packet contract.
6. Avoid `--parallel` by default; it multiplies outputs and reconciliation work. Use only for explicitly parallel exploratory review.

Suggested marker: `JULES_CLI_SESSION_CONTEXT_PACK_OK`.

## Reporting boundary

When reporting this optimization, be precise:

```text
Fred skill-pack docs/tests shipped ≠ live skills installed everywhere.
AGY context-pack wrapper proof ≠ AGY completed the assigned task.
Jules session created ≠ Jules result pulled/reconciled.
CLI help proof is ad-hoc targeted, not canonical suite green.
```
