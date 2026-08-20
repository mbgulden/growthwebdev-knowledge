# AGY one-task proof, packet normalization, and overnight guard — July 2026

## Trigger
Use this reference when moving from AGY canary proof toward staged/overnight AGY work.

## Critical separation
A successful AGY **dispatch** is not the same as an accepted AGY **output**. Treat these as separate gates:

1. Launch/canary proof: exactly one AGY task ran and emitted a packet.
2. Completed-work ingestion: packet persisted and normalized.
3. Merge backlog dry-run: action/branch/proof plan produced.
4. Verification gate: `verification_gate=pass` and `eligible_for_auto_merge=false`.
5. Output review: PR/artifact must still be reviewed normally before any merge/next stage.

## Packet normalization lesson
Do not require AGY to speak the internal completed-work dialect perfectly if safe provenance can be derived. Normalize before gate classification:

- derive `source_path` from safe `result_artifacts.path` when present
- derive a stable synthetic source path only when safe metadata is sufficient
- normalize string `lane_scope` such as `docs` into a gate lane object/scope
- preserve strict rejection for unsafe/underivable provenance
- local/non-`feature/*` branches should become manual-review/scope-review, not automatic rejection, when the rest of the packet is otherwise valid

Regression fixture shape that should normalize instead of hard-reject:

```json
{
  "agent": "agy",
  "issue_identifier": "LOCAL-AGY-CANARY",
  "source_branch": "local-canary",
  "base_branch": "main",
  "changed_files": ["agy-one-task-lane-note.md"],
  "lane_scope": "docs",
  "proof": {"result": "PASS"},
  "marker": "AGY_TASK_RESULT_PACKET_OK"
}
```

## One-task proof boundary
When the user asks for a one-task canary/rerun:

- launch at most one AGY task after preflight
- if preflight fails, that does **not** count as an AGY task launch
- if AGY emits an invalid packet, do not synthesize success by editing the packet after the fact
- report `PARTIAL/BLOCKED` honestly and fix the adapter/prompt before a new one-task rerun

## Overnight readiness guard pattern
The guard is **readiness only**. It must not launch AGY, create PRs, enable auto-merge, or deploy production.

Policy should fail closed on:

- operator pause active
- unknown/disabled agent requested
- `max_tasks` above small cap (1–2)
- `auto_merge=true`
- production deploy requested
- real GitHub PR creation enabled by default
- missing latest one-task success marker
- unresolved previous failure
- missing ingestion / merge-backlog / verification-gate health

Expose operator state through local/gateway APIs and a real-data dashboard card, e.g. readiness state, agents/tasks cap, safety flags, pause state, blockers, and next safe action.

## Verification markers
Useful compact markers:

```text
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_OK
AGY_AUTOPILOT_ONE_TASK_DRY_RUN_BLOCKED
AGY_RESULT_PACKET_NORMALIZED_OK
AGY_OVERNIGHT_READINESS_GUARD_OK
```

Always include non-claims:

```text
bulk_agy_dispatch=false
overnight_autopilot_active=false
auto_merge_enabled=false
production_deploy=false
real_github_pr_created=false
canonical_full_suite_green=false unless actually run
```

## Stale detector handling
For repeated stale-verification reminders, stop elaborating. Emit the exact compact KEY=VALUE block with:

- `CANONICAL_TEST_LINT_BUILD_COMMAND=...`
- `AD_HOC_VERIFICATION=PASS`
- exact `changed_paths_checked=` list from the reminder
- `cleanup=PASS`
- final marker

Use a fresh `/tmp/hermes-verify-*` tempfile each time and remove stale verifier files listed by the detector.
