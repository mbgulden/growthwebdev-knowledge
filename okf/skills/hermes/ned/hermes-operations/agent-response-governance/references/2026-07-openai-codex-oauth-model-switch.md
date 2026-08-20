# OpenAI-Codex OAuth model switch — 2026-07

Reusable pattern from a Ned profile switch from `gpt-5.5` to `gpt-5.6` over the existing `openai-codex` OAuth provider.

## When this applies

Use when Michael asks whether a newer GPT/Codex model can be used through Hermes OAuth, or asks to switch a Hermes profile to a newer OpenAI-Codex OAuth model.

## Safe workflow

1. **Load Hermes guidance if available**
   - Try the local `hermes-agent` skill when present.
   - If it is not installed in the active profile, proceed with live CLI discovery (`hermes --help`, `hermes model --help`, `hermes auth --help`) and say so only if relevant.

2. **Check credential and provider state without exposing tokens**
   - Use `hermes auth list` or `hermes auth status <provider>`.
   - For OpenAI ChatGPT/Codex OAuth, the observed provider was `openai-codex` with base URL `https://chatgpt.com/backend-api/codex`.
   - Do not read or paste OAuth token files/auth JSON.

3. **Probe the target model before changing defaults**
   - Run a minimal one-shot with explicit provider/model:
     ```bash
     HERMES_AGENT_DISABLE_STREAM=1 hermes -z 'Reply with exactly: model-ok' \
       --provider openai-codex -m gpt-5.6 --ignore-rules --toolsets ''
     ```
   - Treat the exact expected reply as proof the model works through OAuth.

4. **Change config through the Hermes CLI**
   - Security-sensitive Hermes config files may refuse direct patch/write edits. Use `hermes config set`.
   - Example primary model switch:
     ```bash
     hermes config set model.default gpt-5.6
     ```
   - For auxiliary slots that already use the same OAuth provider/base URL, set their `.model` keys too:
     ```bash
     hermes config set auxiliary.vision.model gpt-5.6
     hermes config set auxiliary.web_extract.model gpt-5.6
     hermes config set auxiliary.compression.model gpt-5.6
     hermes config set auxiliary.session_search.model gpt-5.6
     hermes config set auxiliary.skills_hub.model gpt-5.6
     hermes config set auxiliary.approval.model gpt-5.6
     hermes config set auxiliary.title_generation.model gpt-5.6
     hermes config set auxiliary.triage_specifier.model gpt-5.6
     hermes config set auxiliary.mcp.model gpt-5.6
     hermes config set auxiliary.tts_audio_tags.model gpt-5.6
     hermes config set auxiliary.kanban_decomposer.model gpt-5.6
     hermes config set auxiliary.profile_describer.model gpt-5.6
     hermes config set auxiliary.monitor.model gpt-5.6
     hermes config set auxiliary.curator.model gpt-5.6
     ```
   - Do not invent unknown auxiliary sections just because their names sound plausible. If accidental scratch keys are created, remove them and validate YAML.

5. **Verify after changing defaults**
   - YAML parse/profile config check:
     ```bash
     python3 - <<'PY'
     import yaml
     from pathlib import Path
     p=Path('/home/ubuntu/.hermes/profiles/ned/config.yaml')
     yaml.safe_load(p.read_text())
     print('gpt-5.5_count=', p.read_text().count('gpt-5.5'))
     print('gpt-5.6_count=', p.read_text().count('gpt-5.6'))
     PY
     ```
   - One-shot using default provider/model:
     ```bash
     HERMES_AGENT_DISABLE_STREAM=1 hermes -z 'Reply with exactly: final-gpt-5.6-ok' \
       --ignore-rules --toolsets ''
     ```
   - Run the profile audit when available:
     ```bash
     python3 /home/ubuntu/.hermes/profiles/ned/scripts/hermes_profile_audit.py --profile ned --verify
     ```

## Reporting caveat

Active Telegram/gateway sessions can remain pinned to the model they started with until a new session or gateway reload. Say this explicitly: future invocations should use the new default; the current conversation may not switch mid-session.
