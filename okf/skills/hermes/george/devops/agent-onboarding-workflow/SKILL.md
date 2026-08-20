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

For a persistent bot, install a profile-specific system service with the standard service name and current model description:

```bash
printf 'Y\nY\n' | sudo hermes --profile <name> gateway install --system --run-as-user ubuntu
systemctl is-active hermes-gateway-<name>.service
systemctl show hermes-gateway-<name>.service -p Id -p Description -p ExecStart -p TimeoutStopUSec -p Restart --no-pager
```

Prefer the standard `hermes-gateway-<name>.service` shape. If you inherit or repair a legacy service such as `<name>-gateway.service`, audit whether it has stale descriptions, retired model names, fallback claims, `--replace`, or nonstandard kill/restart behavior. Normalize the service only after recording the current unit and verifying that no duplicate service will fight for the same profile/token.

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

## George-specific lesson from 2026-07-16

George was created as a Prismatic helper bot to take over Kai's Prismatic workflow guard role so Kai can return to Active Oahu Tours. The best setup was:

- profile name: `george`;
- cloned from `kai`;
- custom `SOUL.md` defining George as Prismatic coordination/helper bot, not AOT owner;
- BotFather token stored in `/home/ubuntu/.hermes/profiles/george/.env`;
- `GATEWAY_ALLOW_ALL_USERS=false`;
- token verified with Telegram `getMe` printing only safe metadata.

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

## Pitfalls

- Cloning a profile can copy the source Telegram token; always replace it before starting gateway.
- Cloning or repairing a profile can leave stale active session routes in the target profile's `state.db`; after a provider/model switch, verify active unended sessions as well as YAML config. For fleet repairs, use the richer Prismatic helper-bot pattern in `prismatic-coordination-workflows` → `references/hermes-profile-fleet-governance.md`, including top-level fallback order, real inference probes, target-only gateway stop, SQLite backup, route update counts, and watchdog proof.
- A bot cannot DM a user until the user starts/messages it first.
- A profile can exist while the gateway is stopped; verify both profile creation and gateway process state.
- Multiple profile gateways may run simultaneously, but duplicate tokens across profiles will fight each other. Ensure the new profile has its own token.
- Avoid hardcoding secrets in skills, SOUL, config, or final reports.
