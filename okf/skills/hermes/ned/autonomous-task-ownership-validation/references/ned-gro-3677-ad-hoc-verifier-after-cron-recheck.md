# GRO-3677 — ad-hoc verifier after cron recheck

## Trigger

After an autonomous implementation task is finalized, a downstream Hermes/system verifier may report:

> workspace does not have fresh passing verification evidence yet / No canonical test/lint/build command was detected

This can happen even when a focused pytest command was run earlier. Do not argue with the verifier or repeat the final report as if suite-green evidence exists.

## Correct recovery pattern

1. Create a temporary verifier under `/tmp` with an OS-safe `tempfile`/`mktemp` path and a `hermes-verify-` filename prefix.
2. Import the changed code from the workspace and assert the behavior directly.
3. Run the script from the repo root.
4. Delete the temporary script after execution when possible.
5. Report the output explicitly as **ad-hoc targeted verification**, not canonical suite green.

## GRO-3677 concrete shape

For the PWP token override merge task, the temp verifier checked:

- precedence: PWP defaults → theme defaults → tenant overrides → controlled page overrides
- page-level dot-path allowlist filtering
- non-mutation of default/theme/tenant/page input dictionaries
- rejection of page overrides when no allowlist is supplied

The useful success marker was:

```text
AD_HOC_VERIFY_OK GRO-3677 override precedence, allowlist filtering, and non-mutation checks passed
```

## Why this matters

The autonomous skeleton says commit early and finalize atomically. If the post-finalize verifier later rejects evidence detection, the branch and Linear transition may already be done. The recovery is not another broad test run or a fabricated claim; it is a small behavior-specific `/tmp/hermes-verify-*` proof that satisfies the recheck without pretending the whole suite was re-run.
