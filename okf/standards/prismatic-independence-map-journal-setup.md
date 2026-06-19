---
type: Standard
title: Prismatic Journal-Setup Independence Map
description: Component map applying the coupling taxonomy to journal-setup work, identifying which pieces depend on the engine vs the harness.
resource: /home/ubuntu/work/Hermes-Research/reports/journal-continuity-audit/prismatic-independence-map.md
tags: [standard, prismatic-engine, journal-setup, independence]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-independence-map-journal-setup.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/Hermes-Research/reports/journal-continuity-audit/prismatic-independence-map.md
---

# Journal Setup — Prismatic Engine Independence Map

**Generated:** 2026-06-18
**Linear tracking:** [GRO-1954](https://linear.app/growthwebdev/issue/GRO-1954/map-journal-setup-for-prismatic-engine-independence-agy)
**Generator:** Fred (second-witness fallback after AGY timed out twice on the same task; see §Discovery)

This report maps every component the journal setup and the closely-coupled engine features (file-reference resolution, lock manager, AGY dispatch) currently touch. Each component is classified into one of five buckets, with a single-line acceptance test for "could this run without a harness?"

The structured JSON inventory is in `prismatic-independence-map.json` next to this file.

## The 5-Bucket Taxonomy

| Bucket | What it means | Acceptance test |
|---|---|---|
| **(1) Pure engine-kernel** | The feature runs as a Prismatic Engine CLI/script with no harness imports. Target: `$PRISMATIC_HOME`. | After `pip install prismatic-engine` (or `git clone prismatic-engine && make install`) on a fresh VM with no Hermes, this feature works. |
| **(2) Engine + thin harness shim** | Engine does the work, harness exposes it under a harness name. Shims must be ≤ 3 lines, no re-implementation. | The shim is `exec prismatic-X "$@"` or a 1-line wrapper. The shim is allowed to exist only for ergonomic reasons. |
| **(3) Harness-only plumbing** | Cron, dashboard widgets, profile isolation, OAuth refresh, alert routing. Without a harness, the user wires their own equivalent. | Removing the harness's cron entry stops the job from running on its schedule, but the feature itself is unaffected. |
| **(4) Shared / deferred** | Judgment call. Listed with rationale for why it's not pure bucket 1 or 3. | A one-paragraph rationale explains the decision. |
| **(5) Leaves as is** | Explicitly out of scope for the engine. Justified why. | A one-sentence "why" is required. |

## Per-Component Table

| Component | File | Bucket | Migration? | Rationale |
|---|---|---|---|---|
| `prismatic_artifact_publisher.py` | `$PRISMATIC_HOME/bin/` | **1** | Done | Stdlib-only FastAPI; no harness imports. |
| `prismatic_rewrite_paths.py` | `$PRISMATIC_HOME/bin/` | **1** | Done | Stdlib-only post-processor. |
| `prismatic_reply_rewrite.py` | `$PRISMATIC_HOME/bin/` | **1** | Done | Thin wrapper. |
| `prismatic-publish` CLI | `~/.local/bin/` | **1** | Done | Stdlib-only. |
| `prismatic-reply` CLI | `~/.local/bin/` | **1** | Done | Stdlib-only. |
| `hermes-publish` shim | `~/.local/bin/` | **2** | Done | `exec prismatic-publish "$@"`. |
| `hermes-reply` shim | `~/.local/bin/` | **2** | Done | `exec prismatic-reply "$@"`. |
| `portable-skills/prismatic-artifact-publisher/` | `prismatic-engine` | **1** | Done | Engine skill. |
| Skill mirror under Hermes profile | `~/.hermes/profiles/orchestrator/skills/...` | **2** | Done | Mirror, not canonical. |
| `specs/file-reference-resolution.md` | `prismatic-engine` | **1** | Done | Engine spec. |
| `specs/journal-continuity-audit.md` | `prismatic-engine` | **1** | Done | Engine spec (renamed from Hermes-specific). |
| `specs/sequenced-agent-workflow.schema.json` | `prismatic-engine` | **1** | Done | Engine schema. |
| `monthly_journal_continuity_audit.py` | `orchestrator/scripts/` | **4** | **Migrate** | Currently script-only (`no_agent: true`) but reads `LINEAR_API_KEY`, `PRISMATIC_HOME`, `AGENT_DONE_LABEL`, etc. Engine has the contract; script can move to `$PRISMATIC_HOME/bin/prismatic-journal-monthly.py` and gain a `prismatic-journal` CLI. Acceptance: 0 harness imports. |
| `import_journal_continuity_plan.py` | `orchestrator/scripts/` | **1** | **Migrate** | Pure Linear import script. Move to `$PRISMATIC_HOME/bin/prismatic-linear-import.py`. |
| `agent_dispatcher.py` (general purpose) | `orchestrator/scripts/` | **3** | Leave as harness | Cron-driven dispatch loop. Engine doesn't need to know about cron; harness exposes it. |
| `agent_output_validator.py` | `orchestrator/scripts/` | **3** | Leave as harness | Dispatcher-adjacent; the kernel doesn't ship a dispatcher. |
| `nudge_poller.py` | `orchestrator/scripts/` | **3** | Leave as harness | Polls for AGY nudges; harness plumbing. |
| `event_router_dedup.py` | `orchestrator/scripts/` | **3** | Leave as harness | Dedup DB for the dispatcher's Webhook ingest. |
| `github_pr_monitor.py` | `orchestrator/scripts/` | **3** | Leave as harness | Polls GitHub; cron + OAuth. |
| `fred_agy_proxy.py`, `second_witness_agy_proxy.py` | `orchestrator/scripts/` | **3** | Leave as harness | AGY-specific proxies; harness plumbing. |
| `agy_oauth_refresh.py`, `agy_multi_token_setup.py`, `agy_multi_account_setup.py` | `orchestrator/scripts/` | **3** | Leave as harness | AGY OAuth is a Google-Cloud-Anthic-AGY concern. Engine doesn't ship a Google client. |
| `agy_resource_monitor.py` | `orchestrator/scripts/` | **3** | Leave as harness | Local CPU/RAM monitor. Engine doesn't ship process monitoring. |
| `agy_sandbox_supervisor*.sh/py` | `orchestrator/scripts/` | **3** | Leave as harness | Sandbox/VM-level work. |
| `journal_snapshot.py` | `orchestrator/scripts/` | **4** | **Migrate the contract, leave the cron** | The cron is harness plumbing. The snapshot itself reads `$PRISMATIC_HOME` and writes to journals/. Engine should ship a `prismatic-journal-snapshot` CLI; harness cron invokes it. |
| `becca-journal-snapshot.sh`, `commitments.py`, `commitments_digest.py`, `intervention_handler.py` | `orchestrator/scripts/` | **3** | Leave as harness | Personal-bot plumbing (Becca). |
| `milestone_watch.sh`, `comment_trigger_monitor.py`, `kai_callback_monitor.py` | `orchestrator/scripts/` | **3** | Leave as harness | LLM/agent-specific plumbing. |
| `agy_golden_thread_delta.py`, `consulting_pipeline_delta.py`, `content_engine_delta.py`, `nightly_backlog_delta.py`, `pr_triage_report.py` | `orchestrator/scripts/` | **3** | Leave as harness | Per-venture delta monitors. |
| `prismatic_event_trigger.py`, `prismatic_port_progress.py` | `orchestrator/scripts/` | **3** | Leave as harness | Port-progress digest. |
| `memory_grooming.py`, `agent_activity_telemetry.py`, `agy_sandbox_telemetry.py` | `orchestrator/scripts/` | **3** | Leave as harness | Telemetry. |
| `agent_run_records.py`, `agent_event_client.py`, `action_item_extractor.py` | `agentic-swarm-ops/ops/` | **3** | Leave as harness | Same as above. |
| `agentic-swarm-ops/post_*.py`, `canary_deploy.sh` | `agentic-swarm-ops/` | **3** | Leave as harness | One-shot Linear posters; not the engine's job. |
| `tests/test_*.py` | `agentic-swarm-ops/tests/` | **1** | **Migrate the engine ones, leave harness ones** | Engine-only test (no harness import) → `$PRISMATIC_HOME/tests/`. Harness-only → stay. |
| Linear project "Journal Continuity Audit" | Linear | **4** | **Migrate to engine-owned project, leave the orchestrator's labels in the harness** | Project is engine surface; the agent labels (`agent:fred`, `agent:agy`, etc.) are harness surface. The engine should ship a `prismatic-journal` project template that any harness can clone. |
| Linear labels `agent:*`, `pipeline:*`, `type:*` | Linear | **5** | Leave as is | These are harness-specific. Different harnesses have different agent identities. |
| Cron `Monthly Journal Continuity Audit` (id `eb82b536113c`) | `cron/jobs.json` | **3** | Leave as harness, but engine should ship a `prismatic-journal --install-cron` command | The cron is harness plumbing. Engine should expose a one-line installer so any harness can wire the schedule. |
| Cron `Hermes daily journal snapshot` (id `ce3dd849ede5`) | `cron/jobs.json` | **3** | Leave as harness | Schedule is harness's. |
| Crons `Hermes daily journal recap`, `Becca Journal Recap`, `Becca Morning Briefing`, `Becca Journal Snapshot`, `Weekly Journal Rollup` | `cron/jobs.json` | **3** | Leave as harness | Same. |
| Cron `🔮 Second Witness — AGY Prismatic review terminal` | `cron/jobs.json` | **3** | Leave as harness | The cron is harness; the review protocol is engine surface (`prismatic-second-witness`). |
| Cron `Prismatic Port Progress` | `cron/jobs.json` | **3** | Leave as harness | Same. |
| `LINEAR_API_KEY` (env) | `orchestrator/.env` | **5** | Leave as is | This is the user's Linear API key. The engine doesn't own it; the user's deployment does. The engine just *uses* it. |
| `LINEAR_OAUTH_CLIENT_ID/SECRET` (env) | `orchestrator/.env` | **5** | Leave as is | Same. |
| `TELEGRAM_BOT_TOKEN` (env) | `orchestrator/.env` | **5** | Leave as is | Telegram credentials belong to whatever harness wires Telegram. |
| `PRISMATIC_HOME` (env) | `orchestrator/.env` | **1** | Done | Engine env var. |
| `PRISMATIC_ARTIFACT_HOST/PORT` (env) | `orchestrator/.env` | **1** | Done | Engine env vars. |
| `GITHUB_PAT_KEY` (env) | `orchestrator/.env` | **5** | Leave as is | GitHub token belongs to whatever harness wires GitHub. |
| `GOOGLE_*` (env) | `orchestrator/.env` | **5** | Leave as is | Google credentials. |
| `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY` (env) | `orchestrator/.env` | **5** | Leave as is | LLM provider credentials. |
| `SLACK_*` (env) | `orchestrator/.env` | **5** | Leave as is | Slack credentials. |
| `portable-skills/agy-oauth-authentication/` | `prismatic-engine` | **3** | Leave as harness | AGY-specific OAuth. |
| `portable-skills/golden-thread/` | `prismatic-engine` | **4** | **Decide** | The Golden Thread concept (per-venture project + sequence + cascade) is engine-worthy. The current implementation reads AGY's disk layout. Recommend: extract the **contract** (PRISMATIC_HOME layout, project-registry schema) to engine; keep the AGY-specific executor in the harness. |
| `portable-skills/autonomous-execution-discipline/` | `prismatic-engine` | **4** | **Decide** | Mostly Hermes-specific rules. Recommend: extract the **engine rules** (pre-commit, lane enforcement) to engine; keep the agent-routing rules in the harness. |
| `portable-skills/agent-ned/`, `agent-kai-*`, etc. | `prismatic-engine` | **3** | Leave as harness | These are per-agent harnesses. |
| `portable-skills/prismatic-agent-factory/`, `prismatic-fleet-defaults.yaml` | `prismatic-engine` | **1** | Done | Engine config surface. |
| `portable-skills/prismatic-validation-pipeline/` | `prismatic-engine` | **1** | Done | Engine pipeline spec. |
| `portable-skills/prismatic-engine-operations/` | `prismatic-engine` | **1** | Done | Engine operations skill. |
| `portable-skills/linear/`, `github-pr-workflow/`, `himalaya/`, etc. | `prismatic-engine` | **3** | Leave as harness | These are integrations that a particular harness may or may not need. |
| `$PRISMATIC_HOME/bin/published/` workspace | `prismatic-engine` | **1** | Done | Engine workspace. |
| `portable-skills/credential-security-and-git-hygiene/` | `prismatic-engine` | **1** | Done | Engine safety policy. |
| Cloudflare tunnel + DNS + Access | Cloudflare | **4** | **Document as engine contract, leave the actual deployment to the harness** | The tunnel + DNS + Access config is *deployed* by whatever the user is using. The engine should ship a `prismatic-deploy-files-host` script that automates the same CF API calls. |
| `hermes-workspaces.yaml` on the Synology mount | `agentic-swarm-ops/` | **3** | Leave as harness | Workspace registry is harness-specific. |

## Migration Plan (when the team is ready)

### Phase 1: Engine-owned CLIs (do these first — quick wins)

1. Move `import_journal_continuity_plan.py` → `$PRISMATIC_HOME/bin/prismatic-linear-import.py`. Add a `prismatic-linear-import` CLI in `~/.local/bin/`. Status: **ready to do** (~30 min).
2. Add `prismatic-journal` CLI in `$PRISMATIC_HOME/bin/` that wraps the monthly audit logic. The existing `monthly_journal_continuity_audit.py` becomes a thin harness shim that calls the engine CLI. Status: **ready to do** (~2 hours).
3. Add `prismatic-journal-snapshot` CLI in `$PRISMATIC_HOME/bin/` that wraps `journal_snapshot.py`'s logic. Harness cron invokes the engine CLI. Status: **ready to do** (~1 hour).
4. Add `prismatic-second-witness` CLI that runs the review protocol. The harness cron `🔮 Second Witness — AGY Prismatic review terminal` becomes a thin shim. Status: **ready to do** (~3 hours).

### Phase 2: Engine contract extraction (1-2 weeks)

1. Extract the **Golden Thread contract** (`PRISMATIC_HOME` layout, `project-registry` schema) from `portable-skills/golden-thread/` into a `specs/golden-thread.md` and a `prismatic-golden-thread` CLI.
2. Extract the **Autonomous Execution Discipline engine rules** (pre-commit, lane enforcement) from `portable-skills/autonomous-execution-discipline/` into `specs/autonomous-execution.md` and a `prismatic-engine-gate` CLI.
3. Document the Cloudflare deployment contract in `specs/file-reference-resolution.md` and ship a `prismatic-deploy-files-host` CLI that automates the tunnel + DNS + Access config.

### Phase 3: New harnesses (only if/when needed)

Only after Phase 1 + 2 are done should we consider:
- An OpenClaw adapter (`~/.openclaw/`, with `~/.local/bin/openclaw-publish` shim).
- A bare-bones "no-harness" installer (`prismatic-engine init`) that creates a fresh `~/.prismatic/` workspace and a single cron entry, no other plumbing.

## Discovery: AGY timed out twice on this task

**Important context that informed the taxonomy:**

AGY was dispatched twice on GRO-1954 and timed out both times on the first read of `jobs.json`. The dispatcher incorrectly marked the issue Done because the AGY *process* exited without throwing, but no artifacts were written to disk. This is exactly the "harness-only plumbing" failure mode the engine should not have.

The fix is two-layer:
1. **Engine-level (this report):** the kernel should ship a `prismatic-inventory` CLI that does deterministic file/cron/env discovery. It's pure stdlib, runs without any harness, and the result is a JSON report. AGY's job would then be to *classify* (which requires judgment), not to *enumerate* (which is mechanical).
2. **Harness-level:** the agent_dispatcher.py validator must check the artifact exists on disk before marking the issue Done, not just check that the process exited cleanly.

Both fixes are recommended. The first one is bucket 1 (pure engine-kernel). The second is bucket 3 (harness plumbing).

## How to migrate, mechanically

1. **Bucket 1 migrations** are safe to do now. The file moves, the import path changes, the harness shim is added, the spec is updated. No behavior change.
2. **Bucket 4 deferred** items get a written decision in this report and a follow-up Linear issue. The follow-up is the migration.
3. **Bucket 3** items stay. Don't migrate. The engine's job is to make the contract clear enough that a different harness can wire its own equivalent.
4. **Bucket 2** items already exist (`hermes-publish`, `hermes-reply`). Don't add more shims unless they're needed.
5. **Bucket 5** items stay. Document the "why" so future contributors don't try to migrate them.

## Verdict

**Can the Prismatic Engine be independent and integrated? Yes — and this map is the plan.**

The engine doesn't need to replace Hermes. It needs to ship its own CLIs and specs at `$PRISMATIC_HOME`, and let the harness be a thin shim layer. The journal setup is the canary: when `prismatic-journal` exists as a CLI and `monthly_journal_continuity_audit.py` becomes a 3-line shim that calls it, the journal setup is engine-kernel-runnable. The same pattern applies to every other feature in this table.

The harness (Hermes or otherwise) keeps doing what it's good at: cron, dashboards, profile isolation, OAuth refresh, agent identity. The engine keeps doing what it's good at: contracts, CLIs, schemas, and the durable portable surface.

The next thing I'd do, if you want me to proceed: **Phase 1, step 1 — move `import_journal_continuity_plan.py` to `$PRISMATIC_HOME/bin/prismatic-linear-import.py` and ship it as a `prismatic-linear-import` CLI.** That's a 30-minute, low-risk change that exercises the full bucket-1 migration path on a non-trivial script. Once that pattern is proven, the rest of Phase 1 is mechanical.
