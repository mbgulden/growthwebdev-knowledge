# Frontier model landing → Prismatic integration pattern

Use this note when a model-availability watch fires for a frontier model family and Michael wants it folded into Prismatic Engine.

## Session lesson

When the GPT-5.6 Sol/Terra/Luna watch fired, the important correction was: **treat provider catalog presence as the start of a governed Prismatic integration, not as permission to flip defaults.** Michael wanted next steps and Prismatic incorporation; the durable workflow is a staged capability lane.

## Post-hit sequence

1. **Stop the alert loop immediately.**
   - Pause/remove the availability watch once Michael replies after the hit.
   - Preserve the state file as evidence.
   - Do not keep escalating on a condition that has already been discovered.

2. **Name the availability evidence correctly.**
   - Say “catalog/provider availability,” not “production-ready.”
   - If the model appears via OpenRouter, explicitly note that free-tier/credit behavior still needs a tiny smoke test.

3. **Record the integration decision in OKF.**
   - Add an operations doc with:
     - provider/model slugs found,
     - discovery cron/job id,
     - paused state,
     - staged rollout plan,
     - explicit “do not change global defaults yet” guardrail,
     - fallback mapping.
   - Index the doc in `okf/operations/INDEX.md`.

4. **Create a capability lane, not a default flip.**
   Example shape:

   ```yaml
   frontier_models:
     orchestrator:
       primary: openai/gpt-5.6-sol
       fallback: openai/gpt-5.5
       provider: openrouter
     review:
       primary: openai/gpt-5.6-sol-pro
       fallback: openai/gpt-5.5-pro
       provider: openrouter
     builder:
       primary: openai/gpt-5.6-terra
       fallback: openai/gpt-5.5
       provider: openrouter
     synthesis:
       primary: openai/gpt-5.6-luna
       fallback: openai/gpt-5.5
       provider: openrouter
   ```

5. **Smoke before routing.**
   - Run low-token bounded calls first.
   - Capture only non-secret evidence: status, latency, model slug, non-empty response, rate/cost blocker.
   - Do not expose keys/headers.

6. **Benchmark one safe slice.**
   - Use PR review, architecture synthesis, or dispatch triage.
   - Compare against current baseline before enabling autonomous loops.

7. **Verify changed docs/config with ad hoc scripts.**
   - Use `/tmp/hermes-verify-*` via `tempfile`.
   - For docs, assert model slugs, staged rollout, paused watch, fallback guardrails, and index link.
   - Label as ad hoc targeted verification, not suite green.

## Pitfalls

- Do not conflate OpenRouter catalog visibility with free-tier capacity.
- Do not make the model global default on discovery day.
- Do not leave the discovery cron active after the target has been found.
- Do not create a narrow one-model skill for every landing; keep this as a model-provider/Prismatic integration pattern under the umbrella skill.
