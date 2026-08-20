---
name: headless-cli-oauth-login
category: devops
description: Use when authenticating a CLI tool on a headless Linux server (no browser, no GUI) that supports OAuth. Covers the loopback-redirect + --callback-url resume pattern used by zapier-sdk, gcloud, gh, aws sso, stripe, and similar CLIs. Includes pitfalls for backgrounded stdout buffering, the "CLI exits cleanly after printing URL" trap, and how to surface the authorization URL reliably.
---

# Headless CLI OAuth Login

When a CLI needs OAuth login but you're on a headless server (no browser), the standard pattern is:

1. CLI prints an authorization URL.
2. User opens URL in a **local browser** (not the server).
3. User pastes the **final loopback callback URL** back to the terminal.
4. CLI exchanges the code for a token and saves credentials locally.

The trick is that the CLI does **not** hold a background process open waiting for the callback. It prints the URL and exits. The callback resume is a separate invocation using a `--callback-url <url>` flag.

This applies to, among others:
- `zapier-sdk` (`@zapier/zapier-sdk-cli`)
- `gcloud auth login --no-launch-browser`
- `gh auth login --web` (then resume with `gh auth login --with-token` for PAT, or accept callback for OAuth)
- `aws sso login` (uses `--use-device-code` style variant)
- `stripe login` (opens `https://dashboard.stripe.com/setup/.../vR3fSxxxx`)

## When to use this skill

- A user pastes a `*sdk login --non-interactive --headless`-style instruction.
- A CLI needs authentication but the server has no GUI.
- You need to relay an authorization URL to a user and then resume once they paste the callback.

### When the user pastes a step-by-step instruction from another model (Gemini, Claude, GPT, etc.)

If the user hands you a numbered checklist from another model — "TASK: Authenticate X, then do steps 1..4" — **do not execute it verbatim.** Read this skill first (it's why you load it). Common drift between pasted instructions and reality:

- The pasted flags may be wrong or use a deprecated CLI syntax. This skill's `npx -y <pkg>` patterns are the canonical ones.
- The pasted step ordering may bury a pitfall (e.g. "if a step times out, re-run with `--timeout 600`") that this skill already documents as a built-in flag.
- The pasted instruction may omit the `stdbuf -oL -eL` wrapper that this skill carries — without it, backgrounded stdout buffers indefinitely and the agent concludes the CLI is hung.

The pattern: load this skill → cross-reference the pasted instruction against the skill's numbered steps → use the skill's command shape, even if the pasted prompt says something subtly different. Only diverge from the skill if the user explicitly directs you to.

## Core workflow

### 1. Verify prerequisites first

- Confirm Node / Python / runtime is available and at the version the CLI requires.
- Confirm the CLI is reachable (global `which` or `npx -y <pkg>`).
- If it must be globally installed, prefer `npx -y <pkg>` over `npm install -g` to avoid `EACCES` permission issues on shared hosts.

### 2. Kick off the headless login — unbuffered + short polling

```bash
# stdbuf -oL -eL forces line-buffered stdout/stderr so the URL
# appears in process(action='log') immediately, not after the CLI exits.
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli login --non-interactive --headless --timeout 600 --name "<label>" 2>&1
```

Run as a **background process** (`background=true`, `notify_on_complete=true`).

**Critical pitfall:** do NOT just `process(action='poll')` and wait forever for "output_preview" to show non-empty. Many CLIs buffer stdout under stdin-not-a-tty detection and only flush at exit. If polling shows empty output but the process is alive, call `process(action='wait', timeout=30)` to force a flush, then `process(action='log')` to read.

### 3. After the URL prints

The CLI will exit **cleanly (exit code 0)** after printing the URL. **This is normal.** It is not waiting for input — the script is done until the user returns a callback URL.

Extract from the output:
- The authorization URL (printed as `Open this login URL in a browser to continue:`).
- The expected `state` parameter (printed or embedded in the URL — verify the user pasted it back unchanged).
- The expected `redirect_uri` (usually `http://localhost:<port>/oauth` — this is a **loopback** on the server, not the user's machine; the browser will fail to load it, but the URL with the `code=` param will be visible in the address bar).

Relay to the user, including:
1. The full URL (clickable).
2. The expected redirect URL shape so they know what to look for.
3. The instruction to copy the **full address-bar URL** including the `code=` and `state=` params, even if the browser shows a "site can't be reached" error.
4. A warning that if the `state` parameter doesn't match what the CLI printed, the token exchange will fail and the flow must be re-initiated.

## Step 4 — Resume with `--callback-url`

## Step 5 — Verification (live 2026-07-29)

```bash
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli list-connections --json 2>&1
# + ls -la ~/.zapier   # credential artifact check
```

The 2026-07-29 run returned 2 active connections (Google Calendar `mbgulden@gmail.com`, WooCommerce `tikitiki.com`) with both `is_stale=false` and `is_expired=false`. The `errors[]` array in the JSON was empty — that's the real connectivity proof; exit code 0 alone is not sufficient (per `ad-hoc-verification-contracts`).

The full procedure is also captured in the project OKF as a runbook entry:

- `active-oahu-tours-mirror-2529/okf/ops-runbook/zapier-cli-headless-login.md` — verified at the project level, with bidirectional Linear cross-references (GRO-4373..4376).

**Critical pitfall:** the `--callback-url` flag requires a fully-qualified URL. The user almost always pastes the URL **without** the `http://` scheme (because the browser stripped it from the address bar display in some setups, or they just typed the hostname). If you re-run with `localhost:49505/oauth?...` the CLI rejects with:

```
❌ Error: Expected the final OAuth callback URL to start with http://localhost:49505/oauth.
```

**Fix:** prepend `http://` yourself before re-running. Do not ask the user to re-paste — they hit the paste button, verified the page, and moved on; you have all the inputs to fix it. Verified on `zapier-sdk login --callback-url` 2026-07-29. Other CLIs (gcloud, gh, aws sso) may have different scheme requirements — check the CLI's `--help`, but most follow the same "fully-qualified URL" rule.

Success output (2026-07-29 verified):

```
Exchanging authorization code for tokens...
👤 Logged in as michael@growthwebdev.com

Generating credentials so this machine can make authenticated requests on your behalf.
✅ Credentials "ned-headless" created and set as default. You are ready to use the Zapier SDK.
```

Watch for:
- Exit code 0.
- A success message naming the credential profile (e.g. `Saved credentials as "ned-headless"`).
- Any error referencing `state mismatch`, `invalid code`, or `expired` — all mean re-initiate.

### 5. Verify the credentials landed

Two independent checks:

```bash
# A. CLI-level: ask the CLI to list connections
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli list-connections --json 2>&1

# B. Filesystem-level: confirm the credential file exists with recent mtime
ls -la ~/.zapier  # or ~/.config/zapier, ~/.cache/zapier — check the CLI's docs
find ~ -maxdepth 4 -name "credentials.json" -path "*zapier*" 2>/dev/null
```

Exit code 0 is **not** proof. Verify the credential file exists and is non-empty (see `scripts/check-headless-login-artifacts.sh`).

## Pitfalls

| Pitfall | What goes wrong | Fix |
|---|---|---|
| **Stdout buffering in background** | `process(action='poll')` shows empty output forever; CLI is alive but silent. | Use `stdbuf -oL -eL` wrapping. Or call `process(action='wait', timeout=30)` to force flush. |
| **Assuming the CLI is awaiting input** | Agent waits "for the callback" indefinitely; the CLI actually exited clean after printing the URL. | Check `process(action='poll')` `status` — if `exited`, the CLI is done. Resume with `--callback-url`. |
| **Redirect to localhost fails, user panics** | User sees browser "site can't be reached" on `localhost:49505` and abandons the flow. | Pre-empt this in the user-facing message: explain the loopback is on the server, the URL with `code=` is still valid, just copy it. |
| **`state` mismatch** | User pastes a callback URL from a stale browser tab or a different OAuth flow. | The CLI will reject it. Re-initiate the login and tell the user to use the fresh URL. |
| **Global install fails with `EACCES`** | `npm install -g` on a shared server. | Fall back to `npx -y <pkg>` for every invocation. |
| **Trusting exit code 0** | CLI exits 0 but the credential file doesn't exist. | Verify with `ls/find` or `scripts/check-headless-login-artifacts.sh`. |
| **Not setting `--name`** | Default profile name is `<email>@<hostname>` and may prompt interactively. | Pass `--name "<label>"` upfront to keep the flow non-interactive. |
| **`--callback-url` requires a fully-qualified URL** | The user pastes `localhost:49505/oauth?code=...&state=...` (no scheme); the CLI rejects with `❌ Error: Expected the final OAuth callback URL to start with http://localhost:49505/oauth`. | Prepend `http://` yourself before re-running. Don't ask the user to re-paste — they hit the paste button, verified the page, and moved on; you have all the inputs to fix it. Verified on `zapier-sdk login --callback-url` 2026-07-29. Other CLIs (gcloud, gh, aws sso) may have different scheme requirements — most follow the same "fully-qualified URL" rule. |
| **Background process is still alive while the CLI is actually done** | Agent waits for the callback on a sleeping background process; the CLI printed the URL and exited clean long ago. | After the auth-URL prints, the CLI is typically done. Do not `process(action='wait')` forever — check `process(action='poll')` `status` for `exited`; if `running`, the CLI is genuinely hung (rare). The Zapier CLI exits 0 within ~5s of printing the URL. |

## Naming conventions

- `--name` label: prefer `<purpose>-<host>` (e.g. `kpi-publisher-ubuntu`, `cf-access-prod-pve6`). Avoid spaces and emoji.
- Timeout: default 300s is usually fine; bump to 600s if the user is slow on the browser side.

## Support files

- `references/zapier-sdk-cli-example.md` — full worked transcript of a real headless login with output snippets, the exact failure modes hit, and the resolution.
- `scripts/check-headless-login-artifacts.sh` — deterministic post-login artifact check (credential file present, non-zero size, mtime within last 5 min, JSON-parseable if applicable).
