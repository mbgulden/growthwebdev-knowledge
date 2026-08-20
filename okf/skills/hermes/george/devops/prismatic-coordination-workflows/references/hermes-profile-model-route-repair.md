# Hermes profile model-route repair notes

## When this applies

Use this when a Hermes profile fleet watchdog reports healthy YAML config but live Telegram sessions are still routed to an old/non-preferred provider model.

## Durable lesson

A Hermes profile can be correctly configured at the YAML/provider layer while unended Telegram session routes remain pinned to an older provider/model. Fixing the profile config alone will not clear those retained session rows; verify and repair both layers.

## Safe repair sequence

1. **Audit three layers separately**
   - profile YAML primary provider/model;
   - top-level fallback provider order;
   - active unended Telegram session routes in each target profile `state.db`.
2. **Probe real inference** for the desired primary and fallback providers. Treat a successful inference probe as stronger than model-discovery output, but keep the credential boundary explicit.
3. **Stop only target gateways** before mutating active session rows. Do not stop the operator profile.
4. **Expect service-state ambiguity after intentional stop.** A Hermes gateway service may show `failed` rather than `inactive` after a guarded/intentional shutdown; key the migration on the target process/PID reaching zero plus the intended unit identity, not on `inactive` alone.
5. **Back up each target SQLite DB** immediately before any session-row mutation. If the stop check fails, make no DB writes.
6. **Update only matching active Telegram routes** for the target profiles/sources/threads. Record per-profile update counts.
7. **Start/restore target gateways** and verify new PIDs, service health, route counts, and real primary-provider inference.
8. **Run the watchdog directly** after the repair. A healthy watchdog should be silent and the scheduled cron should end with `last_status=ok`.
9. **Clean temporary migration scripts/backups** after verification, or keep them only if needed for rollback and report their paths explicitly.

## Proof packet

```text
CONFIG_PRIMARY=<provider/model per profile>
FALLBACK_ORDER=<ordered provider/model fallback list>
ACTIVE_ROUTE_DRIFT_BEFORE=<profile: stale route counts>
UPDATED_SESSIONS=<profile: count>
OLD_PIDS=<pid list>
NEW_PIDS=<pid list>
ACTIVE_ROUTE_DRIFT_AFTER=<profile: stale route counts, expected 0>
PRIMARY_INFERENCE=<PASS|FAIL per profile>
FALLBACK_INFERENCE=<PASS|FAIL per profile if checked>
WATCHDOG=<silent/direct PASS + scheduled last_status>
DB_BACKUPS=<removed|kept paths>
NOT_CLAIMING=<profiles or services not touched>
MARKER=HERMES_PROFILE_MODEL_ROUTE_REPAIR_OK
```

## Pitfalls

- Do not report a fleet model repair from config diffs alone; stale active Telegram sessions can keep using the old provider.
- Do not mutate session databases while the target gateway is still running.
- Do not use `systemctl inactive` as the only safe-stop condition; verify the target MainPID/process is gone.
- Do not assume a profile-local `.env` must contain fallback credentials. Hermes may resolve credentials through a broader effective environment; verify with an actual, non-secret inference probe.
- Do not include tokens, API keys, or raw secret-bearing environment output in the proof packet.
