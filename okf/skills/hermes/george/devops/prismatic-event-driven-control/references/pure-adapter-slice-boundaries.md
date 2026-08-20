# Pure adapter slice boundaries

Use this reference when a Prismatic slice is a provider/gateway/status adapter around an already-existing core verification or policy engine, and the event-driven dashboard admission gate is active.

## Signal

A preflight may reveal that the first task draft mixes separable concerns:

1. pure deterministic adapter logic;
2. gateway/webhook ingress hardening;
3. outbound provider transport such as REST POST/PATCH;
4. producer admission or dashboard control-plane work.

Do not keep the broad task just because all items are related. Split the slice so the pure adapter can be proved without network, credential, gateway, queue, deployment, or merge side effects.

## Preferred bounded contract

For a pure adapter slice, define:

- exact allowed paths;
- public immutable models and functions;
- accepted input and fail-closed rejection rules;
- deterministic IDs/digests/replay keys;
- binding between adapter output and the canonical core receipt/policy model;
- a projection payload, if needed, but no transport call;
- explicit non-claims for gateway wiring, provider REST mutation, producer start, deploy/restart, task-manager updates, and merge authorization.

## Verification expectations

Require tests that prove:

- valid fixtures normalize/project deterministically;
- malformed, unsigned, unsupported, stale, revoked, mismatched, or ambiguous cases fail closed;
- no raw secrets, raw payload, arbitrary issue/PR text, logs, or command output appear in public outputs/errors;
- environment, local config, filesystem credential discovery, subprocess, network, gateway/event bus, and task-manager access are monkeypatched to raise and remain unused;
- distribution proof installs a built wheel non-editably in a fresh environment and imports from an empty CWD.

## Coordination rule

If a pure adapter task is contract-ready but the live dashboard lacks verified task admission, keep it `QUEUED_NOT_ADMITTED_EVENT_ONLY`. It is valid to launch a separate read-only preflight for the admission endpoint/ledger/UI prerequisite, but do not start the implementation producer until an authenticated durable admission receipt binds the exact task digest and writer cap.
