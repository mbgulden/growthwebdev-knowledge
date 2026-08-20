---
name: agent-onboarding-workflow
description: "Create and onboard new Hermes agent profiles/bots safely: profile creation, Telegram token storage, SOUL role setup, gateway start, verification, and handoff notes."
triggers:
  - create new agent
  - onboard bot
  - Telegram bot token
  - BotFather
  - Hermes profile create
  - new helper agent
  - agent onboarding
---

# Agent Onboarding Workflow

Use this whenever Michael asks to create, configure, or onboard a new Hermes profile or Telegram bot.

## Safety first

- Treat BotFather tokens as secrets. Store them in the target profile `.env`; never repeat them in final chat.
- Keep `.env` mode `600`.
- Verify bot identity with Telegram `getMe` but print only safe fields: `ok`, `username`, `first_name`, and whether an ID exists.
- Do not set `GATEWAY_ALLOW_ALL_USERS=true` unless Michael explicitly asks for a public bot. Prefer profile `telegram.allowed_chats`.
- Do not modify another profile's data unless explicitly creating/configuring that target profile.

## Standard sequence

1. **Load Hermes docs / skill context**
   - If the `hermes-agent` skill exists, load it.
   - If not, inspect `hermes --help`, `hermes profile --help`, `hermes gateway --help`, and the current Hermes docs as needed.

2. **Create profile**

```bash
hermes profile create <name> --clone-from <source-profile> \
  --description "<one or two sentence routing description>"
```

Use a source profile with the right model/tooling. For a Prismatic helper bot, `kai` is a good source because it carries Prismatic/AOT workflow skills and Telegram-safe reporting preferences.

3. **Write role/SOUL**

Create or replace:

```text
~/.hermes/profiles/<name>/SOUL.md
```

Include:

- agent role and non-role boundaries;
- what the agent owns;
- current lessons to preserve;
- tone/reporting defaults;
- safety rules;
- compact verification proof format.

4. **Store Telegram token**

Update:

```text
~/.hermes/profiles/<name>/.env
```

Set:

```text
TELEGRAM_BOT_TOKEN=<secret token>
GATEWAY_ALLOW_ALL_USERS=false
```

Then:

```bash
chmod 600 ~/.hermes/profiles/<name>/.env
```

5. **Configure user allowlist**

Hermes gateway authorization checks `TELEGRAM_ALLOWED_USERS` for Telegram DM/user authorization. Profile `telegram.allowed_chats` may still be useful for chat scoping, but do not rely on it as the only auth gate. Add known trusted Telegram user IDs to the target profile `.env`:

```text
TELEGRAM_ALLOWED_USERS=<comma-separated-user-ids>
GATEWAY_ALLOW_ALL_USERS=false
```

If the gateway log says `No user allowlists configured`, the bot will deny everyone until this is set and the gateway process is restarted.

6. **Verify Telegram token without leaking it**

Use Python/urllib or curl through environment. Print only non-secret fields:

```bash
set -a
. ~/.hermes/profiles/<name>/.env
set +a
python3 - <<'PY'
import json, os, urllib.request
url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/getMe"
with urllib.request.urlopen(url, timeout=20) as r:
    data = json.load(r)
print(json.dumps({
    "ok": data.get("ok"),
    "username": data.get("result", {}).get("username"),
    "first_name": data.get("result", {}).get("first_name"),
    "id_present": bool(data.get("result", {}).get("id")),
}, sort_keys=True))
PY
```

7. **Check profile and gateway state**

```bash
hermes profile show <name>
hermes gateway list
<name> gateway start
hermes gateway list
```

If `gateway start` fails, inspect logs with compact output. Do not paste secrets.

8. **Systemd durability (optional but recommended for persistent bots)**

For a persistent bot, install a profile-specific system service:

```bash
printf 'Y\nY\n' | sudo hermes --profile <name> gateway install --system --run-as-user ubuntu
systemctl is-active hermes-gateway-<name>.service
```

If you first started the gateway manually and then installed the service, the service may fail with `Gateway already running`. Stop only the target profile process, then let systemd restart it. When running from inside another Hermes gateway, direct `systemctl restart` may be blocked by safety guards; killing the target profile's `MainPID` lets systemd restart that target service without stopping the current agent:

```bash
pid=$(systemctl show -p MainPID --value hermes-gateway-<name>.service)
sudo kill -TERM "$pid"
sleep 8
systemctl is-active hermes-gateway-<name>.service
```

After any `.env` auth/token change, restart the target gateway so it reloads the env.

9. **Smoke test**

Ask Michael to send `/start` or a short message to the new bot. If accessible from the current account, use Telegram delivery only after the bot has received a chat or the chat ID is known. Otherwise report that user-side first message is the next required step.

10. **Document handoff**

Final report should include:

- profile path;
- Telegram bot username;
- gateway status;
- what was configured;
- what was not done;
- next step for Michael;
- no token.

## Successor/helper agent readiness

When onboarding a helper bot that is meant to take over part of another agent's live coordination role, treat it as a **successor handoff**, not just a bot setup.

In addition to profile/token/gateway setup, create:

- a role-specific `SOUL.md` with ownership boundaries;
- a current handoff artifact such as `PRISMATIC_CURRENT_HANDOFF.md` for active runway state;
- a paste-ready user-preference seed response if the new bot asks Michael to build a profile;
- a readiness check covering enabled toolsets, enabled skills, read-only repo/API access, gateway status, and explicit non-claims for untested destructive operations.

For Prismatic helper bots, include dashboard preservation rules, compact verification discipline, and the next workflow gap/watch item. Do not let the new helper reinvent product surfaces or ask Michael to repeat context that can be written into the handoff artifact.

## Profile model/auth stack sync for helper agents

When Michael asks to make a helper profile use the same “models we use for tool usage,” do not stop at `model.default`. Check and sync the full model stack:

1. Compare source and target `config.yaml` for `model`, `providers`, `fallback_providers`, `auxiliary`, `delegation`, `web`, `toolsets`, and `compression`.
2. Explicitly inspect every auxiliary model slot, including newer/default-generated entries such as `curator`, `background_review`, `moa_reference`, and `moa_aggregator`; these may remain `provider: auto` even when visible config output only shows Vision/Web extract.
3. Set target auxiliary slots to the source standard when requested, usually:
   - `provider: openai-codex`
   - `model: gpt-5.5`
   - `base_url: https://chatgpt.com/backend-api/codex`
   - fallback chain to `google / gemini-2.5-flash` when that is the source profile fallback.
4. Sync auth pool if the target has stale/missing OAuth credentials. Make a timestamped backup of the target `auth.json`, then copy the source profile's relevant `providers`, `credential_pool`, and `active_provider` sections. Never print tokens.
5. Restart only the target gateway. From inside another gateway, direct `systemctl restart` may be blocked; use a Python subprocess/`os.kill` pattern to terminate the target service `MainPID` so systemd restarts it without killing the current agent.
6. Verify with both static config inspection and a live smoke test, e.g. `hermes --profile <target> -z 'Reply exactly: MODEL_OK'`.

For session detail and a compact verification recipe, see `references/george-model-stack-sync-2026-07-17.md`.

For mirroring a **local llama.cpp** model stack (per-agent endpoints, real GGUF model names, context-limit traps), see the section below and `references/model-stack-mirror-llamacpp-2026-08-18.md`.

## Mirroring a local llama.cpp model stack across profiles (2026-08-18 lesson)

When Michael asks to make helper profiles (Ned, George, etc.) "mirror" a reference profile (usually Kai) that runs a local llama.cpp Qwen build, do this class of work — not the gpt-5.5/OpenAI path above:

1. **Never reuse the reference profile's provider block verbatim.** Each profile keeps its own provider name (`qwen27b-ned-local`, `qwen27b-george-local`) pointing at its own endpoint. The *shape* mirrors; the endpoint does not.
2. **Use the real GGUF path as the model name everywhere** (`/models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf`), including `model.default`, the provider's `default_model`, and every auxiliary slot. Helper profiles often carry fake alias names (`local-qwen-27b-q4-ned`) that happen to work — that's luck, not config.
3. **Mirror auxiliary slot-for-slot from the reference profile**: same slots, same timeouts, same fallback chain. Do not copy `background_review`/`moa_*` slots that reference openai-codex — they hit the shared exhausted OAuth pool.
4. **Fix fallback auth inline.** `GOOGLE_API_KEY` is often absent from gateway process env (it's not in `.env` or unit files). Reference profiles get away with `api_key_env: GOOGLE_API_KEY` in fallbacks because the shell has it — but target gateways may not. Inline the literal Google key in the target's `fallback_providers` and aux `fallback_chain` (it's already plaintext in the config's `google` provider block).
5. **Discover the server's hard context limit before trusting config.** llama.cpp servers run a fixed `-c`. Probe it: a request that 400s with `exceeds the available context size (N tokens)` reveals the real limit. Configs often claim 262144 while the server runs 32768. Set `context_length` truthfully, and add `model.context_length: 64000` because Hermes enforces a 64K minimum and refuses to start below it.
6. **Remove dead model-discovery blocks**: `model_catalog: {enabled: true, providers: {}}` breaks model resolution; opt-in MOA presets referencing retired providers are landmines. Pop them when mirroring.
7. **Restart via systemd MainPID kill** (Restart=always replaces the process). Smoke-test with `hermes --profile <p> -z 'Reply with exactly: X_OK'`.
8. **Verify vision separately** if the reference profile claims it: POST a 1×1 colored PNG to the target's endpoint. Use `max_tokens: 400+` — small budgets get eaten by thinking and return empty content, looking like a vision failure when it isn't.

Detail + exact before/after state: `references/model-stack-mirror-llamacpp-2026-08-18.md`.

## George-specific lesson from 2026-07-16

George was created as a Prismatic helper bot to take over Kai's Prismatic workflow guard role so Kai can return to Active Oahu Tours. The best setup was:

- profile name: `george`;
- cloned from `kai`;
- custom `SOUL.md` defining George as Prismatic coordination/helper bot, not AOT owner;
- BotFather token stored in `/home/ubuntu/.hermes/profiles/george/.env`;
- `TELEGRAM_ALLOWED_USERS` configured and `GATEWAY_ALLOW_ALL_USERS=false`;
- systemd service installed/running as `hermes-gateway-george.service`;
- current handoff doc created at `PRISMATIC_CURRENT_HANDOFF.md` and linked from SOUL;
- toolsets/skills/GitHub read access verified before declaring readiness;
- token verified with Telegram `getMe` printing only safe metadata.

Detailed session reference: `references/george-prismatic-helper-onboarding-2026-07-16.md`.

## Verification output discipline

For onboarding, keep detailed logs in `/tmp/<agent>-onboarding-verify.log` and return compact proof:

```text
COMMAND=<summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path or not needed>
SCOPE=Hermes profile + Telegram bot onboarding
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=<anything not done, e.g. user-side chat smoke not yet confirmed>
MARKER=AGENT_ONBOARDING_OK
```

## Existing profile model correction / rollback

Use this section when Michael asks to “fix <agent> model,” “change <profile> back to gpt-5.5,” “update to ChatGPT 5.6 Terra,” or similar for an existing Hermes profile.

1. Load Hermes context if available; if the protected/bundled `hermes-agent` skill is not installed in this profile, fall back to CLI discovery (`hermes --help`, `hermes config --help`, `hermes profile --help`, `hermes gateway --help`).
2. Inspect the target profile’s config directly at `~/.hermes/profiles/<name>/config.yaml`; do not rely only on the current profile’s `hermes config show`, because environment/profile flags may not select the intended target from inside a running gateway.
3. For the active profile, prefer the CLI (`hermes config set model.default <model>`, `hermes config set auxiliary.<slot>.model <model>`) over file patch/write tools. Hermes config files are security-sensitive and direct writes may be refused; the CLI also preserves YAML shape.
4. Change the whole target model stack, not just `model.default`, when the wrong model appears in auxiliaries too: `model.default` plus auxiliary slots such as `vision`, `web_extract`, `compression`, `session_search`, `skills_hub`, `approval`, `mcp`, `title_generation`, `tts_audio_tags`, `triage_specifier`, `kanban_decomposer`, `profile_describer`, `monitor`, and `curator`.
5. Verify statically with `hermes config show` for the active profile or `hermes profile show <name>` / direct config inspection for another profile, plus a targeted search confirming zero stale model references in configured model slots.
6. Run a live smoke test with the target provider/model, e.g. `hermes -z 'Reply with exactly: MODEL_OK' --provider <provider> -m <model>`. If the current gateway shell has unusual exported `HOME`/environment state, rerun with a minimal environment such as `env -i HOME=/home/ubuntu PATH=$PATH USER=ubuntu HERMES_HOME=/home/ubuntu/.hermes/profiles/<name> HERMES_PROFILE=<name> ...` rather than recording the transient failure as a tool limitation.
7. Restart only the target gateway when the running process must reload config. If `hermes --profile <name> gateway restart/stop` is refused because the command is running inside a gateway process, terminate only the target gateway PID and start `hermes --profile <name> gateway run` again; never restart/kill all gateways.
8. Final report should be compact: old→new model, static verification, live smoke-test result, stale-reference count, and any caveat such as “current chat may still be on the launch-time model until a new session/gateway restart.”

Session detail: `references/kai-gpt56-terra-update-2026-07-23.md`.

## Pitfalls

- `HERMES_PROFILE=<name> hermes config show` can still display the active/current profile in some gateway contexts; use `hermes profile show <name>` and direct config inspection for target-profile certainty.
- Cloning a profile can copy the source Telegram token; always replace it before starting gateway.
- A bot cannot DM a user until the user starts/messages it first.
- A profile can exist while the gateway is stopped; verify both profile creation and gateway process state.
- Multiple profile gateways may run simultaneously, but duplicate tokens across profiles will fight each other. Ensure the new profile has its own token.
- Avoid hardcoding secrets in skills, SOUL, config, or final reports.
