---
name: api-key-management
category: devops
description: Guidelines for securely managing API keys and making API calls, particularly when dealing with environment variable persistence between terminal and execute_code, and specific API authorization formats.
---

## Overview

This skill provides a robust approach to handling API keys and making API calls, especially when using `execute_code` in a Hermes agent environment. It addresses common pitfalls related to environment variable persistence and API-specific authentication requirements.

## Key Learnings

1.  **Environment Variable Persistence (`terminal` vs. `execute_code`):**
    *   Environment variables set using `export` in a `terminal` call **do not persist** into subsequent `execute_code` blocks. Each `execute_code` block runs in a fresh, isolated Python environment.
    *   To make an environment variable (like an API key) available within an `execute_code` block, you must retrieve it from its source (e.g., a `.env` file) *within* that `execute_code` block.

2.  **Robust API Key Retrieval within `execute_code`:**
    *   The recommended pattern for retrieving an API key from a `.env` file (e.g., `/home/ubuntu/.hermes/profiles/orchestrator/.env`) is to use a `terminal` command with `grep` and `cut` within the `execute_code` block.

    ```python
    from hermes_tools import terminal
    
    get_key_command = "grep '^API_KEY_NAME=' /path/to/.env | cut -d= -f2-"
    key_output = terminal(command=get_key_command)
    api_key = key_output['output'].strip()
    
    if not api_key:
        print("Error: API_KEY_NAME not found or is empty.")
    ```

3.  **Using `requests` for API Calls:**
    *   Prefer Python's `requests` library within `execute_code` for making API calls. This avoids complex shell escaping issues that can arise when constructing `curl` commands, especially with nested JSON payloads and dynamic headers.

    ```python
    import requests
    import json
    # ... (API key retrieval as above) ...

    url = "https://api.example.com/endpoint"
    headers = {
        "Authorization": api_key, # Or "Authorization": f"Bearer {api_key}" if needed
        "Content-Type": "application/json",
        "X-Custom-Header": "Value"
    }
    payload = {"key": "value"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    ```

## Pitfalls

*   **Incorrect `Authorization` Header Format:** Always verify the specific `Authorization` header format required by the API. Some APIs require `Bearer ***`, others expect the raw key directly. Refer to `references/` for specific API quirks.
*   **Shell Escaping Hell:** Avoid constructing complex `curl` commands with nested quotes and backslashes in `terminal` calls. Use `requests` in `execute_code` instead.
*   **`/proc/<pid>/environ` is exec-time only — a red herring.** It captures the environment at process start and does NOT show vars set afterwards (dotenv loaders, `os.environ` mutations). Hermes loads the profile `.env` at CLI import, *after* exec, so keys present in the live `os.environ` show ABSENT in `/proc/<pid>/environ`. To verify what a running process can actually see, run a fresh interpreter that invokes the same loader (e.g. `hermes_cli.env_loader.load_hermes_dotenv()` with the right `HERMES_HOME`) and inspect `os.environ`. Never conclude "key missing from process" from `/proc` alone — it cost a full wrong-diagnosis cycle (2026-08-22).
*   **Canonical field name vs alias in provider config.** In Hermes profile `config.yaml` `providers:` entries, the auxiliary/named-custom resolution path (vision / compression / title-gen / curator) reads **`key_env` only** and silently ignores the documented `api_key_env` alias, while the main-chat path lifts the alias. A provider entry declaring only `api_key_env` therefore resolves to an **empty key** on the aux path and 401s on the endpoint (log: `named custom provider ... has no resolvable api_key`), while normal chat works fine — which is what makes it look like an OpenAI/masked-key problem. Fix: declare canonical `key_env` (keeping the alias is harmless). Full diagnosis recipe + probe code: `hermes-agent` skill, "key_env vs api_key_env" pitfall.
*   **Don't reinvent credential lookup per-client.** When multiple API clients (Stripe, GitHub, Google, Linear, Vercel, Cloudflare, etc.) need to share the same credential-resolution rules, build ONE canonical `auth_loader` module that all clients call. Re-implementing credential discovery inside each client is a recurring source of stale env-var bugs. See `references/auth-loader-pattern.md` for the canonical Ned/PWP shape: resolve via explicit arg → env vars → profile `.env` → gcloud ADC → project `.env` → registered secrets, returning `AuthResult(value, source, hint, redaction)` so callers never log raw secrets and can show the user *where* a missing credential was searched.

*   **Overlap note for curator:** `api-key-handling-for-ned` covers the
    same territory (terminal-vs-execute_code persistence, env retrieval).
    Consider consolidation once auth-loader-pattern.md matures; both
    skills currently duplicate the "read .env inside execute_code" recipe.

## Related References

*   [Linear API Authentication Quirks](references/linear_api_auth.md)
*   [auth-loader-pattern.md](references/auth-loader-pattern.md) — canonical
    credential-lookup pattern shared across Stripe / GitHub / Google /
    Linear / Vercel / Cloudflare clients in PWP. Five resolution paths,
    redaction discipline, register_secret write path, end-to-end
    verification recipe, and known gotchas (GITHUB_PAT_KEY, HERMES_PROFILE
    shapes, env-var persistence into execute_code, Google OAuth refresh
    TTL).
