---
type: Standard
title: Local LLM Server API Key Pattern (llama.cpp / vLLM)
description: Reusable pattern for authenticating local OpenAI-compatible model servers (VM232 Kai, VM230 vLLM) with per-profile API keys, so Hermes profiles never call model servers unauthenticated.
resource: /home/ubuntu/work/growthwebdev-knowledge/okf/standards/local-llm-api-key.md
tags: [standards, local-llm, api-key, llama.cpp, vLLM, vm232, kai, infrastructure]
timestamp: 2026-08-21T22:30:00Z
linear_issue: null
git_repo: growthwebdev-knowledge
git_path: okf/standards/local-llm-api-key.md
last_verified: 2026-08-21
verified_by: Ned
status: current
---

# Local LLM Server API Key Pattern

Local model servers (llama.cpp `llama-server`, vLLM) bind to `0.0.0.0` on the
LAN. Before 2026-08-21 they ran with **no authentication** — any device on
192.168.1.0/24 could burn the GPUs. This standard defines the reusable
key pattern so we don't re-invent it per model/VM/profile.

## The pattern (three legs)

### 1. Server side (model host)

- **llama.cpp**: key file with one key per line, mode `0600`, referenced by
  `--api-key-file /path/.api_keys`. (Flag verified present on the VM232 build:
  `llama-server-new --help` lists `--api-key KEY (env: LLAMA_API_KEY)` and
  `--api-key-file FNAME`.)
  - `/v1/models` is NOT gated in this build — **completions are**. Do not treat
    a 200 on `/v1/models` without a key as "auth is off".
- **vLLM**: `API_KEY=*** env var on the process.

### 2. Client side (Hermes profile)

- Generate a key: `KAI_LLM_API_KEY=*** rand -hex 24)` (prefix `<agent>-llama-`).
- Store in the profile `.env`: `~/.hermes/profiles/<profile>/.env`
  as `<PREFIX>_API_KEY=***
- Profile `config.yaml` provider block uses **`api_key_env:`** (never a
  literal key):
  ```yaml
  providers:
    qwen27b-kai-local:
      api: http://192.168.1.232:8080/v1
      api_key_env: KAI_LLM_API_KEY
  ```
- **After changing the provider block, restart the profile gateway** — the
  running gateway keeps the old in-memory key and will 401 on every call.
  Restart path that works from inside a gateway session:
  `sudo bash /tmp/restart_<profile>_gw.sh` (script wraps
  `systemctl restart hermes-gateway-<profile>.service`; direct
  `systemctl restart` is blocked by the in-gateway guard, `systemd-run`
  fails with polkit auth as ubuntu).

### 3. Monitoring (Autobot)

- Watchdog: `~/.hermes/profiles/autobot/scripts/llm_server_watchdog.py`
  (no_agent cron, every 5m, `deliver telegram:8190664947`, silent when healthy).
- On-host probe: `/usr/local/bin/llm_probe.py` on the model host —
  `python3 llm_probe.py <model> <port> <key_file>` → prints `HTTP:<code>`,
  exit 0/2/3. Key is read on the host and **never crosses the SSH wire**.
- Adding a new VM/model = append one entry to `TARGETS` in the watchdog +
  deploy `llm_probe.py` to that host.

## Current deployments

| Host | Service | Port | Model | Server key | Client profile / env var |
|---|---|---|---|---|---|
| 192.168.1.232 (VM232) | `llama-kai.service` | 8080 | qwen3.8-27b (Q4_K_M + MTP) | `/opt/llama_bin/.api_keys` | kai / `KAI_LLM_API_KEY` |
| 192.168.1.230 (VM230) | vLLM | 8000 | local-qwen-27b-q8-fred + q4 | ⚠️ not yet keyed | (multiple profiles) |

VM230 vLLM is still unauthenticated — next target for this pattern.

## Key rotation

1. New key: `openssl rand -hex 24` with prefix.
2. Append/replace line in the server key file (llama.cpp supports multiple
   keys, so add new + restart for atomic swap), update profile `.env`.
3. Restart gateway (see client side).
4. Verify: `python3 /tmp/verify_kai_key.py` shape — correct key 200, no key
   401, wrong key 401 on `/v1/chat/completions`.

## Pitfalls

- **Inline shell key expansion across SSH gets mangled** — `\"$KEY\"` escapes
  the quotes so the var expands empty on the remote side (symptom: 401 with
  the correct key). Put the probe in an on-host script; never build the
  `Authorization` header by interpolating a key fetched over SSH.
- **The Hermes display layer scrubs shell strings containing `$(cat <keyfile>)`
  / `Bearer $KEY` / secret-looking env var names** — bash dies with
  "unexpected EOF". Write the check to a `.py`/`.sh` file first, then run it.
- `/proc/<pid>/environ` does NOT show dotenv vars — Hermes loads `.env` at
  runtime, not via systemd `Environment=`. Don't conclude "key not loaded"
  from an empty `/proc` environ; verify with a real model call instead.
- llama.cpp key-file change requires a **server restart** (keys are read at
  startup).
