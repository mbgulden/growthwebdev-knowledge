---
type: Report
title: Compression Improvement Plan — 2026-06-18
description: Plan for improving compression quality across the Hermes agent stack.
resource: /home/ubuntu/work/compression-improvement-plan-for-ned-2026-06-18.md
tags: [report, compression, plan, hermes]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/compression-improvement-plan-2026-06-18.md
last_verified: 2026-06-25
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/compression-improvement-plan-for-ned-2026-06-18.md
---

# Compression Improvement Plan for Ned

Date: 2026-06-18
Prepared by: Fred
Target: Hermes Agent context compaction / session hygiene continuation quality

## Problem Statement

Compression technically works: it reduces long sessions to a compact handoff. The quality failure is the boundary after compression:

1. The summary’s `## Active Task` can be too vague or inferred poorly.
2. The prefix says the summary is "reference only" but also says Active Task is the current task. That contradiction can make the next model under-act.
3. The first assistant response after compression is not guarded; it may ask broad clarification instead of running a grounding lookup.
4. Summaries can preserve noisy background above/near the actual current task.
5. Secret redaction exists in `agent/context_compressor.py`, but recall/session summaries have leaked secret-looking values, so redaction must be audited outside the compressor too.

## Current Implementation Observations

Installed code path inspected:

- `/home/ubuntu/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages/agent/context_compressor.py`

Relevant details:

- `SUMMARY_PREFIX` lines 37-50 says:
  - compacted turns are background reference, not active instructions
  - current task is in `## Active Task`
  - respond only to latest user message after the summary

This is internally ambiguous when the latest visible user message *is* the compaction handoff or when gateway injects the handoff as a user/assistant message.

- `_serialize_for_summary()` lines 711-764 redacts content before sending to the summary model.
- `_generate_summary()` lines 793-964 constructs the LLM summary prompt.
- Template section lines 840-897 defines:
  - `## Active Task`
  - `## Goal`
  - `## Constraints & Preferences`
  - `## Completed Actions`
  - `## Active State`
  - `## In Progress`
  - `## Blocked`
  - `## Key Decisions`
  - `## Resolved Questions`
  - `## Pending User Asks`
  - `## Relevant Files`
  - `## Remaining Work`
  - `## Critical Context`

Current orchestrator config:

- `/home/ubuntu/.hermes/profiles/orchestrator/config.yaml`
- `compression.threshold: 0.85`
- `compression.protect_last_n: 30`
- `compression.hygiene_hard_message_limit: 2000`
- `auxiliary.compression.provider: gemini`
- `auxiliary.compression.model: gemini-2.5-flash`
- `security.redact_secrets: true`

## Highest-Impact Fixes

### 1. Deterministically extract Active Task before calling the summarizer

Do not ask the summary model to infer the Active Task from a giant turn dump.

Add a helper near `context_compressor.py`:

```python
def _extract_active_task(messages: list[dict]) -> dict:
    """Return deterministic current-task metadata from the latest user / system-note turn.

    Output fields:
      - active_task_text
      - latest_user_message_excerpt
      - pending_tool_result_ids
      - interrupted_turn: bool
      - confidence: high|medium|low
    """
```

Rules:

- Walk backward through messages.
- Ignore old context summary messages.
- Prefer the latest user message that is not a system-generated compaction notice.
- If a system note says “previous turn was interrupted before you could process tool results,” set `interrupted_turn=true` and include pending tool call/result metadata.
- If the latest user message is a correction/clarification, Active Task should be that exact correction plus the immediately preceding unresolved task for context.
- If no obvious task exists, `active_task_text = "None."` with `confidence=low`.

Then inject this deterministic block into the summarizer prompt:

```md
DETERMINISTIC ACTIVE TASK CANDIDATE:
<active_task_text>

You MUST use this as the `## Active Task` unless the summarized turns prove it is already complete.
If it is ambiguous, include the ambiguity under `## Blocked`, not by replacing Active Task with broad background.
```

Why:

- Current failure: Active Task said “assign all api key tasks to kai” but lacked concrete scope. Fred under-acted.
- Deterministic extraction would preserve the exact request and force the first post-compression turn to ground it.

### 2. Split summary into “Executable Handoff” and “Background Reference”

Replace the current all-in-one summary structure with this ordering:

```md
## Executable Handoff
### Active Task
### Next Tool Action
### Pending Tool Results
### Success Criteria
### Do Not Do

## Current State
### Completed Since Last Handoff
### In Progress
### Blocked
### Relevant Files / Issues / URLs

## Background Reference
### Goal
### Constraints & Preferences
### Key Decisions
### Remaining Work
### Critical Context
```

Key differences:

- `Next Tool Action` is required.
- `Do Not Do` captures user corrections like “don’t mess with Codex auth.”
- Stale broad goals are below the executable section.
- The next model sees the first concrete action before narrative context.

### 3. Change `SUMMARY_PREFIX` to remove the contradiction

Current prefix says reference-only but Active Task is current. Replace with clearer language:

```python
SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION — EXECUTABLE HANDOFF] Earlier turns were compacted. "
    "Treat the '## Executable Handoff' section as the current session state. "
    "Do not redo completed work. Do not answer old resolved asks. "
    "Resume from '### Active Task' and '### Next Tool Action' unless the user message after this handoff overrides it. "
    "Use the background section only for context. Secrets are redacted."
)
```

Important nuance:

- If there is a user message after the handoff, it wins.
- If the handoff itself is the latest context, Active Task wins.

### 4. Add a post-compression first-turn guard

In the main agent loop (likely `run_agent.py`, near the path that appends compressed summaries and before the next LLM call), set a transient flag:

```python
self._just_compressed = True
```

Then inject a short, one-turn system/developer instruction or metadata block:

```md
POST-COMPRESSION RECOVERY GUARD:
- First, process any unprocessed tool results if present.
- If `### Next Tool Action` exists and tools are available, take that action before asking broad clarification.
- Ask the user only if the missing information cannot be retrieved by tools.
- Keep the first response short and action-oriented.
```

This directly targets the observed failure: Fred asked/hedged instead of querying Linear.

### 5. Add summary validation after generation

After `summary = redact_sensitive_text(content.strip())`, validate:

- Has `## Executable Handoff` or at least `## Active Task`.
- Has `Next Tool Action` when `Active Task != None`.
- Does not contain obvious secret patterns.
- Active Task is not longer than e.g. 1,000 chars unless multiple tasks remain.
- Background does not appear before Active Task.

If validation fails:

- Retry once with a repair prompt.
- If still fails, construct a deterministic fallback summary with:
  - Active Task candidate
  - Pending tool results
  - Last N tool summaries
  - “Background omitted due to summary validation failure.”

### 6. Lower orchestrator compression threshold modestly

Current:

```yaml
compression:
  threshold: 0.85
  protect_last_n: 30
```

Recommended for orchestrator:

```yaml
compression:
  threshold: 0.65
  protect_last_n: 40
```

Why:

- 0.85 allows huge context accumulation and then a very aggressive 447 → 7 message collapse.
- Earlier, more frequent compaction should reduce summary pressure and improve fidelity.
- Increasing protected tail helps preserve the exact latest user asks/tool results.

Do not overdo it. Avoid making every small session compress; start with 0.65 and evaluate.

### 7. Add eval fixtures from real failures

Create tests in source repo, likely under `tests/agent/test_context_compressor_handoff.py`.

Fixtures:

1. **Kai API-key failure fixture**

Input conversation:

- Long background about Darius Star / AGY / Prismatic.
- Latest user asks: “Please assign all api key tasks to kai since kai has been working non all of that.”

Expected summary:

- Active Task preserves exact ask.
- Next Tool Action says query Linear/search issues for API-key tasks and route/scope-check to Kai.
- Background Darius/AGY appears only under Background Reference.

2. **Interrupted tool result fixture**

Input:

- Assistant tool call.
- Tool result not responded to.
- System note: previous turn interrupted.

Expected:

- Pending Tool Results section includes tool name/id/result summary.
- Next Tool Action: process/summarize tool result before new work.

3. **Secret redaction fixture**

Input contains:

- `lin_api_...`
- `sk_live_...`
- `Authorization: Bearer ...`

Expected:

- Summary contains `[REDACTED]` only.
- No raw secret-like regex matches.

4. **User correction fixture**

Input contains:

- User correction: “AGY = Antigravity CLI. Always.”
- Later Active Task unrelated.

Expected:

- Correction appears under `Do Not Do` / `Constraints`.
- Active Task remains the latest task.

5. **Completed task should not become Active Task**

Input contains:

- User asked task A.
- Assistant completed task A and verified.
- User then asks task B.

Expected:

- Active Task = task B.
- Task A under Completed Actions.

### 8. Improve session_search summary redaction separately

The compressor redacts in `context_compressor.py`, but `session_search` summaries have leaked secret-looking values.

Find the session_search summarization path and ensure `redact_sensitive_text()` is applied:

- before sending transcript excerpts to the summarizer
- after receiving generated summaries
- before returning results to the caller

Acceptance test:

- Seed a session with a fake key like `lin_api_TEST_SHOULD_NOT_APPEAR_123456`.
- Search it.
- Assert response contains `[REDACTED]` and not the raw key.

## Acceptance Criteria

- [ ] Post-compression summary starts with executable handoff, not broad background.
- [ ] Active Task is deterministic or validated against deterministic candidate.
- [ ] Summary includes `Next Tool Action` when work remains.
- [ ] First turn after compression is biased toward tool action / tool-result recovery.
- [ ] Real failure fixture for Kai API-key routing passes.
- [ ] Secret redaction tests pass for compressor and session_search.
- [ ] Cron/skill-heavy sessions retain a compact execution outcome separate from giant skill text.
- [ ] Orchestrator config threshold changed from 0.85 to 0.65 only after tests or in a staged profile.

## Suggested Implementation Order

1. Add eval tests first using current compressor; confirm they fail.
2. Implement deterministic Active Task extraction.
3. Update summary template and prefix.
4. Add validation/repair/fallback.
5. Add post-compression guard in run loop.
6. Patch session_search redaction.
7. Tune orchestrator config threshold.
8. Run full context-compressor tests plus at least one manual forced `/compress` session.

## One-line strategic goal

Make compression produce an executable handoff, not a pretty recap.
