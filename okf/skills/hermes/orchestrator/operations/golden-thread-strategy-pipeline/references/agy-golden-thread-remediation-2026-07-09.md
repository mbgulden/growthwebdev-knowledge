# AGY Golden Thread Remediation — 2026-07-09

## Trigger

The AGY Golden Thread Project Review cron delivered a compact Telegram alert:

```text
[AGY-GT-REVIEW] Project state changed
[AGY-GT-REVIEW] AGY exit: 0
Gaps Detected
Security/Credential Bleeds
Remediation Paths
```

The compact delivery only proved a delta existed; it did **not** include the concrete rows. The correct move was to treat the cron message as a trigger, not evidence, and recover/reproduce the full output before remediation.

## Recovery Pattern

1. List/identify the cron job to confirm script and job id.
2. Inspect the no-agent script to understand whether it persists output or only prints stdout.
3. Search scheduler/session output for the full report.
4. If not recoverable, rerun the script once in foreground to reproduce the rows.
5. Do not remediate from section headings alone.

In this case, rerunning `/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_golden_thread_delta.py` reproduced full rows showing registry/Linear drift, not populated Security/Credential Bleed rows.

## Remediation Pattern Used

### Registry/Linear drift

- Verify every issue mentioned by AGY with live Linear before editing registry state.
- Correct AGY hallucinations explicitly rather than propagating them:
  - `GRO-1854` was claimed as a WAG next-title item, but Linear showed it was unrelated credential-hygiene work.
  - `GRO-895` was canceled and should not remain in active next actions.
- Update `/home/ubuntu/work/project-registry.json` to point at live active issues and record known-bad references when needed.
- Keep blocked/deferred compliance work out of `next_action` when active revenue-path issues exist.

### Credential hygiene findings

Credential-bleed rows from AGY need careful handling: remediate local exposure without printing or preserving the secret, and separate what can be fixed locally from what requires an external dashboard/API owner.

#### Credentialized git remotes

While verifying the remediation path, a real local credential hygiene issue appeared: multiple `.git/config` remotes under `/home/ubuntu/work` embedded GitHub credentials.

Safe remediation:

```bash
git remote set-url origin https://github.com/OWNER/REPO.git
```

For a broader sweep, enumerate `remote.*.url` and `remote.*.pushurl`, strip embedded credentials from `https://user:token@github.com/...` or `https://token@github.com/...`, and never print token values.

Verifier invariant:

```text
credentialized_github_remotes_under_work = 0
```

#### Local `.env` secret values

If AGY flags a local `.env` secret such as a Stripe secret key:

1. Do not echo or include the value in any report.
2. Replace the local value with a host-env placeholder such as `__SET_IN_HOST_ENV_<KEY>__` when the file is local operational state rather than a committed template.
3. Scan the resulting file for common secret prefixes (for example live/test secret and webhook-secret prefixes) without recording the original value.
4. Document external rotation/revocation separately: removing local plaintext exposure is not proof that the upstream key was revoked.
5. Verify the OKF evidence artifact itself does not contain token prefixes such as GitHub PAT prefixes, Stripe secret prefixes, webhook secret prefixes, or `Bearer ` tokens.

## Verification Pattern

Use a focused `/tmp/hermes-verify-*` script that checks:

- Registry JSON parses.
- Correct project next actions mention the active issue identifiers.
- Known-bad/hallucinated issue references are recorded as bad, not active.
- Relevant PR metadata is recorded if it is part of the remediation.
- GitHub remotes under `/home/ubuntu/work` no longer match credentialized HTTPS remote patterns.
- No common token prefixes (`ghp_`, `github_pat_`, `Bearer `) leaked into the evidence artifact.

Then rerun the watchdog once. In this case, it returned:

```json
{"cron": "agy-golden-thread", "status": "green", "delta": "none"}
```

## OKF Evidence

Promote durable evidence to OKF, not Hermes output:

```text
/home/ubuntu/work/okf/audits/YYYY-MM-DD-agy-golden-thread-remediation.md
```

Run a second focused artifact verifier over the OKF file itself and label it **ad hoc targeted verification**, not suite-green.
