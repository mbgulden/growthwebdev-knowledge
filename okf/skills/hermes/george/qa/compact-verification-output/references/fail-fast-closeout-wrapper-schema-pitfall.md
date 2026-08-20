# Fail-fast closeout wrapper and schema pitfall

## When this applies

Use this when a final closeout verifier wraps multiple Python/readback assertions, shell cleanup, log hashing, and a compact proof packet.

## Lesson

A shell wrapper can accidentally return success after the verifier failed if it captures the failing output, continues to cleanup/hash steps, and prints a receipt without `set -e` or an explicit `exit "$rc"`. This creates a dangerous split: the log contains a traceback, but the tool call exit code is `0`.

A second recurring pitfall is assuming persistent JSON schema shape. Hermes cron stores may represent `jobs` as either a list or a mapping depending on version/profile/state. Verification should tolerate both when reading state, then assert the exact job by `id`.

## Preferred pattern

```bash
set -euo pipefail
VERIFY=$(mktemp /tmp/hermes-verify-closeout-XXXXXX.py)
LOG=/tmp/<task>-closeout.log
trap 'rm -f "$VERIFY"' EXIT

# write verifier to "$VERIFY"
python3 "$VERIFY" >"$LOG" 2>&1
python3 -m py_compile <changed-python-files>
cat "$LOG"
rm -f "$VERIFY"; trap - EXIT
printf 'TEMP_CLEANUP=PASS\nLOG=%s\nLOG_SHA256=%s\nAD_HOC_OR_CANONICAL=ad-hoc targeted closeout\n' \
  "$LOG" "$(sha256sum "$LOG" | cut -d' ' -f1)"
```

For cron/job state readback inside the verifier:

```python
jobs = json.loads(path.read_text())["jobs"]
values = jobs.values() if isinstance(jobs, dict) else jobs
matches = [job for job in values if job.get("id") == expected_job_id]
assert len(matches) == 1
```

## Reporting boundary

If the first closeout wrapper failed because of the verifier itself, say so directly, keep the failed log path/digest if useful, fix the verifier, and rerun. Do not treat the failed verifier as product failure, and do not report PASS until the corrected wrapper fails fast and exits nonzero on verifier errors.
