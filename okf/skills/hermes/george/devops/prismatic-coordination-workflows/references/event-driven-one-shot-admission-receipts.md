# Event-driven one-shot admission receipts

Use this reference when launching a reviewed Prismatic task admission package into AGY/Fred/Ned or any durable producer lane.

## Contract

After exact-byte reviews pass and the final gate is clean, invoke the reviewed launcher **once**. Then perform exactly one immediate post-admission proof packet and stop observation. Do not create a polling loop or parallel producer unless the governing task explicitly says to.

## Immediate post-admission proof packet

Capture non-secret evidence only:

```text
COMMAND=<exact reviewed launcher command>
EXECUTION_COUNT=1
LAUNCHER_RC=<rc>
HTTP_STATUS=<201 or failure>
RESULT=<launcher result enum>
EVENT_ID=<task-admission event id>
CLAIM_ID=<consumer claim id, if claimed>
OUTBOX_STATE=<queued|processed|...>
CONSUMER_STATE=<claimed|completed|...>
LIFECYCLE=<claimed;validated;launch_started;launched or actual sequence>
WRITER_LEASE=<count>
POLICY_RESTORED=<true|false>
CONTROL_RESTORED=<true|false>
TEMP_CONFIGS_REMOVED=<true|false>
```

If a producer run is launched, resolve its durable coordinates once:

```text
RUN_ID=<durable run id>
PRODUCER_IDENTITY=<producer/model identity>
MODEL=<model>
ACTIVE_SLOT=<slot path/name>
OWNER_PID_AT_HANDOFF=<slot owner pid>
PANE_PID_AT_HANDOFF=<harness/tmux pid>
CHILD_PID_AT_HANDOFF=<producer child pid>
PLAN=<spool PLAN.md path if present>
RESULT_PATH=<expected RESULT.md path>
RUN_STATE=<running|completed|failed from run metadata>
```

## Stop condition

Once the lifecycle and active producer identity are proven, stop. The next action is event-driven:

```text
NEXT_ACTION=Await durable result notification or operator-visible completion artifact; then independently review exact candidate head/diff/logs before merge/deploy consideration.
NOT_CLAIMING=producer completion,candidate acceptance,canonical tests,PR,merge,deployment,Linear mutation,parent completion
```

Do not keep polling just because the producer is active. Polling undermines the event-driven control lane and risks duplicate or overlap behavior.

## Handoff requirement

Immediately write the hot handoff with:

- one-line state: reviewed package admitted once; run id active; no polling/parallel producer;
- `in_flight[]` entry for the active run;
- execute report path and hash;
- expected `RESULT.md` path;
- boundary/non-claims;
- next action framed as review-after-result, not active monitoring.
