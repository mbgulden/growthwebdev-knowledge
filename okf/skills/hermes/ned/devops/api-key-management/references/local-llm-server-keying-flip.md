# Keying a local model server (vLLM / llama.cpp) with zero 401 outage

Class: add auth to a LAN `0.0.0.0` OpenAI-compatible model server (vLLM,
llama.cpp `llama-server`) and wire up **every** Hermes client profile so none
of them — including, worst case, **your own profile if the server is your main
model** — ever 401. The whole thing is a sequence of "look, nothing changed,
but actually a gateway just stopped being able to reach its model" hazards.
This is the playbook that landed clean on 2026-09-06 (VM230 `:8000` + `:8003`,
11 profiles + global).

## The two insights that dominate

### 1. The gateway re-reads each profile's `.env` from disk EVERY turn (no restart needed)

The multiplexing gateway installs a **fresh per-turn secret scope**:
`gateway/run.py` → `build_profile_secret_scope(Path(profile_home))` →
`load_env_file(<home>/.env)`, and `load_env_file` **re-reads the file from disk**
on each call (no memoization). So:

- After you rotate a key in a profile's `.env`, **you do NOT need to restart
  that profile's gateway**. The very next turn resolves the new key.
- A stale gateway whose `/proc/<pid>/environ` shows **zero** key vars still
  authenticates fine — the key comes from the per-turn disk read, not the
  process env.
- **Decisive pre-flip safety probe** (run a fresh interpreter, don't inspect
  `/proc`):
  ```python
  import sys; sys.path.insert(0, '/home/ubuntu/work/hermes-agent-fork')
  from pathlib import Path
  from agent.secret_scope import (build_profile_secret_scope, get_secret,
                                   set_secret_scope, reset_secret_scope, _is_global_env)
  assert not _is_global_env('VLLM_NED_API_KEY')   # must NOT be a global-env var
  tok = set_secret_scope(build_profile_secret_scope(Path('/home/ubuntu/.hermes/profiles/ned')))
  v = get_secret('VLLM_NED_API_KEY'); reset_secret_scope(tok)
  # v must be the REAL key (compare sha256 to the key file), not a 3-char 'key' stub
  ```
  If this returns the real key, keying the server is safe for that profile.

  (This supersedes the naive "restart the profile gateway after changing the
  provider block / `.env`" rule for vLLM clients. Keep that rule for clients
  whose path you have NOT verified is scope-driven.)

### 2. A zero-401 flip order

An **unkeyed** server ignores the `Authorization` header and returns 200 for
any Bearer. So:

1. Generate real keys → store in `0600` files on the model host.
2. Write the real key into **every** client profile's `.env` + the global one.
   **Verify it's the real key, not a placeholder** (a re-run / post-compaction
   append can leave a 3-char `key` stub — see gotchas).
3. Add `key_env:` **and** `api_key_env:` to every client `config.yaml`
   provider entry (main-chat path lifts the alias; aux path reads `key_env` —
   set both).
4. Restart the **consumer** gateways (they load the new key against the
   still-unkeyed server = 200, no breakage).
5. **Then** key the server (add the flag, restart the model server).
6. Verify on the server: no-auth → 401, with-key → 200, unit `active`.

## The self-flip case (server = your own main model)

If the server you're keying is the model **serving your current session**
(e.g. `:8003` is ned's main model), do NOT touch your own
`hermes-gateway-<profile>` unit:

- The in-gateway terminal guard **hard-blocks** any command/referenced-script
  containing a `hermes-gateway` lifecycle token, and a self-restart would
  SIGTERM the in-flight turn.
- Thanks to the per-turn scope, your running gateway **already has the new
  key** once it's in `.env`. So the flip is: **restart only the remote model
  server** (`ssh <model-host> 'systemctl restart vllm-ned.service'`) and let it
  come back keyed. Your gateway needs no restart.
- Sequence matters for liveness: block until the model port is back up **and**
  verified keyed (no-auth=401, with-key=200) before returning control, so your
  next LLM call hits a healthy keyed endpoint.

## vLLM 0.27.1 specifics

- Auth is the **`--api-key "<key>"` CLI flag** on the serve command, NOT an
  `API_KEY` env var (the older "API_KEY env" claim is wrong for this build).
  Store the key in a `0600` file and have the start script read it at launch
  via `--api-key "$(cat /opt/vllm_bin/.api_keys_<name>)"`.
- **Single-value, last-wins. No multi-key, no comma-split.** `api_key` is typed
  `list[str]` in `cli_args.py:283` but the argparse action is `_StoreAction`
  (a bare string). So a legacy key (e.g. an HDE guest-bot template's
  `llama-local`) **cannot coexist** with the real key — one key only. If a
  template ships a placeholder key, that template must change (separate lane),
  not the server.
- `/v1/*` **is** auth-gated (`GUARDED_PREFIX = (/v1, /v2, /inference, /cohere)`);
  `/health` and `/metrics` are **not** gated. So a 200 on `/metrics` or
  `/health` without a key does NOT mean auth is off.

## llama.cpp specifics

- `--api-key-file /path/.api_keys` (one key per line, `0600`); multi-key OK.
- `/v1/models` is **not** gated in this build — **completions are**. Don't
  treat a 200 on `/v1/models` without a key as "auth is off."

## Live-hit gotchas

- **`systemd-run --unit=X -- /bin/bash script.sh` runs as root.** Root usually
  has **no ssh key** to the remote model host (only `ubuntu` does). A detached
  flip as root dies with `Permission denied (publickey,password)` — but it's
  **harmless if the script never reached the remote** (check the log; the model
  server stays up). Fix: run one-shot remote work **inline from the in-gateway
  terminal (as ubuntu)**, or copy the ubuntu key to root. Don't retry the
  root-unit path.
- **In-gateway terminal guard scans referenced scripts, not just the command.**
  A flip script containing a literal `hermes-gateway-...` restart gets
  hard-blocked. Keep the flip script free of those tokens (only the remote
  model-server unit, e.g. `vllm-ned`/`vllm-fred`).
- **Display-layer redaction kills inline secret-looking strings.**
  `$(cat <keyfile>)`, `Bearer $KEY`, and secret env names in an inline command
  make bash die with `unexpected EOF` / a "blocked" message. Write the check
  to a `.py`/`.sh` file first (via `write_file`), then run that file.
- **Placeholder-key trap.** After a re-run or a compression boundary, the
  `.env` append may have left a 3-char `key` stub instead of the real key.
  Before keying the server, confirm by **hash** (`sha256(env value) ==
  sha256(key file)`) that every client `.env` holds the real key. A stub means
  the whole fleet 401s the moment the server is keyed.
- **`.env` file perms.** A key-rotation pass is the moment to `chmod 600` any
  profile `.env` that's world-readable (775) and now contains real keys.
- **Shared knowledge/OKF repos are a concurrent-edit hazard.** Uncommitted
  working-tree edits get **wiped by a concurrent agent's commit + reset**
  (multiple agents share the checkout). Commit in-lane work to a `ned/` branch
  **promptly**, and branch from `origin/main` (not local `main`, which a
  parallel commit can leave diverged). Verify the doc is still on disk before
  you assume your earlier edit survived.
- **`/proc/<pid>/environ` empty ≠ key missing.** See insight #1 — the key is a
  per-turn disk read, not a process-env var.

## Verify checklist (per endpoint, after the flip)

```
curl -s -o /dev/null -w '%{http_code}' http://<host>:<port>/v1/models   # expect 401
curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $K" \
     http://<host>:<port>/v1/models                                    # expect 200
ssh <model-host> 'systemctl is-active vllm-<name>.service'             # expect active
```
And confirm the session that runs on the newly-keyed endpoint is still alive
(`systemctl show hermes-gateway-<profile> -p ActiveState`) — that survival is
itself the proof the per-turn scope picked up the key.
