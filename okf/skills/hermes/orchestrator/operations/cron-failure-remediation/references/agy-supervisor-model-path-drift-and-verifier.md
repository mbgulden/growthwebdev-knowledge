# AGY supervisor model/path drift + verifier proof packet

Session pattern: a persistent/Fred factory monitor reported `SUPERVISOR DEAD` and repeated restarts of `agy_sandbox_event_supervisor_cron.sh`. Restart logs showed two load-bearing contract failures:

1. **Profile HOME path drift** — cron/monitor execution inherited a Hermes profile HOME, so `Path.home()` resolved AGY paths under `~/.hermes/profiles/*/home` instead of the machine account where AGY is installed/configured.
2. **AGY model label drift** — current AGY CLI rejected legacy lowercase model IDs like `gemini-3.5-flash`; the accepted values were display labels such as `Gemini 3.5 Flash (Medium)` and `Gemini 3.5 Flash (High)`.

## Minimal remediation pattern

Patch the wrapper/supervisor at the contract boundary:

- In the cron wrapper, pin runtime paths before launching Python:
  - `export HOME=/home/ubuntu`
  - `export AGY_BIN=/home/ubuntu/.local/bin/agy`
  - `export AGY_TOKEN_DIR=/home/ubuntu/.gemini/antigravity-cli`
  - `export AGY_ABANDONMENT_GUARD=/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_abandonment_guard.py`
  - `export CRON_JOBS_PATH=/home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json`
  - `export AGY_POOL_ROUTER_PATH=/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_pool_aware_router.py`
  - `export PRISMATIC_HOME=/home/ubuntu/work`
- In the supervisor/router mapping, use AGY display labels for defaults and agent-label routing:
  - `Gemini 3.5 Flash (Medium)`
  - `Gemini 3.5 Flash (High)`
  - `Gemini 3.1 Pro (High)`
  - `Claude Sonnet 4.6 (Thinking)`
  - `Claude Opus 4.6 (Thinking)`
- Preserve legacy aliases only as compatibility/fallback inputs; do not let them be the load-bearing default or primary route.

## Required proof packet

After editing cron code, do not rely only on live process recovery or manual smoke output. Create an OS-safe temporary verifier with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`, run it, then delete it.

The verifier should assert:

- `python3 -m py_compile` passes for changed Python files.
- `bash -n` passes for changed shell wrappers.
- Wrapper text contains the pinned path exports.
- Supervisor AST/config uses current display-label models for default and routing maps.
- A bounded live AGY smoke with the current display-label default returns `OK`.
- Any markdown/inbox status file changed from `DEAD` to `RECOVERED` contains explicit recovered evidence, not just prose.

Report as: **Ad hoc targeted verification only — not canonical suite green.**

## Pitfalls

- Do not encode “AGY is broken” or “model X does not work” as durable knowledge. The durable lesson is to verify current AGY accepted model labels and pin the wrapper environment when cron runs outside the machine account HOME.
- If the user/system asks for a fresh `/tmp/hermes-verify-*` proof packet, rerun a fresh verifier even if a previous live smoke passed. The proof packet itself is part of the contract.
