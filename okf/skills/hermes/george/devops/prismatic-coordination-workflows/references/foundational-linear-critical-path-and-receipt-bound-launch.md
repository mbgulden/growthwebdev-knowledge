# Foundational Linear critical path + receipt-bound launch

Use this reference when Michael redirects George from exploratory/contract work back to a named Prismatic foundational Linear issue (for example `GRO-4317`) and says to use the latest valid checkpoint plus standing authorization.

## Workflow correction captured

When Michael explicitly says to get back on the foundational Linear critical path:

1. Pull the live Linear graph/source of truth first; do not rely on handoff/session history alone.
2. Identify the first uncompleted critical-path issue and keep downstream issues held until that issue is independently accepted.
3. Use the latest valid checkpoint and standing authorization already granted for that issue/slice.
4. Do **not** create more precontracts, blocker documents, or adjacent reviews unless a newly observed hard blocker exists.
5. If a bounded, exact-line implementation defect is found, fix that defect directly and run a targeted proof; use at most a bounded exact-line review when independent acceptance is needed.
6. After independent `CLEAN/PASS`, execute the authorized cap-1 lane rather than drafting another contract.

## Receipt-bound producer handling

For an admitted cap-1 AGY producer that launches successfully but is still running:

- Confirm the launch receipt, event id, replay status, consumer status, active slot, PID, and process start ticks.
- Verify `/proc/<pid>/stat` start ticks match the launch receipt before binding the run.
- Use a passive wait bound to the receipt PID, e.g. `tail --pid=<pane_pid> -f /dev/null` in a tracked background process with `notify_on_complete=true`.
- Do not use dashboard polling loops, inactivity kills, wall-clock caps, or repeated reposts while activity indicates the producer is working.
- Record the boundary clearly: event accepted/consumed and producer running are not producer completion, exact-head acceptance, Linear completion, merge, or deploy.

## Compact proof shape

```text
LINEAR_SOURCE=live
CRITICAL_PATH=<first active issue>
DOWNSTREAM_HELD=<ids>
EVENT_ID=<event id>
REPLAYED=false
CONSUMER_STATUS=processed
CAP=1
LAUNCH_ID=<run id>
PANE_PID=<pid>
PANE_START_TICKS=<ticks>
PROCESS_IDENTITY_MATCH=true
ACTIVE_SLOT_COUNT=1
PASSIVE_WAIT=<Hermes process id>;tail--pid=<pid>;notify_on_complete=true
NOT_CLAIMING=producer completion, exact-head acceptance, Linear Done, merge, deploy
```

## Pitfalls

- A pending or invalid delegated review is not a reason to create a new broad precontract if Michael has already redirected to the Linear critical path.
- A live event accepted once must not be reposted because the producer is still running.
- A `running/working` activity receipt is progress evidence, not completion evidence.
