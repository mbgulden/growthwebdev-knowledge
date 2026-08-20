# Linear API Budget Gating for Event-Driven Supervisors

## When this matters

Use this pattern when Linear is rate-limited even though the system was supposedly moved to event-driven dispatch. The likely failure mode is not "Linear is flaky"; it is usually that a legacy polling/safety-net path still makes direct GraphQL calls outside the shared budget layer.

## Durable lesson

Event-driven does not mean event-only. Long-running supervisors often keep safety-net polling, startup preflight probes, single-issue fallback fetches, and helper-module mutations. All of those must share the same tenant-level Linear budget and 429 cooldown contract.

## Fix pattern

1. Inventory live Linear callers, not just the intended event path:
   - `api.linear.app/graphql`
   - `LINEAR_API_KEY`
   - helper wrappers like `linear_helpers._linear_gql`
   - long-running supervisor flags such as `--from-linear`, `--watchdog`, and `--watchdog-interval`
2. Identify direct HTTP calls that bypass the canonical budget DB.
3. Add one shared budget gate before every network request.
   - Prefer one tenant/global bucket for shared Linear quota, not per-agent buckets that each allow 2500/hour.
   - Fail closed if the budget module is unavailable; do not silently fall back to unmetered calls in operational supervisors.
4. Add a 429 cooldown marker.
   - On real Linear 429, write a timestamp marker such as `linear_rate_limit_until.txt`.
   - Before future requests, check the marker and block locally until cooldown expires.
5. Demote safety-net polling back to safety-net cadence.
   - If event bus is primary, polling should be slow enough to catch missed events without becoming the main workload.
   - Verify CLI flags are actually applied, not merely printed.
6. Patch shared helper modules too.
   - Fixing the supervisor fetch path is not enough if state/comment/label helpers still call Linear directly.

## Verification pattern

Use a focused `/tmp/hermes-verify-*` script with OS-safe `tempfile` creation. Keep it isolated and avoid real Linear calls.

Minimum checks:
- `py_compile` for changed Python files.
- `bash -n` for changed shell wrappers.
- Static assertions that all relevant call sites route through the budget wrapper.
- Monkeypatch `urllib.request.urlopen` to a fake success response and verify the budget DB logs a consume before the fake network call.
- Monkeypatch `urlopen` to raise HTTP 429 and verify a cooldown marker is written.
- Verify a follow-up budget check blocks locally without increasing fake network-call count.
- Verify shared helper modules consume the same global budget bucket.
- Delete the temporary verifier and fixture DB afterwards.

Report explicitly as: `ad hoc targeted verification only — not canonical/full-suite green`.

## Pitfalls

- Do not trust budget DB silence as proof Linear is quiet. It can mean the hot path bypasses the budget layer.
- Do not create per-agent 2500/hour buckets for a tenant-scoped API quota; that multiplies the allowed burn.
- Do not leave startup preflight probes outside the budget gate. Repeated watchdog restarts can burn quota before any real work starts.
- Do not stop after adding a CLI flag; verify the script actually applies it to runtime state.
- Do not keep pinging Linear after a 429 just to see if it recovered. Use a local cooldown marker and retry later.
