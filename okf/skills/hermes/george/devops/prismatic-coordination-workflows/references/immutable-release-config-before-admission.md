# Immutable release/configuration before event admission

## Trigger

Use this when Michael authorizes deployment/configuration of Prismatic launcher/runtime code but explicitly says to stop before admitting a task or launching a producer.

## Durable lesson

Treat **deployment/configuration** and **admission/producer launch** as separate gates. A safe deployment slice can install an immutable release, versioned venv, private exact-task configuration, and a clean worktree while still proving that no policy was widened, no admission event was posted, no one-shot consumer was invoked, and no producer started.

## Procedure

1. Rebind the exact merged commit/tree before creating the release.
2. Create or verify the immutable release directory with no git alternates and a clean worktree.
3. Build/install a versioned runtime environment tied to that release.
4. Create the clean task worktree at the exact base commit/tree.
5. Copy/bind the task contract byte-for-byte; hash the external and worktree copies.
6. Write private config files with exact hashes and mode `0600`.
7. Constructor-validate config/parser/harness without calling dispatch.
8. Restart/verify the live service only after release/config proof is ready.
9. Prove the stop boundary:
   - admission policy not created or widened;
   - AGYCW task outbox count is zero;
   - writer leases are zero;
   - runtime/spool directories are empty;
   - AGY admission tmux/session count is zero;
   - one-shot consumer was not invoked.
10. Update handoff with `DEPLOYED=true`, `RUNTIME_CONFIGURED=true`, `AGYCW*_ADMITTED=false`, and `PRODUCER_LAUNCHED=false`.
11. Run a final `/tmp/hermes-verify-*` ad-hoc verifier after the handoff/config writes that reads back every changed artifact, including removed temporary files if they appeared in a detector manifest.

## Proof packet shape

```text
RESULT=PASS|FAIL|BLOCKED
RELEASE=<immutable release path>
MERGE_SHA=<sha>
TREE=<tree>
CONFIG_SHA256=<private config hash>
TASK_SHA256=<external/worktree byte-equal hash>
SERVICE_HEALTH=<route/status>
WRITER_LEASES=0
TASK_OUTBOX_EVENTS=0
RUNTIME_SPOOL_EMPTY=true
ADMITTED=false
PRODUCER_LAUNCHED=false
AD_HOC_OR_CANONICAL=ad-hoc deployment/configuration boundary proof
NOT_CLAIMING=admission, producer launch, task completion, canonical suite green unless separately run
```

## Pitfalls

- Do not treat a healthy service restart as implicit task admission.
- Do not update task status metadata after the final verifier without rerunning a post-write artifact verifier.
- If a temporary systemd drop-in or verifier file is removed but appears in the changed-path manifest, assert its absence in the final verifier rather than ignoring it.
- If a health probe fails, verify the correct live/documented route before treating the deployment as unhealthy; keep the failed route as a verifier/probe issue unless service status/logs prove product failure.
