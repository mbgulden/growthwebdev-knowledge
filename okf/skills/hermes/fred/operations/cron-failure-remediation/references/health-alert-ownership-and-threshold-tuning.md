# Health alert ownership + threshold tuning pattern

Use this when Michael replies to machine-health / homelab / Proxmox / inventory alerts with ownership or threshold corrections.

## Durable lessons

### 1. Respect alert ownership boundaries

If Michael says a monitor should not run on Fred's gateway because Autobot owns that class of health monitoring, do **not** keep tuning the Fred-side cron. Stop the duplicate sender.

Recommended sequence:

1. `cronjob(action="list")` to identify the exact job ID by name/script.
2. Search for the alert text across profile scripts/logs only if needed to detect duplicate senders.
3. Remove or pause the Fred-side cron that is producing the duplicate alert.
4. Verify the job is absent from scheduler-visible state and that no matching live process remains.
5. Report Autobot-owned health aggregation remains in place if verified from the cron list.

This is an ownership fix, not a threshold fix.

### 2. Threshold correction belongs in the alert producer

When Michael says to move a warning threshold (for example storage warnings from 80% to 90%), patch the script that constructs the alert text and condition, not just the display copy.

For Sovereign Sentinel weekly inventory storage alerts, the durable pattern is:

- Update the docstring / comment describing the threshold.
- Replace the hard-coded comparison threshold.
- Update both storage pool and root disk alert text.
- Update the “all clear” message so it does not still say the old threshold.
- Run a focused fixture verifier proving:
  - old noisy value below the new threshold is silent;
  - value above the new threshold alerts;
  - emitted text contains the new threshold;
  - no old threshold strings remain.

## Verification recipe

Use an OS-safe temporary script such as `/tmp/hermes-verify-<topic>-XXXXXX.py` and clean it up.

For threshold changes, include:

- `py_compile` for the changed Python alert producer.
- An imported-function fixture test if the producer exposes a function like `detect_drift`.
- A negative fixture at the old noisy value, e.g. `81.8%` should be silent after moving threshold to `90%`.
- A positive fixture above threshold, e.g. `90.5%` should alert.
- Text assertions for `Threshold: 90%` or the requested value.
- A source-text assertion that stale strings like `Threshold: 80%` / `under 80% capacity` are gone.

Report this as **ad hoc targeted verification**, not full suite green.

## Pitfalls

- Do not re-pitch a monitor after Michael says Autobot owns it. Remove the duplicate Fred-side cron.
- Do not change only the human-readable threshold. The comparison and all-clear text must match.
- Do not claim the host/storage condition is healthy just because the alert is quieted; report only that the alert threshold changed.
- Do not commit unrelated dirty files in a repo with existing staged/modified work. Report the changed path and verification evidence unless explicitly asked to commit/push.
