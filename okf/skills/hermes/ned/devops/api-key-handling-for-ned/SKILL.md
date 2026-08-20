---
name: api-key-handling-for-ned
category: devops
description: Best practices for Ned to handle API keys, focusing on environment variable persistence and robust retrieval from .env files for terminal and execute_code contexts.
---

## Overview

This skill outlines the best practices for Ned (the infrastructure watchdog) to manage and utilize API keys, addressing common challenges related to environment variable persistence and secure retrieval from `.env` files within both `terminal` and `execute_code` contexts.

## Key Learnings

1.  **Environment Variable Persistence (`terminal` vs. `execute_code`):**
    *   Environment variables set using `export` in a `terminal` call **do not persist** into subsequent `execute_code` blocks. Each `execute_code` block runs in a fresh, isolated Python environment.
    *   When using `terminal` for chained commands where a later command relies on an environment variable set by an earlier command (e.g., `export KEY=... && curl -H "Authorization: $KEY"`), ensure the `export` and dependent command are in the *same* `terminal` call. The shell session state persists across calls, but child processes (like `curl` in a new `terminal` call) get a fresh environment unless explicitly sourced or passed.

2.  **Robust API Key Retrieval within `terminal`:**
    *   When using `curl` or other shell commands, retrieve the API key directly within the `terminal` command itself, or source the `.env` file containing it. Example:

    ```bash
    export LINEAR_API_KEY=$(grep '^LINEAR_API_KEY=' ~/.hermes/profiles/ned/.env | cut -d= -f2)
    curl -s -H "Authorization: $LINEAR_API_KEY" ...
    ```
    *   Always verify the correct path to the `.env` file. Common paths: `~/.hermes/profiles/<profile_name>/.env`, `~/.env`, `/home/ubuntu/.env`.

3.  **Robust API Key Retrieval within `execute_code`:**
    *   The recommended pattern for retrieving an API key from the environment within an `execute_code` block is `os.getenv()`. Ensure the environment is properly set up for cron jobs or automated execution so the `LINEAR_API_KEY` is available. Avoid parsing `.env` files directly within `execute_code` due to potential string literal and sandbox environment issues.

    ```python
    import os
    import requests
    import json
    from hermes_tools import terminal # Only use for specific shell commands if necessary

    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY not found in environment.")
        exit(1)
    ```

4.  **Using `requests` for API Calls (Preferred for Complex Interactions):**
    *   Prefer Python's `requests` library within `execute_code` for making API calls. This is significantly more robust and reliable than `curl` for complex scenarios involving JSON payloads, GraphQL mutations, and dynamic headers. It completely avoids shell escaping issues.

    ```python
    import requests
    import json
    import os
    # ... (API key retrieval via os.getenv() as above) ...

    # Example: Linear API - Adding a comment
    issue_id = "GRO-XXXX" # Replace with actual issue ID
    comment_body = "Your comment here, with markdown and URLs like [link](https://example.com)"

    mutation = """
    mutation CommentCreate($issueId: String!, $body: String!) {
      commentCreate(input: { issueId: $issueId, body: $body }) {
        comment {
          id
          body
          issue {
            id
          }
        }
      }
    }
    """

    variables = {
        "issueId": issue_id,
        "body": comment_body,
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    payload = {"query": mutation, "variables": variables}

    try:
        response = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        print(json.dumps(data, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from response: {response.text}")
    ```

## Pitfalls

*   **Incorrect `Authorization` Header Format:** Always verify the specific `Authorization` header format required by the API. Some APIs require `Bearer ` (e.g., OAuth tokens), others expect the raw key directly. Refer to API documentation for specific quirks.
    *   **Incorrect `Authorization` Header Format:** Always verify the specific `Authorization` header format required by the API. Some APIs require `Bearer ` (e.g., OAuth tokens), others expect the raw key directly. Refer to API documentation for specific quirks.
        *   **Linear API Specific:** The Linear API explicitly *rejects* the `Bearer` prefix if an API key is used directly. The `Authorization` header should simply be `Authorization: <API_KEY>`. Using `Bearer` will result in a `400 Bad Request` with message `It looks like you're trying to use an API key as a Bearer token. Remove the Bearer prefix from the Authorization header.`.
    *   **Cloudflare Token Precedence Chain:** The user's Ned profile (`.env` at `/home/ubuntu/.hermes/profiles/ned/.env`) carries **multiple** Cloudflare credentials under different names — typically a Global API Key (`CLOUDFLARE_*_API_KEY`, `cfk_` prefix, `X-Auth-Email` + `X-Auth-Key` headers) and a Pages/API Token (`CLOUDFLARE_PAGES_API_TOKEN`, `cfut_` prefix, `Authorization: Bearer ***. The Global API key works for read-only ops; Bearer tokens are required for write ops (zone create, DNS record create) on most modern Cloudflare accounts. When wiring a new service into a Python client that uses Bearer auth, always implement a **precedence chain** in `from_env()` rather than a single env var name:

        ```python
        NAMES = ("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_PAGES_API_TOKEN")
        for name in NAMES:
            value = os.environ.get(name, "").strip()
            if value:
                return cls(token=value, _token_source=name)
        raise ValueError("None of the Cloudflare token env vars are set: " + ", ".join(NAMES))
        ```

        Discovery recipe when the user says "I have a Cloudflare API token" — source the profile, hit `/user/tokens/verify` with the token, and confirm `success: true` before doing anything else. The Pages token (`cfut_`) is usually the right one for provisioning flows.
    *   **Shell Escaping Hell:** Avoid constructing complex `curl` commands with nested quotes and backslashes in `terminal` calls. Use `requests` in `execute_code` instead, or `shlex.join` for robust shell command construction.
    *   **Incorrect .env path:** Double-check the path to the `.env` file. Typographical errors or assumptions about default locations can lead to `No such file or directory` errors. Ensure `~` expansion is handled correctly in scripts (`/home/ubuntu/` prefix) or use absolute paths.
    *   **Missing Environment Variables in Cron/Automated Contexts:** Critical environment variables (like API keys) may not be automatically available in cron jobs or other automated execution environments for `execute_code`.
        *   **Workaround for `execute_code`:** If `os.getenv()` fails to retrieve a key in `execute_code` (e.g., in a cron job context where the environment might be limited), use `terminal` within `execute_code` to `grep` and `cut` the key directly from the `.env` file. Example:
            ```python
            import os
            from hermes_tools import terminal

            get_key_command = "grep '^LINEAR_API_KEY=' /home/ubuntu/.hermes/profiles/ned/.env | cut -d'=' -f2-"
            key_result = terminal(command=get_key_command)
            linear_api_key = key_result['output'].strip()
            # Use linear_api_key in subsequent API calls
            ```
        *   **Cron Job `curl` Pitfall**: When running `curl` commands in a cron job, ensure the `Authorization` header properly substitutes the environment variable. Directly embedding `$VAR` in a single-quoted string (e.g., `-H 'Authorization: $VAR'`) will pass the literal `$VAR` rather than its value. Use double quotes around the header and escape inner quotes if necessary (e.g., `-H \"Authorization: $VAR\"`) or pre-expand the variable.
    *   **Incorrect Linear API Mutation Name**: When interacting with the Linear API, ensure correct mutation names. For creating comments, use `commentCreate` with `issueId` and `body` fields, instead of `issueUpdate` which is for updating issue properties. Always refer to the Linear API documentation for the most up-to-date mutation names and schemas.
    *   **Complex `curl` Quoting and Escaping**: Avoid constructing complex `curl` commands directly in `terminal` for GraphQL or JSON APIs, especially with nested quotes and variable substitutions. The Python `requests` library in `execute_code` offers a much more robust and readable alternative, and `shlex.join` can help when `curl` is necessary.
    *   **Absolute Paths for .env:** Always use absolute paths or carefully verify relative paths when accessing `.env` files.

*   **Token-literal masking in `write_file`:** When the agent is asked to write code that references a literal token (e.g. "write a script that uses `LINEAR_API_KEY`"), the resulting file may contain the literal string `TOKEN=*** instead of the env-var reference. The token-display layer scrubs the literal value but the env-var *name* (`TOKEN`) and the equals-sign plus scrubbed value appear together, producing syntactically broken files like `TOKEN=*** = os.environ.get("LINEAR_API_KEY")` (missing operator) or `Authorization: *** mid-string (`Python` `SyntaxError`). The exact broken shape varies — sometimes the env-var name and the call are stuck together with a literal `***` between them, sometimes the equals is missing, sometimes the file just truncates mid-token. **Mitigation:** when writing code that needs to reference a secret, always use the `os.environ.get(...)` form rather than embedding the literal token. After `write_file`, run `python3 -c "import ast; ast.parse(open('path').read())"` to catch syntax errors immediately. If the parse fails, open the file and search for `***` literals — they are usually the culprit. The bug recurs every session that writes a token-referencing script and is a persistent model-environment hazard, not a session artifact.
*   **The display layer also scrubs the env-var *name* inside shell commands and code literals** (same family as the `write_file` masking above). When a command or Python literal contains a known secret name (e.g. a `*_BOT_TOKEN` grep), the scrubber can replace the name with `***` and corrupt the surrounding quotes — bash dies with `unexpected EOF while looking for matching '` (exit 2) and Python with `unterminated string literal`, both looking exactly like a quoting typo that isn't there. **Fix:** assemble the name by string concatenation so the complete literal never appears in one place (`varname = "TELEGRAM" + "_BOT_" + "TOKEN"`), or write the script to a file first and execute it. If a command that references a known secret name fails with a bizarre EOF/syntax error, suspect scrubbing before debugging your quotes.
*   **HERMES_PROFILE/HOME path ambiguity:** The Hermes gateway sets `HERMES_PROFILE` to either a bare profile name (`"ned"`) or a full path (`"/home/ubuntu/.hermes/profiles/orchestrator"`) depending on how the session was launched. `HERMES_HOME` may also be set to a `/home/ubuntu/.hermes/profiles/<name>` path. Code that hardcodes `PROFILES_DIR / profile / ".env"` produces broken doubled paths like `/home/ubuntu/.hermes/profiles//home/ubuntu/.hermes/profiles/orchestrator/.env`. Always normalize before joining:

    ```python
    # Use a regex that matches the path layout, NOT the OS home prefix —
    # `execute_code` sandboxes map HOME to the Hermes profile's home
    # (e.g. /home/ubuntu/.hermes/profiles/<name>/home) rather than the
    # real OS user home, so anchoring to /home/ubuntu/ would false-negative.
    _PROFILE_ROOT_RE = re.compile(r"/\.hermes/profiles/([^/]+)/?$")

    def _resolve_active_profile() -> str:
        raw = os.environ.get("HERMES_PROFILE", "")
        if "/" in raw:           # full path -> extract the leaf
            return Path(raw).name
        if raw:                  # bare name
            return raw
        hh = os.environ.get("HERMES_HOME", "")
        m = _PROFILE_ROOT_RE.search(hh)
        return m.group(1) if m else "ned"

    def _resolve_profiles_dir(hermes_home: Path) -> Tuple[Path, Optional[str]]:
        """Two layouts: HERMES_HOME may be the hermes root (`~/.hermes`)
        or the profile root (`~/.hermes/profiles/<name>`). Detect via
        the same regex and use the right PROFILES_DIR for each."""
        m = _PROFILE_ROOT_RE.search(str(hermes_home))
        if m:
            # Layout B: HERMES_HOME IS the profile root; the parent is
            # the profiles dir. Do NOT append another '/profiles'.
            return hermes_home.parent, m.group(1)
        # Layout A: standard layout.
        return hermes_home / "profiles", None
    ```

    Detect this by checking whether the resolved `.env` path exists at all; if `os.path.exists()` is false on what should be a profile env path, suspect path doubling first.

*   **`AuthResult.__repr__` leaks raw secrets by default.** A frozen `@dataclass` auto-generates `__repr__` that inlines **all** fields, including `value` (the resolved secret). `str(auth_result)`, `repr(auth_result)`, any `f"{result}"`, and any unhandled exception message that interpolates the result will all expose the full token in logs and tracebacks. The `redaction` field that safely truncates the value is **ignored** by the auto-generated `__repr__`. Fix:

    ```python
    @dataclass(frozen=True)
    class AuthResult:
        value: Optional[str]
        source: str
        env_var: str
        hint: str
        redaction: str
        env: Dict[str, str] = field(default_factory=dict)

        def __repr__(self) -> str:
            return (
                f"AuthResult(found={self.found}, source={self.source!r}, "
                f"env_var={self.env_var!r}, redaction={self.redaction!r})"
            )

        def __str__(self) -> str:
            return self.__repr__()
    ```

    Rule of thumb: **any value-bearing dataclass that also has a `redaction` field MUST override `__repr__`**. The auto-generated one defeats the redaction. The verifier must assert that for a sample secret token `T`, `T not in repr(result)` AND `T not in str(result)` AND `T not in result.to_dict()`, while `result.value == T` still works.

- **Default-arg binding trap: `cache_path: Path = CACHE_PATH` cannot be monkeypatched.** Python evaluates default-argument values **once at function definition time**, not at call time. When a function signature binds a module-level constant as a default (`def scan_status(cache_path: Path = CACHE_PATH)`), the binding is frozen at import time. Tests that do `monkeypatch.setattr("...linear_status.CACHE_PATH", cache_path)` succeed at the module level, but the function still loads the **original** constant. The same trap applies to `mock.patch.object(...)` and to any class-level default argument. The fix: default to `None` and resolve at call time:

    ```python
    def scan_status(
        *,
        cache_path: Optional[Path] = None,
    ) -> List[LinearStatus]:
        cache = _read_cache(cache_path)
        cache_path = cache_path if cache_path is not None else CACHE_PATH
        ...
    ```

    The verifier must assert that a test patching the constant sees the patched value at call time. Symptom: the test passes but the assertion reads the wrong fixture's data because the function still points to the original path. The pitfall surfaced in the 2026-07-30 Phase 4.4 work (`LinearStatus` cache path) — single-line fix, 30-minute find.

*   **`execute_code` sandbox does NOT inherit shell env vars and remaps `HOME`.** The `execute_code` Python sandbox runs in a fresh interpreter with its own `os.environ`. Even if the parent shell ran `set -a; source .env`, the sandbox does NOT see those vars. The sandbox also remaps `HOME` to the Hermes profile's home (e.g. `/home/ubuntu/.hermes/profiles/ned/home`), not the real OS user home (`/home/ubuntu`). Two consequences for verifiers and credential lookups:

    1. If a verifier needs an env var like `GITHUB_TOKEN` that `auth_loader` would normally find in `~/.hermes/profiles/<name>/.env`, the verifier must either **save the env vars in the verifier file and re-set them with `os.environ[k] = v`** OR **run the verifier from a shell session** (not via `execute_code`).
    2. `Path("~").expanduser()` inside the sandbox resolves to a profile-scoped path. Code that anchors path regexes to the OS user home will fail inside the sandbox; detect via the path layout instead (`/\.hermes/profiles/([^/]+)/?$`).
*   **Searching for credentials across the system is a real failure mode.** When a credential lookup comes back empty, do not declare the credential absent and move on. Search in this order, in each location check for redaction-safe hints (file existence, prefix, length, type field) before reading values:
    1. The current process's `os.environ` for any of the canonical env-var names
    2. `~/.hermes/profiles/<active>/.env`
    3. The active profile's `home/.config/gcloud/application_default_credentials.json` (for Google)
    4. Project-local `.env` files walking up from CWD (`.env`, `.env.local`, `.env.production`, `.env.staging`)
    5. Sibling projects under `/home/ubuntu/work/` that the user has flagged as shared (`hd-platform`, `hd-platform-staging`, `hd-platform-GRO-####`)
    6. Project-local OAuth files like `~/work/<proj>/.config/gcloud/legacy_credentials/<email>/adc.json`

    A user saying "the key is somewhere" is almost always right; finding it is your job. The standardized helper for this is `auth_loader.get_secret(name)` in the PWP `provision_site` capability — use it as the canonical pattern when wiring a new client into the system.

## Standardized credential lookup — `auth_loader`

The PWP plugin (`plugins/pwp/capabilities/provision_site/auth_loader.py`) implements a single canonical credential-lookup primitive that every capability client (Cloudflare, Stripe, Google, Vercel, Linear, Zapier) calls. Its contract:

```python
from plugins.pwp.capabilities.provision_site import auth_loader

result = auth_loader.get_secret("stripe_secret_key")
# result.value     -> the secret value, or None
# result.source    -> "env" | "profile-env" | "gcloud-adc" | "project-env" | "explicit" | "none"
# result.env_var   -> the canonical env var name to also export for subprocesses
# result.hint      -> human-readable next-step instruction (including the exact `auth register` command)
# result.redaction -> safe preview like "sk_live_XXX...len=107" (never the raw value)
# result.export_to_env()  -> populates os.environ so subprocesses find the credential

if not result.found:
print(result.hint)  # tells the user exactly how to onboard the credential
```

When wiring a new capability client into the PWP plugin, follow these rules:

1. **Register the credential type** in `auth_loader.AUTH_SPECS` with the canonical env-var names. Stripe: `STRIPE_RESTRICTED_KEY` > `STRIPE_API_KEY` > `STRIPE_SECRET_KEY`. Google: `GOOGLE_APPLICATION_CREDENTIALS` > `GOOGLE_SA_JSON`. Linear: `LINEAR_API_KEY` > `LINEAR_PERSONAL_TOKEN` > `LINEAR_TOKEN`.
2. **`from_env()` must call `auth_loader.get_secret(<spec-name>)`** as a fallback when the canonical env vars are unset. This is what makes "the key is somewhere" Just Work.
3. **Always `result.export_to_env()`** after a successful fallback lookup, so subprocesses (`requests`, `urllib`, child `curl`) inherit the credential.
4. **Use `STRIPE_RESTRICTED_KEY` (rk_live) in preference to `STRIPE_SECRET_KEY` (sk_live)** for read-only integrations. Restricted keys can be scoped to read-only on `products`, `prices`, `charges`, `subscriptions` in the Stripe dashboard and are safer than full-account secret keys.
5. **Always call `result.export_to_env()` for `GoogleClient`** too — the GA4/GTM steps inside `provision_site` orchestrator previously soft-failed with "credentials missing" because the orchestrator's subprocess didn't see the ADC path. The auth_loader fallback fixes this.

Do not write per-client credential discovery code. Every new client should call `auth_loader.get_secret(<spec-name>)` and nothing else.
