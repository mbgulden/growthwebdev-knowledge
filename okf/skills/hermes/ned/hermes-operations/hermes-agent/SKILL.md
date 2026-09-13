---
name: hermes-agent
description: Operate, configure, troubleshoot, and verify Hermes Agent profiles, providers, gateway services, messaging adapters, sessions, cron jobs, tools, skills, plugins, and upgrades using current docs and live evidence.
---

# Hermes Agent Operations Baseline

Authoritative documentation: <https://hermes-agent.nousresearch.com/docs>

Load this skill before changing or diagnosing Hermes Agent itself. Current documentation overrides this skill when they differ.

## Core rules

- **Cron Job Script Execution (`no_agent=True`):** When using `cronjob` with `no_agent=True`, ensure scripts are located in `~/.hermes/scripts/` and referenced by filename only. Thoroughly test the script for syntax errors and correct execution before scheduling, as the cron system will execute it directly without LLM interpretation. For debugging, temporarily remove output redirection and add `set -xe` to the script to trace execution.
- **Gateway Restart Safety:** An agent cannot `sudo systemctl restart` or `stop` its own gateway process from within its own session due to a safety guard. Such actions must be performed from an external context (e.g., another session or a detached cron job).
## Core rules

- **Cron Job Script Execution (`no_agent=True`):** When using `cronjob` with `no_agent=True`, ensure scripts are located in `~/.hermes/scripts/` and referenced by filename only. Thoroughly test the script for syntax errors and correct execution before scheduling, as the cron system will execute it directly without LLM interpretation. For debugging, temporarily remove output redirection and add `set -xe` to the script to trace execution.
- **Gateway Restart Safety:** An agent cannot `sudo systemctl restart` or `stop` its own gateway process from within its own session due to a safety guard. Such actions must be performed from an external context (e.g., another session or a detached cron job).
- **Python `ModuleNotFoundError` in Systemd Services:** When a systemd service running a Python script fails with `ModuleNotFoundError`, especially when the script runs fine manually, suspect differences in the Python environment or `sys.path`. If `pip install` fails for the module, it might be a local project. Identify the local path of the module (e.g., using `find`) and install it into the service's virtual environment using `pip install <path_to_module>`.

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

Hermes may block `systemctl stop/restart` from inside a gateway because termination can propagate to the command. Respect that guard. This means you cannot directly use `sudo systemctl stop/restart <gateway_service>` for the *current* running gateway from within an agent session. For such operations, schedule a detached cron job or execute from a separate shell outside the running gateway process.

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

### Pitfall: Script path and execution with `no_agent=True`
When using `cronjob(no_agent=True)`, the `script` parameter expects a simple filename (e.g., `my_script.sh`) that resides directly under `~/.hermes/scripts/`. Do not embed the shebang (e.g., `#!/bin/bash`) as part of the filename or provide an absolute path with the interpreter (e.g., `/bin/bash /tmp/my_script.sh`). This will lead to execution errors where the system attempts to resolve the shebang or absolute path as part of the script's *name* rather than its content or execution method. Ensure scripts are properly located and referenced by filename.


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

### Named custom provider: `key_env` vs `api_key_env` (aux/vision 401 trap)

Symptom: main chat works but `vision_analyze`, context compression, and title generation all 401 with `Invalid API Key` against a **local** OpenAI-compatible endpoint. Log line: `resolve_provider_client: named custom provider 'X' has no resolvable api_key — request will be sent with placeholder no-key-required and will 401`. The user's guess is often "OpenAI key is masked/wrong" — **it is not**; the local provider's key is being silently dropped.

Root cause: two different resolvers read the provider entry differently.
- Main-chat path goes through `_normalize_custom_provider_entry` (hermes_cli/config.py), which lifts the `api_key_env` alias → `key_env`. Works.
- The **auxiliary** path (vision/compression/title/curator) goes through `_get_named_custom_provider` (hermes_cli/runtime_provider.py), whose new-style `providers:` dict branch reads **only `key_env`** (plus inline `api_key`). It does NOT apply the `api_key_env → key_env` alias lift. So a config entry that only declares `api_key_env: SOME_VAR` resolves to an EMPTY key → `no-key-required` placeholder → 401.

Diagnose (prove, don't guess — run the exact aux resolver in the profile's env):

```bash
cat > /tmp/repro.py <<'PYEOF'
import os, sys
os.chdir('/home/ubuntu/.hermes/profiles/<profile>')
for line in open('.env'):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1); os.environ.setdefault(k,v)
sys.path.insert(0,'/home/ubuntu/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages')
os.environ['HERMES_HOME']=os.getcwd()
from hermes_cli.runtime_provider import _get_named_custom_provider
e=_get_named_custom_provider('<provider-name>')
ak=(e or {}).get('api_key') or ''
print('api_key', ('<set len %d>'%len(ak)) if ak else 'EMPTY  <-- this is the bug')
PYEOF
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python /tmp/repro.py
```

If it prints EMPTY while the env var is set, that's the bug.

Fix: in that profile's `config.yaml`, add the canonical field alongside the alias on the affected `providers:` entries (keeping both is harmless — both code paths then win):

```yaml
providers:
  my-local-llm:
    api: http://192.168.1.232:8080/v1
    key_env: MY_LLM_API_KEY      # canonical — aux/vision path reads THIS
    api_key_env: MY_LLM_API_KEY  # alias — main-chat path already read this
```

Restart the profile gateway (detached transient unit — direct restart is blocked from inside the running gateway), then prove end-to-end with a real `vision_analyze` on a generated image through that profile (not just the main-chat `-z` probe, which would pass even before the fix):

```bash
hermes --profile <profile> -m <model> --provider <provider> -z 'Use vision_analyze on /tmp/t.png and describe the circle color.'
```

A passing main-chat `-z` probe does NOT prove the aux path — the whole point is the two paths diverge. Verify zero `no resolvable api_key` / 401 lines on the new PID after restart.

**Verification trap (hit this):** to prove the fix, run `_get_named_custom_provider` with the **`custom:<name>`** form (e.g. `custom:minimax`), NOT the bare name. For canonical built-in names (`minimax`, `deepseek`, `google`, …) the bare-name request intentionally returns `None` (defers to the built-in registry) — so a bare-name probe prints `api_key EMPTY` and looks like the fix failed when it didn't. The named-custom branch (where `key_env` is read) is only exercised by `custom:<name>` or a genuinely non-canonical name. Probe both paths: `custom:<name>` for the config-entry key, and `load_hermes_dotenv()` → `os.environ` for the built-in env-var path.

**Two red herrings that waste an hour:**
1. `/proc/<MainPID>/environ` showing the API key **ABSENT** does NOT mean the process lacks it. That file captures only the **exec-time** environment; Hermes `load_hermes_dotenv()` (called at `hermes_cli.main` import, `override=True`) mutates `os.environ` *after* exec. Read the key from a fresh `load_hermes_dotenv()` + `os.environ` check, not `/proc`.
2. `EnvironmentFile=` in the gateway unit is **defensive, not required** for env-based providers — the dotenv loader pulls the profile `.env` itself. The decisive fix for the aux 401 is the `key_env` config field. (Adding `EnvironmentFile=` is still fine as belt-and-suspenders, but don't chase it as the root cause.)
3. `load_config()` is `(mtime_ns, size)`-cached, so a `key_env` config edit is picked up **live on the next aux call — no gateway restart needed.** Restart is only required for changes to `os.environ` at exec time.

Second, independent cause that produces the identical 401: the profile's systemd unit missing `EnvironmentFile=/home/ubuntu/.hermes/profiles/<profile>/.env`, so the key never enters the process environment at all. Check `/proc/<MainPID>/environ` for the key var; if absent, that's the cause and the unit needs the `EnvironmentFile=` line. Both can be true simultaneously — fix both, then verify.
