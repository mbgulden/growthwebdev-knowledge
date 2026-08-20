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

When a bot reports the wrong model or falls back unexpectedly, verify all five layers:

1. `config.yaml` model provider/default and fallback types.
2. Active session route in `state.db`.
3. Target gateway PID and service ownership.
4. Provider credential health (`hermes --profile <profile> auth status <provider>`).
5. A real exact-model inference response.

**Layer 1 checklist (config.yaml):**
- Is `fallback_providers:` at root level or nested inside `model:`?
- Is it a proper YAML list or a JSON string?
- Is `model_catalog.enabled` false or absent? (Enabled + empty `providers: {}` breaks model resolution)
- Does `hermes --profile <profile> config show` match the raw YAML?
- Are there duplicate top-level keys (`grep -n "^key:" config.yaml`)?

**Layer 4 quick checks:**
```bash
hermes --profile <profile> auth status openai-codex  # OAuth status
hermes --profile <profile> config check             # YAML validity
```

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
### Gateway restart pattern

**Correct approach (background=true + notify_on_complete):**
```bash
# Kill existing PIDs
ps aux | grep -E "hermes.*<profile>.*gateway" | grep -v grep | awk '{print $2}' | xargs -I {} kill {} 2>/dev/null
sleep 2

# Start new with background=true + notify_on_complete
hermes --profile <profile> gateway run --replace > /tmp/<profile>-gateway.log 2>&1 &
# OR using the terminal tool:
terminal(background=true, command="hermes --profile <profile> gateway run --replace > /tmp/<profile>-gateway.log 2>&1", notify_on_complete=True)
```

**What NOT to do:**
- Do NOT use `nohup ... &` in terminal foreground — Hermes will reject with "Foreground command uses shell-level background wrappers"
- The `exit code 1` + "To run a command as administrator (user 'root')" message is a **benign wrapper script exit** — the actual gateway process still runs fine
- Verify with: `ps aux | grep -E "hermes.*<profile>.*gateway" | grep -v grep`

**Verify gateway is healthy:**
```bash
ps aux | grep -E "hermes.*<profile>.*gateway" | grep -v grep
tail -50 /tmp/<profile>-gateway.log | grep -i "error\|401\|expired\|failed"
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

## YAML duplicate detection

Config files can accumulate duplicate top-level keys (e.g., two `fallback_providers:` or two `model_catalog:` sections) when manual edits or repeated `hermes config set` calls are made over time. The second occurrence takes precedence in most YAML parsers, but `hermes config show` may display a merged/nested view that obscures the actual file structure.

**Always verify with:**
```bash
grep -n "^key_name:" /path/to/config.yaml   # detect duplicate top-level keys
grep -n "^  key_name:" /path/to/config.yaml  # detect duplicate nested keys
```

**Common duplicates that break model routing:**
- `fallback_providers:` appearing both inside `model:` AND at root level
- `model_catalog:` appearing both inside `model:` AND at root level
- `model:` section containing `fallback_providers` as a JSON string instead of proper YAML list

**Correct structure (root level):**
```yaml
model:
  default: gpt-5.6-terra
  provider: openai-codex
  model_catalog:
    enabled: false  # or absent; Kai has no model_catalog at all

fallback_providers:
  - provider: minimax
    model: MiniMax-M3
  - provider: google
    model: gemini-2.5-flash
```

**Incorrect (inside model: as JSON string):**
```yaml
model:
  default: gpt-5.6-terra
  provider: openai-codex
  fallback_providers: '[{"provider": "minimax", "model": "MiniMax-M3"}]'  # WRONG
  model_catalog:
    enabled: false
```

**When `hermes config show` output differs from raw YAML:**
The CLI merges/nests config trees. Always `grep` the raw file when diagnosing why a setting isn't taking effect.

**MiniMax model naming:**
- `MiniMax-M3` = MiniMax model 3 (newer, better)
- `MiniMax-M2.7-highspeed` = MiniMax model 2.7 high speed variant
- Set via `hermes --profile <profile> config set model.default MiniMax-M3`

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
- **Michael operates as a "free agent" / "untethered" owner** — he expects exhaustive programmatic attempts before manual intervention. Never start with "I can't" without trying 10 options. The directive "you're acting helpless" or "figure it out" is a signal to pivot to action, not a complaint.
- **"Yolo mode"** means aggressive credential searching, trying all programmatic options, and not stopping at the first blocker. Search environment variables, session history, files, and skill references before admitting defeat.
- **"Act like a free agent"** means take initiative. If one approach fails, try 5 more before asking for help. Document what was tried so Michael can see the effort.
- **Model changes** — when switching Fred/Ned models, always also update `model.provider` to match (e.g., `minimax` provider for `MiniMax-M3` model, not `openai-codex`). If provider is wrong, model will fail and fall back immediately.
- **Fred/Ned/George config corruption pattern** — these profiles accumulate a malformed `fallback_providers` JSON string inside the `model:` section. Always check `grep -n "fallback_providers" config.yaml` to ensure there's only ONE at root level and it's proper YAML list, not a JSON string. Remove any inside `model:`. The same applies to duplicate `model_catalog:` sections.
- **Michael prefers concise proof reports** — when task is done, report evidence + next step. Not "I did X", but "Done. Evidence: [link/path]. Next: [specific action]."

## OpenAI Codex OAuth: Profile Credential Sharing

All Hermes profiles on the same host **share the same OAuth credential pool** for `openai-codex`. They share the same `dashboard device_code` credential ID (e.g., `64332f`). When one profile uses the refresh token, all other profiles get `refresh_token_reused` errors and fall back.

**Symptoms:**
```
WARNING agent.auxiliary_client: resolve_provider_client: openai-codex requested but no Codex OAuth token found
WARNING agent.conversation_loop: API call failed ... HTTP 401: Provided authentication token is expired
```

**Diagnosis:**
```bash
hermes --profile <profile> auth list | grep -A5 "openai-codex"
```

**When OAuth sharing blocks Fred/Ned — Two paths:**

### Path A: Accept MiniMax as primary (Michael's preferred path)
When Kai is active, Fred/Ned cannot use openai-codex simultaneously. Switch Fred/Ned to MiniMax-M3 as primary:
```bash
# Primary model = MiniMax-M3, provider = minimax
hermes --profile <profile> config set model.default MiniMax-M3
hermes --profile <profile> config set model.provider minimax
hermes --profile <profile> config set model.fallback_providers '[{"provider": "minimax", "model": "MiniMax-M3"}, {"provider": "google", "model": "gemini-2.5-flash"}]'
```

### Path B: Individual ChatGPT accounts (each profile needs its own OAuth)
Each profile must authorize with a **different ChatGPT account**. The same account's refresh token cannot be shared across multiple profiles.

**Non-interactive OAuth URL capture** (avoids PTY/interactive timeout issues):
```bash
cd /tmp && script -q -c "timeout 20 hermes --profile <profile> auth add openai-codex --no-browser 2>&1" /dev/null | head -20
# Output:
# 1. Open this URL in your browser:
#    https://auth.openai.com/codex/device
# 2. Enter this code:
#    XXXX-XXXXX
```
**Common failure modes:**
- `hermes --profile <profile> auth add openai-codex --no-browser` alone times out with no output
- Redirecting to a file (`> output.txt`) may also fail silently
- The `script -q -c` approach works because it wraps the command in a pseudo-TTY

**Auth reset does NOT fix shared credential exhaustion** — `hermes auth reset` clears exhaustion status but the underlying refresh token is single-use and gets consumed by whichever profile uses it first. All profiles on the same host share the same credential pool, so resetting Fred's credentials still leaves Ned unable to refresh because Kai (or another profile) already used the shared refresh token. Individual OAuth logins per profile are required, OR accept MiniMax as primary for Fred/Ned.

**Key insight from 2026-07-26 session:** All three profiles (Kai, Fred, Ned) share the same OAuth credential ID `64332f` ("dashboard device_code"). The `last_refresh` timestamps show Kai's credential was last refreshed `2026-05-31T19:42:45Z` and all three share the same token length (1888 chars access token, 90 chars refresh token). This is credential pool deduplication — the same underlying OAuth tokens are aliased across profiles. When Kai uses it, Fred and Ned get `refresh_token_reused`.

### OpenRouter as Permanent Alternative — BLOCKED

**Michael has explicitly rejected OpenRouter as a permanent solution ("Never open router. Only open AI OAuth").** Do NOT switch Fred/Ned to OpenRouter under any circumstances when the user is not present. Accept MiniMax-M3 as the primary model for Fred/Ned when openai-codex OAuth is unavailable due to credential sharing.
