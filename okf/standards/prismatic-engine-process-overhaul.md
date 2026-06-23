---
type: Standard
title: Prismatic Engine Process Overhaul — Lessons Learned (2026-06-23)
description: The canonical "lessons learned" doc from the /yolo session. Every bug that was found and fixed, the pattern that caused it, and the explicit anti-pattern rules. Future agents and humans MUST read this before touching the agent swarm.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/prismatic-engine-process-overhaul.md
tags: [standard, lessons-learned, post-mortem, anti-pattern, agent-swarm, dispatchers, agy, kai, ned, jules, recurring-bugs, must-read]
timestamp: 2026-06-23T08:15:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-engine-process-overhaul.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Prismatic Engine Process Overhaul — Lessons Learned

> **Why this doc exists:** In one /yolo session (2026-06-23 04:00-08:15 UTC), we found and fixed **5 recurring bugs** that had been silently breaking the Prismatic Engine agent swarm for weeks. This doc captures the patterns + fixes so we don't hit them again.
>
> **MUST READ before touching:** The dispatcher scripts (`*.py` in `~/.hermes/profiles/orchestrator/scripts/`), the cron schedule (`cron/jobs.json`), the AGY Sandbox Supervisor, the AGY Watchdog, or the agent lane labels (`agent:*` in Linear).

## The 5 recurring bugs (and the anti-patterns that caused them)

### Bug #1: `--model "<broken name>"` silently falls back to default

**What broke:** Three dispatchers (Ned Delta Dispatcher, Kai Delta Dispatcher, AGY Golden Thread Review) used bogus model names: `"Claude Sonnet 4.6 (Thinking)"` (the namespaced version, not the real model ID), `"sonnet"` (short alias that doesn't exist), or just the default. Every AGY call silently fell back to `"Gemini 3.5 Flash (Medium)"` — the actual "model flavor" label system was a fiction.

**Pattern:** Anywhere AGY is invoked via subprocess, the `--model` flag must use a real, verifiable model name from `agy models` output. Never trust documentation that lists display names; verify with `agy models`.

**Fix:** Changed all 3 dispatchers to use `"Gemini 3.5 Flash (High)"` (verified via `agy models`). Commits: `28c4ae5` + `3fdfa57`.

**Anti-pattern rule:** "Don't trust, verify" — before invoking an LLM, run `--help` or `models` and confirm the model name exists.

### Bug #2: `orderBy: priority` — Linear API enum mismatch

**What broke:** The AGY Sandbox Supervisor's `fetch_linear_issues()` used `orderBy: priority` in its GraphQL query. Linear's `PaginationOrderBy` enum has 6 values (`createdAt`, `updatedAt`, `canceledAt`, `completedAt`, `startedAt`, `dueDate`) but **NOT `priority`**. Every supervisor fetch returned HTTP 400. The supervisor never saw new issues, so it force-shut-down after 5 min with 0/0 done.

**Pattern:** Linear's API enums are restrictive. A query that compiles may still 400 because of an invalid enum value.

**Fix:** Changed `orderBy: priority` → `orderBy: createdAt` in both `agy_sandbox_event_supervisor.py` and `agy_sandbox_supervisor.py`. Commit: `f930288`. Verified: query now returns 41 issues from Linear.

**Anti-pattern rule:** "Test API queries with the actual endpoint, not in isolation" — the query worked in isolation (curl test), but the supervisor's invocation exposed the bug. Always test in the full call path.

### Bug #3: heartbeat checking `transcript.jsonl` that never existed

**What broke:** Both the AGY Sandbox Supervisor's heartbeat AND the AGY Watchdog checked `transcript.jsonl` size in `~/.gemini/antigravity-cli/brain/` for progress. **AGY's `--print` mode writes to stdout, not a transcript file.** The file never existed or never grew. Result: 5-min "no transcript progress" warning always fires, regardless of whether AGY is actually stuck.

**Pattern:** When checking for "progress," always verify that the signal source actually exists and is written to. Many tools don't write to a transcript by default.

**Fix:**
- **Supervisor** (commit `5479696`): Use `sandbox_dir.rglob('*').stat().st_mtime` — any file modified in the sandbox = progress.
- **Watchdog** (commit `3aaaf36`): Search recursively for `brain/<uuid>/.system_generated/logs/transcript.jsonl` and `transcript_full.jsonl`. The brain dir has 508 subdirs (one per AGY session); top-level `.md` files never existed.

**Anti-pattern rule:** "The heartbeat source must be proven to update" — before relying on a file/socket/pipe for liveness, write a test that mutates it and confirms the watcher fires.

### Bug #4: 5-minute wall-clock cap kills real work mid-stream

**What broke:** The supervisor's `idle_event.wait(timeout=300)` and the watchdog's `STALL_KILL_SECONDS = 300` were hardcoded 5-min timeouts. Real AGY work (commits + builds + tests + sync) takes 5-15 min per session. The supervisor would force-shut-down workers mid-task; the watchdog would SIGKILL AGY processes during normal processing.

**Pattern:** Hardcoded short timeouts in long-running systems always cause premature termination. The number 300 (5 min) was a copy-paste from "interactive" expectations, not "agentic" ones.

**Fix:**
- **Supervisor**: Raised to 1800s (30 min) cap + check sandbox mtime before shutdown. If any file modified in last 90s, re-wait (recurse) — only kill truly idle workers.
- **Watchdog**: Raised `STALL_KILL_SECONDS` 300→1800s, `INACTIVITY_KILL_SECONDS` 300→1800s, `API_WAIT_SECONDS` 180→600s.

**Anti-pattern rule:** "Timeouts in agentic systems should be based on actual workflow duration, not copy-pasted from interactive UIs" — measure the longest realistic task and add 2x margin.

### Bug #5: AGY exits 0 with "DONE" but never saves RESULT.md

**What broke:** The supervisor checked for `DONE: <issue_id>` in AGY's log to mark a task ✅ Done. But AGY's `--print` mode often just prints the DONE line to stdout without writing `RESULT.md`. Result: 14 issues marked "Done" in the supervisor summary but with no deliverable artifact. The "🟡 Other" category silently absorbed these ghost-stuck completions.

**Pattern:** Verifying completion by parsing log output is brittle. Always check for the actual artifact (file, database row, API response).

**Fix:**
- **Post-condition check** (commit `5479696`): After AGY exits, check `(sandbox / "RESULT.md").exists()`. If "DONE" but no file → downgrade to new "🟡 MissingResult" status.
- **AGY prompt rewrite**: New `MANDATORY FINISH PROTOCOL` in the supervisor's prompt — explicit 4-step sequence: (1) Write RESULT.md, (2) include specific fields (files changed, commit hashes, follow-ups), (3) only then output DONE, (4) if can't save, output ERROR.
- **New summary category**: `✅ Done`, `⏰ Timeout`, `❓ Clarify`, `🟡 MissingResult`, `🟠 Other`.

**Anti-pattern rule:** "Trust the artifact, not the log" — for any "task complete" signal, check the actual deliverable. Don't rely on parsing free-text output.

### Bonus bugs found and fixed

### Bug #6: `pwp_ingest_generic.py` — no fallback for `docs/` dir + hangs on large AGY prompts

**What broke:** The script assumed every project uses `okf/` for docs, but `agentic-swarm-ops` uses `docs/`. Also, the AGY extraction prompt took 5+ min for large OKFs, often timing out.

**Fix:** Added auto-detection of `docs/`, `knowledge/`, `documentation/` alternatives + a `--no-agy` flag for fast ingestion without LLM extraction. Commit: `cff0581`.

**Anti-pattern rule:** "Don't hardcode conventions — detect them" — always try common alternatives before failing.

### Bug #7: Ned Delta Dispatcher — wrong state.type enum values (`"todo"`, `"inProgress"`)

**What broke:** Ned used `state: { type: { in: ["todo", "inProgress", "backlog"] } }`. Linear's actual enum values are `"unstarted"` (Todo), `"started"` (In Progress/In Review), `"backlog"`. Wrong values → 0 issues returned every run → `[SILENT]`. Kai already used the correct values.

**Fix:** Changed Ned to `["unstarted", "started", "backlog"]`. Same fix applied to `nightly_backlog_delta.py`. Commits: `2ecbbe6` + `6a15dbc`.

**Anti-pattern rule:** "Verify enum values from the API spec, not from documentation" — when in doubt, query Linear for the actual enum values via `workflowStates { nodes { type } }`.

### Bug #8: AGY Watchdog — same transcript.jsonl detection bug as the supervisor

**What broke:** The watchdog's `get_latest_brain_transcript()` looked for top-level `*.md` files in `~/.gemini/antigravity-cli/brain/`. But that dir contains 508 subdirs (one per AGY session), each with `.system_generated/logs/transcript.jsonl`. The function returned None every call → permanent "no transcript progress" alerts + the 300s/300s thresholds would SIGKILL healthy AGY sessions.

**Fix:** Rewrote `get_latest_brain_transcript()` to search recursively for `transcript.jsonl` and `transcript_full.jsonl` in brain subdirs. Raised thresholds to 900s warn / 1800s kill. Commit: `3aaaf36`.

**Anti-pattern rule:** "The same bug can exist in multiple files" — when you fix a bug in one cron script, grep the entire scripts directory for the same pattern.

### Bug #9: Hard 5-30 min timeouts killed real work; no operator visibility until 5+ min

**What broke:** The supervisor's `idle_event.wait(timeout=300)` and `wait_for_completion(timeout=1800)` were hardcoded timeouts. The heartbeat watcher slept 60s between checks. Operators would watch silence for 5+ min before getting any "stuck" verdict.

**Per Michael's directive (2026-06-23):**
1. "5 mins is way too long to be waiting without knowing anything. We should 'know' within 2 minutes if it's actually working."
2. "Get rid of timeouts if there is real progress going on, let's raise the limit to 1hr. Or, there is no hard limit, like, if at 55mins, it's still going, it gets the roof raised and keeps checking?"

**Fix (commits `d64ec46` + `42a2059`):**
- `heartbeat_watcher` v4: dynamic check interval (30s early, 60s after). At exactly 2 min after AGY launch, emits a verdict:
  - 🟢 "AGY wrote RESULT.md — done!"
  - 🟢 "healthy — sandbox activity recent" (last 60s)
  - 🟡 "slow — last activity Xs ago" (60-300s, still within tolerance)
  - 🔴 "stuck — no activity for Xs, will warn at 5 min"
- `wait_for_completion` v5: initial cap raised to 3600s (1hr). At cap, check sandbox mtime:
  - All stuck → force-shutdown (only when ALL workers have no activity >90s)
  - Mixed → kill stuck, raise the roof by 1hr for active workers
  - All active → raise the roof by 1hr
- `linear_watchdog_loop` v6: poll # log so operator can see watchdog is alive ("fetched 0 issue(s), 0 new (0.2s)")

**Anti-pattern rule:** "Operators should NEVER wait >2 min without knowing what's happening" — every long-running process needs an early status signal AND a way to raise timeouts when progress is real.

### Bug #10: Prismatic Port Progress + Morning Digest — same root cause (prismatic.gql returns already-unwrapped data)

**What broke:** Both scripts assumed `linear_call()` returns the full `{"data": ..., "errors": ...}` envelope, then did `out["data"]` again. But `linear_call()` (via `prismatic.dispatcher.gql`) already returns `body.get("data", {})` — so the second `["data"]` lookup raised `KeyError: 'data'`.

**Plus:** Morning Digest's `send_telegram()` only supported `parse_mode: Markdown`. When the message contained characters Telegram's old Markdown parser rejected, it returned HTTP 400 and the script crashed.

**Fix:**
- `prismatic_port_progress.py` (commit `493b23c`): `gql()` returns `out` directly (already unwrapped). Added defensive type check for errors.
- `morning_digest.py` (commit `493b23c`): `send_telegram()` now tries Markdown first, falls back to plain text on 400. Real errors re-raise.

**Verified:** Both scripts now run cleanly.

**Anti-pattern rule:** "When you wrap a library function, know whether it already unwraps" — read the source. The `prismatic.dispatcher.gql` returns unwrapped data; don't unwrap again.

### Bug #11: 88 unlabeled Linear issues (no `agent:*` label) — invisible to all dispatchers

**What broke:** Linear has 88 Todo/Backlog issues with no `agent:*` label. The 5 dispatchers only pick up issues matching their watch list (`agent:agy*`, `agent:ned*`, `agent:kai*`, `agent:jules`). Unlabeled issues sit in the queue forever.

**Why:** Pre-rollout issues never got labels. Some new issues bypass the labeling convention.

**Fix:** Filed [GRO-2200](https://linear.app/growthwebdev/issue/GRO-2200) for triage. Filed [GRO-2203](https://linear.app/growthwebdev/issue/GRO-2203) for dispatcher standardization (shared error handling, shared enum validation).

**Anti-pattern rule:** "Make routing impossible to skip" — add a Linear validator that warns on issue creation without an `agent:*` label.

### Bug #12: Cloudflare tunnel — stale processes with wrong tokens, public URLs return HTTP 530

**What broke:** All `https://files.growthwebdev.com/raw/...` URLs returned HTTP 530. Local publisher on port 9120 was fine. `cloudflared tunnel info` error: "Cannot determine default origin certificate path".

**Real root cause (deeper than the cert.pem error suggested):** TWO stale `cloudflared` processes (PIDs 1372 + 1497) were running with old `--token` JWTs that mapped to DIFFERENT tunnels (abe7bbd9-... and another). The config.yml's correct tunnel `4a6097ff-...` was NOT being served. The misleading cert.pem error was because `cloudflared tunnel info` reads config.yml, not the running tokens.

**Fix (manual, not yet automated):**
- Killed PIDs 1372 + 1497
- Restarted with `cloudflared --config /home/ubuntu/.cloudflared/config.yml run 4a6097ff-...` (now PID 221947)
- Verified: 5 OKF doc URLs return HTTP 200 (was 530)
- GRO-2199 marked Done

**Anti-pattern rule:** "Verify with the actual URL, not with the health check" — the local publisher health check was passing (HTTP 200 on port 9120), but the public Cloudflare tunnel was down. Always test public-facing endpoints.

**Anti-pattern rule:** "Trust the actual logs, not the error message" — `cert.pem` was a red herring. The real issue was stale processes from old token authentications.

## Dispatcher architecture (the source of truth)

The Prismatic Engine has **5 dispatchers**, each responsible for a slice of agent lanes:

| Dispatcher | Cron ID | Watches labels | Mode |
|---|---|---|---|
| AGY Sandbox Supervisor (event-driven) | `faf8d91da716` | `agent:agy*` (9 flavors) | Event-driven (watchdog polls Linear every 90s) |
| AGY Sandbox Supervisor (non-event) | `e6a8d04d4e9b` | `agent:agy*` (9 flavors) | Batch (reads issue-batches/*.txt) |
| Ned Delta Dispatcher | `48876764f897` | `agent:ned*` (4 sub-lanes) | Polling |
| Kai Delta Dispatcher | `5fe7de2a1d9a` | `agent:kai*` (4 sub-lanes) | Polling |
| Jules Session Watchdog | `d895167114c9` | `agent:jules` | Polling |

**When filing Linear issues, the issue's `agent:*` label must match a dispatcher's watch list** — otherwise the issue sits in Todo forever. Use the `agent:agy` label for general AGY work, `agent:agy-pro` for the pro model, `agent:ned` / `agent:ned-infra` for Ned's code/infra lanes, etc.

## Cron-based vs interval-based scheduling

**Cron-based jobs** (schedule `kind: cron`, e.g., `0 9 * * *`) **don't auto-catch up after downtime**. If the scheduler is down for 2+ days, missed daily/hourly/weekly runs are **lost**. The interval-based jobs (every 5m/15m/30m) **DO keep working** through the gap because they self-trigger on next tick.

**Known root cause:** Around 2026-06-19, the orchestrator server was down for ~2 days. When it came back, interval crons caught up but cron-based ones didn't. The Next Step + Becca morning briefings, Golden Thread daily digests, and memory grooming all stopped silently.

**Workaround until scheduler is fixed:** Manually trigger missed jobs via `cronjob(action='run', job_id='...')` after any downtime.

## Heartbeat file locations (the source of truth)

| Tool | Path pattern | What it writes |
|---|---|---|
| AGY supervisor sandbox | `/tmp/agy_sandboxes/<ISSUE_ID>/RESULT.md` | Final task result |
| AGY brain transcripts | `~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/transcript.jsonl` | Step-by-step conversation log |
| AGY token | `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json` | OAuth credentials |

**Gotcha:** The brain dir has UUID subdirs (one per session). Don't assume top-level files exist.

## File locations (canonical)

| Component | Path |
|---|---|
| Dispatchers | `~/.hermes/profiles/orchestrator/scripts/*.py` |
| AGY Watchdog | `/home/ubuntu/work/agentic-swarm-ops/ops/agy_watchdog.py` |
| AGY Sandbox Supervisor | `~/.hermes/profiles/orchestrator/scripts/agy_sandbox_*.py` |
| Cron config | `~/.hermes/profiles/orchestrator/cron/jobs.json` |
| Cron output | `~/.hermes/profiles/orchestrator/cron/output/<job_id>/*.md` |
| PWP system | `~/.hermes/profiles/orchestrator/scripts/pwp/*.py` |
| Hermes profiles | `~/.hermes/profiles/<name>/` |
| Brain transcripts | `~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/` |
| gdrive MCP | `/home/ubuntu/work/local-gdrive-mcp/` |

## Anti-pattern rules (the gold)

1. **Don't trust, verify** — run `--help` / `models` before invoking any LLM CLI
2. **Test API queries with the actual endpoint, not in isolation** — compile-time success ≠ runtime success
3. **The heartbeat source must be proven to update** — write a test that mutates it first
4. **Timeouts in agentic systems should match workflow duration + 2x margin** — not copy-pasted from interactive UIs
5. **Trust the artifact, not the log** — for any "task complete" signal, check the actual deliverable file
6. **Don't hardcode conventions — detect them** — try common alternatives before failing

## Verification checklist (run this every Monday)

- [ ] `agy models` — verify the dispatcher model name is in the list
- [ ] `cat ~/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py | grep orderBy` — should be `createdAt`
- [ ] `cat /home/ubuntu/work/agentic-swarm-ops/ops/agy_watchdog.py | grep STALL_KILL_SECONDS` — should be `1800`
- [ ] Run the supervisor once with `--issues GRO-XXXX` — should not 400 on Linear fetch
- [ ] Check `/tmp/agy_sandboxes/` for any sandboxes with no `RESULT.md` after AGY exits
- [ ] Check the AGY Watchdog's last 3 runs in `~/.hermes/profiles/orchestrator/cron/output/500749c7949d/`

## Open follow-ups (post-2026-06-23 session)

- [ ] The cron-based scheduler still has the "no catch-up after downtime" bug — need to add a replay mechanism (separate from this doc)
- [ ] The Cloudflare tunnel returns HTTP 530 for public URLs — out of scope here, separate fix needed
- [ ] The 11 process-overhaul P1/P2 tasks filed in this session are now all queued — agent swarm should pick them up on next cron tick

## Change log

- **2026-06-23 08:15 UTC**: This doc. Captures 6 bugs fixed this session, 5 anti-pattern rules, 5 dispatcher architecture details, weekly verification checklist.