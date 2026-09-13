---
name: scheduled-reminder-management
description: "Manage Hermes scheduled reminders/cron jobs: stop, pause, remove, audit, and diagnose no_agent script failures (env stripping, HOME rewrite, ~/.config CLI auth)."
triggers:
  - stop reminder
  - stop cron
  - remove scheduled job
  - pause reminder
  - noisy watchdog
  - live monitor reminders
---

# Scheduled Reminder Management

Use this skill when the user asks to stop, pause, remove, list, or audit scheduled reminders/cron jobs.

## Core rule

When the user says **"stop reminder <name>"**, act immediately. Do not explain first, do not ask for confirmation unless multiple matching destructive choices are ambiguous, and do not leave the reminder running while summarizing.

## Safe removal workflow

1. Run `cronjob(action="list")` first. Never guess job IDs.
2. Match by exact or clearly intended job name/preview.
3. If one clear match exists, remove it with `cronjob(action="remove", job_id=...)`.
4. Run `cronjob(action="list")` again to verify the target job disappeared.
5. Report compactly:

```text
job_id=<id>
name=<job name>
schedule=<schedule>
RESULT=REMOVED
verified_absent=yes
```

## When the user repeats the stop request

A repeated message like:

```text
stop reminder LIVE result writeback reconciler — Prompt 4 agents
stop reminder LIVE result writeback reconciler — Prompt 4 agents
```

is a strong signal to prioritize removal over any in-progress implementation/reporting. Stop the matching reminder first, then resume only if needed.

## Adjacent reminders/watchers

Remove only the exact reminder requested unless the user names additional jobs. If a related watcher remains, say so explicitly instead of silently removing it:

```text
Removed: LIVE result writeback reconciler — Prompt 4 agents
Still running separately: Watch Prompt 4 completed-work packets — Agent Output Resilience
```

If the user then asks to stop that adjacent watcher too, list again, remove that exact job, and verify absence.

## Pitfalls

- Do not confuse **paused** with **removed**. If the user says stop/remove and the job is noisy, removal is usually the expected action.
- Do not report "stopped" from memory. Verify with a fresh cron list after removal.
- Do not remove unrelated recurring business/AOT jobs just because they are also scheduled.
- Do not preserve live monitors after the user clearly asks to stop reminders; noisy live monitors are operator-experience bugs once unwanted.

## Diagnosing cron job failures (`no_agent` scripts)

When a `no_agent` job (plain script, no LLM) fails, the Telegram alert often shows only a **generic wrapper** — e.g. "provider authentication error" is what the scheduler reports for ANY `no_agent` non-zero exit, not an actual provider-config problem. Don't chase the wrapper:

1. Read the real record: `profiles/<name>/cron/jobs.json` (job config: `no_agent`, `workdir`, `script`, last-run status/timestamp) + the run output under `profiles/<name>/cron/output/<job_id>/`. A **MISSING output file for the failed run = the script died before writing its report** — distinct from "ran, wrote output, exited non-zero".
2. **Env context is not what it looks like:** `no_agent` spawns start from the **gateway** process's env, then `apply_subprocess_home_env()` rewrites `HOME` to the profile home (e.g. `/home/ubuntu/.hermes/profiles/kai/home`), then `_sanitize_subprocess_env()` strips secret env vars. Net: a cron script sees profile-home `~` (no `.config/` under it — `~/.config/gh`, ssh, git-credential all invisible) AND no secret env vars. The agent terminal has the same `~` but its env still carries profile tokens (e.g. `GITHUB_TOKEN`), so `~/.config/`-based CLI auth and env-based auth can pass interactively while failing in cron — a naive "switch HOME only" reproduction false-passes. Scripts using `Path.home()`/`expanduser()` resolve DIFFERENT files in each context; `~`-based paths inside cron scripts are a latent bug.
3. **The scheduler strips secret-bearing env vars** (VLLM_*, GITHUB_TOKEN, …) from `no_agent` subprocesses — scripts cannot rely on env vars and must fall back to the profile `.env` file on disk. Reproduce exactly with `env -i` (NOT `env -u` for a few keys — the agent terminal has more secrets than you'd guess, which masks the failure): `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/home/ubuntu/.hermes/profiles/kai/home python3 /abs/path/to/script.py` and compare exit codes.
4. Verify gateway env: `tr '\0' '\n' < /proc/<gateway PID>/environ | grep -E '^(HOME|VLLM_)='` (mask values).
5. Only after the runtime env is proven equivalent, suspect network/target service — and diagnose service-side failures by temporal correlation, not key-comparison (see `local-llm-inference-ops` → vLLM 401 diagnostics).
6. **`~/.config/`-based CLI tools are double-blind** (no token env + no config under profile home) — e.g. `gh pr list` in a governance script warns "run `gh auth login`". Fix in-script, not in env: pin the config dir (`os.environ['GH_CONFIG_DIR'] = '/home/ubuntu/.config/gh'`), or export a token from the profile `.env`, or degrade the check to skip/info with an explicit reason. Expected side effect: real WARNs the auth failure had been masking surface after the fix. Verified 2026-09-05 on aot_governance_watchdog open-prs — details in `references/no-agent-cron-cli-auth.md`.
