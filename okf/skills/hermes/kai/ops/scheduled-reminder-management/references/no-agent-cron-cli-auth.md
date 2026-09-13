# no_agent cron: `~/.config/`-based CLI auth (gh) — diagnosis + fix

Session 2026-09-05. AOT governance watchdog, job `ce2574aadd6c`; script
`/home/ubuntu/.hermes/profiles/kai/scripts/aot_governance_watchdog.py` → guard
`scripts/prismatic_web_governance.py` (repo `/home/ubuntu/work/active-oahu-tours-mirror`,
`gh_json` helper wraps `gh pr list`).

## Symptom

```
🟡 open-prs: warn — Could not query GitHub PRs with gh.
  - To get started with GitHub CLI, please run:  gh auth login
  Alternatively, populate the GH_TOKEN environment variable with a GitHub API authentication token.
```

Other checks (workspace, branch-drift, live-production) all passed — only the
gh-dependent section failed, which is the fingerprint of an auth/env problem,
not a GitHub-side problem.

## Root cause chain (confirmed by reading the fork source)

1. `cron/scheduler.py`: `no_agent` spawn uses `env=_sanitize_subprocess_env(os.environ.copy())`
   → strips `GITHUB_TOKEN`/`VLLM_*`/other secrets from the subprocess env.
2. `hermes_constants.py`: `apply_subprocess_home_env()` rewrites `HOME` to
   `/home/ubuntu/.hermes/profiles/kai/home/` before exec.
3. Profile home has **no** `.config/gh/` (real interactive gh config lives at
   `/home/ubuntu/.config/gh/` with token in `hosts.yml`) → gh finds no token, no config → auth error.
4. **Masking in the agent terminal:** the terminal env still carries `GITHUB_TOKEN`,
   so `gh pr list` passes there under *any* HOME. A reproduction that only switches
   `HOME` (or only `env -u GITHUB_TOKEN` when other secrets remain) false-passes.
   Faithful reproduction needs `env -i`.

## Faithful reproduction

```bash
# what cron actually sees → expected: auth error
env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/home/ubuntu/.hermes/profiles/kai/home \
  gh pr list --repo <owner/repo> --state open --json number

# with the fix env → expected: real data
env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/home/ubuntu/.hermes/profiles/kai/home \
  GH_CONFIG_DIR=/home/ubuntu/.config/gh \
  gh pr list --repo <owner/repo> --state open --json number
```

## Fix (applied, verified)

In the kai-side wrapper (`aot_governance_watchdog.py`), not the repo guard —
lane-safe, no AOT repo changes. `prepare_gh_env()` called at top of `main()`:

```python
REAL_GH_CONFIG = '/home/ubuntu/.config/gh'  # real home's gh config (hosts.yml holds the token)
os.environ['GH_CONFIG_DIR'] = REAL_GH_CONFIG
# future-proof: also export GH_TOKEN from the profile .env if one is ever added
```

Verification: full watchdog run under `env -i` cron env → exit 0; `open-prs`
returned real PR data (stale #131 report) and `stale-branches` surfaced real
findings (12 old `audit/agy-GRO-*` branches) that the auth failure had masked.

## Pitfalls

- `env -u` for the one known key is not enough — use `env -i`. The agent
  terminal env holds more secrets than expected; any survivor masks the failure.
- Do not put a gh token into cron env; the config-dir pin is token-free in env
  and HOME-proof (same pattern as the LLM watchdog's absolute `.env` path).
- After the fix, expect NEW WARNs (stale PRs/branches). That is recovered
  visibility, not a regression — do not "fix" it back to a pass.
- If the guard is in a shared repo and you cannot touch the wrapper, the
  in-repo alternative is the same `GH_CONFIG_DIR` export at the top of the
  guard script's GitHub section, or degrading the check to `skip` with an
  explicit reason string so the alert is not a false "GitHub is down".
