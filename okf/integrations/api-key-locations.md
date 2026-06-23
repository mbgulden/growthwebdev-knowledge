---
type: Reference
title: Hermes Orchestrator — API Keys, Tokens & Secrets Locations
description: Canonical locations for every API key / token / secret the orchestrator uses. Future agents must read this FIRST before searching.
timestamp: 2026-06-22T23:50:00Z
last_updated: 2026-06-22T23:50:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/api-key-locations.md
last_verified: 2026-06-23
verified_by: ned
status: current
---

# API Keys, Tokens & Secrets — Locations

**Why this exists:** Future agents (and Fred himself) waste too much time hunting for API keys. They're scattered across profiles, env files, Cloudflare Tunnels, and OAuth clients. This doc lists every key, where it lives, and how to use it.

**Rule:** before searching for any API key, read this file end-to-end. If a key isn't listed here, add it when you find it.

## Quick reference table

| Service | Variable / Name | File location | Sandbox sees it? |
|---|---|---|---|
| Linear | `LINEAR_API_KEY` | `/home/ubuntu/.hermes/profiles/orchestrator/.env` | ❌ NO (terminal yes) |
| Linear OAuth Client | `LINEAR_OAUTH_CLIENT_ID`, `LINEAR_OAUTH_CLIENT_SECRET` | same `.env` | ❌ NO |
| Linear Webhook | `LINEAR_WEBHOOK_SIGNING_SECRET` | same `.env` | ❌ NO |
| Telegram (Fred / orchestrator) | `TELEGRAM_BOT_TOKEN` | `/home/ubuntu/.hermes/profiles/orchestrator/.env` | ❌ NO |
| Telegram (Autobot relay) | `TELEGRAM_BOT_TOKEN` | `/home/ubuntu/.hermes/profiles/autobot/.env` | ❌ NO |
| Telegram (Becca) | `TELEGRAM_BOT_TOKEN` | `/home/ubuntu/.hermes/profiles/becca/.env` | ❌ NO |
| Cloudflare API | `CLOUDFLARE_API_TOKEN` | env or `/home/ubuntu/.cloudflare/credentials` | ❌ NO |
| Cloudflare GrowthWeb zone | `CLOUDFLARE_GROWTHWEB_ZONE_PRISMATICENGINE` | `/home/ubuntu/.hermes/profiles/orchestrator/.env` | ❌ NO |
| Cloudflare GrowthWeb account | `CLOUDFLARE_GROWTHWEB_EMAIL`, `CLOUDFLARE_GROWTHWEB_API_KEY` | `/home/ubuntu/.hermes/profiles/{orchestrator,fred,ned,kai}/.env` | ❌ NO |
| Cloudflare GrowthWeb Pages token | `CLOUDFLARE_PAGES_API_TOKEN`, `CLOUDFLARE_PAGES_ACCOUNT_ID` | `/home/ubuntu/.hermes/profiles/{orchestrator,fred,ned,kai}/.env` | ❌ NO |
| Cloudflare AOT account (michael@activeoahu.com) | `CLOUDFLARE_AOT_EMAIL`, `CLOUDFLARE_AOT_API_KEY`, `CLOUDFLARE_AOT_ACCOUNT_ID`, `CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS` | `/home/ubuntu/.hermes/profiles/{orchestrator,fred,ned,kai}/.env` | ❌ NO |
| Cloudflare Tunnel token | embedded in `cloudflared` cmdline | `ps aux | grep cloudflared` | ❌ NO |

> **Two Cloudflare accounts!** GrowthWebDev (`michael@growthwebdev.com`) and AOT (`michael@activeoahu.com`) are separate accounts with different credentials, account IDs, and zones. See [`./cloudflare-account-activeoahu.md`](./cloudflare-account-activeoahu.md) for the AOT-specific reference.
| AGY OAuth token | JSON token file | `/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token` | ❌ NO |
| Hermes gateway state | n/a | `/home/ubuntu/.hermes/profiles/orchestrator/gateway_state.json` | ❌ NO |
| AGY sandbox dedup DB | n/a | `/home/ubuntu/.prismatic/state/dedup_log.db` | ❌ NO |

## Sandbox pitfall — IMPORTANT

**The `execute_code` Python sandbox does NOT inherit environment variables from the shell.** A common loop:

1. `terminal(grep 'LINEAR_API_KEY' .env)` shows the key exists
2. `execute_code(os.environ.get('LINEAR_API_KEY'))` returns `None`
3. Agent concludes "key not in env" and wastes 10 minutes debugging

**Fix:** do the API call from `terminal(...)` (which DOES inherit env), or `export` the key in the terminal subprocess:

```bash
export LINEAR_API_KEY=$(grep '^LINEAR_API_KEY=' /home/ubuntu/.hermes/profiles/orchestrator/.env | cut -d= -f2-)
python3 script.py   # now os.environ['LINEAR_API_KEY'] works
```

The orchestrator's env file (`/home/ubuntu/.hermes/profiles/orchestrator/.env`) is the canonical source. Other profiles (autobot, becca, etc.) have their own `.env` files with their own tokens — never cross-use them.

## Linear API gotchas

These hit me personally and are in the kanban as recurring review issues (GRO-1644 etc.):

1. **IssueFilter `identifier` is wrong — use `number` (Int).**
   ```graphql
   issues(filter: {number: {eq: 2093}})  # WORKS
   issues(filter: {identifier: {eq: "GRO-2093"}})  # HTTP 400
   ```
2. **Issue labels are case-sensitive.** `"agent:agy"` not `"AGY"` or `"agy"`.
3. **GraphQL field aliases matter.** The dispatcher script uses `labels: {some: {name: {eq: "agent:agy"}}}` — copy-paste the exact filter shape.

## Per-service usage patterns

### Linear API
```bash
export LINEAR_API_KEY=$(grep '^LINEAR_API_KEY=' /home/ubuntu/.hermes/profiles/orchestrator/.env | cut -d= -f2-)
python3 <<'PY'
import json, urllib.request, os
body = json.dumps({"query": "{ issues(first: 5) { nodes { identifier title } } }"}).encode()
req = urllib.request.Request("https://api.linear.app/graphql", data=body,
    headers={"Authorization": os.environ['LINEAR_API_KEY'], "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=15) as r:
    print(json.loads(r.read()))
PY
```

### Telegram (orchestrator / Fred)
The orchestrator's `TELEGRAM_BOT_TOKEN` is for Fred. To send to Michael's chat (8190664947):
```python
import urllib.request, json
TOKEN = open("/home/ubuntu/.hermes/profiles/orchestrator/.env").read()
TOKEN = [l.split("=",1)[1].strip() for l in TOKEN.splitlines() if l.startswith("TELEGRAM_BOT_TOKEN=")][0]
req = urllib.request.Request(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data=json.dumps({"chat_id": "8190664947", "text": "hello"}).encode(),
    headers={"Content-Type": "application/json"})
urllib.request.urlopen(req, timeout=10)
```

### Telegram (autobot relay)
For alerts that should appear from `@Autob0tautob0t_bot`, use the autobot token:
```python
TOKEN_PATH = "/home/ubuntu/.hermes/profiles/autobot/.env"
# Hardcode path because orchestrator's HOME is /home/ubuntu/.hermes/profiles/orchestrator/home
# so ~ doesn't expand right.
```

### AGY (Google Antigravity CLI)
- Binary: `/home/ubuntu/.local/bin/agy` (wrapper) or `/home/ubuntu/.local/bin/agy-bin` (real CLI)
- OAuth token file: `/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token`
- Token shape (verified): `{"token": {"access_token", "refresh_token", "expiry"}, "auth_method": "consumer"}`
- Token refresh is handled by the `d8660aee2fb0` cron (every 45 min)

### Cloudflare
- Tunnel token is embedded in the `cloudflared` command line: `ps -ef | grep cloudflared`
- API tokens are in `/home/ubuntu/.cloudflare/credentials` (or env vars)
- Zone IDs are in `/home/ubuntu/.hermes/profiles/orchestrator/.env`
- **Pitfall:** `CLOUDFLARE_GROWTHWEB_ZONE_PRISMATICENGINE` misleadingly points to `prismaticengine.com` zone, NOT `growthwebdev.com`. Always list zones and match by name.

### Hermes orchestrator internal
- Gateway state: `/home/ubuntu/.hermes/profiles/orchestrator/gateway_state.json` (note: this is NOT in HOME — orchestrator HOME is a chroot dir)
- Cron state: `/home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json`
- AGY dispatch results: `/tmp/agy_dispatch_results/` (or `/home/ubuntu/work/research/prismatic-engine/agy-dispatch-results/` for older)
- AGY sandbox logs: `/home/ubuntu/.gemini/antigravity-cli/log/` AND per-profile variant `/home/ubuntu/.hermes/profiles/<profile>/home/.gemini/antigravity-cli/log/` (depends on which profile launched the AGY process)

## How to discover a NEW key location

If you find a key that isn't in this table:
1. Grep `/home/ubuntu/.hermes/profiles/*/.env` for the service name
2. Check `/home/ubuntu/.cloudflare/`, `/home/ubuntu/.gemini/`, `~/work/*/.env`
3. Run `env | sort | grep -i <service>` in a `terminal()` call (which inherits env)
4. If found, **add it to this OKF doc immediately** so future agents don't repeat the search

## Secret-rotation protocol

Per the user-profile memory note: *"SECRETS: never paste them in chat. If a secret appears in any transcript, rotate immediately on first sight regardless of context."*

If any of these keys leak into a Telegram message, log file, or OKF doc:
1. Rotate the key immediately at the provider (regenerate API token)
2. Update `/home/ubuntu/.hermes/profiles/orchestrator/.env` (or wherever it lives)
3. Restart any service that loaded the old key
4. Audit any transcripts / logs for the old key and scrub them
