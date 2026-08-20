# Local llama.cpp / GGUF provider check

Session-derived recipe (2026-08-18, George profile): verifying a Hermes `custom_providers` entry that points at a local or LAN llama.cpp server, including whether a claimed multimodal capability is real.

## When

- Michael asks "what model are you using" and the provider is a local/GGUF endpoint.
- A `custom_providers` block references a local `http://<ip>:<port>/v1`.
- The vision auxiliary is pointed at a local model and you must know if it actually works or silently falls through to the fallback.

## Sequence

1. **Read the config endpoint** (secret-safe: redact api_key lines):
   ```bash
   grep -nA 14 '<provider-name>' <profile>/config.yaml | sed -E 's/((api_key|token)[^:]*:).*/\1 <redacted>/I'
   ```
2. **Resolve the real server — do not trust the port.** The port on the Hermes host is frequently owned by an unrelated service. Compare the configured IP against `hostname -I`, then inspect the listener:
   ```bash
   hostname -I
   ss -tlnp | grep ':<port>'
   tr '\0' ' ' < /proc/<pid>/cmdline   # confirm it is actually llama.cpp
   ```
   Pitfall found: local `:8002` was hd-platform's payment server; the real llama.cpp lived on another LAN box (192.168.1.230:8002).
3. **Liveness + model discovery:**
   ```bash
   curl -sS -m 8 http://<ip>:<port>/health
   curl -sS -m 8 http://<ip>:<port>/v1/models
   ```
   Cross-check `n_ctx` in `/v1/models` `details` against the config `context_length`. Cross-check every model ID listed under `custom_providers.<name>.models` against `/v1/models` — IDs the server no longer serves are dead entries (404 if selected). Report them as stale config, not outages.
4. **Text smoke test** (16–24 tokens is enough):
   ```bash
   time curl -sS -m 60 http://<ip>:<port>/v1/chat/completions -H 'Content-Type: application/json' \
     -d '{"model":"<model-id>","messages":[{"role":"user","content":"Reply with exactly: SMOKE-OK"}],"max_tokens":16}'
   ```
   Read `timings`: `prompt_per_token_ms`, `predicted_per_second` (decode speed), and MTP/speculative fields (`draft_n`, `draft_n_accepted`) when present.
5. **Multimodal claim verification** (only when the server or config claims vision, or a vision auxiliary routes here). Do NOT infer "text-only GGUF ⇒ broken vision" from the model name or file type — a Q4 GGUF can be genuinely multimodal. Prove it two ways:
   - **End-to-end through Hermes**: generate a self-checking card with PIL (title, a code string, and a written claim like "Red squares: 3" next to 3 actual red squares + 5 green circles), save to /tmp, run `vision_analyze` asking for exact readback. A correct readback of the *actual* shape counts (not just the written claim) proves real vision.
   - **Direct to the server** (bypasses any fallback, so it proves *the local model* answered):
     ```bash
     B64=$(base64 -w0 /tmp/card.png)
     curl -sS -m 120 http://<ip>:<port>/v1/chat/completions -H 'Content-Type: application/json' \
       -d "{\"model\":\"<model-id>\",\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"How many red squares? Reply with ONLY the number.\"},{\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/png;base64,$B64\"}}]}],\"max_tokens\":120}"
     ```
     Evidence of genuine visual processing: `prompt_tokens` jumps well above the text-only length, and `reasoning_content` describes what it *sees* ("a row of red squares on the left side… one, two, three").
6. **Report** with the standard proof block; NOT_CLAIMING should say which backend answered the Hermes-routed vision call if you only ran step 5a (the text-analysis shape does not identify the backend).

## Pitfalls

- **Reasoning-capable small models eat the completion budget.** With `max_tokens` too small, `content` comes back empty and the whole budget is `reasoning_content` (`finish_reason: "length"`). Give 3–6x headroom or inspect `reasoning_content` before declaring the model "not answering."
- **`vision_analyze` success ≠ local model.** Hermes text-analysis responses don't identify the backend; a 400 from the local model plus gemini fallback looks identical to a direct local success. The direct curl in 5b is the only way to attribute vision to the local model.
- **Stale `HERMES_PROFILE` env var** in the agent process (pointing at another profile) while the service is correctly named for this profile is usually harmless launcher noise — note it, don't "fix" it without checking the running service.
- Dead model IDs under `custom_providers.<name>.models` (e.g. an INT8-MTP variant the server never loaded) are config staleness: one-line removal after confirming `/v1/models`, then re-verify.
