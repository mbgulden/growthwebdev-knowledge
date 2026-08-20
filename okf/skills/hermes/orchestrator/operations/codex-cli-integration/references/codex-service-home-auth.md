---
name: codex-service-home-auth
description: Verify Codex CLI auth boundary before any auth-related decision; the auth file lives under the service HOME, not a universal ~/.codex.
type: reference
---

# Codex service-HOME and auth boundary

A Prism atic Engine dispatch service runs under a specific service HOME. Codex CLI resolves its auth file under that HOME, NOT a universal `~/.codex/auth.json`. Treat auth as **per-service**, not per-host.

## What the verifier shows

`codex doctor --json` (run from the service's HOME) reports:

```json
"auth.credentials": {
  "id": "auth.credentials",
  "category": "auth",
  "status": "fail",
  "summary": "no Codex credentials were found",
  "details": {
    "auth file": "/home/ubuntu/.hermes/profiles/fred/home/.codex/auth.json",
    "auth storage mode": "File"
  },
  "remediation": "Run codex login or provide an API key through a supported auth env var."
}
```

The `auth file` field is the source of truth. **Do not assume** `~/.codex/auth.json`.

## How to verify before any auth-related decision

```bash
# 1. Confirm the service HOME you intend to dispatch from
echo "HOME=$HOME"

# 2. Confirm Codex resolves auth under that HOME
codex doctor --json | jq '.checks.auth.credentials.details."auth file"'

# 3. Confirm the file exists (or doesn't) at the resolved path
ls -la "$(codex doctor --json | jq -r '.checks.auth.credentials.details."auth file"')" 2>&1 | head -3
```

If the resolved auth file's parent directory does not exist, Codex will create it lazily. Verify the parent is writable and owned by the service account, not by another profile's account.

## Why this matters

- **Credential reuse across services is unsafe.** The Hermes `george` profile, the Hermes `fred` profile, and a hypothetical `pe-dispatch` service each have their own `~/.codex/auth.json`. Copying credentials from one to another is a security violation; the live CLI will also bind each auth file to a distinct OpenAI account or subscription.
- **A wrong HOME breaks dispatches silently.** A lane that assumes `~/.codex/auth.json` will produce `401 Unauthorized` against `wss://api.openai.com/v1/responses` even after `codex login` ran successfully under the actual service HOME. Verify auth file path before debugging 401s.
- **Lane code must pin `HOME`.** When the lane shells out to `/usr/bin/codex`, it should set `env={**os.environ, "HOME": "<service-home>"}` explicitly, OR rely on the OS-level HOME of the dispatch process. Document which one it does.

## Auth decision workflow

The auth ownership decision is **operator-side**, not code-side. The lane never logs in. The flow:

1. **Operator** chooses the PE service account (e.g., a dedicated `pe-dispatch@` ChatGPT account, separate from Michael's personal or `george` accounts).
2. **Operator** ensures the service HOME has the desired HOME layout (e.g., `/home/ubuntu/.hermes/profiles/pe-dispatch/home/` for a Hermes-managed service HOME).
3. **Operator** runs `codex login` from that HOME (browser-mediated flow, requires human).
4. **Lane** verifies `codex doctor --json` reports `auth.credentials.status == ok` BEFORE dispatch. If `fail`, refuse dispatch + surface to Linear as `dispatch:blocked` + `agent:needs-human-review`.
5. **Lane** always reads the actual auth-file path from `codex doctor --json`, not a hardcoded path.

## When auth changes

If the operator rotates auth (new ChatGPT login, new account, revoked token):

1. Operator performs `codex logout` + `codex login` under the service HOME.
2. Lane should re-run `codex doctor --json` before next dispatch.
3. If a dispatch in-flight receives 401 mid-stream, the lane should treat it as a transient auth break, not a model error; surface to Linear as `dispatch:blocked`; defer to the operator.

## Pitfalls

- Hardcoding `~/.codex/auth.json` in code or docs. Always resolve from `codex doctor --json` or `HOME` + canonical subpath.
- Assuming `codex login` happened because `~/.codex/` directory exists. The directory can exist without an auth file.
- Copying Hermes `codex-*` profile credentials into a service HOME. Each profile has its own auth boundary.
- Setting `HOME=/root` or `HOME=/home/ubuntu` in the lane subprocess without verifying where `codex doctor --json` then resolves auth. The auth file path shifts with HOME.
