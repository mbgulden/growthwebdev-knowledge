# Frozen input execution gates

## Session pattern

A Prismatic one-shot admission package can pass envelope review while still being unsafe if the launcher only verifies one source file at execution time. Review-time matching of config/source hashes is not enough: every frozen input that the envelope depends on must be enforced by the executable immediately before it opens any control or credential window.

## Blocker shape

Treat this as a real blocker:

```text
ENVELOPE_BINDS=policy,control,private-config,task_admission,consumer,agy-launcher
LAUNCHER_EXECUTION_CHECKS=task_admission_only
RESULT=BLOCKED
REASON=review-time hashes do not prevent execution-time drift of the other frozen inputs
```

Even if the currently deployed files match the envelope, the launcher is not execution-grade until it fails closed on drift for each bound input.

## Required correction

Add one narrow frozen-input verifier that checks every envelope-bound input:

- path exists;
- path is a regular file;
- private/control files are not symlinks;
- private/control modes remain restrictive, normally `0600`;
- SHA-256 equals the frozen envelope value.

Call it at least during:

1. zero-mutation preflight;
2. execution live gate;
3. immediately before opening policy/control/token/credential windows.

The final call should happen after process/socket/health/zero-state checks and as close as possible to the first mutation-capable action.

## Failure injection proof

Before re-review, prove the correction with disposable copies or monkeypatched constants. The local proof should include every frozen input independently drifting and blocking:

```text
SIX_FROZEN_INPUTS_PASS=PASS
SIX_DRIFT_INJECTIONS_BLOCK=PASS
IMMEDIATE_PRECONTROL_RECHECK=PASS
ZERO_LIVE_STATE=PASS
```

Do not mutate the live bound files to test drift. Use temporary files, copied config, or injected paths/hashes.

## Envelope Vn+1 requirements

When freezing the superseding envelope:

- preserve Vn launcher and envelope hashes;
- name the shared review blocker;
- bind the corrected launcher hash;
- bind the fresh zero-mutation preflight report and hash;
- bind the failure-injection proof log and hash;
- state `EVENT_COUNT=0` and `PRODUCER_STARTED=false` until the corrected exact bytes receive independent CLEAN/PASS.
