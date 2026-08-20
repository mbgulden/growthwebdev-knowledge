---
name: cron-failure-remediation
description: Investigate and remediate Hermes/Prismatic cron failures, especially silent no-agent failures surfaced by watchdogs, with explicit ad hoc verification evidence.
triggers:
  - User asks to check silent cron errors, watchdog findings, cron failures, or scheduled job health
  - Tier-1 Silent Failure Watchdog reports new/continuing failures
  - A cron job has last_status=error, exit -15, missing output, or delivery-local failures that need triage
  - Code/script changes are made to repair a cron and the user/system requires verification evidence
  - User asks for a no-agent cron that watches refreshed provider/API state and stays silent until a target appears
---

# Cron Failure Remediation

Use this skill when a scheduled Hermes/Prismatic cron is failing silently or a watchdog surfaces cron health issues. The goal is not just to identify the failing job: repair the smallest load-bearing contract, re-run the affected job, and leave clear evidence that distinguishes **ad hoc targeted verification** from full suite green.

## Operating principle

A cron health fix is complete only when all three are true:

1. The failing job's actual output/log explains the root cause.
2. The repair addresses the failing contract, not just the symptom.
3. A fresh run or focused `/tmp/hermes-verify-*` probe proves the changed behavior.

## Workflow

1. **List jobs and identify current failures.**
   - Use `cronjob(action="list")` for scheduler state.
   - For watchdog reports, inspect the watchdog's output file/digest to get the exact job IDs and names.
   - Ignore paused/disabled archival jobs unless the user explicitly asks to revive them.

2. **Read the latest real cron outputs and verify current state before treating recap flags as live failures.**
   - Cron outputs are commonly directories under profile paths like:
     - `~/.hermes/profiles/<profile>/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md`
   - Prefer the latest output file for each failing job.
   - Compare the recap/watchdog claim against `cronjob(action="list")` and, when safe, a fresh `cronjob(action="run")` or direct script run. Daily recap indexes can preserve errors from earlier in the day even after the cron is already green.
   - Capture exact failure contracts: import error, schema mismatch, timeout, missing module, killed process, delivery error, stale log indexing, external OAuth invalid_grant, etc.

3. **Classify each failure.**
   - **Broken script contract:** module/function moved or removed; wrapper must own the contract or import the new location.
   - **Profile sandbox/path contract:** no-agent cron scripts must resolve under the active profile `scripts/` directory. If a job points at an archived sandbox or another absolute path, create a profile-local wrapper and update the cron to use the relative wrapper name.
   - **Data shape drift:** caller assumed one JSON shape; make the reader tolerate known durable variants (for example, registry `_last_sync` may be either a dict of counters or a string timestamp).
   - **Unbounded subprocess:** process hangs until scheduler kills it; add bounded timeout and explicit retry/failure output.
   - **Resource monitor false positive:** alert logic uses an absolute metric where normalized capacity is required (for example, raw load average without CPU core count); fix the threshold contract, not just the wording.
   - **Noisy repeated monitor alert:** the condition may be real but too common; add event/cooldown state keyed by alert condition (for example `node:load:high`) so repeated pings are suppressed for a clear cooldown window.
   - **Wrong alert owner / duplicate gateway monitor:** if Michael says Autobot owns the health lane, stop the Fred-side cron instead of tuning it. List jobs, remove/pause the exact duplicate monitor, and verify the job is absent and no matching process remains. If he says a machine-health monitor is cluttering Fred or is not helpful, treat that monitor class as rejected for Fred-facing output: remove active emitters, quarantine runnable stale scripts, and patch aggregators to suppress that class while retaining unrelated actionable failures.
   - **Threshold too sensitive:** patch the producing script's comparison, alert text, docs/comments, and all-clear text together; then fixture-test both below-threshold silence and above-threshold alerting.
   - **External credential/delivery issue:** report plainly; do not hard-code secrets or declare the tool broken. If OAuth refresh returns `invalid_grant`, inspect for alternate token files first; if all available tokens are revoked/expired, create or repair a deterministic reauth helper that prints an authorization URL, stores state, exchanges the pasted redirect URL, writes tokens with safe permissions, and then re-run the live capability check.
   - **Cron delivery target missing / `Chat not found`:** distinguish job execution success from delivery success. Check `channel_directory.json` and `last_delivery_error`; if the target chat is not a known live channel, switch affected jobs to `deliver=local` rather than continuing failed sends. Re-run the jobs to clear stale `last_delivery_error`, inspect latest local output for prior error text, and restore direct delivery only after the recipient has handshaked with the bot. If a paired skill is missing, route to the available class-level skill in the same slice so local artifacts are clean while delivery is quarantined. See `references/telegram-chat-not-found-delivery-quarantine.md`.
   - **Stale log/index noise:** daily journals may index old gateway/errors.log lines as current blockers. First prove whether the collector samples the **head** of an append-only log merely because the file mtime is current. Patch the producer to read a tail window, discard partial first lines, filter parsed timestamps to a recent window (for example 24h), suppress non-actionable Git stderr such as `not a git repository`, and fixture-test that an old error is excluded while a current error remains detected. Identify the executable’s imported runtime module before editing: repository source and scheduler runtime can diverge. If current-day generated inbox/index artifacts were polluted, preserve a timestamped backup, rebuild only those generated artifacts, then run the scheduler and assert stale markers and `git_*` events are absent. A direct runtime-package patch is a temporary bridge; promote it through a clean feature worktree, focused regressions, active-runtime package install/import readback, and a fresh scheduler run before opening a review PR. Do not merge around CI/review gates. See `references/journal-collector-runtime-skew-and-stale-log-repair.md` and `references/canonical-journal-runtime-release.md`.
   - **Fragile LLM-only digest cron:** if a digest has a stable reporting contract but fails on missing skills, unresolved env-var paths, or repo-context assumptions, replace it with a deterministic profile-local no-agent script. Use absolute source paths, explicit `gh -R owner/repo` checks, remove missing skill dependencies, and keep read-only digests from mutating registries. See `references/golden-thread-digest-deterministic-cron.md`.
   - **No-agent AGY/LLM cron leaking scratchpad:** if a `no_agent` script invokes AGY/Codex/Claude and the scheduler delivers stdout to Telegram, never pass raw model/CLI output through. Strip interactive progress chatter (`I am going to…`, `I will…`, `Let me…`), background task scaffolding, and local diagnostic prefixes; preserve only compact user-facing blocker tables/recommendations. Green/no-delta must produce empty stdout. Verify with fixtures for scratchpad stripping, retained markdown table, deterministic fallback, direct no-delta silence, and latest scheduler output. See `references/no-agent-agy-output-sanitization.md`.
   - **No-agent delta/quota cron printing routine all-clear:** if a shared delta helper prints `[SILENT]` or green JSON, or a quota/status poller prints healthy tables every run, patch the producer so all-clear stdout is empty while local state/log artifacts are still written. Alert stdout should remain for true failures/exhaustion only. Verify the helper directly and then run the affected cron through the scheduler so the latest output reads `Status: silent (empty output)`. See `references/no-agent-delta-and-quota-noise.md`.
   - **No-agent backlog gap cron repeating already-routed work:** if a backlog delta worker pages Michael with a long gap table, live-check cited Linear issues before routing. Suppress issues that already have `dispatch:ready`, `dispatch:paused`, or concrete owner labels (`agent:fred`, `agent:agy`, `agent:jules`, `agent:kai`, etc.); those belong to owner lanes, not the Michael-facing gap feed. Park explicit “do not start until Michael initiates” issues with `dispatch:paused` instead of dispatching. If verification surfaces detector-created cron-fix issues, execute/verify the underlying cron and close duplicate detector issues only with fresh scheduler evidence. See `references/nightly-backlog-gap-routing-and-transient-backup-retry.md`.
   - **Multi-cron remediation queue:** when several active crons/digests are noisy or partially broken, do not stop at a ranked plan. For each cron, state the plan, execute the smallest producer/config/action fix, run the scheduler job, and finish with one focused `/tmp/hermes-verify-*` batch verifier. Common fixes: active-problems-only digest silence, `Chat not found` delivery quarantine to `local`, missing-skill reroute to the class-level skill, dispatcher batch caps, stale registry wording cleanup, and human-approval rows packaged as checklists rather than falsely completed. See `references/multi-cron-fleet-remediation-plan-execute.md`.
   - **Linear budget guard flags an active deterministic digest:** if the active `Linear API Budget Guard` cron reports a script bypassing `linear_api_compat`, patch the offender to call `linear_call("cron.<name>", query, variables)` instead of whitelisting it. Remove raw Linear endpoint constants, direct `urllib`/`curl` GraphQL calls, and direct Authorization header construction for task queries. Then run the guard directly, run the guard cron through the scheduler, and dry-run Tier-1 to confirm the recovered job no longer appears. See `references/golden-thread-digest-linear-budget-guard.md`.
   - **Post-publish stuck alert stale Linear labels:** if a stuck-alert cron pages Michael for an issue that is already Linear `Done`/completed but still has labels like `dispatch:ready` or `agent:post-publish-doc-update`, fix both layers: remove stale operational labels from the completed issue/add `agent:done`, and patch the producer to suppress completed/canceled/duplicate issues and `agent:post-publish-done` even when stale post-publish labels remain. Also route the script through `linear_api_compat.linear_call("cron.post_publish_stuck_alert", ...)` instead of raw Linear GraphQL so the alert cron respects the shared API budget. Verify direct quiet mode returns empty stdout and scheduler output is `Status: silent (empty output)`.
   - **Alert cron polluted by test/smoke debris:** if a stuck-alert cron pages Michael for a live Linear issue whose title/description clearly marks it as `[TEST]`, `TEST:`, or smoke-test debris, verify the issue live, then filter that class from Michael-facing alerts rather than closing or mutating the issue without evidence. If the scheduler already owns Telegram delivery, remove internal Telegram sends and make quiet/all-clear output empty. See `references/post-publish-stuck-alert-test-debris.md`.
   - **Mutable-state backup tar/read failure:** if a backup cron fails with tar/read symptoms such as `unexpected end of data` while archiving a live state directory, first rerun directly and through the scheduler to distinguish transient filesystem churn from a broken script contract. Harden the wrapper with a one-time retry that removes any partial archive before retrying, then fixture-test the retry by mocking the first tar open/read to fail and asserting the second pass creates a valid archive. See `references/nightly-backlog-gap-routing-and-transient-backup-retry.md`.
   - **AGY OAuth PKCE login:** before making Michael race the short browser-code timeout, check for an existing refresh token in all expected AGY/Hermes token paths. Empty or corrupt token files from failed attempts should be skipped so a later valid fallback token can be refreshed non-interactively. Prefer refresh-token candidates over access-token-only files, copy refreshed tokens back to every durable token path, and smoke-test AGY with a bounded minimal prompt. If browser auth is still required, the authorization code is bound to the exact still-running CLI process/link that generated it. If a code returns `invalid_grant` / `Invalid code verifier`, start a fresh PTY listener, send the new link, and submit the new code to that same process before its short timeout. See `references/agy-oauth-pkce-refresh.md` and `references/agy-oauth-resilient-refresh.md`.
   - **AGY supervisor model/path drift:** if a supervisor cron repeatedly restarts and logs show AGY under `~/.hermes/profiles/*/home` or model rejections for lowercase IDs like `gemini-3.5-flash`, fix the wrapper and model contract together. Pin `HOME`, `AGY_BIN`, token/router/cron paths in the cron wrapper; update default/routing maps to current AGY display labels such as `Gemini 3.5 Flash (Medium)`; then run a fresh `/tmp/hermes-verify-*` proof packet that checks py_compile, `bash -n`, path exports, model mapping, bounded live AGY smoke, and any recovered inbox markdown. See `references/agy-supervisor-model-path-drift-and-verifier.md`.
   - **Duplicate runtime source:** if the alert keeps firing after the Hermes cron script was patched, stop tuning thresholds and prove the sender. Check `ps`, `systemctl cat/status`, root-level `~/.hermes/scripts/` copies, and hardlinked profile scripts for the exact old alert text. Disable/mask stale daemons before declaring the cron fixed.
   - **Gateway/profile slow but healthy:** if a live Hermes profile feels slow, first separate cron load from model/context/tool latency. Check gateway state, active model, recent `agent.log` context size/API latency, long tool calls, Telegram flood control, host load, and the profile cron list/latest outputs. A silent no-agent watcher is usually not the root cause, but can be paused briefly to clear the lane. If pausing, schedule a local no-agent one-shot resume and verify the helper with `bash -n` plus exact job-id assertions. See `references/profile-cron-temporary-pause-and-auto-resume.md`.
   - **Gateway active but agent not responding:** if a Hermes profile/gateway service is `active` but the agent does not answer Telegram, do not stop at process health. Inspect `journalctl -u <profile>-gateway.service`, the profile `gateway_state.json`, and platform state. Repeated `telegram connect timed out` reconnect loops mean the Telegram adapter is wedged even while systemd is green. Restart the gateway, verify `platforms.telegram.state=connected`, smoke the profile model path separately, and harden systemd `TimeoutStopSec` to at least the gateway drain timeout. See `references/hermes-gateway-telegram-reconnect-wedge.md`.

4. **Patch the smallest load-bearing layer.**
   - If editing Prismatic workspace files, follow lane governance: lock file before edit, unlock after the edit/commit boundary.
   - If lane governance blocks push/PR after a valid fix, do **not** stop at “blocked.” Immediately route the work to the lane owner who can move it: create/update a Linear issue with `dispatch:ready`, the correct `agent:*` owner label, the exact patch/diff or branch/commit, fresh verification output, and the precise lane-guard error. Keep any safe local runtime fix in place only as a temporary bridge, then report the handoff handle.
   - For Hermes profile scripts, keep wrappers self-contained when upstream modules are absent or unstable.
   - When fixing a blocked no-agent cron path, prefer a thin profile-local wrapper over moving the canonical project script. The wrapper should run the canonical script from its project workdir, use a bounded timeout, validate output, write any durable artifact, and print a concise JSON success payload.
   - For no-agent crons, make failure modes explicit in stdout/stderr so future watchdogs have useful evidence.

5. **Re-run the affected cron(s).**
   - Use `cronjob(action="run", job_id="...")` when available.
   - Confirm `last_status=ok` afterwards.
   - Read the latest output file to confirm it contains real success evidence, not just scheduler metadata.

5a. **For availability/watchdog/report crons that should only alert on a target condition.**
   - Build them as no-agent, profile-local scripts with a relative script name so scheduler execution matches the profile sandbox.
   - Force the live/provider refresh first; use cache only as a fallback and record fallback state without claiming the target exists.
   - Normalize target IDs aggressively: lowercase, strip provider prefixes, convert separators, and compare known variants.
   - Stay silent on absence/all-clear/no-drift/no-warning conditions; write concise JSON/Markdown state under the profile `state/` directory or local cron output instead of sending “still absent,” “0 failures,” fleet stats, or “no drift” heartbeat notifications.
   - If the scheduler delivery target itself can page Michael, set the cron delivery to `local` and let the script perform explicit Telegram delivery only on actual alert conditions. For no-agent crons, remember that any non-empty stdout may be delivered verbatim; make all-clear stdout empty when the user expects silence.
   - On presence/problem, emit exactly the user-requested alert contract and persist an escalation counter if repeated alerts are desired.
   - Verify both branches with isolated fixtures: all-clear produces empty stdout and no Telegram/send call; alerting still sends and includes the problem details.
   - See `references/model-availability-watch-crons.md` for the GPT-5.6 provider-list watch pattern.
   - See `references/alert-only-cron-all-clear-silence.md` for the Tier-1 Silent Failure Watchdog and weekly homelab inventory all-clear suppression pattern.

5b. **For watchdog/all-clear crons that should not page Michael when green.**
   - Treat non-empty stdout from no-agent crons as deliverable user-facing output. Do not print headers, scan counts, all-clear summaries, or fleet stats before determining there is a real problem.
   - On all-clear, return `0` with empty stdout. If useful, write state/forensics to a local file only.
   - Check whether the script sends Telegram/HTTP internally. If so, changing the cron `deliver` target to `local` is insufficient; patch the producer so the all-clear branch does not call the send function.
   - Preserve the alert path: actual failures/drift/warnings should still print/send exactly once.
   - Verify with a `/tmp/hermes-verify-*` fixture that monkeypatches the send function: all-clear produces `stdout == ''` and zero sends; alert produces output and one send.
   - See `references/no-agent-watchdog-all-clear-silence.md` for the concrete pattern.

6. **Run a focused ad hoc verification script when code changed.**
   - Create the script using Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` or equivalent OS-safe tempfile creation.
   - Verify behavior against isolated fixtures where possible rather than mutating live state.
   - Include at minimum:
     - `py_compile` for changed Python scripts
     - assert the runtime imports the same module/worktree you patched when duplicate Prismatic worktrees exist (`inspect.getfile(module)` or `module.__file__`)
     - isolated fixture tests for repaired parsing/report/backup behavior
     - bounded subprocess test for timeout/hang fixes
     - for profile-local cron wrappers: execute the wrapper, parse its stdout contract, assert any artifact exists, and verify artifact content matches the payload
     - watchdog/detector dry-run confirming recovered job IDs are removed from the silent-failure bucket, even if unrelated credential jobs remain failing
   - For shared external API budget fixes, monkeypatch the network layer and assert: budget consumed before network, exhaustion blocks before network, 429 writes cooldown, and cooldown blocks follow-up without network.
   - Delete the temporary script after the run when possible.
   - Report the result as **ad hoc targeted verification**, not full suite green.

7. **If remediation is blocked by an external rate limit or governance/lane wall, create a real handoff/retry path.**
   - Do not stop at “try again later” or “blocked by lane guard” when the user asked for completion.
   - If a workspace lane guard blocks your patch, do not bypass it. Find the existing owner-lane PR/branch if one exists, comment with the exact failing contract, evidence, and proven patch delta, then re-route Linear labels to the owner with `dispatch:ready` and verify the labels changed.
   - Make retry/handoff idempotent: it should verify existing partial work, upsert only missing pieces, and be safe to run multiple times.
   - For no-agent retry crons, stay silent while still rate-limited, print a final success report exactly once, and write a completion marker so later runs stay silent.
   - Use relative script names for Hermes cron scripts under the active profile scripts directory; absolute script paths may be rejected by the scheduler.

8. **For API budget burn, fix the shared budget contract, not only the caller that failed.**
   - Inventory every live caller of the API endpoint and key, including startup preflight probes, watchdog/safety-net polls, single-item fallback fetches, and shared helper modules.
   - Gate all calls through one tenant-level budget bucket before network I/O. Do not use independent per-agent buckets when the upstream limit is tenant-scoped.
   - Fail closed if the budget module is unavailable in operational supervisors; do not silently fall back to unmetered direct HTTP.
   - On upstream 429, write a local cooldown marker and block follow-up calls locally until reset instead of probing repeatedly.
   - If the system is “event-driven,” confirm legacy polling is only a slow safety net and that any `--watchdog-interval` style flag is actually applied at runtime.
   - When a budget-guard cron reports a specific active offender, patch the offender script to use the shared shim instead of whitelisting it. Even read-only digest/report crons must use the budget gate. After patching, run the guard through the scheduler so `last_status` clears, then run Tier-1 dry-run/no-linear to prove the recovered job is absent.

9. **Re-run the watchdog/detector in dry-run mode if possible.**
   - For Tier-1 silent failure work, run the detector dry-run/no-linear mode after repairs.
   - Look for `Current silent failures: 0` or explicit recovered job IDs.

## Pitfalls

- Do **not** stop at “last_status=ok” if the script was changed; add focused verification evidence.
- Do **not** call ad hoc checks “suite green.” Michael explicitly wants scope labels.
- Do **not** preserve an import of a removed upstream module just because it used to exist. If the cron owns an operational contract, make the wrapper robust or point it at the current module.
- Do **not** let a subprocess run with unlimited timeout inside a frequent cron. A killed cron (`exit -15`) is a silent-failure generator.
- Do **not** alert on raw system load without normalizing by available CPU cores. Load `6.0` on a 64-core host is quiet; load `6.0` on a 4-core host may be high. Include the denominator and ratio in monitor output.
- Do **not** treat unreachable SSH/Tailscale nodes as proof the servers are down. Label it as monitor connectivity state unless another source verifies host failure. If SSH is gated by Tailscale auth, try the Proxmox API on `https://<node>:8006/api2/json` when credentials are available.
- Do **not** assume the script copy you edited is the only one in play. Search all Hermes profiles for the alert text and check hardlinks/inodes when duplicate profile scripts exist.
- Do **not** trust “event-driven” as proof polling is gone. Inspect active process flags and code paths; safety-net watchers, startup probes, and helper modules can still burn API quota.
- Do **not** trust a quiet local budget DB as proof an upstream API is protected. It may mean the hot path bypasses the budget layer entirely.
- Do **not** call repeated guard-requested tempfile checks “suite green.” Treat them as fresh ad hoc evidence, and make the verifier itself prove no real upstream calls were made.
- Do **not** treat a failed tempfile verifier caused by your own quoting/scripting mistake as target verification evidence. Create a fresh OS-safe `hermes-verify-*.py`, prefer `"\n".join([...])` for embedded Markdown samples over nested triple-quoted strings, run it, clean it, and report the passing verifier path/exit/cleanup as ad-hoc targeted verification only.
- Do **not** let availability watches become noisy heartbeat reminders. Absence should normally be silent; only the target condition should produce stdout/delivery.
- Do **not** let all-clear health/watchdog crons print routine summaries. In no-agent mode, even a harmless “0 failures” or “no drift” stdout body can become a Michael-facing delivery. All-clear should be empty stdout unless the user explicitly asked for heartbeat reports.
- Do **not** let wrappers hide alert-producer failures or create noisy fragments. Avoid `tail -c ...` plus forced `exit 0` for alert crons; preserve the producer exit code and make the producer responsible for concise stdout.
- **Do not let the plan name "system cron" or "always-on daemon" as the trigger authority without verifying the deployment model.** If the user says the product is mobile/laptop-first and the host is not always on, the trigger authority must be opportunistic wakeup (system-cron thin hook + app-startup catch-up sweep + manual + external-event) into one canonical runner — see `plan-reconciliation-after-peer-review` → "Mobile-first product trap."
- Do **not** keep tuning a Fred-side machine-health cron after Michael says Autobot owns that lane. Remove/pause the duplicate Fred cron and verify it is gone.
- Do **not** treat historical transcripts, archived scripts, cron backup snapshots, or old logs as active health-alert emitters. Verify current scheduler entries, live processes, systemd state, runnable script dirs, and active aggregators instead.
- Do **not** patch an aggregator by broadly dropping all health/crons. Suppress only the rejected monitor class (for example Proxmox/PVE load/unreachable clutter) and fixture-test that unrelated actionable failures are still retained.
- Do **not** update only alert copy for a threshold change. The comparison, emitted threshold text, docs/comments, and all-clear copy must agree.
- Do **not** treat AGY OAuth authorization codes as reusable. They are PKCE-bound to the active CLI listener that generated the link; a code from an older link will fail with `Invalid code verifier`. Generate a fresh link and submit the new code to the same still-running process.
- Do **not** assume the source tree you edited is the runtime import source. In Prismatic worktree-heavy environments, prove `prismatic.journal.__file__` / `inspect.getfile()` resolves to the patched tree before claiming a core cron fix.
- Do **not** require the whole Tier-1 watchdog to be green when the user asked to fix one job. Report the requested job as recovered and name any unrelated continuing failures separately.

## Verification language template

Use concise wording like:

```text
Ad hoc targeted verification: PASS
- /tmp/hermes-verify-xxxx.py created with tempfile and cleaned up
- py_compile passed for changed Python files
- isolated fixture verified <behavior>
- bounded timeout verified <script> returns before scheduler kill
Scope: ad hoc targeted verification only — not full canonical suite green.
```

## References

- `references/tier1-silent-failure-remediation-2026-07.md` — concrete patterns from a Tier-1 Silent Failure Watchdog remediation: data-shape drift, removed module wrapper repair, no-agent report replacement, and bounded AGY timeout handling.
- `references/profile-safe-cron-wrappers-and-shape-drift.md` — profile-local wrapper pattern for no-agent crons blocked by archived/absolute script paths, plus registry `_last_sync` string-vs-dict drift handling and verifier shape.
- `references/deterministic-cron-and-second-witness-recovery.md` — pattern for replacing fragile LLM-only crons with deterministic no-agent scripts and restoring bounded “Second Witness” review behavior with fallback output.
- `references/resource-monitor-normalized-thresholds.md` — pattern for fixing noisy resource monitors by normalizing load by CPU cores and verifying alert/no-alert fixtures.
- `references/proxmox-monitor-capacity-and-cooldown.md` — Proxmox-specific monitor pattern: verify host/vm cores via API, normalize load, detect duplicate/hardlinked profile scripts, and add per-alert cooldown state.
- `references/shared-api-budget-cooldown-remediation.md` — pattern for fixing shared external API quota burn: inventory live callers, route through one budget gate, add provider 429 cooldown, demote polling, and verify with no-real-API fixtures.
- `references/linear-api-budget-gating.md` — pattern for stopping Linear/API credit burn in event-driven supervisors: inventory direct callers, enforce a shared tenant-level budget before network I/O, write 429 cooldown markers, demote safety-net polling, and verify with no-real-API-call fixtures.
- `references/golden-thread-digest-linear-budget-guard.md` — concrete active-cron recovery pattern when the Linear API Budget Guard flags a deterministic digest such as Golden Thread Daily Digest for raw Linear GraphQL calls; patch through `linear_api_compat.linear_call`, run the guard cron, and verify Tier-1 recovery.
- `references/profile-safe-wrapper-and-shape-drift-2026-07.md` — pattern for fixing no-agent cron scripts rejected for external absolute paths and for hardening JSON readers against durable shape drift, with focused watchdog verification.
- `references/profile-local-cross-profile-cron-wrapper.md` — thin active-profile wrapper pattern for no-agent crons that need to call another profile's canonical script without violating the scheduler's allowed scripts directory.
- `references/status-page-health-contracts.md` — pattern for restoring degraded dashboards/status pages by separating current health from stale synthetic drills, cumulative restart history, and durable recovery logs, with live UI/API proof.
- `references/model-availability-watch-crons.md` — pattern for no-agent provider/model availability watches: refreshed provider list, variant normalization, silent absence, escalating hit alerts, and focused verification.
- `references/stale-daemon-vs-cron-alert-source.md` — pattern for cases where an alert continues after the Hermes cron was fixed: find duplicate `systemd`/root-script/runtime sources, disable stale daemons, replace unsafe script copies, and verify no stale process remains.
- `references/prismatic-journal-core-browser-pattern.md` — pattern for fixing daily journal cron failures in Prismatic core: `_last_sync` shape coercion, runtime workspace resolution, read-only journal tree/file APIs, dashboard journal browser, and watchdog verification.
- `references/health-alert-ownership-and-threshold-tuning.md` — pattern for Michael's machine-health alert corrections: respect Autobot ownership by stopping duplicate Fred crons, and patch/verify storage/resource thresholds end-to-end.
- `references/fred-facing-machine-health-noise-removal.md` — pattern for rejected Fred-facing machine-health monitors: suppress Proxmox/PVE load/unreachable clutter from aggregators, quarantine stale runnable artifacts, and verify active emitters only.
- `references/agy-oauth-pkce-refresh.md` — pattern for AGY OAuth cron/token recovery: PKCE code/link/process binding, short listener timeout, fresh-link retry, and safe verification without storing secrets.
- `references/journal-recap-stale-log-and-lane-handoff.md` — pattern from a journal/cron cleanup session: verify recap flags against live cron state, filter stale timestamped gateway log noise, repair OAuth invalid_grant with a stateful reauth helper, and route lane-blocked patches to the owner PR/Linear label instead of stopping.
- `references/golden-thread-digest-deterministic-cron.md` — pattern for replacing fragile Golden Thread/daily digest LLM crons with deterministic profile-local no-agent scripts using canonical registry paths, explicit `gh -R` repo context, and focused scheduler verification.
- `references/agy-oauth-resilient-refresh.md` — pattern for avoiding repeated short PKCE-code races by discovering fallback refresh tokens across AGY/Hermes paths, skipping empty/corrupt token files, refreshing non-interactively, copying tokens to durable paths, and verifying with isolated fixtures.
- `references/gdrive-mcp-oauth-refresh.md` — Google Drive MCP `invalid_grant` repair pattern: generate a consent URL, validate state, exchange pasted redirect URL, write `.gdrive-server-credentials.json`, and verify both direct Drive API and Hermes MCP `drive_about`.
- `references/no-agent-watchdog-all-clear-silence.md` — pattern for health/watchdog crons that should stay silent when green: empty stdout on all-clear, no internal Telegram send, preserve alert path, and verify both branches with monkeypatched sends.
- `references/post-publish-stuck-alert-test-debris.md` — pattern for stuck-alert crons polluted by live `[TEST]`/smoke Linear issues: verify live issue state, filter non-production debris from Michael-facing alerts, use one Telegram delivery owner, make quiet mode silent, and fixture/live-verify stdout behavior.
- `references/no-agent-agy-output-sanitization.md` — pattern for no-agent crons that invoke AGY/LLM CLIs: strip scratchpad/background-task scaffolding, preserve compact blocker tables, make green/no-delta stdout empty, and verify scheduler output.
- `references/no-agent-delta-and-quota-noise.md` — pattern for shared delta helpers and quota/status pollers that print routine all-clear output: keep local state/log writes, make stdout empty unless there is a true alert, and verify direct helper behavior plus scheduler output.
- `references/nightly-backlog-gap-routing-and-transient-backup-retry.md` — pattern for recovering Nightly Backlog Worker gap tables, suppressing already-routed/held Linear issues, parking explicit Michael-initiation guardrails, closing duplicate cron-fix detector issues with scheduler evidence, and hardening mutable-state backup tar failures with a one-time retry plus tempfile verifier.
- `references/multi-cron-fleet-remediation-plan-execute.md` — pattern for turning a ranked cron queue into executed fixes across several active jobs: active-problems-only digests, delivery quarantine, missing-skill reroutes, dispatcher batch caps, stale registry wording cleanup, remediation packets, scheduler runs, and one batch verifier.
- `references/hermes-gateway-telegram-reconnect-wedge.md` — pattern for a profile/gateway that is `systemctl active` but not responding: Telegram reconnect timeout loops, `gateway_state.json` platform-state proof, direct model smoke, restart, and `TimeoutStopSec` hardening.
- `references/stale-bash-spawned-gateway-blocking-systemd.md` — pattern for a gateway in `activating (auto-restart)` loop with `❌ Gateway already running (PID <stale>)` in journal: a non-systemd bash-spawned instance from a prior interactive session is holding the duplicate-check lock. Signal only the bash-spawned PID (PPID must be bash, not systemd), let systemd recover. Distinct from the Telegram reconnect wedge.
- `references/linear-budget-guard-digest-remediation.md` — pattern for clearing Linear API Budget Guard failures caused by active digest/report crons with raw GraphQL calls: patch offender to `linear_api_compat.linear_call()`, run the guard through scheduler, and verify Tier-1 dry-run recovery.
- `references/agy-supervisor-model-path-drift-and-verifier.md` — AGY supervisor recovery pattern for profile-HOME path drift plus legacy lowercase model IDs, including the required fresh `/tmp/hermes-verify-*` proof packet shape.
