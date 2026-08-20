---
name: agent-response-governance
description: Govern Hermes agent response speed, verification depth, result-link reporting, cross-profile preference rollout, and golden-path next-step behavior for Michael. Use when Michael critiques response slowness, result clarity, final report format, completion behavior, or asks to apply a behavioral preference across profiles.
triggers:
  - user complains responses are slow, over-verified, unclear, too procedural, or missing final links
  - user asks to apply a response/workflow preference to all profiles
  - completing a task/project/report for Michael where the final answer needs result links, verification, and next step
  - YOLO/autonomous mode is active and the agent must decide whether to continue after an increment
  - refreshing Hermes profile sessions/gateways to pick up behavior/memory changes
---

# Agent Response Governance

## Purpose
Keep Michael's agents fast for simple work and rigorous for operational work, without burying him in process noise. The expected output is a usable result: status, clickable artifact/result links, verification evidence, and a next step aligned to the goal's golden path.

## Response contract

### 1. Choose the right execution path first
Before using tools, classify the request:

| Request class | Default behavior |
|---|---|
| Conceptual/advisory/editorial | Answer directly first. Do not fan out tools unless live state is required. If relevant, state that live state was not inspected. |
| Live system/file/API/status question | Inspect the live source and report grounded evidence. |
| Build/fix/deploy/verify request | Use tools, perform the work, and verify the result before claiming done. |
| Ambiguous but low-risk | Take the obvious default and proceed. |
| Ambiguous with irreversible/destructive side effects | Ask or stop at the safety boundary. |

Pitfall: do not treat every request like a production incident. Over-verifying simple asks makes the system feel slow and hides the answer.

### 2. Put the result before the procedure
Final reports should lead with the outcome, not a transcript of effort.

Preferred structure:

```md
✅ Done: <plain-English result>

**Open it:** [Result/artifact link](https://...)

**Changed**
- ...

**Verified**
- `<command/check/API>` returned <short concrete result>

**Next Step**
<one concise next action aligned to the project's golden thread/golden path>
```

If blocked:

```md
🔴 Blocked: <specific blocker>

**Impact**
- ...

**Evidence**
- `<command/check/API>` returned `<exact short error/status>`

**Needed**
- <specific action/input/permission needed>

**Next Step**
<best safe next move aligned to the golden path>
```

### 3. Always surface final product links
When work produces or touches something Michael should inspect, include the clickable result/artifact link. Examples:

| Artifact | Link/report requirement |
|---|---|
| Linear issue | Markdown link to the issue/dashboard URL |
| PR | GitHub PR URL |
| Deployment | Live deployed URL and/or deployment URL |
| Workspace file | Workspace-tree link when applicable |
| Generated media/file | `MEDIA:/absolute/path` or direct artifact URL |
| Cron/job | Job name, ID, schedule, and delivery target |
| Dashboard/status page | Direct dashboard URL |

Pitfall: “updated the config” is not enough. Michael should not have to ask where the result is.

### 4. Verification evidence must be scoped and readable
For operational work, report what was actually verified and the scope of that verification. If the platform asks for a fresh ad-hoc verifier, include the verifier result **and** a short human-language outcome recap: what changed, whether it actually happened, and what remains.

Good:
- `npm test -- --runInBand` passed, 42 tests.
- Live URL returned HTTP 200.
- `systemctl is-active ned-gateway.service` returned `active`.

Bad:
- “Looks good.”
- Long raw logs without a summary.
- A procedural narrative with no outcome.

### 5. Next Step / golden path rule
Every completed task/project/report should include a **Next Step** section. It should name the next action that best aligns with the specific project/task/goal vision — the golden thread/golden path — not a generic TODO.

If YOLO mode is active:
1. Complete the current increment.
2. Report only if useful or required.
3. Continue along the next-step path when the next action is safe, reversible, and within scope.
4. Stop at irreversible/destructive actions, missing credentials, unclear priority, or a scope boundary.

Pitfall: do not become complacent after one completed increment when the user explicitly requested ongoing YOLO execution.
## Cross-profile preference rollout

When Michael asks to apply a durable response/workflow preference across all profiles:

### Task pickup / completion reporting repair

When Michael says a profile is not responding when he sends a task, or not reporting back when a task finishes, treat that as a response-contract failure, not a cosmetic preference.

Required checks and fixes:

1. Inspect the profile's autonomous cron/job delivery target. If the worker is meant to report to Michael, `deliver` must not be `local`; use `origin` unless he explicitly asked for local-only behavior.
2. Inspect the autonomous prompt/instructions, not just memory. The prompt must explicitly require:
   - a brief pickup acknowledgement when a real task is claimed, and
   - a concise completion report with evidence when the task finishes.
3. Verify the fix by reading back the cron/job definition after updating it; do not assume the mutation stuck.
4. Update the governing skill/memory so future task-handling sessions inherit the behavior.
5. If a live gateway/session restart is needed to pick up the new behavior, arrange it from outside the running gateway/session process and report that boundary honestly.

Pitfall: fixing only memory is insufficient when the autonomous worker runs from a self-contained cron prompt or script. The delivery target and prompt contract are the durable levers.

When Michael asks to apply a durable response/workflow preference across all profiles:

1. Add the preference to each profile's `memories/USER.md` as a concise declarative preference.
2. Avoid bloating memory with task-specific artifacts, PR numbers, or transient errors.
3. Back up existing `USER.md` before bulk edits when practical.
4. Verify every detected profile contains the entry.
5. Tell Michael whether existing sessions/gateways need refresh to pick it up.
6. If asked to do the next step, refresh active sessions/gateways safely and verify status.

When a profile-audit cron reports cross-profile response-contract warnings:

1. Inspect the cron artifact and run the underlying audit directly to expose full warning context.
2. Patch only the affected `memories/USER.md` files with the missing durable preference snippets.
3. Re-run the audit until warnings/critical are zero.
4. If the watchdog alert hid the warning details, harden its output filter so future alerts include `[WARN]`, `current:`, and `recommended:` lines.
5. Run the watchdog smoke test and manual cron job; healthy script-only watchdogs should return silent output.

## Hermes OAuth model/provider adjustments

When Michael asks whether a newer GPT/Codex model can be used through Hermes OAuth, verify the provider/model before changing defaults:

1. Check `hermes auth list`/provider status without reading token files or exposing OAuth secrets.
2. Run an explicit one-shot probe with `--provider openai-codex -m <model>` before editing config.
3. Use `hermes config set`, not direct file patch/write, for security-sensitive Hermes config changes.
4. Update primary `model.default` plus existing auxiliary model slots that already use the same provider/base URL; do not invent unknown auxiliary sections.
5. Validate YAML, run a default one-shot probe, and run the profile audit when available.
6. Tell Michael existing warm Telegram/gateway sessions may stay pinned until a new session or gateway reload.

See `references/2026-07-openai-codex-oauth-model-switch.md` for the observed `openai-codex` → `gpt-5.6` OAuth switch workflow and verification commands.

## Hermes goal-turn/config adjustments
When Michael asks to change Hermes goal/agent turn limits, use the installed CLI shape rather than assuming a `get` subcommand exists:

```bash
hermes config set goals.max_turns 90
hermes config show
```

Then verify the active profile file directly, e.g. `/home/ubuntu/.hermes/profiles/ned/config.yaml`, confirming both relevant keys when present:

```text
agent.max_turns = 90
goals.max_turns = 90
```

Pitfall: `hermes config get ...` may not exist in this install; valid observed subcommands were `show`, `edit`, `set`, `path`, `env-path`, `check`, and `migrate`. If the dedicated `hermes-agent` skill is unavailable in this profile, proceed with live CLI discovery and report that explicitly.

## Hermes session/gateway refresh guidance
New chats usually pick up updated memory automatically. Existing warm sessions may need `/new` or a gateway/session restart.

When refreshing gateways:
- Prefer restarting only affected active profile gateways, not the whole machine.
- Verify with service status and process start times.
- If restarting the current gateway, schedule or launch the restart from outside the running gateway process, then arrange a follow-up verification report.
- If a systemd unit is crash-looping with “gateway already running,” check for a manually launched gateway for the same profile. Patch the supervised unit to use `gateway run --replace` only when service ownership is intended, then reload/enable the unit outside the live gateway turn.

### Profile response-delivery audits
When Michael says a profile does not respond to tasks or completion reports, audit the whole chain before treating it as a style-only issue:
1. Check the profile config, gateway state, channel directory, gateway logs, cron jobs, and service status.
2. Probe the configured model with a bounded one-shot command; authenticated models can still silently hang.
3. Check cron delivery targets. Autonomous task loops that use `deliver: local` will complete silently; switch task/completion jobs that Michael should see to `deliver: origin` and patch their prompt to acknowledge task pickup plus final completion.
4. Verify with the profile audit script and a default one-shot model probe before claiming fixed.

Reference: `references/2026-07-ned-profile-response-delivery-audit.md`.

See session references for concrete examples:

- `references/2026-07-response-speed-result-links-next-step.md` — original response-speed/result-link correction that created this skill.
- `references/2026-07-cross-profile-refresh-and-watchdog.md` — cross-profile rollout, safe gateway refresh via external `systemd-run`, Fred refresh, and watchdog hardening pattern.
- `references/2026-07-profile-audit-warning-triage.md` — profile-audit cron warning triage, cross-profile response-contract memory repair, and watchdog grep/output hardening.

## Quality bar
A good final answer for Michael is:
- brief by default
- result-first
- link-rich
- verification-backed when needed
- honest about blockers
- includes a golden-path Next Step
- continues autonomously only when YOLO mode and safety boundaries allow it
