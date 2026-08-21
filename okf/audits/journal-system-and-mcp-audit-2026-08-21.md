---
type: Audit
title: Journal System & MCP — End-to-End Audit (2026-08-21)
description: Full end-to-end audit of the Prismatic journal system (collector → cron → corpus → retention) and the MCP surface (journal / okf / hd), with all gaps, severity, and exact fill steps. Verified live, not from memory.
tags: [journal, mcp, prismatic, audit, retention, infra]
status: current
owner: kai
last_verified: 2026-08-21
verified_by: kai
related:
  - standards/hermes-memory-skills-boundary-discipline.md
  - integrations/journal-mcp.md
  - standards/prismatic-independence-map-journal-setup.md
---

# Journal System & MCP — End-to-End Audit

**Auditor:** Kai (Hermes profile `kai`) · **Date:** 2026-08-21 · **Method:** live verification — every claim below was checked against the running system on the audit day, not from notes.

**Scope:** (A) the Prismatic journal system end-to-end — collector code, cron jobs, corpus layout, freshness, retention, searchability; (B) the MCP surface — `journal`, `okf`, `hd` servers, registration across profiles, protocol-level behavior.

## 1. System map (verified)

| Layer | Where | State |
|---|---|---|
| Collector code | `prismatic.journal` module (resolves to `/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/prismatic/journal.py` from the hermes-agent pipx venv) + `~/.local/bin/prismatic-journal-snapshot` CLI | ⚠️ source lives in a feature-branch checkout, not a deployed artifact — see G3 |
| Cron owner | **fred profile** (fred/orchestrator are hardlink twins — one `cron/jobs.json`, one brain) | ✅ 7 journal jobs, all `enabled`, `last_status: ok` |
| Corpus | `~/work/Hermes-Research/journals/` | ✅ live, 395 MB, 76 index days (2026-06-03 → 2026-08-21) |
| Becca personal journal | `~/work/next-step-becca/journals/` | ✅ separate by design (HD consent) — not merged, correct |
| Read surface | journal MCP (`mcp_servers.journal`, stdio, 5 tools) | ✅ live in kai config; protocol handshake + `tools/list` + `tools/call journal_freshness` verified this audit |
| OKF read surface | `mcp_okf_*` (okf-mcp.service :8910) | ✅ `active`, bearer auth enforced (401 without token), search returns hits |
| HD read surface | `mcp_hd_ping` | ✅ v1.0.0 ready |

## 2. What works (proof, with timestamps)

- **Freshness:** `journal_freshness()` at 2026-08-21T01:57Z → `last_index_day 2026-08-21`, `index_gaps_last_14d: []`, 76 index days, 62 daily recaps. Today's index already has 75 events (latest `01:09Z`); today's daily recap not yet run (expected — daily cadence).
- **Cron:** all 7 fred/journal jobs green — hourly snapshot, daily recap, weekly rollup, monthly continuity audit, Becca snapshot/recap/morning-briefing.
- **MCP protocol (journal):** full JSON-RPC handshake succeeded — `initialize` → `tools/list` advertised exactly `['journal_latest','journal_read','journal_list','journal_search','journal_freshness']` → `tools/call journal_freshness` returned valid payload. No stderr errors.
- **Inbox pipeline:** `inbox/2026-08-21.md` present (01:09Z, Golden Thread snapshot) — raw-evidence sidecar is draining, not backing up.
- **OKF MCP:** service `active`; unauthenticated probe returns `401 in 2ms` (auth working, not wide open); search over 17K+ docs returns ranked hits with snippets.
- **Retention mechanics:** collector prunes the master `.index/events.json` at 90 days (`_days_ago(90)`, journal.py L588) — pruning is real and running (master index oldest key 2026-06-03 = exactly 79 days old).

## 3. Gaps and how to fill them

### G1 — Retention policy conflict: 90 days in code vs 400 days in governance — **HIGH**
- **Gap:** Governance baseline (2026-07-23 continuity audit) says **400-day** normalized-event retention; collector code prunes at **90 days** (`journal.py` L588). The two cannot coexist ambiguously — one of them is silently wrong.
- **Fill:** Pick one, then make both agree.
  1. Michael decides: 90d (disk-light, ~15 MB/month) or 400d (full year, ~70 MB/month — trivial on this box).
  2. If 400d: change the `_days_ago(90)` constant to a config value (`JournalConfig.retention_days`, default 400) in the prismatic repo, redeploy to the venv, and update `standards/prismatic-independence-map-journal-setup.md` so governance and code cite the same number.
  3. Add a one-line retention statement to `integrations/journal-mcp.md` so the read surface documents its own horizon.

### G2 — Legacy index rows (pre-incremental era) have no stable dedupe keys — **MEDIUM**
- **Gap:** rows before the incremental-cursor era (~before 2026-07-09) lack idempotency keys → not trustworthy as deduplicated evidence. Anyone querying the full 76-day window gets a mixed-reliability corpus with no marker on the seam.
- **Fill:**
  1. Add a `"legacy": true` flag (or `era` field) to rows on ingest; backfill it over the old files (one-shot script, ~70 files, safe).
  2. `journal_search` already returns `summary`-level hits — extend its output to include the era flag so agents can say "history, not proof."
  3. Long-term, the PE SQLite migration (GRO-4189) absorbs this; this is the cheap interim.

### G3 — Collector source-of-truth ambiguity — **MEDIUM**
- **Gap:** the running collector resolves to `/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/prismatic/journal.py` — a **feature-branch checkout**, not a deployed artifact or a clean `main`. A stray commit or branch cleanup in that repo can silently change journal behavior; nobody can `git log` the running code against a known-good ref.
- **Fill:**
  1. Land `prismatic/journal.py` on the Prismatic Engine `main` branch.
  2. Install the venv from the main-branch checkout (or a tagged release) and record the deployed SHA in `integrations/journal-mcp.md` + the OKF infra doc (same-change rule).
  3. `prismatic-journal-snapshot --version`-style output: print the module path + git HEAD so any run is self-identifying.

### G4 — Journal MCP not registered outside kai — **MEDIUM**
- **Gap:** `mcp_servers.journal` exists **only in kai's config** (verified across all 6 active profiles: kai=hd+okf+journal; fred=+gdrive; george/ned/autobot=hd+okf; orchestrator=+gdrive). Every other agent must hand-read 395 MB of files to answer "what happened."
- **Fill:** add the same 3-line `mcp_servers.journal` block to fred, george, ned, autobot, orchestrator (and the 7 legacy profiles if they're migrated). It's read-only and zero-auth (local stdio) — no new attack surface. One `hermes config set` ×3 per profile, then a smoke call.

### G5 — `last_run_at` is `null` on journal cron jobs — **LOW**
- **Gap:** `journal_*` jobs show `last_status: ok` but `last_run_at: None` in `jobs.json` — freshness can't be proven from the job record alone; this audit had to infer it from file mtimes. (Other jobs, e.g. Tier-7 sweep, do populate `last_run_at`, so it's journal-specific.)
- **Fill:** check whether journal jobs run via a different scheduler path (script-only `no_agent` vs LLM) that skips the timestamp write; patch the scheduler or the job definitions so `last_run_at` is always set. Cheap: one code path.

### G6 — Quarantine is a 5.3 MB noise sink with no triage — **LOW**
- **Gap:** `.quarantine/` = 27 files, 5.3 MB of malformed/non-timestamped lines. It proves plumbing exists but is never triaged — it's a dump, not a signal.
- **Fill:** (a) the monthly continuity audit job should emit a quarantine summary (top offending sources, counts) into the recap so noise is *visible*; (b) rotate quarantine to 90-day retention like the index.

### G7 — Orphan journal directories — **LOW (cleanup)**
- **Gap:** `profiles/ned/journals/` (2 one-off evidence files from 2026-06-29), `profiles/kai/home/work/next-step-becca/journals/inbox/` (1 file), `profiles/george/home/work/Hermes-Research/journals/.state/` (stale 2026-08-09 snapshot state).
- **Fill:** the 2 ned evidence files belong in OKF (they're curated findings, not raw journal — promote to a report or delete if superseded); the other two dirs are safe to delete (no live state). ~10-minute task, needs a 30-second "is anything reading these?" check per dir first.

### G8 — PE dashboard Logs → Journals tab + read APIs still paused — **CONTEXT (not a gap I can fill alone)**
- **Gap:** the 2026-07-23 unification plan's end state (PE SQLite events + read APIs + dashboard tab, GRO-4189 / GRO-4190 / GRO-4214–4260) is paused. The journal MCP is the interim read surface — it works, but it's file-based, so it inherits G1/G2/G3.
- **Fill:** unblock via Fred (PR #382 build-gate fix was the blocker). Nothing for me to do until then; the MCP keeps everyone productive in the meantime.

### G9 — 5 profiles still carry legacy `memory.jsonl` alongside the new format — **LOW (out of journal scope, flagged for completeness)**
- **Gap:** `active-oahu, ai-consulting, autobot, google-ai-toolkit, hdengine` still carry `memories/memory.jsonl` (4 of them also `user.jsonl`) **alongside** the new `USER.md` — dual-format state. (`jules`, `next-step` are fully migrated; all 7 use `USER.md`.) The legacy lines are invisible to the `memories/` audit tooling (though they *are* captured in the journal via session events).
- **Fill:** format-only migration of the 5 stragglers — fold any still-relevant legacy lines into `MEMORY.md`/`USER.md`, then delete the `.jsonl`. Do it when each profile is next touched. Michael deferred this on 2026-08-21; left as-is.

## 4. MCP surface summary

| Server | Pattern | Auth | Registered on | Audit result |
|---|---|---|---|---|
| `journal` | stdio (hermes-agent venv) | none (local-only) | kai only | ✅ handshake + tools/list + tools/call all pass |
| `okf` | HTTP :8910 (systemd, bearer) | bearer token | all 6 active profiles | ✅ active, 401 without token, search works |
| `hd` | stdio | none | all 6 active profiles | ✅ ping ready v1.0.0 |

**No MCP gaps beyond G4** (journal not on other profiles). OKF and HD coverage is already swarm-wide.

## 5. Recommended order (cheapest highest-signal first)

1. **G4** (register journal MCP on the other 5 active profiles) — ~15 min, unlocks the whole point for the whole swarm. *Kai can do this in one session.*
2. **G1** (retention decision) — needs Michael's 90d-vs-400d pick, then a one-line code change + doc sync. *Fred for the code, Kai for the OKF sync.*
3. **G3** (pin collector source to main) — *Fred.*
4. **G2 + G5 + G6** — small code additions to the same collector file; bundle into one Fred PR.
5. **G7** cleanup — *Kai, 10 min.*
6. **G8** — unblock via Fred's PR #382; the interim MCP covers the gap until then.

---
*All timestamps UTC. Corpus figures from `journal_freshness()` at 2026-08-21T01:57Z. Re-run this audit after G1/G3 land — the retention row and source-of-truth row are the two that will change.*
