---
type: Reference
title: execute_code fresh-sandbox env loading
description: Each execute_code call runs in a fresh sandbox with no persistent env. Load LINEAR_API_KEY (and other secrets) from .env files at the top of every script that needs them.
resource: operations/golden-thread-strategy-pipeline/references/execute-code-fresh-sandbox-env-loading-2026-07-26.md
git_path: operations/golden-thread-strategy-pipeline/references/execute-code-fresh-sandbox-env-loading-2026-07-26.md
tags: [execute_code, hermes, sandbox, env, linear, secrets]
timestamp: 2026-07-26
linear_issue: pending
git_repo: growthwebdev-knowledge
last_verified: 2026-07-26
verified_by: fred (ad hoc targeted verification, not suite green)
status: active
---

# `execute_code` Fresh-Sandbox Env Loading

## The gotcha

`execute_code` runs Python in a fresh sandbox. `os.environ` does **not** persist between calls. A pattern that works in the chat shell (`os.environ["LINEAR_API_KEY"]`) raises `KeyError` in the next `execute_code` call.

```python
# First call
import os, json, urllib.request
key = os.environ["LINEAR_API_KEY"]  # works (loaded from chat shell env)
# ... do GraphQL work ...

# Second call (fresh sandbox)
key = os.environ["LINEAR_API_KEY"]  # KeyError
```

## The fix — load from .env at the top of every script

Put this loader at the top of every script that needs `LINEAR_API_KEY` (or any other env-only secret):

```python
import os, json, urllib.request

# Load env from .env files. Order matters: first file wins per key.
for src in ["/home/ubuntu/.hermes/profiles/fred/.env"]:
    if os.path.exists(src):
        for line in open(src):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                if k.strip() == "LINEAR_API_KEY" and v.strip():
                    os.environ.setdefault(k.strip(), v.strip())

key = os.environ["LINEAR_API_KEY"]
```

`setdefault` is the right semantic — if the shell already provided the value, keep it; only fall back to the `.env` file when unset.

## Audit-prefix the key, never the value

When logging the key for trace context, log the first 12 chars + `...`:

```python
audit = key[:12] + "..."
print(f"audit_prefix={audit}")  # safe to print
```

Never `print(key)`. Never write the value to a log file. Never include it in an OKF artifact or Linear comment.

## Where to source env from (canonical locations)

| Env var | Canonical location |
|---|---|
| `LINEAR_API_KEY` | `/home/ubuntu/.hermes/profiles/fred/.env` (or the active profile's `.env`) |
| `LINEAR_OAUTH_TOKEN` | Same, but distinct from raw key — uses `Bearer` prefix in `Authorization` header |
| `AGY_BIN` / `AGY_TOKEN` | `/home/ubuntu/.local/bin/` wrappers; orchestrator profile `.env` |
| `PRISMATIC_HOME` | Often already in shell env; `/home/ubuntu/work` default |

Always check the active Hermes profile directory first. If the secret is not there, fall back to the orchestrator profile. Never reach into another profile's `.env` without explicit direction.

## Common pattern — load once, persist intermediate state to /tmp

When a multi-step Linear mutation needs to chain results across calls (parent epic id → child epic ids → child task creation), persist intermediate state to `/tmp/` as JSON:

```python
# First call: create parent + child epics, save ids
open("/tmp/journal_epic_ids.json", "w").write(json.dumps(epic_ids))

# Second call: load epic_ids, create tasks
epic_ids = json.load(open("/tmp/journal_epic_ids.json"))
```

Clean up `/tmp/*.json` files when the work is complete to avoid stale state in future sessions.

## What NOT to do

- **Do not write a wrapper helper that imports the secret at module level.** The fresh sandbox does not preserve module imports across calls either.
- **Do not write the secret into a temp file.** If the script is interrupted, the file lingers.
- **Do not use `subprocess.run` with the key as an argv element.** It ends up in `ps` output.
- **Do not rely on `os.environ.get` returning `None`** — it raises `KeyError` only on direct `os.environ[key]` access, but the absence will fail later when you try to use the value. Check with `if not key: raise SystemExit(...)` early.

## Pitfalls

- **Do not assume any `os.environ` value from a previous `execute_code` call is still present.** Always reload at the top.
- **Do not hard-code secrets in script bodies.** Even in a one-shot script, the file is in the conversation history.
- **Do not use `pathlib.Path(...).read_text()` on a `.env` file** without parsing for comments — many `.env` files contain `# comment` lines that will fail the `KEY=VALUE` parse.

## Verification boundary

Ad hoc targeted verification only — not full docs-suite green. Validated by 2026-07-26 Journal PE Integration session, where the first attempt to mutate Linear in a second `execute_code` call raised `KeyError: 'LINEAR_API_KEY'` until the loader was added at the top of the script.