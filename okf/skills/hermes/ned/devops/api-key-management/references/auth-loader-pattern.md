# auth_loader — Standardized Credential Lookup (Ned / PWP pattern)

## Why

When a single project accumulates multiple API clients (Stripe, GitHub,
Google, Linear, Vercel, Cloudflare, Zapier…), every client ends up
re-implementing "where do I get the credential from?". They drift in
priority order, they leak raw secrets into logs, and the user gets a
different "set ENV X to enable" hint from each one. The fix is one
canonical lookup function.

## The pattern

```python
# auth_loader.py — every API client calls this

@dataclass
class AuthResult:
    value: Optional[str]   # the secret (or None if missing)
    source: str            # "explicit", "env", "profile-env",
                           # "project-env", "gcloud-adc", "registered", "none"
    env_var: str           # the env var that WOULD have worked
    hint: str              # actionable: "set X, or run Y, or register Z"
    redaction: str         # safe-to-log prefix (e.g. "ghp_YTz...len=40")

def get_secret(spec_name: str) -> AuthResult:
    spec = _SPECS[spec_name]   # { env_vars: [...], paths: [...], ... }
    # 1. explicit arg
    # 2. any of spec.env_vars in os.environ
    # 3. profile .env at ~/.hermes/profiles/<active>/.env (or HERMES_HOME override)
    # 4. project .env walked from cwd up + WORK_DIR/<known-project>/.env
    # 5. gcloud ADC at ~/.config/gcloud/application_default_credentials.json
    # 6. registered via auth register --type <name> --value <secret>
    return AuthResult(value, source, env_var, hint, redaction)
```

Resolution priority is documented once. Clients call it like:

```python
class StripeClient:
    @classmethod
    def from_env(cls) -> "StripeClient":
        r = auth_loader.get_secret("stripe_secret_key")
        if not r.found:
            raise StripeError(r.hint)
        return cls(api_key=r.value, token_source=f"auth_loader:{r.source}")
```

The `token_source` lets logs/verifiers show *where* the credential came
from — proving end-to-end discovery, not just "it worked".

## Five resolution paths (priority order)

1. **Explicit argument** — tests pass `token="ghp_..."` for hermetic mode
2. **Environment variables** — `STRIPE_SECRET_KEY`, etc. (multi-alias: try
   each `spec.env_vars` in order)
3. **Active profile `.env`** — `~/.hermes/profiles/<HERMES_PROFILE>/.env`
   or full path per `HERMES_PROFILE` env var
4. **Project `.env`** — walk up from cwd looking for `.env`, plus known
   sibling project dirs under `WORK_DIR` (e.g. `WORK_DIR/hd-platform/.env`)
5. **gcloud ADC** — `~/.config/gcloud/application_default_credentials.json`
   (for Google scopes only)

## Path portability rules

NEVER hardcode `/home/ubuntu/...` — Prismatic's commit gate blocks
those. The defaults MUST be environment-variable-driven:

```python
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
WORK_DIR    = Path(os.environ.get("WORK_DIR",    "~/work")).expanduser()
USER_HOME   = str(Path("~").expanduser())
# When matching <USER_HOME>/.hermes/profiles/<name>, build the regex from
# USER_HOME rather than hardcoding the path.
```

For client-specific defaults (e.g. `STRIPE_SECRET_KEY` should also check
`~/.work/hd-platform/.env`), pass through `PRISMATIC_REPO_ROOT` or walk
up from `__file__`:

```python
base = Path(os.environ.get("PRISMATIC_REPO_ROOT",
                           __file__.resolve().parents[4]))
```

## Redaction discipline

`AuthResult.redaction` MUST be safe to log in plaintext. Use prefix +
length only:

```python
def _redact(value: str) -> str:
    if not value:
        return "<missing>"
    return f"{value[:5]}...{value[-3:]}len={len(value)}"
```

Never log the raw `value`. If you absolutely need the full secret in
memory (for an API call), pass it directly to the SDK constructor and
do not print it.

## register_secret — write path

When the user runs `pwp-kpi-tracker auth register --type github_token
--value ghp_xxx`, write to the profile `.env` with 0600 mode:

```python
def register_secret(spec_name: str, value: str) -> None:
    path = _profile_env_path(ACTIVE_PROFILE)
    line = f'{spec.env_vars[0]}={value}\n'
    # Atomic-ish: read, replace or append, write 0600
    existing = path.read_text() if path.exists() else ""
    # ... filter out existing line for this var ...
    path.write_text(existing + line)
    path.chmod(0o600)
```

## Verification

After wiring a new client to `auth_loader`, prove end-to-end discovery
in a verification script:

```python
r = auth_loader.get_secret("github_token")
assert r.found
assert r.source in {"env", "profile-env", "project-env", "gcloud-adc"}
# Then prove the client actually uses it:
client = GitHubClient.from_env()
user = client.validate()
assert user["login"] == "mbgulden"
```

Don't ship the auth_loader wiring as "done" until the verifier shows
both `auth_loader.get_secret(...)` succeeds AND a real API call through
the client succeeds.

## Known gotchas (from PWP Phase 4.1, 2026-07)

* **`GITHUB_PAT_KEY` (separate PAT) returns 401 on live API** — only the
  `GITHUB_TOKEN` set by `gh auth login` is valid. The loader will
  happily find `GITHUB_PAT_KEY` because it has the right format; the
  client will fail at `validate()`. Surface this in the hint.
* **`HERMES_PROFILE` may be either a bare name (`ned`) or a full path
  (`/home/ubuntu/.hermes/profiles/orchestrator`).** Normalize via
  `Path(raw).name` before using as a directory name.
* **Env vars set in `terminal` via `export` do NOT persist into
  `execute_code`.** Within an `execute_code` block, source the profile
  `.env` manually with `for line in path.read_text().splitlines(): ...`
  before calling `get_secret()` if you need the live value.
* **Google OAuth refresh tokens have a TTL.** `invalid_grant` from
  `https://oauth2.googleapis.com/token` means the user must re-run
  `gcloud auth application-default login --scopes=...`. Surface this
  with the exact `gcloud auth ...` command, not a generic "auth failed".
