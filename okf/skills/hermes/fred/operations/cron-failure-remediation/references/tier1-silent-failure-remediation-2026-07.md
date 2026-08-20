# Tier-1 Silent Failure Remediation — July 2026 Patterns

This reference captures reusable remediation patterns from a Tier-1 Silent Failure Watchdog session. It is not a task log; use it as a recipe bank for similar cron failures.

## Pattern 1 — Data-shape drift in registry/journal readers

**Symptom**

A no-agent journal snapshot failed with an exception like:

```text
AttributeError: 'str' object has no attribute 'get'
```

The code assumed a field such as `_last_sync` was always an object/dict, but the live registry contained a timestamp string.

**Reusable fix**

Make readers tolerate durable shape variants explicitly:

```python
sync = reg.get("_last_sync", {})
if isinstance(sync, dict) and sync:
    # render rich counters
elif isinstance(sync, str) and sync:
    # render timestamp-only fallback
```

Verify both shapes with an isolated temp registry fixture.

## Pattern 2 — Removed upstream module, wrapper still owns cron contract

**Symptom**

A cron wrapper failed with:

```text
ModuleNotFoundError: No module named 'prismatic.backup'
```

or:

```text
ModuleNotFoundError: No module named 'prismatic.observability.overnight_factory_report'
```

The upstream module had been removed/moved, but the cron still needed to satisfy the operational contract.

**Reusable fix**

If the wrapper's job is simple and load-bearing, implement the small contract directly in the wrapper instead of preserving a stale import:

- Backup wrapper: tar the live state directory plus explicitly known external state files into the configured backup directory; include retention.
- Report wrapper: scan cron output directories, classify failed runs by output markers, write JSON/Markdown reports.

Verification should use isolated temp directories, monkeypatch module globals like `STATE_DIR`, `BACKUP_DIR`, `PROFILES_DIR`, and `REPORT_DIR`, then assert artifacts exist and counts match.

## Pattern 3 — Cron killed by scheduler due to unbounded subprocess

**Symptom**

A cron output shows only:

```text
Script exited with code -15
```

The script runs a model/CLI subprocess with no Python timeout and a huge CLI timeout, so the scheduler kills it silently.

**Reusable fix**

Bound the subprocess execution inside the wrapper:

```python
timeout_seconds = int(os.environ.get("SOME_TIMEOUT_SECONDS", "240"))
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds + 30)
except subprocess.TimeoutExpired:
    print("... timed out before producing output")
    print("Leaving delta unacknowledged so the next run retries")
    sys.exit(0)
```

Also handle non-zero return codes or CLI-level timeout text as explicit retry output, not a crash.

**Important nuance**

This turns a silent cron failure green at scheduler level while leaving the underlying throughput **yellow**. Report that distinction plainly.

## Pattern 4 — Required ad hoc verification after script edits

When changing cron scripts, create a temporary verification script under `/tmp` with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`. The script should:

1. `py_compile` all changed Python files.
2. Exercise changed behavior with isolated temp fixtures.
3. Verify timeout/hang fixes with a deliberately low timeout env var.
4. Print `AD_HOC_VERIFICATION_PASS` only after all assertions pass.
5. Clean up the `/tmp/hermes-verify-*` script afterwards.

Report it as:

```text
Scope: ad hoc targeted verification only — not full canonical suite green.
```

## What not to persist

- Do not save current job IDs, timestamps, branch dirtiness, or run filenames as memory.
- Do not encode that AGY/Linear/Hermes is “broken”; encode the bounded-timeout/retry pattern.
- Do not claim full suite green from fixture probes.
