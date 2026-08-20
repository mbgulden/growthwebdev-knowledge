# AGY packet normalization rerun — session detail

Use this reference when a one-task AGY dry run emits a structured packet that ingests but is rejected by the completed-work gate.

## What happened

A first one-task canary obeyed boundaries (`resolved_agent=agy`, `launched_tasks=1`, `bulk_dispatch=false`, `auto_merge=false`) but the persisted row classified as `rejected` because AGY omitted `source_path`.

The packet dialect AGY emitted was not garbage; it contained:

```text
agent, issue_identifier, source_branch or branch, base_branch, changed_files,
lane_scope/verification_lane, proof or verification, non_claims, marker
```

The durable fix was **not** to synthesize/fix that packet after the fact. The fix was to add an adapter before completed-work classification so canonical AGY result packets normalize into the gate dialect when they contain legitimate provenance.

## Adapter behavior that worked

In `prismatic/agy_completed_work.py`, normalize before `classify_completed_work()`:

```text
source_branch = packet.source_branch or packet.branch
source_path = first safe absolute /home/ubuntu/... result_artifact
           or controlled /home/ubuntu/.prismatic/agy-result-packets/<issue_identifier>
           when issue_identifier + branch/source_branch exist
base_branch = packet.base_branch or "main"
lane_scope = object derived from merge_lane/verification_lane + changed_files
proof = verification.result + commands + log_path + marker + non_claims
normalization.marker = AGY_RESULT_PACKET_NORMALIZED_OK
```

Do not derive a fallback if explicit/result artifact paths are unsafe. Unsafe examples that should still reject:

```text
../ traversal
/home/ubuntu/.ssh/*
/home/ubuntu/.aws/*
/home/ubuntu/.config/*
/home/ubuntu/.gemini/*
secret/token/credential path components
node_modules/vendor/dist/build generated paths
```

## Regression coverage to keep

- canonical AGY result packet without explicit `source_path` but with safe `result_artifacts` becomes `merge_ready`;
- packet missing both source path and derivable issue/branch/artifact provenance remains `rejected`;
- derived `source_path` is stable/deterministic;
- traversal/secret/generated artifact paths remain rejected;
- `non_claims` stay non-claims and never imply production/auto-merge proof;
- the original blocked one-task fixture normalizes out of `rejected` into a non-rejected manual-review state.

## CI/security scanner pitfall

The public security readiness scanner may flag long realistic `/tmp/fred-...verify.log` fixture strings as high-confidence secret-like values. For static test fixtures, use neutral paths such as:

```text
/tmp/agy-proof.log
```

Keep real runtime verifier logs under `/tmp/fred-...log`; the scanner issue was in committed fixture text, not the runtime proof pattern.

## Successful rerun proof shape

After deploying the adapter, rerun exactly one new AGY task. The successful proof had:

```text
AGY_task_count=1
no_other_tasks_launched=true
result packet omitted source_path intentionally
normalization_marker=AGY_RESULT_PACKET_NORMALIZED_OK
completed_work_row.classification=merge_ready
merge_backlog.action=open_or_update_pr
merge_backlog.verification_gate=pass
eligible_for_auto_merge=false
real_github_pr_created=false
MARKER=AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK
```

Do not reuse the previously blocked packet as success proof; it is only a regression fixture.