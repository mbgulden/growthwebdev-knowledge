# Profile-safe cron wrappers + data-shape drift

Session pattern from fixing Tier-1 Silent Failure Watchdog findings for two no-agent jobs.

## Failure contracts observed

1. **No-agent script outside profile scripts dir**
   - Cron job referenced an absolute archived sandbox path, e.g. `/archive/.../compute_transits.py`.
   - Hermes rejected it before execution because no-agent cron scripts must resolve under the active profile `scripts/` directory.
   - Durable fix: create a small profile-local wrapper in `~/.hermes/profiles/<profile>/scripts/` and update the cron to use the relative wrapper script name.
   - Wrapper should own the operational contract:
     - check canonical project script exists
     - run it from its project workdir
     - use a bounded timeout
     - parse/validate output
     - write a concrete artifact if useful
     - print a concise JSON success report
     - emit explicit `BLOCKED:` messages on missing path / parse failure

2. **Registry data-shape drift**
   - Journal snapshot code assumed `project-registry.json['_last_sync']` was a dict and called `.get()`.
   - Live registry had `_last_sync` as a string timestamp, causing `AttributeError: 'str' object has no attribute 'get'`.
   - Durable fix: readers of cross-run registry/cache fields should tolerate known durable variants. For `_last_sync`, support both:
     - dict with counters (`linear_in_progress`, `github_prs_open`, etc.)
     - string timestamp (`Last sync: ...`)

## Verification pattern

After patching:

- run both failed jobs through `cronjob(action='run', job_id=...)`
- read latest cron outputs and confirm success payloads, not just `last_status=ok`
- run Tier-1 detector with `--dry-run --json --no-linear`
- create `/tmp/hermes-verify-*.py` via `tempfile.mkstemp(...)` and verify:
  - `py_compile` for changed scripts
  - isolated fixture for data-shape drift
  - profile wrapper executes and writes/validates artifact
  - watchdog reports `silent_failures=0` and `failures=[]`
  - temp verifier and workdir are removed

Report explicitly as **ad hoc targeted verification**, not full suite green.
