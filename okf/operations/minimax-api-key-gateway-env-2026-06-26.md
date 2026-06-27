---
type: Operations
title: MINIMAX_API_KEY Missing from Hermes Gateway Process Environments
description: Every long-running Hermes gateway (autobot, kai, next-step, ned, orchestrator) was started without MINIMAX_API_KEY in its process environment, causing all vision_analyze / browser_vision calls to fail with 401.
linear: GRO-2483
severity: medium
status: identified
date: 2026-06-26
---

# MINIMAX_API_KEY Missing from Hermes Gateway Process Environments

## TL;DR

Hermes auxiliary vision tools (`vision_analyze`, `browser_vision`, screenshot OCR paths) call MiniMax-M3 via `auxiliary.vision.api_key_env: MINIMAX_API_KEY`. The key is present in every profile's `~/.hermes/profiles/<profile>/.env`, but **none of the long-running gateway subprocesses have it loaded into `/proc/<pid>/environ`**. Every vision call from those gateways returns `401 — login fail: Please carry the API secret key in the 'Authorization' field of the request header (1004)`.

## Discovery

Triggered while captioning screenshots for GRO-2472 / GRO-2476 fixes. Captured browser screenshots came back fine, but `vision_analyze` and `browser_vision` returned 401 consistently. Verified the MiniMax API itself was healthy by calling MiniMax-M3 directly via Python with the same key — succeeded with 200 OK. Confirmed the issue is hermes' auxiliary client, not the network or the key.

## Root cause

Hermes loads profile env files only at gateway **startup time**, not per-call. The gateways were started 21+ hours ago (pid 1195, 1233, 1239, 1245) before any of the following:

- `/home/ubuntu/.profile` had a `[ -f ~/.hermes/profiles/orchestrator/.env ] && set -a && source ... && set +a` block
- `/home/ubuntu/.bashrc` had a similar auto-source block
- The user explicitly exported `MINIMAX_API_KEY` in their shell

So at the time the gateway process was exec'd, `MINIMAX_API_KEY` was **not in its environment**. The auxiliary client's OpenAI SDK now sends `Authorization: Bearer ` (empty token), which MiniMax correctly rejects with 401.

A freshly-started gateway subprocess (pid 173483, the `gateway restart` runner) **does** have the key in its environment and works correctly — proving this is purely an env-loading issue at gateway startup.

## Detection command

```bash
PID=$(pgrep -f 'hermes.*--profile orchestrator.*gateway' | head -1)
tr '\0' '\n' < /proc/$PID/environ | grep MINIMAX
```

If nothing prints, the gateway needs to be restarted with the env loaded.

## Affected gateways (snapshot 2026-06-26 00:00 UTC)

| PID  | Profile    | Up time  | Has MINIMAX_API_KEY in /proc env |
|------|------------|----------|----------------------------------|
| 1195 | autobot    | 21h24m   | NO  → needs restart |
| 1233 | kai        | 21h24m   | NO  → needs restart |
| 1239 | next-step  | 21h24m   | NO  → needs restart |
| 1245 | ned        | 21h24m   | NO  → needs restart |
| 173483 | (gateway restart runner) | 14h17m | YES — reference for correct env |
| n/a  | orchestrator (this session) | — | running, env loaded at process start |

## Fix

For each affected profile gateway:

```bash
# 1. Confirm key exists in profile env (already true)
grep MINIMAX_API_KEY ~/.hermes/profiles/<profile>/.env

# 2. Graceful shutdown — pick the right method for the deployment
hermes --profile <profile> gateway stop
# OR
kill -TERM $(pgrep -f 'hermes.*--profile <profile>.*gateway')

# 3. Start with the env explicitly exported
set -a; source ~/.hermes/profiles/<profile>/.env; set +a
nohup hermes --profile <profile> gateway run >/var/log/hermes-<profile>.log 2>&1 &
# OR use systemd / docker restart that already sources the env

# 4. Verify the new process has the key
sleep 5
PID=$(pgrep -f 'hermes.*--profile <profile>.*gateway' | head -1)
tr '\0' '\n' < /proc/$PID/environ | grep MINIMAX_API_KEY

# 5. Smoke-test a vision call
hermes --profile <profile> -z "Use vision_analyze to look at /home/ubuntu/.hermes/profiles/orchestrator/cache/screenshots/browser_screenshot_a46b1d2296dc4738b0640fe7f965ae6c.png and tell me what H1 it shows" -t vision
```

A successful smoke test returns `success: true` and a model answer referencing "Eating Your Way from Windward Oahu to the North Shore" as the H1.

## Prevention

1. **Gateway start script** (in hermes CLI or system service) should always `set -a; source ~/.hermes/profiles/<profile>/.env; set +a` before exec.
2. **Systemd unit** should have `EnvironmentFile=/home/ubuntu/.hermes/profiles/%i/.env` directive.
3. **Docker compose** should use `env_file:` directive pointing at the profile's .env.
4. **Doctor check** — `hermes doctor` should fail when a gateway process lacks any api_key_env in its /proc env. Currently it only checks connectivity, not env propagation.

## Risks

- Restarting `kai`, `ned`, `autobot`, `next-step` may interrupt in-progress background work. Schedule for next idle window.
- Restarting `orchestrator` ends THIS conversation. Only do it after user acknowledges or accepts the break.
- Some profile's `.env` may have **incomplete** api keys (different from missing). Detection command should check `wc -c` per key, not just presence.

## Out of scope

- Migrating vision provider away from MiniMax (separate decision — costs vs latency vs privacy).
- Adding new vision providers (OpenAI gpt-5-vision, Anthropic Claude Sonnet vision, etc.).
- Refactoring hermes' auxiliary client to read .env per-call instead of at startup (separate refactor with backward-compat implications).

## Related

- GRO-2483 — this work (created)
- GRO-2472 — AOT snorkel funnel restore (where this was first noticed)
- GRO-2476 — AOT style fix (where captions were needed but failed)
- `/home/ubuntu/.hermes/profiles/orchestrator/logs/errors.log` — vision error stream
- `/home/ubuntu/.hermes/profiles/orchestrator/.env` — source of truth for MINIMAX_API_KEY

## Verification artifacts

- Screenshot: `/home/ubuntu/.hermes/profiles/orchestrator/cache/screenshots/browser_screenshot_a46b1d2296dc4738b0640fe7f965ae6c.png`
- Caption (via direct MiniMax-M3 call): confirms H1 "Eating Your Way from Windward Oahu to the North Shore"
- Direct MiniMax-M3 call (Python `urllib.request`) succeeds with 200 OK using same key — proves key is valid, env propagation is the only issue.