# Merge closeout and next-slice admission

Use this pattern when a Prismatic repair/slice PR has exact-head independent `CLEAN` and Michael's policy authorizes merge after exact-head independent/local proof.

## Trigger

- A focused Prismatic PR has exact-head independent `CLEAN` review.
- Local proof is bound to the reviewed commit/tree.
- The next task is ready but writer cap must remain controlled.

## Closeout sequence

1. **Bind the merge to the reviewed artifact before overclaiming.**
   - Record reviewed PR head and tree.
   - Merge only after authorization/policy allows it.
   - After merge, verify merge commit and tree.
   - If merge tree equals reviewed tree, say so explicitly; if not, treat it as new unreviewed material.

2. **Create an immutable release checkout for durable proof.**
   - Make a release directory keyed by merge SHA/date.
   - Detach it from mutable worktrees and alternates when possible.
   - Verify `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, `git fsck`, and absence of `.git/objects/info/alternates`.
   - Run focused checks, lint/format checks, wheel/import/runtime probes, or the appropriate bounded proof suite from that release checkout.
   - Save noisy logs to `/tmp` or a durable artifact and report the log SHA.

3. **Separate proof classes.**
   - Hosted CI blocked by account/spend/config is not product failure and not canonical green.
   - Exact-tree equivalence plus local proof can justify the merge/release claim, but do not claim deployment, service restart, Linear write, or generic dispatch unless performed and verified.
   - If later broad tests fail from known live/budget state, report them separately from canonical exact-tree proof.

4. **Update durable handoff/control state before the next dispatch.**
   - Include merge SHA/tree, release path, log path/digest, active cap, and non-claims.
   - After editing handoff/control JSON/Markdown, run a final ad-hoc readback verifier covering the changed state and key release facts.

5. **Admit the next producer at cap 1.**
   - Create/reset a clean worktree from the merge SHA, not from a mutable dev checkout.
   - Preserve `GRO4210_PLUS=PAUSED` / generic dispatch paused until the current producer is reviewed.
   - Record the next task file path and SHA256.
   - Launch the producer and keep the process/session/log handle.

## AGY CLI launch notes

When using the AGY CLI lane for Gemini-model work:

- Do not assume provider-style flags such as `--provider`; inspect CLI usage or use the installed CLI's model labels.
- Model selection may require the exact configured display label, e.g. `--model 'Gemini 3.6 Flash (High)'`.
- For non-interactive producer dispatch, use `--print-timeout` long enough for the bounded task and redirect output to a log.
- If the first print attempt times out, retry with an explicit longer `--print-timeout` rather than treating the producer/task as failed.

Example skeleton:

```bash
TASK=/home/ubuntu/prismatic-agent-bus/tasks/GRO-XXXX/TASK.md
LOG=/tmp/agy-groXXXX-launch.log
TASK_SHA256=$(sha256sum "$TASK")
HOME=/home/ubuntu/.hermes/profiles/orchestrator/home \
  /home/ubuntu/.local/bin/agy \
  --model 'Gemini 3.6 Flash (High)' \
  --print-timeout 30m \
  --add-dir /home/ubuntu/prismatic-agent-bus \
  --dangerously-skip-permissions \
  --print "$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).read_text())' "$TASK")" \
  >"$LOG" 2>&1
```

## Compact closeout packet

```text
STATUS=<PASS|PARTIAL|BLOCKED>
REVIEWED_HEAD=<sha>
REVIEWED_TREE=<tree>
MERGE_SHA=<sha>
MERGE_TREE=<tree>
MERGE_TREE_EQUALS_REVIEWED_TREE=<true|false>
RELEASE=<path>
RELEASE_PROOF_LOG=<path>
RELEASE_PROOF_LOG_SHA256=<sha256>
NEXT_TASK=<issue/slice>
NEXT_TASK_SHA256=<sha256>
ACTIVE_PRODUCER=<agent/model/process>
CAP=<n>
NOT_CLAIMING=<deployment/restart/Linear/generic dispatch/canonical CI as applicable>
MARKER=<marker>
```

## Pitfalls

- Do not launch the next slice from an old feature branch after merge; reset from the merge SHA.
- Do not confuse reviewed PR head with merge SHA; bind both and compare trees.
- Do not let a successful merge imply deployment or runtime adoption.
- Do not admit `GRO4210+` while a cap-1 producer for the current slice is still active.
- Do not let AGY launch errors caused by unsupported flags or short default print timeout become durable negative claims about AGY; correct the invocation and retry with the configured model label and longer timeout.
