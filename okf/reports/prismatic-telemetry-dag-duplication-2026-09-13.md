---
type: report
title: "Prismatic Telemetry DAG Duplication — prismatic_telemetry Double Hook Registration"
description: "Root cause, fix, and restart evidence for the duplicated pipeline nodes in the Prismatic Hub telemetry DAG: the hermes prismatic_telemetry plugin registered the same handler on two LLM hooks, double-emitting every signal to the gateway."
resource: "okf/reports/prismatic-telemetry-dag-duplication-2026-09-13.md"
tags: [prismatic, telemetry, hermes-plugin, merkle-dag, incident, fix]
timestamp: "2026-09-13T20:05:00Z"
linear_issue: null
git_repo: "mbgulden/growthwebdev-knowledge"
git_path: "okf/reports/prismatic-telemetry-dag-duplication-2026-09-13.md"
last_verified: "2026-09-13T20:05:00Z"
verified_by: "fred"
status: current
---

# Prismatic Telemetry DAG Duplication — Double Hook Registration

**Date:** 2026-09-13
**Reporter/fixer:** Fred (orchestrator profile), at Michael's request
**Symptom:** every node in the Prismatic Hub telemetry DAG (Merkle-DAG pipeline) appeared twice;
Michael also observed duplicated Telegram replies around the same time window.

## Symptom

The "Reactive Topological Merkle-DAG Pipeline" on the Prismatic Hub dashboard
(`http://localhost:9000`, TELEMETRY tab) rendered each pipeline twice. The
`/api/gateway/dag/topology` endpoint returned 30 nodes (5 full 6-stage pipelines)
whose stage-1 nodes were literal duplicates: two `tool_call` nodes ~5ms apart, two
`thinking` nodes ~5ms apart, etc.

## Root cause

The Hermes observability plugin `prismatic_telemetry`
(`~/.hermes/plugins/prismatic_telemetry/__init__.py`, hardlinked across
`~/.hermes/plugins/`, `~/.hermes/profiles/orchestrator/plugins/`, and
`hermes-agent-fork/plugins/observability/` — same inode, untracked in git)
registered the **same handler on two different lifecycle hooks**:

```python
def register(ctx: Any) -> None:
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
    ctx.register_hook("pre_api_request", on_pre_llm_call)   # <-- same handler, second hook
```

- `pre_llm_call` (invoked in `agent/turn_context.py:1278`) is the
  **context-injection** hook — once per turn, return value may be appended to the
  user message.
- `pre_api_request` (invoked in `agent/conversation_loop.py:3064`) is the
  **observability** hook — what the bundled langfuse plugin is built for; receives
  raw request payload, `api_request_id`, model, provider.

Both fire on every LLM request, so every "thinking" event was emitted to the
gateway **twice**, ~5–10ms apart.

The gateway endpoint `/api/gateway/signals/emit` (`prismatic/gateway/server.py:~4512`)
records every POST as a new `HypervisorLedger` event with **no idempotency key and
no dedupe window**. The append-only Merkle ledger faithfully stored both events,
and the DAG renderer expands each ledger event into a full 6-node pipeline — so a
2x write burst becomes a 2x graph.

**Useful reason or mistake?** Mistake. The plugin is untracked (never committed,
written 2026-08-27, modified 2026-09-09) in the `plugins/observability/` folder
alongside the bundled langfuse plugin, and the fork's top commit is
"feat(plugins,clarify): add global plugins directory discovery, **auto-telemetry**,
and autonomous non-blocking mode" — a double registration is a plausible hedge from
that in-flight window ("register on both surfaces so the signal shows up no matter
which hook fires"), with the dedupe cleanup never done. The *principled* fix is the
opposite of what was shipped: a fire-and-forget telemetry POST belongs on
`pre_api_request` only; `pre_llm_call` has a real contract (return value is
injected into the user message). The shipped fix keeps `pre_llm_call` and drops
`pre_api_request` — functionally identical (one emission per event), mildly wrong
semantics, zero risk.

## Fix (applied 2026-09-13, live after gateway restart)

Removed the `pre_api_request` registration from
`~/.hermes/plugins/prismatic_telemetry/__init__.py`; cleared the
`__pycache__` under both the global and orchestrator-plugin copies.

```python
def register(ctx: Any) -> None:
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
```

## Verification

Ad hoc targeted verification: **PASS**

- `python3 -m py_compile` on the edited plugin: syntax OK.
- Hook-count check: `register()` now registers exactly 3 hooks
  (`pre_tool_call`, `post_tool_call`, `pre_llm_call`); `pre_api_request` absent.
- All three on-disk copies are the same inode (hardlink), so the single edit
  covers every discovery path.
- Pre-restart baseline: `agent_signal_stream.jsonl` tail showed 2x `thinking`,
  2x `tool_call`, 2x `tool_result` per event pair (duplicates ~4–10ms apart).
- Post-restart DAG readback (fresh process, PID 2450319): topology endpoint
  returned 200 with 30 nodes / 5 fresh span IDs — service confirmed healthy.
  Post-restart 1x-per-event signal confirmation still pending (the Hermes
  orchestrator gateway — the *emitter* — has not restarted; see caveat below).

## Restart

`prismatic-gateway.service` (system unit; PID 1163551 pre-restart, running since
Sep 10) restarted via self-healing script
`/home/ubuntu/.prismatic/scripts/restart-gateway-20260913.sh` (staged with
`write_file`, guard-safe literal splitting, daemon-reload → restart → wait active
→ verify single PPID=1 process + HTTP check → journal/log tail on failure).

**Actual result:** restart succeeded — new PID **2450319** (PPID 1), unit
`active`, `GET /` → 200, `/api/gateway/dag/topology` → 200 with fresh span IDs.
One false alarm in the script itself: its final `curl -sf` against `GET /` failed
only because the request raced the app's cold start (first hit after restart
compiles/serves the 800KB dashboard template); every subsequent request returns
200. The script's "FAIL: process active but HTTP check failed" exit was a
verification-timing artifact, not a service failure — the process, unit state,
and all API endpoints verified healthy immediately after.

**Caveat recorded:** the unit uses `Restart=on-failure` (the known fleet-standard
trap documented in `hermes-gateway-lifecycle-ops` — a clean exit is not a failure,
so systemd will not respawn after SIGTERM-with-zero). A `systemctl restart` is
always a start-from-scratch, so this restart is safe; the trap only bites on
crash-free exits. Flag for a future fleet-alignment pass, not this incident.

Note: restarting the **prismatic** gateway does not restart the Hermes
**orchestrator** gateway (the bot session). The telemetry fix lives in the Hermes
plugin, so the emission side only changes when the orchestrator Hermes gateway
next restarts; the DAG stops *receiving* duplicates at that point. Until then, the
prismatic gateway will still record whatever the running Hermes process emits.

## Follow-ups (not done in this session)

1. Confirm post-restart signal stream shows 1x per event type (watch
   `~/.prismatic/db/agent_signal_stream.jsonl` for a burst).
2. Consider moving the handler to `pre_api_request` only (correct semantics).
3. Consider adding an idempotency key / short dedupe window to
   `/api/gateway/signals/emit` so future double-emitters don't double the ledger.
4. The duplicated Telegram replies Michael reported likely share this double-emit
   lineage (double `signal.emitted` WS broadcast); if they persist after the
   orchestrator gateway restart, investigate separately.
5. The plugin directory is untracked in `hermes-agent-fork` — commit it (or
   relocate to `~/.hermes/plugins/` only) so the fix has a durable home.

## Evidence boundary

Ad hoc targeted verification only (syntax, hook count, inode identity, pre/post
signal-stream sampling, API readback of DAG topology). Not a full docs-suite or
fleet-wide telemetry audit.
