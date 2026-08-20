# Model-availability watch cron pattern — July 2026

Use when Michael wants a scheduled Hermes cron to watch refreshed provider/model lists for a newly released model and alert only when it appears.

## Durable pattern

1. **Make the watch a no-agent profile-local script.**
   - Store under the active profile `scripts/` directory.
   - Use `cronjob(action="create", no_agent=True, script="relative_script.py", schedule="every 3h", deliver="origin")` for direct alert delivery.
   - Keep normal/absent checks silent: no-agent stdout should be empty unless there is something actionable.

2. **Force a real provider refresh, then fall back safely.**
   - Prefer Hermes internals that clear and rebuild `provider_models_cache.json`, equivalent to model picker `--refresh` behavior.
   - If refresh fails, read the last cache only as a fallback and record the blocker/state; do not invent availability.
   - Redact or avoid printing auth/provider token output from refresh commands.

2a. **If the user names a specific provider/account, isolate it before matching.**
   - Example: “the OpenAI OAuth codex GPT-5.6, the one I’m using to run GPT-5.5” means `openai-codex` only.
   - Do not let OpenRouter/OpenAI API/Copilot hits satisfy a Codex OAuth watch.
   - The alert copy should state the scoped provider and explicitly say excluded providers are ignored.
   - Verification must include negative fixtures proving non-target-provider GPT-5.6 hits stay silent.

3. **Normalize model variants aggressively.**
   - Compare exact targets and variations after lowercasing, provider-prefix stripping, and separator normalization.
   - Handle examples like:
     - `gpt-5.6`
     - `GPT 5.6 Sol`
     - `openai/gpt_5_6_terra`
     - `openai/gpt-5-6-luna`
   - Convert `gpt-5-6[-suffix]` to `gpt-5.6[-suffix]` before matching.

4. **Persist alert state.**
   - Keep a JSON state file under the profile `state/` directory with `last_checked`, `last_result`, `hits`, `first_seen`, `last_seen`, and `alert_count`.
   - On no-hit, update state and stay silent.
   - On hit, increment `alert_count` and print the requested alert text.

5. **User-specific celebration/escalation contract.**
   - For Michael’s GPT-5.6 watch, the alert should start with “it’s here…” and escalate each no-response run toward an emoji-wall celebratory “ITS HERE!!!!”.
   - The alert should tell him to reply to stop escalation and trigger the follow-up workflow installation.
   - If he replies after the hit, stop/pause/remove the escalation cron before installing the requested workflow skill.

6. **Verification shape.**
   - Use a `/tmp/hermes-verify-*` script created via `tempfile.mkstemp`.
   - Include:
     - `py_compile` for the watch script
     - normalization fixtures for exact and variant names
     - absent detection fixture proving no hits/no alert condition
     - present detection fixture for every target variant
     - provider isolation fixture proving GPT-5.6 in non-target providers does not alert when the watch is scoped
     - escalation/message assertions from “it’s here…” to “ITS HERE!!!!” or scoped provider-specific alert copy
     - real smoke run of the script with bounded timeout
     - cron job config assertion: enabled, no-agent, correct relative script, schedule, delivery
   - Label result as ad hoc targeted verification only, not full suite green.

## Pitfalls

- Do not alert every absence; absent checks must be silent to avoid notification fatigue.
- Do not rely only on public launch articles. The actionable trigger is the refreshed provider list for the configured Hermes account/provider.
- Do not store job IDs or transient cache timestamps in memory; keep them in the session report/state file.
- Do not install the follow-up workflow skill until the user replies after the hit; otherwise the system will encode a model-specific workflow before access is real.
