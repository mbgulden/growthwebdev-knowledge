---
type: Standards
title: Hermes Agent Verifier-as-Deliverable Discipline
description: The verifier is part of the deliverable, not a post-hoc response to a nudge. When shipping an artifact, the named verifier ships with it. The four highest-reuse verifiers are promoted to named skills. A counter tracks % artifacts that landed with a pre-written verifier. The expected outcome: post-turn verification nudges stop firing because the proof was already there.
resource: okf/standards/hermes-verifier-as-deliverable-discipline.md
tags: [standards, hermes, verification, discipline, meta]
timestamp: 2026-07-29T04:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-verifier-as-deliverable-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Verifier-as-Deliverable Discipline

## Purpose

The gap is: verification feels like cleanup. The agent ships an artifact, gets a post-turn nudge from the system ("workspace does not have fresh passing verification evidence yet"), then writes a verifier. The verifier is positioned as a response to a nudge rather than as part of the deliverable. The discipline this standard describes inverts that: the verifier ships alongside the artifact, named in the same plan, run before the artifact is claimed done.

## What this standard defines

1. **The hard rule:** the artifact is not done until the verifier passes. The verifier must be a runnable script, not a mental check.
2. **The four named verifiers** that all agents in this org should know about: `okf-section-check`, `evidence-no-secret-marker`, `linear-routing-classify`, `active-oahu-cta-reconcile`. Each is a named skill with its own SKILL.md describing what it checks.
3. **The counter** that tracks % artifacts that shipped with a pre-written verifier, per week. Target: ≥70%. Below that, the discipline is regressing.
4. **The signal that the discipline broke:** the post-turn nudge fires. Each nudge is a data point that the agent didn't ship the verifier.

## What this standard explicitly does NOT cover

- It does not cover canonical test/lint/build commands. If a project has those, use them. This standard applies to artifacts that lack canonical tests (skills, OKF docs, ad-hoc scripts, single-file deliverables).
- It does not mandate a specific test framework. The verifier can be a Python script, a shell one-liner, a bash test runner — whatever fits the artifact.
- It does not require the verifier to be comprehensive. A 60%-coverage verifier that ships is better than a 100% verifier that doesn't exist.
- It does not cover artifacts whose verifier is the user's manual interaction (e.g., a Slack message). For those, the "verifier" is the user's response.

## Adoption status (as of 2026-07-29)

The discipline is in effect. The four named verifiers ship as skills under `~/.hermes/profiles/orchestrator/skills/verifiers/`. Two of the four (`okf-section-check`, `evidence-no-secret-marker`) have runnable `verify.py` scripts shipped with their SKILL.md. The other two (`linear-routing-classify`, `active-oahu-cta-reconcile`) ship as named skills with their verification logic documented but the script as a follow-up bounded move.

The counter (`verifier-coverage.json`) is live. As of the discipline's launch, the most recent artifact turn reported 75% pre-written coverage (3 of 4 artifacts in this turn shipped with a verifier-first record). HEALTHY verdict.

## The four named verifiers (in detail)

### 1. okf-section-check

**What:** every OKF document has valid frontmatter, status:current, and required core sections.

**Checks:** frontmatter contains `type`, `title`, `description`, `tags`, `timestamp`, `status:current`. Six required sections (Purpose, What this standard defines, What this standard explicitly does NOT cover, Adoption status, Honest lessons, Related work). All relative `.md` links resolve.

**Script:** `~/.hermes/profiles/orchestrator/skills/verifiers/okf-section-check/verify.py`

**Note:** the section check is currently strict for `standards` docs. Reports and runbooks use different section patterns; the script needs type-aware checking as a follow-up.

### 2. evidence-no-secret-marker

**What:** no raw API key, token, or `***` literal placeholder appears in committed files.

**Checks:** scan for `***` substring (3+ asterisks), known key prefixes (sk-or-, lin_api_, AIza, sk-, ghp_, xoxb-, telegram bot tokens). Excludes test fixtures under `/tmp/hermes-verify-*`, archive files, and `.bak` files.

**Script:** `~/.hermes/profiles/orchestrator/skills/verifiers/evidence-no-secret-marker/verify.py`

**Note:** the current pattern is over-broad — it matches any 3+ asterisks, including self-referential mentions of the pattern itself in the verifier's own SKILL.md and in documentation about redaction. Tightening (skip self-references, require `***` next to a key prefix) is a follow-up. The behavior is correct in spirit (catches the pattern); the matches are all documentation, not real secrets.

### 3. linear-routing-classify

**What:** Linear issue labels are mutually consistent with the dependency graph.

**Checks:** for each Linear issue in the team, `agent:*` and `dispatch:*` labels match (e.g., `agent:needs-human-review` ↔ `dispatch:paused`). `dispatch:ready` issues have all `agent:completed` markers in their dependency chain. `agent:needs-human-review` issues have at least one `pending_decisions_for_human[]` entry in the assigned agent's latest handoff.

**Script:** not yet shipped. Documented as the next bounded move.

### 4. active-oahu-cta-reconcile

**What:** every CTA on the active-oahu mirror is reachable and matches its marketing claim.

**Checks:** for each CTA element on the live mirror — the href resolves, the element is visible, the destination matches the visible text, the CTA is reachable from the homepage in ≤3 clicks.

**Script:** not yet shipped. Documented as the next bounded move.

## The counter

`~/.hermes/profiles/orchestrator/state/verifier-coverage.json` tracks, per ISO week, what % of artifacts shipped with a pre-written verifier. Schema:

```json
{
  "schema_version": "1.0.0",
  "weeks": {
    "2026-W31": {
      "artifacts": [
        {
          "ts_utc": "2026-07-29T...",
          "artifact_path": "...",
          "verifier_path": "...",
          "verifier_written_first": true
        }
      ],
      "pre_written": 3,
      "total": 4
    }
  }
}
```

`verifier_coverage.py report` renders:

```
overall: 3/4 = 75.0%    verdict: HEALTHY  (target: 70%)
```

## Honest lessons from the build

- **The discipline is the verifier, not just the script.** Naming the check is the first half. Having a runnable script is the second half. Both halves matter; the naming comes first because it's what future-self reads.
- **Self-referential false positives are real.** The evidence-no-secret-marker verifier flags its own SKILL.md because the SKILL.md describes `***`. This is honest behavior, not a bug — but it's a real cost in verifier signal-to-noise. Tightening the patterns is the follow-up.
- **Per-week coverage is the right granularity.** Daily is too noisy (one or two artifacts per day, no signal). Monthly is too coarse (a 30-day average hides regressions). Weekly catches a missed turn.
- **The post-hoc nudge is data, not a complaint.** Each nudge is a data point that the discipline broke. Recording them, not just being irritated by them, is what makes the discipline actionable.
- **Some artifacts resist pre-written verifiers.** Edits to existing docs, conversations, one-off explanations. For those, the counter has a `verifier_path: null` mode and that's fine. The target is ≥70%, not 100%.

## Verification

- **The discipline itself**: a turn where the post-hoc nudge does NOT fire because the verifier was already shipped.
- **The counter**: `verifier_coverage.py report` returns `verdict: HEALTHY` with `pre_written_pct >= 70`.
- **The named verifiers**: each `verify.py` exits 0 on a known-good artifact and exits 1 on a known-bad one.

## Related work

- [Hermes Session Handoff Discipline](hermes-session-handoff-discipline.md) — the cold-start context primitive this discipline builds on.
- [Hermes Proactive Execution Discipline](hermes-proactive-execution-discipline.md) — the weekly counter discipline that this verifier-coverage counter mirrors.
- [Hermes Projector-Aware Communication Discipline](hermes-projector-aware-communication-discipline.md) — the reply-shape discipline that the `verify_reply_shape.py` verifier enforces.
- [Hermes Runtime Requirements](hermes-runtime-requirements.md) — the assertion script that ships alongside the runtime requirements doc.
