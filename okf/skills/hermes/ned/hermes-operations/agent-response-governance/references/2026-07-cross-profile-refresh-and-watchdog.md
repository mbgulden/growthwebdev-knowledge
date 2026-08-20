# 2026-07 cross-profile response-contract rollout, refresh, and watchdog hardening

## Trigger
Michael complained that agents were slow on simple asks, buried results in procedural jargon, omitted clickable final-product links, and stopped after completed increments without a golden-path `Next Step`. He then asked to apply the behavior across all profiles and to keep executing the next step.

## Durable lesson
This is not just memory. It is a class-level response-governance workflow:

1. Encode the preference in every profile's `memories/USER.md`.
2. Refresh active warm gateway sessions so they actually pick up the new memory.
3. Verify active service status and process start times.
4. Harden an existing profile-audit watchdog so the preference does not drift out of any profile later.
5. Final reports must lead with status/evidence and include a `Next Step` aligned to the golden path.

## Cross-profile memory shape used
Concise declarative memory entries, not task logs:

- Michael prefers a fast/simple response path for conceptual/editorial/advisory requests; live/build/fix/deploy work still needs tools and verification, but final reports lead with status and clickable links.
- Michael wants completed task/project reports to include a concise `Next Step` aligned to the project/task/goal golden thread/golden path; when YOLO mode is active, agents continue safely along that path.

## Refresh pattern
Direct `systemctl restart` from inside a gateway process can be blocked because the gateway would terminate its own child command. The working pattern was:

1. Write a small script under `/tmp` that restarts the target services and records evidence to `/tmp/<name>.status`.
2. Run it through `sudo systemd-run --wait --collect --unit=<unit> /tmp/script.sh` so the restart happens outside the gateway process tree.
3. For restarting the current profile's gateway, schedule a delayed one-shot systemd unit/timer, then arrange a follow-up verification report.
4. Verify with `systemctl is-active` and `ps -eo pid,lstart,cmd` process start times.

## Services refreshed in this session
- `autobot.service`
- `hermes-kai-gateway.service`
- `jeff.service` (`next-step` profile)
- `ned-gateway.service` via delayed external restart
- `hermes-fred-gateway.service`

## Watchdog hardening pattern
When the user says “do the next step and keep doing the next step,” do not stop at manual refresh if a safe durable guard is available.

In this session, Ned's `hermes_profile_audit.py` was hardened to:

- audit 22 detected profiles instead of a stale shorter default list,
- include Fred and other profile dirs that were previously omitted,
- check each profile's `memories/USER.md` for the response-contract snippets,
- treat profiles without `config.yaml` as still auditable for user-memory-contract checks,
- verify `Profiles audited: 22`, `Warnings: 0`, `Critical: 0`, `Total patches: 0`.

## Pitfalls
- Profile discovery can miss symlinked or config-less profiles. Check `memories/USER.md` even when `config.yaml` is absent.
- Do not encode transient tool failures as durable negative claims. Capture the working pattern: external `systemd-run` script/timer for gateway refresh.
- Do not broadly reboot the machine; refresh only affected gateways and verify.
- Avoid same-minute cron races between a watchdog and its heartbeat monitor. Schedule the monitor shortly after the producer job (example: watchdog at `0 */6 * * *`, heartbeat monitor at `15 */6 * * *`) so it verifies the new heartbeat instead of checking just before it is emitted.
- In `set -u`/cron shell scripts, avoid `grep -c PATTERN || echo 0` inside command substitution. `grep -c` prints `0` but exits 1 when there are no matches, so the fallback appends a second `0` and can leak stray lines into reports. Prefer `awk '... END {print c+0}'` for counters.
- If YOLO mode is active, continue only while the next action is safe, reversible, and in scope.
- When Michael says to continue through “the next step” repeatedly, keep executing the golden path until a real safety boundary appears. For GitHub cleanup, that means not stopping at opening a PR if checks/merge/closeout are safe and requested; continue through verification, merge, stale-PR closure, and final open-PR verification.
