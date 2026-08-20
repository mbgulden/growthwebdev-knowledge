# Finite approval and cap-1 spine pattern

Use this when a Prismatic coordination/review session starts drifting into repeated review loops, broad Linear sequencing, or dashboard/task-admission restart planning.

## Trigger signals

- User says the process feels too rigid, will never be approved, or was close hours ago.
- A review loop keeps expanding the acceptance criteria after the artifact gets closer.
- The backlog is ready to move again, but bulk dispatch would blur ownership and proof.
- A control-plane foundation exists, but the next step is unclear between more harness work and real task execution.

## Operating correction

Do not turn `Don't trust, verify` into open-ended adversarial approval. Convert it into a finite acceptance contract:

1. Name the exact accepted boundary.
2. Fix only valid blockers that affect that boundary.
3. Preserve checkpoints instead of replaying/rolling back completed stages.
4. Stop adding new gates unless they protect the named boundary.
5. Move one bounded horse through the system before scaling.

## Recommended sequencing shape

For Prismatic Linear/control-plane restart after packet completion:

```text
foundation spine first:
  GRO-4270 CronRunReceipt base schema
  GRO-4345 trigger identity bound to durable outcomes
  GRO-4319 immutable trigger/runtime authority
  GRO-4317 canonical claim and reconciliation runner

then one cap-1 canary:
  admit one inert/bounded trigger
  establish one execution claim
  produce one durable outcome
  reconcile terminal state
  prove duplicate delivery converges on the same execution identity
  confirm no second producer, orphaned lease, or false success

then expand tracks:
  HTTP: GRO-4276 -> GRO-4277 -> GRO-4278 -> GRO-4279/GRO-4281 -> GRO-4282
  Projection/rollout: GRO-4317 -> GRO-4318 -> GRO-4336; GRO-4319 -> GRO-4320
  Codex: GRO-4314 -> GRO-4315 -> GRO-4316 through PE AgentHarness, not a Hermes profile
```

## Dispatch guardrail

If the gateway/admission route is healthy but consumers/producers are masked or intentionally bounded, report readiness as `ready for one controlled admission`, not `ready for bulk dispatch`.

Use this proof shape:

```text
GATEWAY=<active|inactive>
HEALTH=<url + status>
TASK_ADMISSION_ROUTE=<present|missing>
WRITER_LEASES=<count>
ACTIVE_CLAIMS=<count>
OUTBOX=<status counts>
CONSUMER=<masked|active|unknown>
RECOMMENDATION=<one exact next task>
```

## Tone/legibility rule

When Michael pushes back on rigidity, answer with an operational correction, not a defense. Lead with the admission that the gate expanded, then give the exact smaller path forward. Prefer: `build minimum spine -> run one canary -> expand`.
