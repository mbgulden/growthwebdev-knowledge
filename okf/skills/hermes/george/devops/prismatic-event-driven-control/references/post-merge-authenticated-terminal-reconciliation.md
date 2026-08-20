# Post-merge authenticated terminal reconciliation

Use this pattern only after a stale outbox/claim bootstrap repair has been implemented, independently reviewed clean, merged, and explicitly authorized for deployment/live mutation.

## Preconditions

- Exact repaired candidate has independent `CLEAN` review at head/tree.
- PR is merged and the merge tree is proven to equal the reviewed candidate tree.
- An immutable, non-local release checkout exists and passes focused release validation / `git fsck`.
- Deployment/restart authorization is explicit and scoped to the reconciliation route.
- Source evidence for the stale task is revalidated against Git/GitHub or the canonical source of truth.
- Zero active producers and no writer lease are proven immediately before mutation.

## Safe execution sequence

1. Build a versioned runtime/venv for the immutable release; do not run the route from a mutable dev checkout.
2. Install a higher-priority systemd drop-in that binds the service WorkingDirectory and executable to the versioned release/venv.
3. Restart the gateway and verify systemd `ActiveState=active`, `SubState=running`, exact `ExecStart`, exact `WorkingDirectory`, and `/health`.
4. Prefer the merged API parser to validate the exact request body before sending it.
5. If the control plane is hash-only and no plaintext operator token is stored, provision an in-memory one-time operator credential only for the exact request:
   - add only the digest to the private auth file;
   - send the request in the same process;
   - restore the original auth file byte-for-byte in `finally`;
   - never print the token or digest.
6. Read back the response and the database state independently:
   - stale outbox row is terminal (`failed` or contract-specific terminal state);
   - claim is terminal with expected error code;
   - launch receipt remains null when no launch happened;
   - lifecycle has exactly one reconciliation event with expected detail digest;
   - writer lease count is zero.
7. Prove the ordinary consumer predicate no longer selects the stale event, and prove the global next candidate is null or is the expected successor. Do **not** invoke the ordinary consumer as proof.
8. Remove executable one-time request scripts and request bodies after successful final verification to prevent accidental replay.
9. Update the handoff/report to distinguish the deployed gateway route from any separate runtime/orchestrator convergence that remains undeployed.

## Compact proof fields

```text
RELEASE=<immutable release path>
RELEASE_HEAD=<merge sha>
RELEASE_TREE=<tree sha>
GATEWAY_SERVICE=<unit>
WORKING_DIRECTORY=<release path>
EXECUTABLE=<versioned venv python>
HEALTH_HTTP=200
HTTP_STATUS=200
REPLAYED=false
LAUNCH_PERFORMED=false
OUTBOX_STATUS=<terminal state>
CLAIM_STATE=<terminal state>
ERROR_CODE=<bounded reason>
LAUNCH_RECEIPT=null
TERMINAL_RECONCILED_ROWS=1
WRITER_LEASE_ROWS=0
EVENT_MATCHES_CONSUMER_PREDICATE=0
GLOBAL_NEXT_CANDIDATE=<null or expected id>
ACTIVE_PRODUCERS=0
ONE_TIME_ACTOR_PRESENT=false
REQUEST_SCRIPT_REMOVED=PASS
REQUEST_BODY_REMOVED=PASS
NOT_CLAIMING=<producer completion, successor admission, unrelated runtime convergence>
```

## Pitfalls

- Do not mutate SQLite directly if the whole purpose of the slice was to add an authenticated control route; use the route and then independently read back SQLite.
- Do not mistake deploying the gateway route for deploying a separate orchestrator/runtime integration. Track separate `GATEWAY_DEPLOYED=true` and runtime-specific `DEPLOYED=false` fields when both appear in the handoff.
- Do not leave one-time request bodies/scripts around after success; they are replay hazards even when the credential has been removed.
- A process-search command can match its own arguments; resolve PID/ancestor identity before treating a single match as an active producer.
