# Multi-profile gateway/model route parity audit

Use this reference when a Hermes swarm has profiles whose YAML config says one provider/model but live Telegram sessions or gateway processes behave like another provider/model.

## Durable lesson

Hermes profile YAML can be correct while active session rows in `<profile>/state.db` retain an older route. A restart alone may not fix the user's next message if the unended Telegram session still points at the retired model. Treat provider/model repair as a three-layer parity problem:

1. profile config (`config.yaml` / `hermes config`);
2. active session route state (`state.db` safe fields only);
3. live gateway process/service and direct provider inference.

## Secret-safe audit shape

For each profile in scope, collect only:

- profile name and config path;
- configured `model.provider`, `model.default`/`model.model`, fallback presence and type;
- gateway service name, `MainPID`, active state, age, memory, and exact `ExecStart`;
- active/unended session IDs, source, model, and provider/model keys from `model_config`;
- platform presence such as Telegram/Slack booleans, never tokens;
- direct one-turn provider probe result and log path/digest.

Never print `.env`, `auth.json`, OAuth tokens, Telegram bot tokens, API keys, refresh tokens, or inline provider config blocks.

## Repair pattern

1. Identify the real service unit for each target profile. Do not assume it is named `hermes-gateway-<profile>.service`; legacy services may exist.
2. Confirm you are not stopping the current assistant's own gateway.
3. If systemd restart/stop is blocked by the Hermes safety guard from inside another gateway, signal only the target unit's `MainPID` and let systemd restart it.
4. While the target old PID is down, normalize profile config and repair only active sessions pinned to the retired provider/model.
5. Remove malformed fallback values that are persisted as literal strings such as `'[]'` or `'null'`; verify YAML types after mutation.
6. Confirm the replacement PID is new and the old PID is gone.
7. Verify exact route by direct inference through the intended provider/model; model discovery can lag or omit a usable OAuth route.
8. Verify Telegram identity with a secret-safe `getMe` result: `ok`, username, first name, and ID presence only.
9. Distinguish old-PID logs from new-PID logs in the report; stale pre-restart Gemini/rate-limit lines are not proof of current failure.

## Acceptance proof block

```text
STATUS=<PASS|PARTIAL|BLOCKED>
CONFIG=<provider/model and fallback type proof>
SESSIONS=<active sessions all expected route or remaining exceptions>
SERVICE=<unit, new PID, active state>
PROBE=<exact direct inference result, log, digest>
PLATFORM=<Telegram identity/state, secret-safe>
BOUNDARY=<what was not changed, e.g. no deploy/no token rotation>
```

## When to propose follow-up hardening

After repairing a multi-profile drift incident, propose:

- a no-agent watchdog that is silent when healthy and alerts only on drift/outage/OAuth probe failure/memory threshold/platform reappearance;
- service unit normalization for legacy gateway units;
- a shared Hermes operations baseline skill instead of copying one-off repairs into each profile;
- role-boundary cleanup so profile-owned cron/plugins do not silently sprawl across agents.
