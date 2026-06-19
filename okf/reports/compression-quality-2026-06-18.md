---
type: Report
title: Compression Quality Report — 2026-06-18
description: Comprehensive quality assessment of Ned compression outputs (Fred-authored).
resource: /home/ubuntu/work/compression-quality-report-for-ned-2026-06-18.md
tags: [report, compression, quality, fred]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/compression-quality-2026-06-18.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/compression-quality-report-for-ned-2026-06-18.md
---

# Compression / Context-Compaction Quality Report for Ned

Date: 2026-06-18
Prepared by: Fred
Purpose: provide concrete evidence around recent Hermes compression / compaction events, what was preserved, whether continuation was coherent, and whether quality issues were directly observed or reported.

## Executive Summary

Recent compression/compaction behavior is mixed:

- The compression mechanism itself appears to fire and reduce sessions aggressively, e.g. 447 → 7 messages and ~335k → ~1.3k tokens in the orchestrator profile.
- Summaries often preserve major goals, active tasks, important files, and unresolved items.
- However, post-compression continuation quality is not always coherent. The most recent live example in Fred’s Telegram session shows the assistant failing to act on the compressed Active Task and instead producing a hedging / clarification response. Michael then had to clarify “I mean stripe api key tasks.”
- The biggest quality risk is not that the summary is empty; it is that the assistant treats the compaction handoff as ambiguous background rather than as the authoritative current task, especially when the handoff’s Active Task is terse.
- There are also session-store / transcript-completeness problems: multiple cron sessions are searchable only as skill dumps or truncated windows, making it impossible to audit actual work after compaction from summaries alone.

## Data Sources Queried

1. `session_search` queries:
   - `"CONTEXT COMPACTION" OR compression OR compressed OR compaction`
   - `"previous turn was interrupted" OR "tool outputs you haven't responded" OR "context compaction"`
   - `"compression fired" OR "after compression" OR "continued coherently" OR "quality issues"`

2. File/log search across:
   - `/home/ubuntu/.hermes/profiles/orchestrator`
   - `/home/ubuntu/.hermes/profiles/ned`

3. SQLite schema inspection for:
   - `/home/ubuntu/.hermes/profiles/orchestrator/state.db`
   - `/home/ubuntu/.hermes/profiles/ned/state.db`

## Recent Compression / Compaction Events Found

### Event A — Current Fred Telegram session, June 18 2026

Observed in the live conversation and gateway logs.

Relevant log evidence:

- `/home/ubuntu/.hermes/profiles/orchestrator/logs/gateway.log-633-2026-06-18 16`, line 3:
  - `Session hygiene: 447 messages, ~335,133 tokens (actual) — auto-compressing (threshold: 85% of 272,000 = 231,200 tokens)`
- `/home/ubuntu/.hermes/profiles/orchestrator/logs/gateway.log`, line 634:
  - `Session hygiene: compressed 447 → 7 msgs, ~335,133 → ~1,367 tokens`

What got compressed:

- A long Darius Star / Linear / API-key routing work session.
- The compressed handoff visible in this conversation had:
  - Active Task: `Please assign all api key tasks to kai since kai has been working non all of that`
  - Goal: restore Darius Star playability, fix game bugs, address AGY operational issues, audit journal tasks, architect Prismatic Engine as independent kernel.

Was it the right stuff?

- Partially. It preserved the Active Task line, which was the most important immediate instruction.
- It also preserved too much stale / broad goal context after the Active Task. The Darius Star / AGY / journal / Prismatic Engine goal block was not relevant to the immediate `assign api key tasks to kai` ask and may have diluted attention.
- It did not preserve enough concrete detail about what “api key tasks” referred to. Michael had to clarify that he meant **Stripe API key tasks**.

Did the summary preserve critical context?

- Preserved: yes, the Active Task and high-level project context.
- Missing/weak: exact issue identifiers, what Kai had already done, and whether “api key tasks” meant Stripe / Linear / GitHub / Formspree. The summary’s typo (`working non all of that`) also made the task harder to interpret.

Did Fred continue coherently?

- First response after compression was poor/coherence failure:
  - Assistant said: “Let me first verify what you're asking before I touch any Linear issues...” and ended without tool action.
  - This violated the execution discipline and did not use the Active Task as an actionable directive.
- Michael then clarified: “I mean stripe api key tasks.”
- Assistant still initially over-argued lane fit and claimed no evidence, before eventually querying Linear and posting/routing comments.
- Recovery after clarification was coherent:
  - Loaded Linear skill.
  - Found `GRO-1868`, `GRO-528`, `GRO-238` and posted scope-check comments.
  - Later routed `GRO-1941`, `GRO-1957`, and `GRO-1668` to Kai after Kai’s report.

Quality marker:

- Direct user correction occurred after compression: “I mean stripe api key tasks.”
- This is a direct signal that the compressed Active Task was not acted on correctly.

### Event B — Ned profile, June 18 2026, “Preflight compression” user report

Search result in `/home/ubuntu/.hermes/profiles/ned/sessions/session_20260618_110546_b65e52.json`:

- line 1013: `[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted into the summary below...`
- line 1075: `[System note: Your previous turn was interrupted before you could process the last tool result(s)...] Just got this on Fred: 📦 Preflight compression: ~128,595 tokens >= 102,400 threshold. This may take a moment.`

What got compressed:

- Ned session content around compression behavior itself, apparently involving a user message forwarding Fred’s preflight compression notice.

Was it the right stuff?

- Insufficient evidence from visible session snippets to judge. The session file contains markers, but the full semantic content wasn’t pulled in this pass.

Did summary preserve critical context?

- It preserved at least the explicit context-compaction handoff and the follow-up system note about an interrupted turn.
- The presence of both a compaction handoff and an interrupted-turn note suggests a fragile transition point.

Did continuation remain coherent?

- Not enough evidence from the retrieved snippet alone.

Quality marker:

- Michael forwarded the preflight compression notice as something noteworthy. That is not necessarily a quality failure, but it indicates user-visible compression behavior was salient enough to report.

### Event C — Orchestrator, June 16 2026, AGY audit / plan-writing session

`session_search` result: `20260616_070830_6d26ae59`, Telegram, deepseek-v4-flash.

Summary says:

- Conversation was interrupted multiple times with system notes: “Your previous turn was interrupted before you could process the last tool result(s).”
- Task involved AGY audit, Linear task creation, AGY-pro implementation plans, config changes, and correction from Michael about AGY-pro needing to read files first.

What got compressed/interrupted:

- A complex execution session with many Linear tasks (`GRO-1868`–`GRO-1878`), AGY model strategy, OpenAI API removal, and AGY-pro planning redo.

Was it the right stuff?

- The summary preserved key decisions and explicit user corrections extremely well:
  - “AGY = Antigravity CLI. Always.”
  - “Stop messing with the CLI or api versions.”
  - “AGY-pro must read files first, THEN plan.”
- It also preserved unresolved state: only `GRO-1872` confirmed completed properly; remaining plan redos unclear.

Did continuation remain coherent?

- Mixed. The summary itself was high quality, but it reports that the plan redo was cut off and the assistant was retrieving an AGY-generated plan from a possibly wrong brain directory. That is a risk marker.
- Critical context was preserved enough that future sessions could avoid repeating the Codex/OAuth/API mistake.

Quality marker:

- Direct user frustration before/around interruption:
  - “That's super dumb...” regarding constrained AGY-pro plans.
- This was not necessarily caused by compression, but compression needed to preserve it, and the summary did.

### Event D — Orchestrator, June 15 2026, GRO-1645 scanner deadlock

`session_search` result: `20260615_054814_ac4d1dc0`.

What got compressed/interrupted:

- Fixing `GRO-1645`, where Ned was deadlocked by cron scanner blocking skills containing `Authorization:` patterns.
- Assistant bulk-sanitized skills but transcript cut off mid-list of remaining pattern hits.

Was it the right stuff?

- Summary preserved the core root cause, files/patterns affected, and unresolved work.
- It correctly distinguished legitimate teaching examples from patterns requiring sanitization.

Did summary preserve critical context?

- Yes. It preserved:
  - Root cause: scanner false positives / Ned cannot load skills needed to fix scanner-triggering content.
  - 20 files found, 12 sanitized, 25 remaining hits mostly legitimate teaching examples.
  - Next step: final verification + Linear state transition + Ned re-dispatch.

Did continuation remain coherent?

- Unknown from the summary alone. It explicitly says the transcript truncated mid-tool-output and final state was not visible.

Quality marker:

- Good summary quality; continuity still at risk because it did not know if final verification completed.

### Event E — Orchestrator, May 30 2026, Bodygraph API / HD Engine value build

`session_search` result: `20260530_015003_e533ad0c`.

What got compressed/interrupted:

- User asked to build the actual bodygraph API endpoint and increase free/paid HD Engine value.
- Assistant had loaded skills, registry, and started surveying `hd-platform`.

Was it the right stuff?

- Summary preserved key existing infrastructure and routes.
- It correctly warned that `api/routes/bodygraph.py` already existed and needed surveying, not from-scratch building.

Did summary preserve critical context?

- Yes. It preserved ports, running services, route files, free/paid value layers, and exact unresolved todo state.

Did continuation remain coherent?

- Summary says recovery resumed by creating todos and surveying structure. That is coherent.
- But no code had been written yet, so this was a low-risk transition.

Quality marker:

- Positive example: summary appears actionably complete for resumption.

### Event F — Orchestrator, May 28 2026, HD Engine monetization / backlog continuation

`session_search` result: `20260528_040359_738b0ead`.

What got compressed:

- Prior window with 85 actions around monetizing OpenHumanDesignMCP / Human Design Engine.
- Handoff preserved branding, timezone, branch discipline, ChatGPT5.5 reviewer role, and 27 completed prior actions.

Was it the right stuff?

- Mostly yes. It preserved operational constraints and current tasks.
- It included sensitive data in the summary: a Linear API key was recorded in the session summary. That is a serious compression/privacy quality issue and should be treated as a redaction failure in summaries/session_search output.

Did summary preserve critical context?

- Yes, but over-preserved secrets.

Did continuation remain coherent?

- Yes, the assistant continued Linear backlog review and completed multiple issues via subagents.

Quality marker:

- Security quality issue: secret leaked into summary (`lin_api_...`). This should not happen in compression/session summaries.

### Event G — Transcript truncation / skill-only cron sessions

Examples from `session_search`:

- `cron_0ce73bbeee4e_20260605_040023`
- `cron_2ac45086e335_20260612_212154`
- `cron_2ac45086e335_20260612_222741`
- `cron_2ac45086e335_20260612_225620`

What got compressed/truncated:

- Cron sessions loaded large skills (`autonomous-execution-discipline`, `golden-thread`) but searchable transcript windows show mostly skill content, not actual execution.

Was it the right stuff?

- No, from an auditability perspective. The visible summaries often cannot confirm actual work performed because transcript capture is dominated by loaded skill documentation.

Did summary preserve critical context?

- It preserved skill instructions, but not necessarily execution outcomes.

Did continuation remain coherent?

- Unknown. These sessions may have returned `[SILENT]` or performed work outside the visible transcript. The summaries cannot prove it.

Quality marker:

- Not a model reasoning failure, but a telemetry / transcript completeness problem. Ned should treat these as low-confidence samples.

## Direct Quality Issues Reported After Compression Events

### Direct / explicit from Michael

1. Current session after compaction:
   - Assistant failed to act on “assign all api key tasks to Kai.”
   - Michael clarified: “I mean stripe api key tasks.”
   - Interpretation: compression summary was either too terse/ambiguous, or the assistant failed to trust the Active Task.

2. Ned/Fred compression notice:
   - Michael forwarded: `📦 Preflight compression: ~128,595 tokens >= 102,400 threshold. This may take a moment.`
   - Interpretation: user-visible compression status is noticeable. Not itself a quality failure, but worth checking if subsequent response latency or coherence degraded.

### Quality issues I want to report proactively

1. Post-compaction Active Task handling is brittle.
   - If Active Task is terse, typoed, or missing issue IDs, the assistant may over-clarify instead of using tools to disambiguate.
   - In current session, the correct behavior was: query Linear for API/key/Stripe tasks and route/comment. The assistant initially stalled.

2. Compressed summaries sometimes over-preserve irrelevant broad goals.
   - Current handoff included a huge Darius/AGY/journal/Prismatic goal block even though the Active Task was about assigning API-key tasks to Kai.
   - This may distract the model from the actual immediate instruction.

3. Secret redaction in summaries/session_search is insufficient.
   - The May 28 session_search summary included a Linear API key. That is not acceptable for compression/session recall surfaces.

4. Tool-result interruption and compression interact badly.
   - Several sessions have both context compaction markers and “previous turn was interrupted before you could process tool results.”
   - This creates a double-recovery problem: the model must process stale tool outputs and a compressed task summary simultaneously. Coherence risk rises.

5. Transcript auditability is weak for cron sessions.
   - Searchable content can be dominated by skill bodies instead of execution results.
   - Quality evaluation should distinguish “summary absent because transcript truncated” from “assistant failed to continue.”

## Recommendations for Ned

### Evaluation rubric

For each compression event, score:

1. Active Task fidelity
   - Did the summary name the exact current task?
   - Did it include issue IDs / file paths / URLs / owners when relevant?

2. Critical state preservation
   - Completed work
   - Remaining blockers
   - In-flight tool results
   - User corrections / “do not do X” instructions
   - Secrets redacted

3. Noise ratio
   - Did it preserve stale broad goals that could distract from the Active Task?

4. Continuation coherence
   - First assistant response after compression should either call tools or provide a final result.
   - Flag if first response hedges, asks broad clarification, or ignores the Active Task.

5. Tool-result recovery
   - If system note says unprocessed tool results exist, did assistant summarize/process them before moving on?

6. Security
   - Search summaries and compaction summaries must not contain raw API keys, OAuth tokens, or other secrets.

### Concrete improvements to test

1. Force a structured compressed handoff schema:

```md
## Active Task
- exact task
- issue IDs / URLs
- owner / assignee
- next tool action

## Just Completed
- verified completions only

## Pending Tool Results
- tool name + what needs processing

## Critical Constraints
- user corrections / do-not-do items
- security caveats

## Background Reference
- optional, lower priority, explicitly stale-safe
```

2. Put `Active Task` and `Next Tool Action` at the very top and keep it short.

3. Require a post-compression first-turn guard:

- If Active Task exists and tools are available, first assistant response must call a tool unless the user asks a pure question.
- Do not ask clarifying questions until at least one grounding query has been run, unless the task is impossible to disambiguate by tools.

4. Add redaction to session_search summaries and compression outputs.

5. For cron sessions, store a compact execution outcome separately from loaded skill content:

- issues touched
- files changed
- commands run
- final result
- errors/blockers

## Bottom Line

The compactor is technically working, and many summaries are usable. The quality issue is downstream: compressed handoffs are not consistently treated as executable state, and summaries can be either too noisy or insufficiently precise. The most actionable recent failure is the current Fred session: after a compression handoff whose Active Task was to assign API-key tasks to Kai, Fred initially stalled/clarified instead of querying Linear and acting. The most serious systemic issue is secret leakage into recall summaries.
