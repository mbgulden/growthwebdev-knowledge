# Kai GPT-5.6 Terra update reference — 2026-07-23

## When this applies

Use for requests like: “update this Hermes profile to ChatGPT 5.6 Terra” or another specific model on an existing profile.

## Working pattern

1. Try to load the `hermes-agent` skill if present. If absent, use CLI discovery:
   - `hermes --help`
   - `hermes config --help`
   - `hermes config set --help`
2. Confirm the active profile config path with:
   - `hermes config path`
   - `hermes config show`
3. Discover/confirm the model ID from local model metadata if needed. For Terra, usable IDs observed:
   - `gpt-5.6-terra`
   - `openai/gpt-5.6-terra`
   - OpenRouter metadata listed context length `1050000` and max completion tokens `128000` for GPT-5.6 Terra.
4. Use `hermes config set`, not direct file patching, for the protected config file:
   - `hermes config set model.default gpt-5.6-terra`
   - Keep provider unchanged unless the user asked to change provider.
5. Update auxiliary slots as well when they are explicitly pinned to the old model. In this session, these slots existed and were set:
   - `auxiliary.vision.model`
   - `auxiliary.web_extract.model`
   - `auxiliary.compression.model`
   - `auxiliary.session_search.model`
   - `auxiliary.skills_hub.model`
   - `auxiliary.approval.model`
   - `auxiliary.mcp.model`
   - `auxiliary.title_generation.model`
   - `auxiliary.tts_audio_tags.model`
   - `auxiliary.triage_specifier.model`
   - `auxiliary.kanban_decomposer.model`
   - `auxiliary.profile_describer.model`
   - `auxiliary.monitor.model`
6. Verify:
   - `hermes config show` displays the new main model and key auxiliary model overrides.
   - Search/read config confirms no stale `gpt-5.5` references in configured model slots.
   - `hermes config check` exits `0`.
   - Live smoke test returns expected text.

## Smoke-test environment pitfall

A direct smoke test failed once with `File name too long` because the running gateway shell had unusual exported environment/HOME state. The durable lesson is not that Hermes smoke tests fail; it is to isolate the environment for CLI verification:

```bash
env -i HOME=/home/ubuntu PATH=$PATH USER=ubuntu \
  HERMES_HOME=/home/ubuntu/.hermes/profiles/kai \
  HERMES_PROFILE=kai \
  hermes -z 'Reply with exactly: terra-ok' \
  --provider openai-codex -m gpt-5.6-terra
```

Expected output in this session:

```text
terra-ok
```

## Reporting caveat

After config change, say clearly that the current running chat may still be using the model it launched with; new sessions and gateway restarts pick up the updated config.
