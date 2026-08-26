---
name: redacted-profile-config-export
description: "Export a Hermes profile's full configuration (config.yaml, .env, systemd unit, MCP servers, model endpoints) as a shareable secret-safe .md — for user requests, handoffs, onboarding, or migration. Use when asked to dump a profile config, output all the settings, send the config to a file, or prepare a profile for transfer/review."
category: operations
tags: [config, redaction, secrets, export, shareable, hermes]
triggers:
  - asked to dump or output a profile config or all the settings
  - preparing a profile handoff, onboarding, or migration document
  - auditing whether a config or config dump is safe to share
---

# Redacted Profile Config Export

## Core principle
A config dump is a shareable artifact the moment it leaves the box — treat it as publish-grade. No secret VALUES, no secret-looking strings, `.env` as names only. The raw config stays on disk; the dump is a redacted projection. Never deliver the raw file.

## Steps
1. **Enumerate every config surface** for the profile: `config.yaml`, `.env` (+ backups), the systemd unit (`systemctl cat`), MCP server definitions, profile-dir listing (names), and LIVE-probe the model endpoint(s) (`/health`, `/v1/models`) — a dump with live verification is worth 10x one without.
2. **Redact config.yaml with a script, not eyeballs** (python, 2 passes):
   - Pass 1 (key name): keys matching `api[_-]?key|token|secret|password|passwd|credential|authorization` whose value is non-empty and NOT an env ref (`${...}`, `env:`, or `*_env` keys) → `[REDACTED]`.
   - Pass 2 (value shape): values starting `sk-`, `xox[bap]-`, `ghp_`, `xai-`, `AIza`, `eyJ`, or matching the Telegram bot-token shape `^\d{8,10}:[A-Za-z0-9_-]{20,}` → `[REDACTED]`.
   - Keep env-ref keys verbatim (`api_key_env: SOME_KEY` is safe AND informative).
3. **Final scan — never skip:** re-scan the FINISHED document with the secret-shape regexes; require zero hits before delivery. Print the hit count in your report.
4. **`.env` → names only:** `cut -d= -f1 | grep -v '^\s*#'`. Never dump `.env` values, not even ones that look safe (tokens, passwords, OAuth secrets).
5. **Structure the doc:** identity/runtime → model routing (provider/model/context/fallback) → model server (live-verified) → key config sections (mcp_servers, platforms, agent/gateway/cron, terminal, memory) → `.env` key names → full redacted config in a yaml fence → systemd unit → fleet status → related docs/pointers.
6. **Flag, don't silently fix:** literal keys where the `api_key_env:` pattern belongs (see OKF `standards/local-llm-api-key.md`), or unauthenticated model endpoints → note as a hygiene finding in the doc and offer the fix.
7. **Deliver:** save under `/home/ubuntu/work/` with a dated name (`<agent>-config-YYYY-MM-DD.md`), send via `MEDIA:<absolute path>`.

## Pitfalls
- **Key names alone are not enough** — a `secret:` under `platforms.webhook.extra` or a bot token in an odd-named key slips past pass 1. The value-shape pass + final scan are what catch them.
- **Use the shipped redactor** — `scripts/redact_config.py` implements both passes plus the `--scan` final check (`python3 redact_config.py config.yaml out.yaml` then `python3 redact_config.py --scan finished.md` → must print `secret-looking tokens found: 0`). Don't hand-roll the regexes per session; if you find a token shape it misses, patch the script.
- **Account for the redaction count**: print the list of redacted key names (e.g. "21 redacted: api_key ×3, secret ×1, token ×...") so the recipient can audit coverage.
- **Build the doc with `write_file`/execute_code** (no guard issues, auditable), not echoed shell heredocs.
- **Live probes belong in the doc with timestamps** — model ids, `max_model_len`, `/health` status — so the dump doubles as a point-in-time infra audit.
- Stale handoff/config assumptions: verify against live state (endpoint probes, `systemctl` state) rather than copying claims from docs.
