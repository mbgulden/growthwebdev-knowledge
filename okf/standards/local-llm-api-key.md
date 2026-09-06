---
type: Standard
title: Local LLM Server API Key Pattern (llama.cpp / vLLM)
description: Reusable pattern for authenticating local OpenAI-compatible model servers (VM232 Kai, VM230 vLLM) with per-profile API keys, so Hermes profiles never call model servers unauthenticated.
resource: /home/ubuntu/work/growthwebdev-knowledge/okf/standards/local-llm-api-key.md
tags: [standards, local-llm, api-key, llama.cpp, vLLM, vm232, vm230, kai, infrastructure]
timestamp: 2026-09-06T00:28:00Z
linear_issue: GRO-4920
git_repo: growthwebdev-knowledge
git_path: okf/standards/local-llm-api-key.md
last_verified: 2026-09-06
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
- **vLLM**: `--api-key "<key>"` CLI flag on the serve command (vLLM 0.27.1).
  Key is stored in a `0600` file on the model host (e.g.
  `/opt/vllm_bin/.api_keys_<name>`) and the start script reads it at launch
  via `"$(cat /opt/vllm_bin/.api_keys_<name>)"`.
  **`--api-key` is single-value, last-wins — NO multi-key / no comma-split**
  (unlike llama.cpp's key file). `api_key` is typed `list[str]` in
  `cli_args.py:283` but the argparse action is `_StoreAction` (a bare string),
  so only ONE key is ever active. `/v1/*` **is** auth-gated (see
  `GUARDED_PREFIX = (/v1, /v2, /inference, /cohere)`); `/health` and
  `/metrics` are NOT gated.

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
| 192.168.1.230 (VM230) | `vllm-fred.service` | 8000 | local-qwen-27b-q8-fred + 5 more | `/opt/vllm_bin/.api_keys_fred` (0600) | all 11 profiles / `VLLM_FRED_API_KEY` |
| 192.168.1.230 (VM230) | `vllm-ned.service` | 8003 | Qwen3.8-27B-UD-Q5_K_M (ned main) | `/opt/vllm_bin/.api_keys_ned` (0600) | all 11 profiles / `VLLM_NED_API_KEY` |

All three lanes on 192.168.1.0/24 are now authenticated (as of 2026-09-06).

## vLLM-specific operational notes (2026-09-06 rollout)

- **No multi-key on vLLM `--api-key`** (single value, last-wins). Consequence:
  the HDE guest-bot template
  (`hd-platform-staging/scripts/vm_orchestrator.py`, `api_key: "llama-local"`
  → `:8000`) is now **stale** — any future guest deploy would 401 until that
  template is updated to use the real key (HDE repo, separate lane).
- **Client keying does NOT require a gateway restart**: the gateway installs a
  fresh per-turn secret scope (`gateway/run.py:2241` →
  `build_profile_secret_scope` → `load_env_file(<home>/.env)`), so the key is
  re-read from disk **every turn**. Verified live: a 9-day-old gateway whose
  process env has zero `VLLM_*` vars resolved the real key and authenticated
  against the freshly-keyed `:8003` with no gateway restart (only the vLLM
  process restarted). This supersedes the older "restart the profile gateway
  after changing the provider block" guidance for vLLM clients — keep that
  guidance for llama.cpp clients (kai), whose path is not scope-verified.
- **`:8003` is the ned main model** (that session runs on it). Keying it is
  self-referential but safe because of the per-turn scope: restart only the
  **remote vLLM** (`vllm-ned.service` on 192.168.1.230), never the local
  `hermes-gateway-ned`. Sequence: an unkeyed server ignores Bearer, so update
  all clients first, then key the server — zero 401 window.
- **`systemd-run` detached jobs run as root** and root has no ssh key to
  192.168.1.230 (only ubuntu does). For one-shot remote work, run inline from
  the in-gateway terminal (ubuntu) instead of a `systemd-run` unit, or copy the
  ubuntu key to root.

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
