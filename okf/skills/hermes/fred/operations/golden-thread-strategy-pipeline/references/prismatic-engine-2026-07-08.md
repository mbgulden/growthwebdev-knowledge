# Prismatic Engine Golden Thread Run — 2026-07-08

## Why this matters

This run exposed durable patterns for Golden Thread cron pipelines: missing requested skills, Linear API rate limiting, orchestrator research timeouts, orchestrator execution self-report errors, and the need to independently verify evidence before reporting.

## Project Selection

- Source: `/home/ubuntu/work/project-registry.json`.
- Selected project: `prismatic-engine` because it was the only registry project with open-ish Linear issues and a stalled `next_action` around Phase 4 distribution.
- Linear initially returned a rate-limit error (`remaining: 0/2500`), so the pipeline continued from registry/local cached issue context and retried Linear later.

## Research Pattern

Build an input JSON with:
- Registry project fields.
- Local repo path and snippets from README, pyproject, PRISMATIC_ENGINE.yaml, docs.
- Known competitors.
- Explicit assumptions.
- Required output schema.

Run three orchestrator research calls:
1. Assumption challenge.
2. Strategy discovery.
3. Gap analysis.

If a call times out, rerun with a smaller prompt, fewer deliverables, JSON-only instruction, and a word cap.

## Synthesis Pattern

Orchestrator research indicated:
- Generic provider-agnostic orchestration is crowded.
- The differentiated wedge is task-tracker/webhook-driven agent execution.
- Public distribution should wait for a first-user readiness gate.

Winning strategy selected:
**Linear/GitHub automation app / webhook wedge** — because it is demoable, differentiated, and supports private-deployment consulting leads.

## Linear Task Pattern

Three tasks were created successfully after the earlier rate-limit condition cleared:
- Add distribution readiness smoke test.
- Create 90-second Linear-label-to-agent demo script.
- Write private-deployment README/CTA section.

Important detail: Linear issue creation defaulted to `Backlog`, so the top issue had to be explicitly moved to the `Todo` workflow state.

## Orchestrator Execution Pitfall and Workaround

The first orchestrator execution attempt timed out after the orchestrator announced it had started background pytest and was waiting.

Workaround prompt shape:

```text
Execute a bounded verification-only gauntlet.
DO NOT start background processes.
DO NOT edit files.
Run at most these foreground checks: ...
Return JSON only: {issue, result, unit, integration, revenue, assumption, blockers}.
```

This produced a usable JSON result.

## Verification Corrections

AGY incorrectly claimed:
- `pyproject.toml` version was `0.2.0`.
- `prismatic.cli` was missing.

Fred verified with terminal evidence:
- `pyproject.toml` was actually `0.1.0`.
- All pyproject console entrypoint modules imported OK, including `prismatic.cli:main`.

Confirmed blockers were:
- No automated distribution readiness test existed.
- README license copy said internal/TBD while pyproject and Dockerfile declared AGPL-3.0-only.
- Package data omitted config YAMLs.
- Repo had pre-existing unrelated modification in `prismatic/journal.py`.

## Durable Lessons

- Orchestrator output is useful but must be treated as a draft, not evidence.
- In cron pipelines, prefer bounded verification prompts after any orchestrator timeout.
- Always retry Linear later if an initial rate-limit blocks discovery but not necessarily mutations.
- Top-created task may need an explicit workflow state update to become `Todo`.
- Report corrected evidence, not raw AGY claims.
