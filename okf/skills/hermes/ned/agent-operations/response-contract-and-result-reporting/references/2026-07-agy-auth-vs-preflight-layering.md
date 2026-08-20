# AGY auth smoke tests vs Prismatic pre-flight readiness — July 2026

## Lesson

A neutral AGY CLI smoke test can prove OAuth/model connectivity while the actual Prismatic/Linear workflow remains blocked. Do not collapse these layers in result reports.

## Observed pattern

- `agy --print 'Reply exactly: AUTH_OK'` passed.
- Signed stdin injection through the AGY wrapper passed.
- The live Prismatic monitor still reported `BLOCKED_PACKET_PRESENT` for Prompt4.
- Event-router launch records showed several AGY runs marked `blocked`, with a later `completed` run insufficient to make the whole lane green.
- Captured AGY logs eventually showed `RESULT=PASS` and the AGY marker, but companion writeback/blocked packet state still prevented the workflow from being ready.

## Reporting rule

When investigating AGY/Antigravity readiness, report each layer separately:

1. Raw CLI auth/model connectivity.
2. Programmatic wrapper/signed task injection.
3. Dispatcher/event-router launch state.
4. Queue/preflight fields and blocked packets.
5. Required companion writeback / downstream gates.

Only call AGY pre-flight healthy when the workflow gate itself is green, not merely because `AUTH_OK` returned.

## Safe phrasing

Good:

```text
AGY auth works; Prismatic AGY pre-flight remains blocked by blocked packet/writeback state.
```

Bad:

```text
AGY is working now.
```

The bad phrasing is a false positive: ping works, app is dead. Seen enough of those.