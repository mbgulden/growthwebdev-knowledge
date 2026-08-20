# OKF trust doctrine + Kai PR #329 prompt pattern — 2026-07-19

## What changed

Michael asked to embed Prismatic's strategic answer into the OKF docs so agents understand why the system exists and what success looks like.

The OKF doctrine now emphasizes:

```text
Objective → Key Result → Function → Evidence → Promotion Decision
```

Core positioning:

```text
AI agent output is becoming cheap, but trustworthy AI work is still expensive.
Claude Code writes work.
Hermes runs agents/tools/plugins.
Prismatic governs work.
```

The trust model should not rely only on an adversarial review agent, chat transcript, or model self-report. A successful Prismatic system builds cumulative trust through packet validation, changed-file scope, logs, artifacts, provenance, policy decisions, review state, dashboard visibility, and promotion history.

## Durable workflow lesson

When writing prompts or audits for Prismatic next slices, include the OKF frame directly in the work packet:

| OKF field | Requirement |
|---|---|
| Objective | What trusted/operator-decisionable outcome this slice serves. |
| Key Result | The concrete proof condition, marker, or route/test state. |
| Function | The API/CLI/dashboard/workflow being exercised. |
| Evidence | Commands, logs, markers, artifacts, route probes, CI, browser proof where relevant. |
| Promotion Decision | merge-ready / merged / blocked / needs_approval / manual_review / reject / clean_rebuild / superseded. |

## Kai prompt pattern from PR #329

For completed-work integration closeout prompts, direct Kai to:

1. Live-check PR state, CI, mergeability, `origin/main`, runtime HEAD, and service/routes before acting.
2. Merge only if explicitly authorized.
3. Sync the durable runtime checkout intentionally after merge.
4. Restart the service intentionally and prove local runtime routes.
5. Use exact known proof routes; warn about stale/404 route guesses.
6. Keep real PR creation, Linear writeback, auto-merge, bulk dispatch, overnight autopilot, and production side effects disabled unless Michael explicitly authorizes them.
7. Return compact proof with explicit non-claims.

Useful marker from this session:

```text
AGY_COMPLETED_WORK_PACKET_CLASSIFICATION_RUNTIME_OK
```

Next-slice framing used:

```text
ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK

one ingested completed-work packet
→ packet classification read model
→ dashboard/operator-visible detail
→ dashboard/Linear dry-run plan
→ verified PR dry-run plan
→ explicit promotion decision
→ George/Kai verification packet
→ no real side effects by default
```

## Pitfall

Do not hand Kai/Fred/AGY a prompt that merely says “verify and continue.” For Prismatic work, the prompt should include the OKF row and promotion decision boundary so the agent understands whether it is proving trust, changing product behavior, or only preparing a merge/deploy recommendation.
