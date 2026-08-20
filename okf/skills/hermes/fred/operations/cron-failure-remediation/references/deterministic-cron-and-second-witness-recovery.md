# Deterministic cron + Second Witness recovery pattern

Use when a scheduled Hermes cron is nominally `ok` but produces useless output, stalls, or depends on an LLM prompt for deterministic operations.

## Signals

- Cron output says a known file cannot be found even though it exists at a canonical absolute path.
- Prompt uses `$PRISMATIC_HOME/work/...` when `PRISMATIC_HOME` may already include `/work`.
- The cron is LLM-driven for tasks that should be deterministic: reading a registry, updating timestamps, computing stale counts, writing a report.
- “Second Witness”/review crons return tool-chatter (`I will...`) or timeout instead of an Insight Density review.

## Durable fixes

1. **Resolve paths with explicit canonical paths inside cron prompts/scripts.**
   - Prefer `/home/ubuntu/work/project-registry.json` over `$PRISMATIC_HOME/work/project-registry.json` in this Prismatic/Hermes fleet, because `PRISMATIC_HOME` can already be `/home/ubuntu/work`.
   - This is a path-contract fix, not a memory fact about all environments. Re-check env vars before generalizing.

2. **Convert deterministic sync/report crons to no-agent scripts.**
   - If the job only needs to read JSON, compute stale/missing counts, query simple CLI/API status, and update a file, make it `no_agent=true` with a script.
   - Keep stdout concise and operational: scanned count, stale count, missing count, activity sample, and exact registry path.
   - Preserve previous state fields before overwriting them, e.g. `_last_sync_previous = _last_sync` before writing a new `_last_sync`.

3. **Restore Second Witness as a bounded reviewer, not a churn loop.**
   - Give the reviewer enough context in the prompt up front (`git status --short`, `git diff --stat`, tracked PEMs, condensed alerts) so it does not need to run tools.
   - Explicitly instruct: do not run shell commands/file reads/tool calls; use only provided context.
   - Use a finite timeout for AGY/model calls.
   - Treat tool-chatter (`I will ...`) or timeout/error output as unusable and produce deterministic fallback review tables instead.
   - Mark the delta handled after fallback output so the cron does not retry forever and become a silent-failure/churn source.

4. **Fallback review shape.**
   - Output the same useful sections as Second Witness normally provides:
     - `### Gaps Detected`
     - `### Security/Credential Bleeds`
     - `### Remediation Paths`
     - local evidence block
   - Use actual local command outputs for evidence, but keep them bounded/truncated.

## Verification recipe

Create a focused temporary verifier under `/tmp` with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`, then clean it up.

Minimum checks for this class of fix:

- `py_compile` the changed cron scripts.
- For deterministic registry sync:
  - point the module-level `REGISTRY` at an isolated temporary JSON fixture;
  - run `main()`;
  - assert `_last_sync_previous` is preserved;
  - assert `_last_sync_stats.project_count`, stale filtering, missing-next-action counts, and `source` marker are correct.
- For Second Witness:
  - run with `SECOND_WITNESS_FORCE=1` and a low `SECOND_WITNESS_AGY_TIMEOUT_SECONDS`;
  - assert exit code `0`;
  - assert output contains either Insight Density sections, JSON green pulse, or deterministic fallback marker;
  - assert elapsed time stays below the scheduler-kill window.

Report explicitly as **ad hoc targeted verification**, not full suite green.

## Pitfalls

- Do not leave a deterministic cron as an LLM planning prompt that says what it *would* do. If the cron needs to sync, make it actually sync.
- Do not let “last_status=ok” hide useless output. Read the latest output file and verify it did the operational job.
- Do not encode a one-off missing env var as a permanent tool limitation. Capture the path contract and the deterministic-script pattern instead.
- Do not let Second Witness retry an unchanged failing delta forever. A bounded fallback report is better than a recurring silent failure.
