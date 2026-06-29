---
type: Standards
title: Agent Dispatch Architecture — Current State, Lanes, Failure Modes, and Target
description: Authoritative description of how agent dispatch currently works in the Prismatic Engine / Hermes Agent system (June 2026), the bugs and gaps, the lane model that exists in labels but not in code, and the target architecture. Required reading for anyone wiring new agents, debugging missed pickups, or designing the next dispatch layer.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/agent-dispatch-architecture.md
tags: [standards, dispatch, agents, lanes, prismatic-engine, architecture]
timestamp: 2026-06-23T05:00:00Z
linear_issue: TBD
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/agent-dispatch-architecture.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Agent Dispatch Architecture — Standards

> **Purpose:** Document the *actual* state of the agent dispatch system so:
> 1. New agents can be added correctly.
> 2. Missed pickups are debugged in the right place.
> 3. Future agents / future-Michael can read this cold and understand the system.
> 4. The gap between "what it is" and "what it should be" is explicit and actionable.
>
> **Scope:** AGY (worker), Ned (audit/review), Kai (specialist), Fred (orchestrator). Plus the `agent:*` label catalog and the dispatcher scripts that read them.

---

## 1. The Six Facts You Need to Know First

These are the load-bearing facts. Everything else is detail.

1. **The only dispatch dimension that works today is the `agent:*` label.** A Linear issue gets routed to an agent because the dispatcher script filters on `labels: {name: {in: ["agent:agy", "agent:agy-pro", ...]}}`. Nothing else — not priority, not project, not state, not due date, not the agent's `assignee` field — is read by any dispatcher.

2. **There are three dispatcher scripts, and only one works.**
   - **AGY Sandbox Supervisor** (`/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_supervisor.py` + `agy_sandbox_supervisor_cron.sh`): working. Polls Linear for `agent:agy*` issues, runs them through bounded sandbox pool, returns RESULT.md.
   - **Ned Delta Dispatcher** (`ned_delta_dispatcher.py`): broken. `--model claude-sonnet-4.6-thinking` is invalid, so every invocation returns "Error: timed out waiting for response" immediately. Exits 0, no work done.
   - **Kai Delta Dispatcher** (`kai_delta_dispatcher.py`): broken. Same bug, same symptom.

3. **All three dispatchers have the same broken model name hardcoded.** It's the same value (`claude-sonnet-4.6-thinking`). The AGY supervisor gets away with it because it has a fallback path; Ned and Kai don't. **All three need to be migrated to a valid model string.**

4. **Ned and Kai have `subprocess.run(timeout=None)`**, which means when their broken AGY calls fail, the dispatcher hangs forever (or until cron SIGKILLs it). This is a second bug stacked on top of the model-name bug.

5. **The "lanes" concept exists only as labels.** The `lane:*` system (per-agent workdir, per-agent skill bundles, per-agent queue depth) does not exist in code. There are 5 workdir shortcuts hardcoded in the AGY supervisor (`darius`, `active-oahu`, `prismatic`, `agentic`, `hd-platform`) but no per-agent mapping. Other agents (Ned, Kai) use absolute paths.

6. **Priority is metadata, not a signal.** The AGY supervisor does `first: 50` ordering, no priority sort. The Nightly Backlog Routing Watchdog cron does look at priority, but only to decide *whether* to route, not to decide *when* the worker picks it up.

---

## 2. The Agent Roster (as of 2026-06-23)

| Agent | Labels | Profile | Workdir (if known) | Dispatcher | Status |
|---|---|---|---|---|---|
| **Fred** | `agent:fred`, `agent:orchestrator` | orchestrator | n/a — Fred IS the orchestrator | self | active |
| **AGY** | `agent:agy`, `agent:agy-pro`, `agent:agy-flash-high`, `agent:agy-gemini-pro`, `agent:agy-gpt-oss`, `agent:agy-opus`, `agent:agy-sonnet`, `agent:agy-thinking`, `agent:antigravity-cli` | agy | `~/work/prismatic-engine` (default) + 5 shortcuts | `agy_sandbox_supervisor.py` | **active** |
| **Ned** | `agent:ned`, `agent:ned-code`, `agent:ned-infra`, `agent:ned-audit`, `agent:ned-review` | ned | varies by lane | `ned_delta_dispatcher.py` | **broken — invalid model + no timeout** |
| **Kai** | `agent:kai`, `agent:kai-content`, `agent:kai-css`, `agent:kai-js` | kai | `~/work/active-oahu-static` | `kai_delta_dispatcher.py` | **broken — invalid model + no timeout** |
| **Hermes** | `agent:hermes`, `agent:local-hermes` | n/a | n/a | (research/scheduler layer) | n/a |
| **Jules CLI** | `agent:jules` | n/a | varies | (Jules CLI is a separate process) | separate |
| **Codex** | `agent:codex` | codex-5-5 | varies | (Codex CLI is a separate process) | separate |
| **Becca** | n/a (Becca has no agent label) | becca | n/a | n/a | n/a |

---

## 3. The Dispatcher Scripts — How They Actually Work

### 3.1 AGY Sandbox Supervisor — the only working one

**File:** `/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_supervisor.py`
**Cron wrapper:** `agy_sandbox_supervisor_cron.sh`
**Triggered by:** the AGY Sandbox Supervisor cron job (`faf8d91da716`, every ~15 min)

**Flow:**
1. Query Linear: `issues(filter: {labels: {name: {eq: "agent:agy"}}}, first: 50)`. **Hardcoded label** — no `agent:agy-pro`, no `agent:agy-flash-high`, etc. Pro-tier work gets picked up by the same pool unless extra labels are present.
2. For each issue, resolve workdir from the 5 `WORKSPACE_RULES` shortcuts (`darius`, `active-oahu`, `prismatic`, `agentic`, `hd-platform`). If the issue references an unknown workdir, defaults to `prismatic`.
3. Create an ephemeral sandbox at `/tmp/agy_sandboxes/<issue_id>/` (tmpfs if mounted, disk otherwise). Try warm cache → shallow git clone → rsync fallback.
4. Write the issue's description into the sandbox as `AGY_TASK.md`.
5. Launch AGY via `agy --model <DEFAULT_MODEL> --sandbox ...`. The model is parameterized but defaults to `claude-sonnet-4.6-thinking` (the broken value).
6. Bounded pool: max 2 concurrent. 5-15s jitter between launches. 8s backoff after each completion.
7. After AGY exits, check log for `DONE:` marker, log size, `timed out waiting for response`, `please clarify`.
8. Write result to `/tmp/agy_sandbox_results/<issue_id>/` and post a webhook back to Linear.

**Known issues (AGY supervisor):**
- Hardcoded model name needs migration.
- The label filter only matches `agent:agy` — `agent:agy-pro` issues are silently ignored unless they ALSO have `agent:agy` (which they don't by convention).
- `WORKSPACE_RULES` is a hardcoded dict, not a config file. Adding a new workdir requires editing the script.
- `first: 50` cap means if there are 51+ `agent:agy` issues, the 51st+ are invisible to the dispatcher.
- Priority is not sorted. (Confirmed by reading `fetch_linear_issues` — no `orderBy` on the query.)
- Ghost-stuck rate is ~33% (per skill memory: "AGY dispatch 2026-06-23: ... ghost-stuck rate ~33%").
- No heartbeat during AGY run — the only signal is the final `DONE:` check after the session ends. AGY can hang for 5+ minutes before anyone knows.

### 3.2 Ned Delta Dispatcher — broken

**File:** `/home/ubuntu/.hermes/profiles/orchestrator/scripts/ned_delta_dispatcher.py`
**Triggered by:** Ned delta cron (every 15 min)

**Flow (intended):**
1. Query Linear: `issues(filter: {state: {type: {in: ["todo", "inProgress", "backlog"]}}, labels: {name: {in: ["agent:ned", "agent:ned-code", "agent:ned-infra", "agent:ned-audit", "agent:ned-review"]}}}, first: 20, orderBy: updatedAt)`. **Better filter than AGY's** — supports all Ned labels, sorts by updatedAt, no 50-cap.
2. If no issues → `exit_silent` (zero tokens, zero output). Token-saving design.
3. If issues found → invoke AGY CLI to do decomposition + execution.

**Bug 1:** Line 195: `cmd = ["agy", "--model", "claude-sonnet-4.6-thinking", ...]`. Invalid model. AGY returns "Error: timed out waiting for response" immediately. Exit code from the subprocess is non-zero, so the function returns `False`. The dispatcher exits "clean" with no work done. Output looks fine in cron logs because the script handles the failure gracefully.

**Bug 2:** Line 201: `subprocess.run(cmd, ..., timeout=None)`. No timeout. When the model name is fixed and AGY hangs (which it will, because of the sandbox-supervisor's own 5-min cap or a network stall), the cron wrapper waits indefinitely until the OS kills it.

**Why it looks like it works:** The cron is `no_agent=True` and writes a 165-byte log file on every run. So `cron/output/<job_id>/` shows fresh timestamps, the cron appears "active," and the failure is invisible. This is a false-positive-green.

### 3.3 Kai Delta Dispatcher — broken (same shape)

Identical bugs to Ned's. Uses `--add-dir /home/ubuntu/work/active-oahu-static` instead of darius-star.

---

## 4. The Label Catalog (current state)

Verified live on 2026-06-23 from the GrowthWebDev team's label list.

### Agent routing labels (load-bearing)
- `agent:fred` — Fred / orchestrator
- `agent:agy` — AGY normal work
- `agent:agy-pro` — AGY review-grade (slower, more thorough)
- `agent:agy-flash-high`, `agent:agy-gemini-pro`, `agent:agy-gpt-oss`, `agent:agy-opus`, `agent:agy-sonnet`, `agent:agy-thinking` — model overrides
- `agent:antigravity-cli` — direct AGY CLI work
- `agent:autobot` — autobot/Telegram relay
- `agent:codex` — Codex CLI
- `agent:done` — terminal completion marker
- `agent:hermes`, `agent:local-hermes` — Hermes (research)
- `agent:jules` — Jules CLI
- `agent:ned`, `agent:ned-code`, `agent:ned-infra`, `agent:ned-audit`, `agent:ned-review` — Ned lanes
- `agent:orchestrator` — Fred
- `agent:qwen-local` — Qwen local

### Pipeline labels (informational, not routing)
- `pipeline:backend-api`, `pipeline:bug-fix`, `pipeline:content-seo`, `pipeline:research-strategy`, `pipeline:simple`, `pipeline:visual-design`

### Type labels (informational, not routing)
- `type:docs`, `type:infra-readonly`, `type:observability`, `type:port`, `type:pricing`, `type:resale`, `type:research`, `type:safety`, `type:schema`

### Workflow labels
- `requires:human-approval` — human approval required

**Critical fact:** Pipeline and type labels are NOT read by any dispatcher. They're metadata. Some agents (AGY, Kai) may consider them when deciding what to do with a `agent:*` issue they picked up, but they don't trigger routing.

---

## 5. The Lane Gap — What's Missing

The skill `orchestrator-delegation-discipline` calls for a "lane" concept where each agent has a defined workdir, skill bundle, queue depth, and concurrency budget. The current system has *labels* for lanes (Ned has 5 lane labels, Kai has 4, AGY has 9 model-flavor labels) but the code path that honors lanes is missing.

**What a real lane would require:**

| Component | Current state | Target state |
|---|---|---|
| Workdir mapping | 5 hardcoded in AGY supervisor; absolute paths elsewhere | One config file: `~/.hermes/agent_lanes.yaml` with `{agent: {lane: {workdir, skills, max_concurrent, model}}}` |
| Skill bundle per lane | Not enforced; AGY loads skills from cron prompt; Ned/Kai don't load per-lane skills | Per-lane `skill_manifest.yaml` that AGY/agent CLI loads via `--skills` flag |
| Concurrency budget | AGY: hardcoded 2. Ned/Kai: 1 (no concurrency, single subprocess) | Per-lane `max_concurrent` from config |
| Priority sort | None on AGY; `updatedAt` on Ned (not priority) | Multi-key sort: priority ASC, then createdAt ASC, with `state: {name: {in: ["Todo", "Backlog"]}}` filter |
| Queue depth | None — `first: 50` cap is a cap, not a depth indicator | `queue_depth` metric per lane, posted via `agent_activity_telemetry.py` |
| Heartbeat | None on AGY (Tier 1 fix in GRO-2101, not yet landed) | Heartbeat every 60s while session runs, posted to Linear comment + heartbeat log file |
| Failure attribution | Mixed: ghost-stuck, timeout, model-invalid all look the same in logs | Per-failure-mode tag in Linear comment when dispatcher aborts |
| Lane observability | None | A `lanes` view in the morning digest: per lane, queue depth, oldest unstarted, last-completed |

**Where to start the build:** The first deliverable is `~/.hermes/agent_lanes.yaml` + a one-line change to AGY supervisor to read it. The config file is the source of truth; the dispatcher becomes a thin shell. After AGY reads it, port Ned and Kai to the same config (which also fixes the model bug, since the model string comes from the config).

---

## 6. Failure Modes — Catalog

These are the dispatch failure modes that have actually been observed (skill memory + recent sessions):

| Mode | Symptom | Root cause | Fix |
|---|---|---|---|
| **Ghost-stuck** | AGY exits 0, no `DONE:` line, no `RESULT.md` | AGY backend timeout during response wait; sandbox cleaned but work product missing | Tier 1 heartbeat fix (GRO-2101), post RESULT.md or kill |
| **Queue jam** | 5-min supervisor cap hits, lower-priority issues left unstarted while a stuck one holds the slot | Bounded pool + per-issue 5-min wall clock | GRO-2101 heartbeat + per-issue soft kill at 5min |
| **Broken dispatcher** | Ned/Kai crons run, log fresh timestamps, no work done | `--model claude-sonnet-4.6-thinking` invalid; Ned/Kai fall through to graceful exit | Migrate to valid model in config |
| **Hang forever** | Ned/Kai subprocess blocks indefinitely | `timeout=None` | Set `timeout=300` and graceful kill |
| **Cron sandbox env contamination** | `LINEAR_API_KEY` from cron sandbox subshell is the wrong one (multiple .env sources) | fork-time env inheritance picks the stub .env | Use absolute path `source $PRISMATIC_HOME/.hermes/profiles/orchestrator/.env` |
| **Auth error 401** | `(jq -Rs ...)` subshell picks up the wrong OAuth token from duplicated env vars | Same as above; subshell fork sees different env than parent | Use `write_file + curl -d @file` (Method C from `linear-label-and-state-ids` skill) |
| **Label ID drift** | `INPUT_ERROR: "labelIds contained an entry that could not be found"` | Hardcoded label ID became stale (e.g., `agent:done` was `d1bfb512-...` but became `a0fa6cec-...`) | Always query live label IDs before mutation; never hardcode |
| **Workdir fallthrough** | Issue silently dispatched with `prismatic` workdir when the work is actually for `active-oahu` | 5 hardcoded shortcuts; anything else falls through to default | Add a workdir resolution step: read `WORKDIR:` from AGY_TASK.md; if absent, ask |
| **Priority ignored** | P1 issue waits behind P3 issue, dispatcher processes in createdAt order | No `orderBy: priority` on the query | Add `orderBy: priority` + secondary `createdAt` |
| **State Drift** | Issue is `Done` in Linear but `RESULT.md` was never written | Comments posted + state changed but no artifact | Tier 1 verification gate: state cannot move to Done without `RESULT.md` present |

---

## 7. The Target Architecture

A clean version of what this should look like, in priority order:

### Tier 1 (this week)
- [ ] **Fix Ned and Kai dispatchers** — migrate `--model` to a valid string, set `timeout=300`, log failure mode explicitly. (3-line change each, but needs verification.)
- [ ] **Add priority sort to AGY supervisor** — change `first: 50` to `first: 50, orderBy: priority, state: {name: {in: ["Todo", "Backlog"]}}`. (One-line query change.)
- [ ] **Fix AGY supervisor label filter** — match ALL `agent:agy*` labels, not just `agent:agy`. (Use `name: {in: [...]}` with the full catalog.)
- [ ] **Add `agent:done` check on state transition** — refuse to move an issue to Done if no `RESULT.md`. (Per skill, 5-line guard in the promotion step.)

### Tier 2 (next week)
- [ ] **Stand up `agent_lanes.yaml`** — first version, AGY-only. (3 lanes: `agy-default`, `agy-pro`, `agy-flash`.)
- [ ] **Heartbeat during AGY session** — Tier 1 fix from GRO-2101, landed.
- [ ] **Lane observability** — per-lane queue depth in the morning digest.

### Tier 3 (this month)
- [ ] **Port Ned and Kai to the lane config** — both benefit from the same `timeout=300` and `--model` fix.
- [ ] **Per-lane concurrency budget** — Ned 2, Kai 2, AGY 2, all bounded by token pool.
- [ ] **Failure attribution tags** — Linear comment format `{result: done|ghost_stuck|timeout|auth_error|model_invalid, ts: ...}`.
- [ ] **Document the standard** — this doc, plus per-agent standards.

---

## 8. The "How Agents Should Work" Standard

This is the target contract for every agent in the system. Once we get here, the OKF doesn't have to be updated every time someone adds a new agent — the contract is the same.

### Input contract
- Agent picks up issues with its `agent:*` label(s) in `Todo` or `Backlog` state.
- Issue description contains: a published OKF doc URL (or local path), step-by-step instructions, acceptance criteria, and a verification command.
- Agent may NOT pick up issues with `requires:human-approval` label — those wait for Michael.

### Execution contract
- Agent works in its lane workdir (resolved from `WORKDIR:` hint in the issue or from `agent_lanes.yaml`).
- Agent uses its lane's skill bundle (or the default skills if no bundle).
- Agent honors its lane's concurrency budget.
- Agent posts a heartbeat comment to Linear at least every 5 minutes while working on a single issue.
- Agent writes `RESULT.md` (or per-lane equivalent) before exiting.
- Agent emits `DONE: GRO-<num> <one-line summary>` as the last line of output.

### Output contract
- Agent posts a single summary comment to Linear with: what changed, the verification command + output, the artifact path, and any deviations.
- Agent moves the issue to `Done` ONLY if `RESULT.md` exists.
- Agent swaps the `agent:*` label to `agent:done` (or removes it, depending on agent convention).
- Agent updates `~/work/agent-outputs/<agent>/<issue_id>/RESULT.md` so future agents can read what happened.

### Failure contract
- If the agent exits with no `DONE:` line: orchestrator flags as ghost-stuck and the issue is re-dispatched on the next tick.
- If the agent blocks more than 5 minutes without a heartbeat: Tier 1 kill + re-dispatch.
- If the agent returns 401 / 500 / auth errors: orchestrator pauses the lane, alerts Michael via autobot, waits for credential refresh.
- If the agent's model name is invalid: orchestrator writes a startup health check that catches this on first invocation and alerts immediately, rather than running silently.

### Observability contract
- Every agent exposes: queue depth, oldest unstarted issue, last-completed issue, current concurrency, token pool size.
- The morning digest includes per-lane: `lane | queued | running | done_24h | oldest_unstarted | last_completed`.

---

## 9. What This Doc Does NOT Cover

- AGY's own internal model selection (the `agent:agy-flash-high` etc. labels are AGY-internal routing, not Prismatic dispatch).
- Jules CLI / Codex CLI — these are external CLIs, not part of the Prismatic dispatcher.
- The autobot (Telegram relay) — that's a notification lane, not a work lane.
- Becca — no `agent:*` label, separate scheduling.
- Webhook-based dispatch (per memory: "Webhook: docs/linear-webhook-architecture. Webhook IS delivery. Do NOT propose polling"). The AGY supervisor polls; the webhook is the separate event-driven path. If/when that becomes primary, the polling supervisor can be demoted or removed.

---

## 10. Related OKF docs
- `~/work/growthwebdev-knowledge/okf/standards/` (this doc lives here)
- `~/work/growthwebdev-knowledge/okf/projects/active-oahu-tours.md` (AOT — the project that prompted this audit)
- `~/work/growthwebdev-knowledge/okf/projects/beyondsaas.md` (BeyondSaaS — used as the test bed for the OKF → Linear dispatch pattern)
- `~/work/growthwebdev-knowledge/okf/integrations/api-key-locations.md` (where all the keys are — also the orchestrator's first stop on auth errors)
- Skills: `orchestrator-delegation-discipline`, `linear-label-and-state-ids`, `okf-dispatch-pattern`, `antigravity-cli-orchestration`, `agy-execution-gauntlet`, `cron-token-optimization`

## 11. Change log
- 2026-06-23: Initial version (Fred). Triggered by Michael's callout during the AOT drift audit (GRO-2113 through GRO-2117) that the lane/priority/dimension system isn't actually implemented in the dispatchers, and that Ned and Kai are idle because their dispatchers are broken.
