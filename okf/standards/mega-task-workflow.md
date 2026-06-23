---
type: Standards
title: Mega Task & Crazy Idea Workflow — Ingestion, Research, Planning, Golden-Path Execution
description: The workflow for ingesting "mega tasks" (multi-day, multi-agent projects) and "crazy ideas" (exploratory, undefined-scope concepts) from Michael. Defines the golden path from raw Telegram message to dispatched Linear issues, the research-and-planning discipline, the standards for how agents should approach these, the patterns that have worked in past mega projects, and the failure modes that have dropped features on the floor.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/mega-task-workflow.md
tags: [standards, mega-task, planning, ingestion, golden-path, orchestration, workflow]
timestamp: 2026-06-23T05:30:00Z
linear_issue: TBD
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/mega-task-workflow.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Mega Task & Crazy Idea Workflow

> **Purpose:** Document the workflow for handling "mega tasks" (multi-day, multi-agent projects with concrete deliverables) and "crazy ideas" (exploratory, undefined-scope concepts) that Michael drops into chat. This is the golden path from raw message → research → plan → dispatched issues → execution → done. It also captures what has worked in past mega projects, what fell short, what features were forgotten, and the inconsistencies that have caused rework.
>
> **When to load:** Whenever Michael says things like "I have a big project," "here's a crazy idea," "we need to do X," "let's tackle Y," or sends a multi-paragraph message that looks like it has 3+ deliverables. Also load when picking up a stale mega-project that was dispatched but never finished.

---

## 1. The Vocabulary

| Term | Definition | Example |
|---|---|---|
| **Mega task** | Multi-day, multi-agent project with concrete deliverables, deadlines (or "soon"), and rough scope. Michael knows what he wants; the orchestrator's job is to make it tractable. | "Get the meeting prep done — audit, pricing, deck, bio, case study, monitoring, systemd, plugin sync" (BeyondSaaS, 2026-06-22). |
| **Crazy idea** | Exploratory, undefined-scope concept. Michael isn't sure if it's feasible or what shape it should take. The orchestrator's job is to research, scope, and decide if it should become a mega task. | "What if we had a mega-app that ran all our agents from one dashboard?" (hypothetical). |
| **Mega project** | A Linear project (or OKF project bundle) that contains a mega task or a related family of mega tasks. The container, not the work. | `Active Oahu Tours — Static Mirror Migration`, `Beyond SaaS — Consulting Brand`, `Prismatic Engine`. |
| **Golden path** | The default dispatch + execution flow that a mega task should follow: OKF doc → research → Linear issues → labeled dispatch → AGY execution → peer review → Fred verify → Done. | See Section 6. |
| **Ingestion** | The 60-90 second triage that happens when a mega task lands: read it, classify it, ask the 1-2 disambiguating questions if needed, write the OKF scaffold. | Section 4. |
| **Planning spree** | The 15-30 minute synthesis after ingestion: research the existing state, scope the work, decompose into Linear issues, file them. | Section 5. |

---

## 2. The 6 Facts About How Mega Tasks Have Actually Gone (June 2026 evidence)

These are the load-bearing truths, grounded in real past projects. Everything in the golden path is a response to one of these.

1. **Michael's mega-task messages are 30% of the message and 100% of the scope.** The first 30% is the ask ("I have a big project"); the remaining 70% is implicit ("and you know what that means: research it, plan it, dispatch it, verify it, report back"). The orchestrator must absorb the whole arc, not just the literal text.

2. **Mega tasks always arrive with a 2-hour-or-2-day deadline signal.** Sometimes explicit ("meeting is in 45 min"), sometimes implicit ("I have a big project after that"). The orchestrator's first move is always to check the clock against the ask, then decide: build-in-parallel (dispatch to AGY + start Fred's own work), or hold-and-wait (let the dispatcher do it).

3. **Most mega tasks decompose into 5-12 sub-issues, not 50.** The BeyondSaaS push had 8 numbered sub-tasks (O1-O8) that mapped to ~12 Linear issues (GRO-2094 through GRO-2105). The AOT drift work had 9 vectors that mapped to 5 issues. The Darius Star rebuild had 40+ issues but they were 4 phases of 10 each — still grouped, not flat.

4. **One of the sub-issues will always need Michael.** Bio content, pricing signoff, decision between options, a credential, a "yes/no" on a meeting. The orchestrator's job is to identify WHICH one early (during ingestion) and surface it to Michael as a single, clean ask — not buried in the middle of a 10-step plan.

5. **The bottleneck is almost never the work; it's the verification + state reconciliation.** Every mega task so far has shipped 60-80% of the work but ended with Fred manually reconciling 2-5 issues in Linear (work was done, card wasn't moved, ghost-stuck AGY session needed a `RESULT.md`). The Tier 1 fix (GRO-2101 heartbeat) is the cure but isn't yet live in the supervisor.

6. **The OKF doc is the artifact that survives.** When the Linear issues are closed and the AGY sandboxes are wiped, the OKF doc is the only thing that says "we did this, here's how, here's what we learned." The audit/reports/decisions/procedures written in OKF during a mega task are 10x more valuable than the issues that got closed. Future agents read OKF, not Linear.

---

## 3. The 4 Failure Modes Mega Tasks Have Hit

| Mode | Real case | Root cause | Mitigation now codified |
|---|---|---|---|
| **Ghost-stuck agent** | BeyondSaaS: GRO-2099, GRO-2100, GRO-2103 all ghost-stuck at 33% rate (session-state doc). | AGY backend timeout; supervisor has no heartbeat; no `RESULT.md` written. | Tier 1 fix (GRO-2101) + reconciliation pattern. **Until heartbeat ships, expect 1-in-3 to ghost-stuck and budget time for Fred to manually reconcile.** |
| **Wrong lane routing** | AOT drift: I assigned CSS+JS work to AGY when `agent:ned-infra` or `agent:kai-css` was the right home. | Dispatcher has the lanes but they don't work (model bug per the dispatch architecture doc). | After GRO-2118 lands: re-label lane-specific work. For now: everything goes to AGY. |
| **Decomposed into the wrong shape** | Darius Star: 40+ issues created flat instead of grouped by phase. Engineer reads "fix sprite 12" without context. | The orchestrator dumped the scope into Linear without enough planning. | Section 5's planning discipline: always group into Phase 0/1/2, attach parent epic, title with `[Phase/Issue]` prefix. |
| **Forgotten Michael-decision** | BeyondSaaS: O2 (bio + case study) was filed as `agent:fred` then sat for 12 hours because it needed Michael to write content. | The orchestrator didn't surface the blocker until late. | Section 4's ingestion: name the Michael-decision in the first message, not buried in the plan. |

---

## 4. The Ingestion Phase (60-90 seconds)

When a mega task or crazy idea lands, the orchestrator does this **before** anything else. No research, no Linear, no agent work.

### 4.1 Read the whole thing

Don't pattern-match on the first sentence. The whole message is the ask. Copy it into a working file. Identify:
- The deliverable (what does "done" look like?)
- The deadline (when does it need to be done?)
- The constraints (budget, tech stack, audience, etc.)
- The implicit ask (what does Michael NOT say that he assumes?)

### 4.2 Classify it

Is this a **mega task** (concrete deliverables, defined scope) or a **crazy idea** (undefined, exploratory)?

- **Mega task** → go to Section 5 (planning spree).
- **Crazy idea** → go to Section 4.3 (research and shape).

### 4.3 For crazy ideas: research before scoping

Crazy ideas need research to become tractable. The workflow:

1. **Quick-scan existing state** (5-10 min). Are we already working on this? Is there related OKF? Is there a Linear project with the name? Run `grep` on `project-registry.json` and `git log --oneline | head -50` on candidate repos.
2. **AGY pro research** (10-15 min). Spawn a research task with goals, anchors, and an artifact target. Not a checklist. The skill `agy-research-metabolizer` defines this pattern.
3. **Shape into a 1-page brief** (10 min). Either: "this is tractable, here's a 5-issue plan" OR "this is too undefined, here's what we need to learn first to decide" OR "this duplicates X, abandon."
4. **Get Michael's call** (1 message). One question, three options max. Don't dump 10 possibilities.

The output of ingestion for a crazy idea is: **a research artifact + a one-question ask OR a Linear project with 3-5 starting issues**.

### 4.4 For mega tasks: surface the Michael-decision IMMEDIATELY

Mega tasks almost always contain 1 sub-decision that needs Michael before any agent can proceed. The first response should:

1. Acknowledge the task ("Got it, here's how I'm thinking about it")
2. Name the Michael-decision in one sentence ("I'll need X from you to unblock Y")
3. State the timeline ("Everything else can run in parallel; Y will be ready when you are")
4. Confirm or kick off Section 5

**Rule:** If the orchestrator can do the entire mega task without any further Michael input, the task is underspecified. Push back and ask for the missing piece.

---

## 5. The Planning Spree (15-30 minutes)

After ingestion, before dispatching. The output: OKF doc + Linear issues with the right shape.

### 5.1 The OKF doc is the planning artifact

Every mega task gets an OKF doc. Even small ones. The doc lives in the project's `okf/` and is published via `prismatic-publish` so it has a stable URL. The doc structure (proven on BeyondSaaS, the AOT audit, and the dispatch architecture doc):

1. **TL;DR / outcomes table** — 1 paragraph + a 4-8 row table of goals and their status
2. **What shipped** — file-by-file or feature-by-feature, with paths
3. **Decisions made** — locked decisions with rationale
4. **What's outstanding** — numbered O1, O2, O3... (the "outstanding items" list that becomes the Linear issue template)
5. **Future-agent runbook** — 6-8 numbered steps to pick this up cold
6. **Verification commands** — `curl` / `ps` / `systemctl` checks
7. **Risk register** — known unknowns with severity + mitigation
8. **Related OKF docs / Linear issues** — cross-links

**Why the doc and not just Linear issues:** Linear issues describe atomic work. The OKF doc describes the *narrative* — what we did, why, what we learned. When a future agent (or future-Michael) wants to know "what happened with the BeyondSaaS push," they read the OKF doc, not the issue history.

### 5.2 The Linear issues are the dispatchable units

Once the OKF doc has the Outstanding Items (O1, O2, O3, ...), each one becomes 1-2 Linear issues. The mapping rules:

| OKF item | Linear shape |
|---|---|
| Single, atomic, verifiable (e.g., "Update pricing.astro to $4,500/$15,000/$5,000") | 1 issue, 1 agent |
| Multi-step deliverable (e.g., "Audit publisher health + add monitoring cron + add systemd unit") | 1 parent epic + 2-4 children with `[O3-A]`, `[O3-B]`, `[O3-C]` titles |
| Decision-locked but execution-deferred (e.g., "Wait for Michael's bio") | 1 issue labeled `agent:fred` with description "Blocked on Michael input at OKF doc URL" |
| Research output (e.g., "What schema.org types does AOT need?") | 1 issue labeled `agent:agy` with `agent:agy-pro` peer review, scoped to "produce spec doc only, no code" |

**Title convention:** `[<Project> O<N>] <imperative task>`. Makes them filterable, sortable, and visually distinct in Linear.

**Description convention:** Must include the OKF doc URL, the specific O<N> reference, the verification command(s), and the "DONE: GRO-XXXX <one-line>" expected output.

### 5.3 The peer-review pair

For every non-trivial code change, file TWO issues: one for the worker (`agent:agy` or `agent:ned-code` etc.), one for the peer reviewer (`agent:agy-pro` or `agent:ned-review`). This is codified in the `agy-peer-review` standard. The peer review issue is filed BEFORE the worker's issue is dispatched, not after — so the review happens on the worker's output, not retroactively.

**Skip the peer review for:** doc-only changes, single-line fixes, `agent:fred` work (Fred is the second-witness by design).

### 5.4 The pre-flight verification

Before filing the Linear issues, do a Phase 0 / 2.5 / 2.8 / 2.9 sweep per the `golden-thread` skill. The sweep finds:
- **What's already shipped?** (curl the live endpoint; check `git log`; check existing files)
- **What's already running?** (`systemctl list-units`, `ss -tlnp`, `ps aux | grep cloudflared`)
- **What's already documented?** (`grep` OKF, search the project repo)
- **What's already in Linear?** (filter by project, by label, by recent activity)

For each pre-flight hit, mark the corresponding Outstanding Item as "already done" — close it as `agent:done` with a verification comment, not by creating a new issue to "do" something that's already there. **The BeyondSaaS hotfix pattern: 5 false-positive tasks closed in one sweep by curl-verifying the endpoints already worked.**

### 5.5 File the issues in the right project

Every Linear project should be venture-scoped, not feature-scoped. A mega task's issues go under ONE project — the venture they advance. The project ID is the one that the venture's OKF index doc points to. Don't create a new project per mega task; that's how you get 35+ ventures that are actually sub-features.

---

## 6. The Golden Path (Execution)

After planning, the issues are filed. From here, the work flows through the same standard pipeline as any other task. The golden path:

```
OKF doc published
  ↓
Linear issues filed (with right labels + right project)
  ↓
[IF critical-path: Fred files AND starts own work in parallel]
  ↓
Dispatcher picks up via agent:* label
  ↓
Worker agent (AGY / Ned / Kai) executes in sandbox
  ↓
Worker writes RESULT.md + DONE: marker
  ↓
Worker posts summary comment to Linear
  ↓
[IF non-trivial: Peer-review agent (AGY-pro / Ned-review) reviews the work]
  ↓
Fred verifies against the OKF doc's acceptance criteria
  ↓
Fred moves to Done, swaps agent:* → agent:done
  ↓
OKF doc updated with status
```

**Skip steps for trivial work.** Doc-only changes don't need peer review. Single-line fixes don't need Fred verify. Use the standard's "if non-trivial" gate as your heuristic.

**The parallel-build pattern** (from the `okf-dispatch-pattern` skill's "When to abandon dispatch" section): when the deadline is 30min-2h, dispatch to AGY AND start Fred's own work in parallel. Ship whichever finishes first. This is not "Fred doing AGY's job" — it's "Fred mitigating AGY's known failure modes (ghost-stuck, queue jam)."

---

## 7. What Features Have Been Forgotten / Dropped

These are the patterns/features that were either built, planned, or implied, then forgotten or silently dropped. The OKF doc should make these *visible* so they don't get re-invented (or re-forgotten) in the next mega task.

### 7.1 Features that shipped but are now stale

| Feature | When shipped | When it went stale | What happened |
|---|---|---|---|
| Nightly Backlog Routing Watchdog | 2026-05 | 2026-06-19 | Reduced to daily (Tier 7 cron reduction per GRO-2050). Last run 2026-06-19 11:06. Now "scheduled" but the script is `no_agent=True` and writes 165-byte status files. Effectively dormant. |
| Tier 1 heartbeat fix (GRO-2101) | 2026-06-22 | not loaded | Code is on disk, supervisor has not been re-exec'd since the change. Until the next cron tick reloads, ghost-stuck rate is still ~33%. |
| Prismatic Engine publisher systemd unit (GRO-2096) | 2026-06-23 | "Done" but no follow-through | Verified on disk, no systemd enable/verify step. The fix shipped; the activation didn't. |
| `agy_sandbox_event_supervisor_cron.sh` | earlier 2026 | paused | The nudge-based IPC chain. Paused in favor of webhook path per `event-driven-dispatch.md`. Should be either deleted or revived — it's currently in limbo. |
| Tier 5/6 docs on AGY activation, Prismatic Engine | 2026-06-19 | mostly current | Some sections (the "agent activation" sequence) are not 100% verified. Future agent reading them may hit discrepancies. |

### 7.2 Features that were promised but never built

| Feature | Source | Status |
|---|---|---|
| Modular dispatch with lanes / recipes / on-off lever | GRO-2105 (filed 2026-06-23) | Not scheduled. ~5 days work. The user-facing control layer for everything in the dispatch architecture doc. |
| `scripts/okf_validate.py` pre-commit hook | beyondsaas-implementation-plan O7 | "Optional" — not started. Would validate OKF frontmatter on every commit. |
| Mode 1 alerting scripts (3 cron jobs for AGY completion, morning digest, long-runner alert) | GRO-2103 (filed 2026-06-23) | Not started. Per the `okf-dispatch-pattern` skill: $0 LLM cost, 3 scripts, autobot Telegram token. |
| Heartbeat during AGY session | GRO-2101 | Code on disk, not loaded. |
| Universal agent_lanes.yaml config | This doc, Section 8 of the dispatch architecture doc | Not started. |
| LinearBudget telemetry dashboard | GRO-2008/2010/2020/2034 history | Built incrementally, never consolidated. |

### 7.3 Inconsistencies between docs and reality

| Doc says | Reality | Where the inconsistency is |
|---|---|---|
| "Ned has 5 lane labels: agent:ned, agent:ned-code, agent:ned-infra, agent:ned-audit, agent:ned-review" | Ned's dispatcher is broken (invalid model + no timeout); every lane is dead-lettered | okf/standards/agent-dispatch-architecture.md (just published) |
| "Cron runs every 15 min" (per many skills) | Multiple crons are now daily (Tier 7 reduction per GRO-2050) | okf/projects/prismatic-engine/tier-7-journey.md |
| "Webhook IS delivery. Do NOT propose polling." (memory) | AGY supervisor is *polling*, not webhook-driven. Webhook path is the production path per `event-driven-dispatch.md`, but the AGY sandbox supervisor is a separate code path. | Memory vs. `agy_sandbox_supervisor.py` source |
| "AGY has final say — not Orchestrator. AGY approves+merges." (memory) | When AGY ghost-stucks, Fred builds the deliverable himself. Peer review is by AGY-pro, but final-merge is Fred-only per the dispatcher bypass detection. | Memory vs. `prismatic/dispatcher.py` line ~2134-2151 |
| "15+ skills per agent" | 41 SKILL.md files = ~856KB = ~214K tokens. Qwen 32B (65K context) overflows before compression can fire. | okf/playbooks/prismatic-engine-tasks.md doesn't mention this risk |

---

## 8. The Mega Task Lifecycle (cheat sheet)

| Phase | Duration | Output | Owner |
|---|---|---|---|
| **0. Ingestion** | 60-90 sec | First Telegram reply: "I see X, I need Y from you, here's the timeline" | Fred |
| **1. Research** (crazy ideas only) | 10-15 min | OKF research doc + 1-question ask OR Linear project with 3-5 starting issues | Fred + AGY pro |
| **2. Pre-flight** (mega tasks) | 5-10 min | Phase 0 / 2.5 / 2.8 / 2.9 sweep results: what's already done | Fred |
| **3. Planning** | 10-15 min | OKF doc (TL;DR + outcomes + outstanding items + runbook) | Fred |
| **4. Issue creation** | 5-10 min | N Linear issues with right labels, right project, right shape | Fred |
| **5. Pre-flight** (post-creation) | 2-3 min | Verify issues landed correctly via Linear API | Fred |
| **6. Parallel execution** | varies | AGY sandboxes running + (if deadline tight) Fred building critical path | AGY + Fred |
| **7. Reconciliation** | 5-10 min per task | Issues moved to Done, `agent:done` labels applied, ghost-stuck work rerouted or hand-built | Fred |
| **8. OKF doc closure** | 5-10 min | Status updated, "what worked / what fell short" section, "future-agent runbook" revised | Fred |
| **9. Verification** | 2-3 min | curl/ps/systemctl/git checks from the OKF doc's "verification commands" section | Fred |
| **10. Report to Michael** | 1 message | "Done. Here's the deliverable. Here's what you need to do." (3 sentences max) | Fred |

**Total budget for a "small" mega task** (5 issues, 1-2 day deadline): 60-90 minutes of Fred's time across the lifecycle. **Total budget for a "big" mega task** (10+ issues, hard deadline, multiple agents): 2-4 hours of Fred's time, with 4-8 hours of agent time running in parallel.

---

## 9. Standards for How Agents Should Approach Mega Tasks

These are the rules that any agent (AGY, Ned, Kai, Jules, Codex) should follow when picking up an issue that's part of a mega task.

### Input expectations
- The issue description has a published OKF doc URL.
- The OKF doc has a "Future-agent runbook" section.
- The issue title has the `[<Project> O<N>]` prefix.
- The verification command is provided.

### Execution expectations
- Read the OKF doc before touching code.
- Don't scope-creep past O<N>. If you discover adjacent work, file a new issue and link it, don't silently absorb.
- Write `RESULT.md` to the workdir (not `/tmp`) so it survives sandbox cleanup.
- Post the summary comment to Linear with: OKF doc URL, what changed, the verification command + output, the artifact path.

### Communication expectations
- If you're stuck, comment on the issue with a 1-paragraph status. Don't disappear.
- If you discover a blocker that needs Michael, post a comment + flag the issue with `requires:human-approval` label.
- If you complete early, post the result and let Fred promote the issue. Don't promote it yourself.

### Peer-review expectations (for review issues)
- The review is on the worker's `RESULT.md`, not on a re-do of the work.
- The verdict is APPROVE / NEEDS_CHANGES / BLOCKED.
- The verdict is the first line of the review comment.
- Findings have severity (High / Medium / Low).
- Required fixes are numbered, not bulleted, so they can be cross-referenced.

---

## 10. The Standards This Doc Depends On

- `okf/standards/agent-dispatch-architecture.md` — the dispatch system today, the lane gap, the failure modes
- `okf/standards/dispatch-production-grade.md` — the 7-layer security + 7-gate dispatch
- `okf/standards/agy-peer-review.md` — the review loop
- `okf/decisions/event-driven-dispatch.md` — why webhook > polling
- `okf/playbooks/prismatic-engine-tasks.md` — where everything lives, how to deploy
- `~/work/growthwebdev-knowledge/okf/projects/beyondsaas-implementation-plan-2026-06-22.md` — the reference mega-task OKF doc
- Skills: `golden-thread`, `okf-dispatch-pattern`, `autonomous-execution-discipline`, `orchestrator-delegation-discipline`, `agent-session-wrapup`, `agy-research-metabolizer`, `fred-strategy-synthesizer`

---

## 11. The Anti-Patterns (Don't Do These)

These are the failure modes the orchestrator has personally hit. The doc is partly a reminder to future-self.

1. **"I'll figure out the structure as I go."** No. Write the OKF doc first, then the issues. Always.
2. **"I'll dispatch and see what happens."** No. The verification gate is the verification gate. Don't skip it.
3. **"The user just wants the deliverable."** Sometimes. But for a mega task, the user wants the *plan* so they can intervene early if needed.
4. **"I'll skip the OKF doc — it's just a doc."** The doc is the only artifact that survives. Don't skip.
5. **"I'll just do it myself, AGY is unreliable."** Sometimes correct (30min-2h deadline). Otherwise: dispatch, verify, report.
6. **"I'll ask 5 questions up front to be sure."** Ask 1 question. The 5-question pattern is procrastination disguised as rigor.
7. **"I'll create 30 issues, that covers everything."** 5-12 is the right range. 30 is scope-sprawl.
8. **"I'll route everything to AGY because it's the only working dispatcher."** True today. After GRO-2118 lands, route to the right lane.
9. **"I'll post a single summary at the end."** Post 1 message per phase. The user (and future agents) need breadcrumbs.
10. **"I'll let the OKF doc grow stale."** Update it at every phase transition. Stale OKF is worse than no OKF.

---

## 12. Change log

- 2026-06-23: Initial version (Fred). Triggered by Michael's "I'll send over the other big task shortly" — recognizing the need for an explicit mega-task workflow + honest accounting of what has worked, what fell short, and what features were forgotten. Grounded in BeyondSaaS, AOT drift, dispatch architecture, and engineering audit evidence from June 2026.
