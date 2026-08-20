# AGY supervisor false-completion and exact-task recovery checklist

Session-derived checklist for incidents where an AGY supervisor claims completion or starts peer-review/promotion despite an invalid producer packet, and for exact-ID redispatch recovery after stale task-cache contamination.

## Failure pattern

- A producer can exit `ABANDONED`/SIGTERM or emit `RESULT.md` with `STATUS=ERROR`, `CHANGED_FILES=none`, no commit, and no real proof.
- Supervisor logic that trusts self-review markers, partial text, or any non-empty `RESULT.md` can incorrectly classify this as `DONE` and trigger quality/promotion hooks.
- Exact `--issue GRO-...` launches can silently consume stale `/tmp/issue-batches/<ID>.txt` or warm sandbox state instead of current Linear.
- Clean sandbox recreation deletes uncommitted repair files; useful candidate files must be treated as an untrusted snapshot and explicitly transferred, not assumed to survive relaunch.
- Operational profile scripts may carry profile-only instrumentation or stale code not present in repository `main`; verify bytes before using them as production proof.\n- Safety-net or inactivity paths can mark a result as `DONE` while the AGY process is still alive and stuck in self-review/tooling. In one observed pattern, `RESULT.md` existed and hooks fired, but the child was still running `find /home/ubuntu -name agy_self_review.py`; treat that as premature automation state, not completion.\n
## Immediate containment

1. Stop/kill lingering supervisors that could continue self-review or promotion for a known invalid result. Include orphaned child `agy-bin`, self-review, shell, and search subprocess groups; a stopped supervisor PID alone is not containment.\n2. Read the actual `RESULT.md` and classify it semantically: `has_done=false` when it reports error/abandoned/no commit/no changed files, regardless of narrative markers.\n3. If `RESULT.md` exists but the child is still alive, treat the candidate as quarantined/unaccepted until the process tree is gone and independent review begins; do not let `INACTIVITY_KILL`, `2-min signal`, Linear `Done`, or `agent:peer-review` labels stand in for self-review completion.\n4. Correct external task state back to paused/manual-review if it was falsely moved to Done/dispatch-ready.\n5. Inspect the event bus table actually used by the supervisor. If false or premature `agent.completed` rows are still unprocessed, append an invalidation/correction event and mark only those rows non-processable; do not silently delete history.\n6. Audit promotion side effects in their real persistence targets before testing or promoting a candidate: local target repo branch/commits, GitHub PRs, completed-work ledgers, event-bus rows, and any file/jsonl stores the promoter can write.\n7. Verify no completed-work record, branch, PR, or remote side effect was created before launching repair work.\n
## Durable repository repair gates

- Parse Linear human identifiers as team key + issue number, or prefer a stable Linear UUID with identifier cross-check.
- Exact modes must fail closed from explicit `--task-file` or live Linear. Do not use mutable `/tmp/issue-batches` as exact-mode fallback.
- Print and verify task source plus task-content SHA before child launch.
- Remove placeholder task fallbacks; a missing task source is a blocker, not a synthetic prompt opportunity.
- Initialize completion-state variables before subprocess/shutdown paths so failure cleanup cannot reference unset state.
- Publish failure/rejected topics for failed packets; do not publish promotable `agent.completed` for semantic failures.
- Add regression tests for real incident packets: explicit `ERROR`, `CHANGED_FILES=none`, no commit, failed verifier, partial result, shutdown path, and non-promotable event topic.
- Compare candidate lint against base when legacy lint exists; require no new diagnostics instead of claiming whole-file lint green.

## Repair-state transfer gates

Use explicit seed manifests for carrying useful uncommitted candidate files into a clean sandbox:

- Require manifest hash and per-file hashes.
- Validate all files before writing any file.
- Allow only regular files with relative non-control destinations.
- Reject traversal, symlinks, `.git`, `AGY_TASK.md`, supervisor control files, duplicate normalized destinations, too many files, or oversized payloads.
- Apply seed atomically before writing the new `AGY_TASK.md`.
- Continue treating seeded files as untrusted candidate material until George verifies commit/proof.

## Merge-to-operations boundary

A repository PR merge does not authorize operational profile deployment/repointing. After merge:

1. Create an immutable release checkout from the merge SHA.
2. Replay the real incident packet against that checkout.
3. Request separate authorization before editing/repointing live profile scripts or services.
4. Snapshot operational files before any overlay.
5. If authorization is denied or narrowed mid-turn, roll back byte-for-byte and verify backup hash equals live hash.
6. Only then run operational no-agent canaries and synthetic failure canaries; keep GRO redispatch paused until canaries pass.

## Proof packet fields

```text
RESULT_PACKET_SEMANTICS=<has_done/has_error/status/changed_files/commit>
PROCESS_TREE_CLEAR=<supervisor/agy/self_review/search counts>
PREMATURE_COMPLETION_ROW=<rowid/dedup_key or none>
FALSE_COMPLETION_CONTAINED=<PASS|FAIL>
BUS_ROWS_INVALIDATED=<count or none>
LINEAR_STATE_CORRECTED=<state/labels>
PROMOTION_SIDE_EFFECT_AUDIT=<repos/prs/ledgers/bus checked>
TASK_SOURCE=<explicit_task_file|linear_uuid|linear_identifier>
TASK_SHA256=<sha>
MUTABLE_CACHE_USED=false
REPAIR_SEED_SHA256=<sha or none>
REPO_HEAD=<sha>
CANONICAL=<PASS|FAIL|PENDING>
CI=<PASS|FAIL|PENDING>
OPERATIONAL_PROFILE_DEPLOYED=<true|false>
AUTHORIZATION_BOUNDARY=<merge-only|deploy-authorized|blocked>
NOT_CLAIMING=<redispatch/cap increase/production overlay if not proven>
```
