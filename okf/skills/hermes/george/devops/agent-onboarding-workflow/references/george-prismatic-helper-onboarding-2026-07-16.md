# George Prismatic Helper Onboarding — 2026-07-16

## Class lesson

When creating a new helper agent to take over a coordination lane, do more than create the Telegram bot/profile. The agent needs role context, current handoff state, user preference seed, tool/access verification, and a durable gateway.

## What worked

- Created profile `george` cloned from Kai so George inherited the relevant model/tool/skill posture.
- Replaced the cloned Telegram token with George's own BotFather token in George's `.env` and kept the token out of final reports.
- Added `TELEGRAM_ALLOWED_USERS` and kept `GATEWAY_ALLOW_ALL_USERS=false`.
- Installed George as a systemd gateway service: `hermes-gateway-george.service`.
- Wrote a George `SOUL.md` describing the Prismatic helper/workflow guard role and explicitly excluding Active Oahu Tours ownership.
- Added a current handoff artifact: `PRISMATIC_CURRENT_HANDOFF.md`, then pointed George's SOUL to read it for current Prismatic runway context.
- Copied the updated onboarding skill into George's profile so he can onboard future agents.
- Verified safe bot identity with Telegram `getMe` while printing only non-secret fields.
- Verified George's enabled toolsets/skills and GitHub PR visibility before declaring him ready.

## Critical response pattern for new helper bots asking to profile Michael

If the new bot asks Michael whether it should build a working profile, provide Michael a paste-ready seed profile. Include:

- Michael prefers direct, operational answers.
- Lead with status, evidence, blockers, and exact next action.
- For build/deploy/live-system work, verify with tools before claiming completion.
- Keep verbose logs in files/artifacts; chat gets compact proof packets only.
- Distinguish ad-hoc targeted verification, GitHub CI, browser proof, production proof, and canonical full-suite green.
- Do not claim canonical full-suite green unless actually run.
- When Michael asks “is it done?”, answer yes/no directly, then evidence/caveats.
- Provide downloadable `.md` prompts for Fred/Ned/AGY when useful.
- Preserve existing good dashboard/product assets; do not reinvent unless explicitly requested.
- Never expose secrets.

## Readiness checklist

Before saying the new helper is fully ready, verify:

```text
profile exists
SOUL.md exists and names role/boundaries
.env has target bot token and allowlist
GATEWAY_ALLOW_ALL_USERS=false
Telegram getMe safe identity check passes
gateway running under systemd or an explicitly accepted long-lived process
toolsets needed for role are enabled
skills needed for role are enabled
repo/API access needed for role is verified read-only
current handoff artifact exists if the role has active work state
final report names what was not tested/mutated
```

## Pitfalls

- A newly cloned profile may inherit the source profile's bot token; replace it before starting the gateway.
- `telegram.allowed_chats` in config is not enough for DM authorization; set `TELEGRAM_ALLOWED_USERS` in `.env`.
- A bot can be running but deny everyone if no allowlist is configured and global allow-all is false.
- If a manual gateway was started first, systemd may briefly fail with “Gateway already running”; stop only the target gateway process and let the target service restart.
- A bot is not fully smoke-tested until Michael sends a message to it, because bots cannot initiate DMs to users who have not started them.
- Do not test destructive capabilities such as Linear mutation, Cloudflare mutation, PR merge, or deploy just to prove access; report these as untested until a real task needs them.

## Compact proof template

```text
COMMAND=profile/tool/access/gateway readiness checks
RESULT=PASS|FAIL|BLOCKED
LOG=/tmp/<agent>-success-readiness-verify.log
SCOPE=<agent> setup for <role>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=<mutations or user-side smoke not tested>
MARKER=<AGENT>_SUCCESS_SETUP_OK
```
