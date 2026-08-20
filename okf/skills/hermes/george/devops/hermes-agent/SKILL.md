---
name: hermes-agent
description: Operate, configure, troubleshoot, and verify Hermes Agent profiles, providers, gateway services, messaging adapters, sessions, cron jobs, tools, skills, plugins, and upgrades using current docs and live evidence.
---

# Hermes Agent Operations Baseline

Authoritative documentation: <https://hermes-agent.nousresearch.com/docs>

Load this skill before changing or diagnosing Hermes Agent itself. Current documentation overrides this skill when they differ.

## Core rules

1. Identify the exact active profile and profile root before reading or writing.
2. Use `hermes --help` and subcommand help instead of inventing commands.
3. Treat config, active session state, process state, provider auth, and platform connectivity as separate layers.
4. Never print API keys, OAuth tokens, bot tokens, Authorization headers, or complete `.env`/auth files.
5. Do not copy credentials between profiles. Prefer Hermes credential pools, profile-local secret references, or a narrow broker.
6. Restart only the target profile. Never stop the gateway executing the current agent.
7. Verify with real execution. Config readback alone is not proof.

## Profile discovery

```bash
hermes profile list
hermes profile show <profile>
hermes --profile <profile> config check
hermes --profile <profile> skills list
hermes --profile <profile> gateway status
```

Profile data normally lives under:

```text
~/.hermes/profiles/<profile>/
```

Inspect secret-safe key names and structural values only. Do not dump `.env`, auth pools, or tokens.

## Model/provider diagnosis

When a bot reports the wrong model, verify all five layers:

1. `config.yaml` model provider/default and fallback types.
2. Active session route in `state.db`.
3. Target gateway PID and service ownership.
4. Provider credential health.
5. A real exact-model inference response.

A correct YAML default does **not** change an already-open Telegram session. Inspect active route metadata read-only:

```python
import sqlite3
c = sqlite3.connect("file:/path/to/state.db?mode=ro", uri=True)
print(c.execute("select id,source,model,ended_at from sessions where ended_at is null").fetchall())
```

If active sessions are pinned to a retired model, preserve the database and messages. Stop only the target gateway, create a temporary SQLite backup, update only the intended active route rows, restart, verify, then remove the temporary backup.

Do not infer availability only from provider discovery caches. A configured OAuth model can execute successfully while absent from the discovery list. Run an exact probe:

```bash
hermes --profile <profile> -m <model> --provider <provider> -z 'Reply with exactly: HERMES_MODEL_OK'
```

Verify exit code and expected response without exposing credentials.

## Gateway and messaging health

Separate these claims:

- process exists;
- systemd service is active;
- messaging adapter is connected;
- bot token identifies the expected account;
- model inference succeeds;
- an existing chat session uses the intended route.

Inspect service ownership:

```bash
systemctl cat <service>.service
systemctl show <service>.service -p ActiveState -p SubState -p MainPID -p ExecStart -p TimeoutStopUSec -p KillMode
cat /proc/<pid>/cgroup
```

Healthy durable units should use a profile-specific service, `Restart=always`, `KillMode=mixed`, and a stop timeout longer than the configured drain timeout.

### Restart safety

Hermes may block `systemctl stop/restart` from inside a gateway because termination can propagate to the command. Respect that guard.

For a different target profile, use its exact systemd `MainPID`, signal only that PID, wait for the old PID to exit, and let systemd replace it. For service migrations, execute the migration from a detached transient systemd unit so it is outside the current gateway cgroup.

Never signal the current profile's gateway.

After replacement, prove:

```text
OLD_PID != NEW_PID
ActiveState=active
SubState=running
MainPID>0
```

Then inspect only the replacement PID's logs. Old-PID shutdown errors are not evidence against the replacement.

## Messaging adapter removal

To remove a platform from one profile:

1. Remove its YAML block from that profile.
2. Remove only that platform's keys from that profile `.env`.
3. Confirm systemd does not inject global platform variables.
4. Replace the target gateway PID.
5. Verify the replacement PID does not initialize/reference the removed adapter.
6. Verify remaining platform identity via a secret-safe API response.

Do not remove another profile's platform configuration because two profiles share a host.

## Config structural safety

CLI values such as `'[]'` or `'null'` may become literal strings. After structural edits:

- parse YAML;
- verify Python types;
- use atomic temporary-file replacement;
- preserve unrelated values;
- run `hermes --profile <profile> config check`;
- verify the live process actually reloaded the change.

## Cron jobs

Use script-only/no-agent cron for deterministic watchdogs. Healthy stdout must be empty; non-empty stdout should be an actionable alert. Direct inference checks should be rate-limited inside the script rather than executed every short tick.

Verify newly created jobs with an immediate scheduler run and inspect `last_status`/delivery errors.

## Skills and plugins

- Use `hermes --profile <profile> skills list` as the loaded-skill truth; `.archive` files are not loaded.
- Do not copy every role-specific skill across profiles.
- Consolidate shared procedures into a maintained umbrella skill.
- Do not duplicate runtime plugins across profiles without an ownership/version manifest and collision review.
- Patch stale skills immediately when live behavior disproves them.

## Verification packet

```text
PROFILE=<profile>
CONFIG=<provider/model or structural scope>
SERVICE=<unit>
OLD_PID=<pid if replaced>
NEW_PID=<pid>
SESSION_ROUTE=<provider/model>
PLATFORM_IDENTITY=<safe username/id presence>
LIVE_INFERENCE=<PASS|FAIL>
LOG=<path>
NOT_CLAIMING=<boundaries>
MARKER=<marker>
```

## Pitfalls

- A running PID is not platform connectivity.
- A correct default model is not the active session model.
- A refreshed model list is not a successful inference.
- Old process logs must not be attributed to a replacement PID.
- Doctor warnings about missing environment keys may be false positives when credentials are loaded from a pool/profile file; prove actual capability.
- Never expose secrets while troubleshooting.
