# Mass-rewriting Hermes auxiliary.* blocks from a cloud provider to a local custom provider

When Michael cancels a cloud subscription (e.g. drop OpenAI Codex), every
`auxiliary.*` block in every `~/.hermes/profiles/<profile>/config.yaml`
that points at `openai-codex` (or any other cloud provider) becomes a
broken path. The fix is a single-pass rewrite of the auxiliary section —
one `provider`/`model`/`base_url` triple per block — not 13 individual
`patch` calls.

**Companion reading:**
- `vision-and-auxiliary-routing-2026-08.md` — captures the *single-block* `auxiliary.vision` pitfall
- `llama-server-runtime-gotchas.md` Gotcha 11/12 — the slot-monopolization `provider.max_tokens` cap
- `auxiliary.vision` block (the first one to migrate, before mass rewrite)

## When to use this recipe

Use when **all** of the following hold:

- `~/.hermes/profiles/<profile>/config.yaml` has multiple `auxiliary.*` blocks pointing at the same cloud provider (typically `openai-codex`, `gpt-5.6-terra`, `https://chatgpt.com/backend-api/codex`).
- Michael has stopped paying for that provider and wants everything routed through a local llama-server instead.
- A `custom:<NAME>-local` provider block already exists at the top of the same file (the local wiring shape from the vision routing pitfall).

Do not use when only one or two auxiliary blocks need migrating — a `patch` call is faster and more surgical than a Python rewrite for small counts.

## Block shape (what to rewrite)

The standard auxiliary block in Hermes looks like:

```yaml
web_extract:
    provider: openai-codex
    model: gpt-5.6-terra
    base_url: https://chatgpt.com/backend-api/codex
    timeout: 360
    extra_body: {thinking: disabled}
    fallback_chain:
    - provider: google
      model: gemini-2.5-flash
```

Three lines identify the provider: `provider`, `model`, `base_url`. Replace those three atomically; leave everything else (timeout, extra_body, fallback_chain) untouched.

## The recipe (Python, in-place)

Run from `webtop-hermes` (or any host with Python + write access to the profile YAMLs):

```python
import re

profiles = {
    'kai': {
        'provider': 'custom:qwen27b-kai-local',
        'model':    'local-qwen-27b-q4-kai',
        'base_url': 'http://192.168.1.230:31002/v1',
    },
    'ned': {
        'provider': 'custom:qwen27b-ned-local',
        'model':    'local-qwen-27b-q4-ned',
        'base_url': 'http://192.168.1.230:31003/v1',
    },
}

# Match the 3 identifying lines, regardless of which keys come first
# inside the block (some blocks put `model:` before `provider:`).
PATTERN = re.compile(
    r'(    provider: )openai-codex\n'
    r'(    model: )gpt-5\.6-terra\n'
    r'(    base_url: )https://chatgpt\.com/backend-api/codex'
)

for profile, cfg in profiles.items():
    path = f'/home/ubuntu/.hermes/profiles/{profile}/config.yaml'
    with open(path) as f:
        text = f.read()
    before = text.count('openai-codex')
    text = PATTERN.sub(
        lambda m, c=cfg: f"{m.group(1)}{c['provider']}\n{m.group(2)}{c['model']}\n{m.group(3)}{c['base_url']}",
        text,
    )
    after = text.count('openai-codex')
    with open(path, 'w') as f:
        f.write(text)
    print(f'{profile}: {before - after} blocks rewritten, '
          f'{after} openai-codex references remain')
```

The script reports the residual `openai-codex` count. Anything > 0 is a block the regex missed — usually because that block has a different key order (e.g. `model:` before `provider:`, like `auxiliary.curator` on Ned). Patch those one-by-one with `patch`.

## Cleanup: removing dead provider definitions

After rewriting, the `openai-codex:` top-level provider definition (if present) becomes dead code. Remove it to keep the file small:

```python
# Remove the entire `openai-codex:` provider block, including any nested keys.
text = re.sub(
    r'  openai-codex:\n(?:    [^\n]*\n)+',
    '',
    text,
)
```

If `openai-codex` is referenced anywhere else in the file after this, the agent didn't catch a block — re-grep manually.

## Verification

After running the rewrite, write a verifier that checks every auxiliary block:

```python
import yaml, sys

OUT = []
def check(name, ok, detail=""):
    line = "PASS" if ok else "FAIL"
    OUT.append((ok, line, name, detail))
    print(f"{line} [{name}] — {detail}")

EXPECTED_AUX = [
    "vision", "web_extract", "compression", "session_search",
    "skills_hub", "approval", "mcp", "title_generation",
    "tts_audio_tags", "triage_specifier", "kanban_decomposer",
    "profile_describer", "monitor",
]
PROFILE_EXTRA = {"ned": ["curator"]}

for profile, port in [("kai", 31002), ("ned", 31003)]:
    path = f"/home/ubuntu/.hermes/profiles/{profile}/config.yaml"
    cfg = yaml.safe_load(open(path))
    raw = open(path).read()

    check(f"{profile}-no-openai-codex", "openai-codex" not in raw,
          f"openai-codex count={raw.count('openai-codex')}")

    expected_provider = f"custom:qwen27b-{profile}-local"
    expected_model    = f"local-qwen-27b-q4-{profile}"
    expected_base_url = f"http://192.168.1.230:{port}/v1"

    aux = cfg.get('auxiliary', {})
    aux_names = set(EXPECTED_AUX) | set(PROFILE_EXTRA.get(profile, []))
    for name in aux_names:
        block = aux.get(name, {})
        check(f"{profile}-{name}-provider-local",
              block.get('provider') == expected_provider,
              f"provider={block.get('provider')!r}")
        check(f"{profile}-{name}-model-local",
              block.get('model') == expected_model,
              f"model={block.get('model')!r}")
        check(f"{profile}-{name}-base-url-local",
              block.get('base_url') == expected_base_url,
              f"base_url={block.get('base_url')!r}")

passed = sum(1 for ok, *_ in OUT if ok)
print(f"\n{passed}/{len(OUT)} PASS")
sys.exit(0 if passed == len(OUT) else 1)
```

This is the canonical verifier for the mass-rewrite. Any `FAIL` line points at a specific block that escaped the rewrite; patch by hand and re-run.

## Caveats

- **Some auxiliary blocks have `api_key:` or `api_key_env:` fields.** The regex above does not match those. The local provider does not need an API key (it accepts any string for `llama-local`), but if a block references `api_key_env: OPENAI_API_KEY` (for example), that env var reference becomes dead. Hermes silently ignores dead env-var refs in auxiliary blocks, so this is cosmetic — leave them for now.
- **Fallback chains (`fallback_chain: - provider: google - model: ...`) must stay intact.** The regex preserves everything outside the three identifying lines. If the fallback chain still references a paid API, rewrite the fallbacks separately — that's a separate concern from the main migration.
- **Top-level `fallback_providers:`** (a list, not a dict) may also reference the old provider. Check and update explicitly with `patch` since the structure is different from `auxiliary.*` blocks.
- **Live verification after restart.** Filesystem-level evidence is necessary but not sufficient: `hermes --profile <profile> -z 'Reply OK'` exercises the real path. Run one probe per profile after `/restart` to confirm the rewrite took effect at runtime.

## Why this is the right level of automation

13 hand-patches is 13 places to introduce a typo. A regex rewrite is one place to make sure the pattern was right, plus a single verifier to confirm all 13. The work scales linearly with profiles but not with the number of aux blocks per profile — once the regex matches the common shape, the cost is verifying the residuals.
