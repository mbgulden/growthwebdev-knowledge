# Status Page Health Contract Remediation — Prismatic Pattern

Use when a status page/dashboard says `degraded`, `critical`, or similar but the underlying services appear to be active.

## Core lesson

A status page should represent **current operational health**, not durable historical logs. Do not let old synthetic drills, cumulative restart counters, or stale recovery test messages keep a dashboard degraded forever.

## Diagnostic sequence

1. **Prove what the user sees.**
   - Load the public page if accessible.
   - If Cloudflare Access blocks the browser, verify the backend directly from the host (`http://127.0.0.1:<port>/`) and label the public-access blocker clearly.
   - Capture the rendered badge text and first-failing layer from live HTML/UI, not only source code.

2. **Find the source contract for the badge.**
   - Search deployed/runtime code, not just the main repo. Prismatic may run from a stable worktree such as `/home/ubuntu/work/prismatic-engine-stable` while the development repo is `/home/ubuntu/work/prismatic-engine`.
   - Check the running process cwd/environ (`/proc/<pid>/cwd`, `/proc/<pid>/environ`) to identify the deployed code path and state directories.

3. **Separate current health from history.**
   - Service `ActiveState=active` and fresh `/health` responses are current health signals.
   - `NRestarts` is cumulative for the active service lifetime; it should only degrade the page when paired with a recent `ActiveEnterTimestamp` / low uptime window (for example, first 5 minutes after recovery).
   - Durable alert/recovery logs are history. Filter stale synthetic drills (`[SYNTHETIC TEST]`, `synthetic=true`, fake services) and old alerts out of the current status panel.

4. **Fix the smallest health contract.**
   - Avoid hiding real failures. Keep current critical/warning alerts visible.
   - Filter only stale/synthetic/test artifacts or convert cumulative counters into time-windowed health signals.
   - Restart the service only after syntax/compile checks pass.

5. **Verify live UI/API after restart.**
   - `py_compile` changed Python.
   - `/health` responds with `status=ok`.
   - Live rendered page shows `HEALTHY`/current green state.
   - First-failing layer is `none`.
   - Recent-alert panel no longer renders stale synthetic drills.
   - Forbidden stale terms are absent from the rendered page.
   - Use `/tmp/hermes-verify-*` tempfile verifier and clean it up. Label this as ad hoc targeted verification, not full suite green.

## Pitfalls

- Do not call the page healthy from source inspection alone; Michael wants live UI proof.
- Do not trust the development repo path if systemd is running a stable worktree or installed package.
- Do not erase durable logs just to make the page green; filter dashboard presentation unless retention itself is the issue.
- Do not suppress real current incidents just because the user asked for green. Fix or explicitly block on the real failing layer.
