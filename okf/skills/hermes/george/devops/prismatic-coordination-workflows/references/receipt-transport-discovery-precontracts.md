# Receipt transport discovery precontracts

Use this reference when a Prismatic child asks whether cron receipts should be projected to another system, a journal endpoint, or an external receiver.

## Session-derived pattern

A read-only discovery can conclude that transport implementation is not ready even when receipt production already exists. Freeze a precontract rather than materializing a task when any receiver/outbox boundary is missing.

## Checks to run before any endpoint/credential/source work

1. Inspect the immutable deployed release, not a mutable dev checkout.
2. Prove whether the proposed receiver route exists. Do not assume a named route such as `/journal/ingest` exists from issue prose.
3. Distinguish generic telemetry/event buses from receipt transport:
   - allowed event types include receipt types;
   - persistence failure is fail-closed before success/ack;
   - dedup/idempotency uses canonical receipt identity, not generated timestamps;
   - durable rows are not pruned in a way that can erase authoritative delivery state;
   - receiver acknowledgment proves durable idempotent acceptance.
4. Search receipt finalization paths and ensure projection coverage includes both ordinary finalizer paths and direct reconciliation/orphan paths.
5. Confirm whether an authority-coupled durable outbox exists in the receipt authority store. If absent, do not adapt generic `/events` as a shortcut.
6. Verify zero event/task/admission state for the child before freezing the discovery artifact.

## Required decision when no receipt outbox/receiver contract exists

```text
DECISION=receipt_projection_requires_authority_coupled_durable_outbox_and_named_receiver_contract
SHORTCUT_FORBIDDEN=do_not_reuse_generic_events_as_receipt_transport
SOURCE_MUTATION_AUTHORIZED=false
ENDPOINT_MUTATION_AUTHORIZED=false
CREDENTIAL_ACCESS_AUTHORIZED=false
EVENT_POST_AUTHORIZED=false
PRODUCER_AUTHORIZED=false
DEPLOYMENT_AUTHORIZED=false
```

## Future implementation contract shape

A bounded implementation task must require:

- outbox insertion in the same transaction as receipt commitment;
- coverage for every receipt producer/finalization path;
- stable idempotency identity derived from destination, schema version, and receipt identity;
- canonical payload bytes and digest;
- fenced delivery leases;
- bounded retries and durable quarantine;
- receiver acknowledgment proving durable idempotent acceptance;
- projection failure never changing the committed terminal receipt;
- separately reviewed receiver contract before any endpoint or credentials are used.

## Proof packet

```text
COMMAND=<deployed source route/outbox inspection + zero-state DB read>
RESULT=PASS
LOG=/tmp/hermes-verify-<task>-transport-discovery.log
SCOPE=read-only discovery precontract
AD_HOC_OR_CANONICAL=ad-hoc targeted discovery proof
NOT_CLAIMING=precontract acceptance,dispatch readiness,receiver selection,outbox implementation,endpoint,credentials,event,producer,merge,deployment,or Linear mutation
MARKER=<TASK>_RECEIPT_TRANSPORT_DISCOVERY_BLOCKED_NO_DISPATCH
```
