# Hermes profile fleet governance for Prismatic helper bots

## When this applies

Use this when coordinating Kai/Fred/Ned/George profile hygiene, model routing, gateway services, role boundaries, cron/watchdog health, or helper-bot capability parity during Prismatic work.

## Core pattern

1. **Separate profile config from live session routes.** A profile YAML may already name the right provider/model while active Telegram sessions remain pinned to an older route. Verify both.
2. **Verify fallback order at the top-level provider chain.** For Prismatic helper bots, enforce the intended primary/fallback/last-resort order in config and in the watchdog; do not only inspect nested provider definitions.
3. **Repair live sessions intentionally.** Update active session records only for the target profile/source/thread set being repaired; do not assume a YAML edit changes retained sessions.
4. **Use safe gateway replacement.** If in-gateway restart guards block `systemctl stop/restart`, use an out-of-cgroup/detached migration or targeted process replacement pattern that does not kill the operator's current gateway mid-command.
5. **Use PID/process disappearance as the stop gate before SQLite writes.** Hermes services may report `failed` rather than `inactive` after an intentional guarded stop; do not mutate active session DBs until the target process/MainPID is gone and the operator profile is not among the targets.
6. **Probe real inference, not only model discovery.** Discovery endpoints can omit a model that real OAuth inference supports. Treat actual successful inference as the stronger health signal, while documenting discovery boundaries.
7. **Watchdog should be silent on health.** For recurring fleet checks, script-only cron should emit nothing when all gates pass and only deliver drift/failure details.
8. **Do not copy credentials across profiles.** Prefer a narrow local broker/client in the profile that already owns the credential, with allowlisted inputs and read-only behavior where possible.
9. **Preserve runtime ownership.** Inventory Fred dashboard/runtime plugin directories and enabled config without duplicating them into George. George should receive manifests/proof, not become accidental runtime owner.
10. **Do not mass-disable mixed business jobs.** Inventory active jobs, but require a named receiving owner and per-job keep/move/retire decision before changing Fred/Ned/Kai business schedules.
11. **Archive role-inappropriate skills instead of deleting useful knowledge from the wrong lane.** Example: Kai can retain AOT skills while Prismatic-only architecture references move out of active loading.

## Minimum proof packet

```text
CONFIG_PROVIDER_MODEL=<profile yaml provider/model>
FALLBACK_ORDER=<top-level ordered fallback provider/model list>
ACTIVE_TELEGRAM_ROUTES=<distinct active route rows before/after>
UPDATED_SESSIONS=<per-profile row counts when repairing routes>
SERVICE=<systemd unit or process identity; old/new PIDs when restarted>
TELEGRAM_IDENTITY=<bot username/id>
INFERENCE_PROBES=<primary/fallback real prompt PASS|FAIL per profile>
WATCHDOG=<scheduled/silent-on-healthy/last_status>
ROLE_BOUNDARY=<what was removed/retained>
CREDENTIAL_BOUNDARY=<no copied secrets; broker/client scope if any>
JOB_BOUNDARY=<inventoried counts; not changed unless owner approved>
PLUGIN_BOUNDARY=<manifested runtime owner; no duplicate runtime>
MARKER=<marker>
```

## Pitfalls

- Do not report “profile fixed” from YAML alone; active session rows can continue routing to stale models.
- Do not enforce fallback policy by checking the wrong config layer. Verify the top-level fallback chain order that Hermes actually evaluates, then run real primary/fallback inference probes.
- Do not mutate session databases while the target gateway is still running; create narrow backups immediately before the mutation and report whether they were removed or retained.
- Do not treat a post-stop `failed` unit state as automatic failure if the target process is gone after an intentional guarded stop; use process/PID disappearance plus recovery start checks as the gate.
- Do not treat OAuth discovery absence as proof the configured model cannot run; perform a real prompt/inference probe when safe.
- Do not inspect services with a command pattern that trips Hermes' self-restart guard during the operator gateway. If blocked, switch to read-only `/proc` cgroup inspection or detached safe migration.
- Do not let an abbreviated CLI tail hide active job scale. Read the cron store directly and tolerate list-vs-map schema variants.
- Do not transfer Fred dashboard plugin runtime into George just because George coordinates Prismatic proof. Runtime owner and coordination reviewer are different roles.
