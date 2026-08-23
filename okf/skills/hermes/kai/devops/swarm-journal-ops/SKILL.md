---
name: swarm-journal-ops
description: "Operate, audit, and query the Prismatic swarm journal — the all-agent evidence ledger at ~/work/Hermes-Research/journals/ plus Becca's private journal. Use when asked what happened (per-agent or swarm-wide), whether the journal is working, to audit journal health/retention/freshness, or to plan journal architecture (MCP read surface, PE dashboard Logs→Journals, OKF boundaries)."
tags: [prismatic, journal, evidence, continuity, memory, okf, audit]
related_skills: [hermes-profile-audit, okf-mcp-hub, active-oahu-operations]
---

# Swarm Journal Operations

Class of work: treating the Prismatic journal as a queryable evidence resource — not raw log files. The journal is the **what-happened layer** in the memory model: `memory = who/what now · skills = how · journal = what happened (evidence, never injected) · OKF = what we know/decided (curated)`. See `references/boundary-model-2026-08-20.md` for the full six-layer model.

## The canonical map (verified live 2026-08-20)

| Surface | Path | What it is |
|---|---|---|
| Swarm journal (all agents) | `~/work/Hermes-Research/journals/` | Daily event index `.index/events-YYYY-MM-DD.json` (1K–31K events/day, ~70 days), recaps `2026/MM/DD.md`, `latest.md` symlink, `.quarantine/` (noisy), `inbox/` |
| Becca personal journal (private HD) | `~/work/next-step-becca/journals/` | Separate corpus by design — personal, consent-gated. Never merge into swarm journal. |
| Collector code | `prismatic.journal` module in hermes-agent pipx venv + `prismatic-journal-snapshot` CLI | Installed package, not a local repo |
| Cron owners | **fred profile** (fred/orchestrator are hardlink twins — same inode `cron/jobs.json`, one brain) | 7 jobs: hourly snapshot, daily recap, weekly rollup, monthly continuity audit, Becca snapshot/recap/morning briefing |
| Architecture docs | `profiles/orchestrator/deliveries/prismatic-journal-unification-plan-2026-07-23.md` + `journal-continuity-audit-and-remediation-plan-2026-07-23.md` | Unification plan (PE = canonical platform, Logs→Journals dashboard tab) + remediation P0–P3 |
| OKF docs | `standards/prismatic-independence-map-journal-setup.md`, `reports/journal-continuity-*`, `skills/hermes/fred/operations/scheduled-journal-recaps/` | Independence map, crack-audits, recap runbook |

## Is-it-working check (run in this order, ~30s)

1. **Cron freshness:** `python3 -c "import json; [print(j['name'],j['enabled'],j['last_status'],j['last_run_at']) for j in json.load(open('/home/ubuntu/.hermes/profiles/fred/cron/jobs.json'))['jobs'] if 'journal' in json.dumps(j).lower()]"` — expect `last_status: ok` with recent timestamps. (fred + orchestrator jobs.json are the same file — hardlink; one check covers both.)
2. **Latest recap exists & is fresh:** `ls -la ~/work/Hermes-Research/journals/2026/MM/$(date +%d).md` and read the Memo section — a healthy recap states its evidence window and what's blocked.
3. **Latest event index:** newest `events-*.json` should be today's date (UTC-lag aside).

## Querying the journal (read-only, never write)

**Preferred path — journal MCP (built 2026-08-20, live):** `~/work/journal-mcp-server/server.py`, registered `mcp_servers.journal` (stdio, hermes-agent venv, no auth, read-only). Tools:
- `journal_freshness()` — ALWAYS call first: last index day, last recap day, gaps (14d), corpus size. Stale = say so.
- `journal_search(query)` — AND-keyword across recap markdown + event-index summaries, ranked hits w/ snippets.
- `journal_read(date)` — `YYYY-MM-DD` daily or `YYYY-Www` weekly, full markdown (60KB cap).
- `journal_latest()` / `journal_list(limit)` — newest daily / available dates (62 dailies, 10 weeklies).
- Pattern = okf-mcp (stdio subprocess, not systemd HTTP). OKF integration doc pending under integrations lane (Jules owns it); draft at `~/work/growthwebdev-knowledge/okf/integrations/journal-mcp.md`. Six-layer split standard: `okf/standards/hermes-memory-skills-boundary-discipline.md` (PR #37).

Fallback (no MCP): read files directly.

- **What happened on date X:** read `2026/MM/DD.md` (curated recap) first — it's the narrative with citations.
- **Raw events for date X:** `.index/events-YYYY-MM-DD.json` — rows are `{type, source, job_name, job_id, status, summary, idempotency_key, _timestamp}`. Filter by `/profiles/<agent>/` in `source` for per-agent views.
- **Pitfall — legacy index:** rows from before the incremental-cursor era (~before 07-09) lack stable idempotency keys → not trustworthy as deduplicated evidence. Cite them as history, not proof.
- **Pitfall — quarantine:** `.quarantine/` is a noisy dump of malformed/non-timestamped lines (5 MB+). It proves plumbing exists, not operational signal. Don't mine it for "evidence."
- **Pitfall — daily file naming:** recap files are `<year>/<month>/<day>.md` where the filename is the BARE day number (`2026/08/20.md`), NOT `2026-08-20.md`. Any code that matches filenames against a full date string silently finds zero files (hit live building the journal MCP — `journal_list` returned 0 dailies until the lister built the date from path components). Same for weekly: `2026-W33.md` style lives alongside.
- **Pitfall — size:** corpus is ~378 MB and ~5 MB/day. `find` over it with broad patterns hangs (observed 180s timeout). Always path-scope to the exact dir; read one day file at a time.

## Landing code changes in prismatic-engine (lane guard)

**Governing rule:** `prismatic-engine` has a pre-push hook (`scripts/pre-push-hook.py`) that enforces **per-agent lane ownership** from `PRISMATIC_ENGINE.yaml`. It maps **branch prefix → agent → owned dirs**:
- `feature/` → **fred** → `['*']` (owns everything)
- `content/` → **kai** → `['content/', 'active-oahu/']`
- `design/` → **agy** → `['assets/', 'designs/', 'research/']`
- `fix/` → **jules** → `[]`
- `ned/` → **ned** → `['scripts/', 'prismatic/', 'plugins/']`

So **PE core code (`prismatic/journal.py`, `scripts/`, `tests/`) is Ned's lane (Fred owns `*`); Kai's `content/` branch cannot push it.** When a journal task requires a code change in PE core, **do not rename the branch to `feature/` (or `ned/`) to slip past the guard** — that defeats its purpose. Instead: complete + verify the work on your own branch (commit stays local, green), then either (a) hand the exact files + test proof + commit to **Ned** (owns `prismatic/`/`scripts/`) or **Fred** (`*`) to land on a `ned/`/`feature/` branch, or (b) get Michael's explicit override. The 2026-08-21 G2+G6 bundle (era flag + quarantine triage) hit this exactly: built + 46/46 tests green on `content/journal-g2-g6-20260821`, push blocked, handed off pending Michael's routing call.

**Pitfall — `prismatic` import resolves to a stale checkout:** running any `prismatic-engine` script that does `from prismatic.journal import ...` from a plain shell can resolve `prismatic` to the **feature-branch checkout `~/work/prismatic-pwp-ubersuggest-auth/`** (the live symptom of the G3 source-of-truth problem — ImportError on new symbols). Fix: pin the repo, `PYTHONPATH=/home/ubuntu/work/prismatic-engine python3 scripts/<x>.py`. Verify with `python3 -c "import prismatic.journal as j; print(j.__file__)"`.

## Architecture decisions (already made — don't relitigate)

- **Prismatic Engine is the canonical journal platform** (2026-07-23 unification plan): SQLite events + read APIs + dashboard **Logs → Journals** tab. Status at audit time: P0 remediation (PR #382 build gate, legacy-index isolation, quarantine cleanup) and PE migration (GRO-4189 read API, GRO-4214..4260 cron migration) paused/backlog.
- **Profiles' `home/` dirs are LIVE state, not orphans.** `profiles/kai/home/` and `profiles/george/home/` hold running agent state (`.prismatic/` bus + sqlite DBs, `.antigravity/`, `.claude/`, `.gemini/`). Never `rmdir`/`rm -rf` them — the 2026-08-21 G7 cleanup only removed the `home/work/...journals/` subtrees and the now-empty `work` shell dirs. Verify what a dir actually contains (`find -maxdepth 4`) before deleting anything under a profile dir.
- **Journals do NOT go in OKF.** Append-only evidence at this volume would be git-churn hell. OKF holds the *conclusions* extracted from journals (standards/reports/decisions) with pointers back to evidence. EXCEPTION: a journal dir containing curated, audit-grade investigations (e.g. ned's 2026-06-29 PE verification-gap docs) should be *promoted* to okf/audits/ with frontmatter, then the source dir deleted (gap G7 pattern, PR #41). The query surface is the **journal MCP** (stdio, built 2026-08-20 — see "Querying the journal" above), not a second copy of the corpus.
- **Becca stays separate and private** — HD consent rules; no cross-user journal access by default.

- **Fleet-wide registration (done 2026-08-21):** all 6 active profiles (kai, fred, george, ned, orchestrator, autobot) carry `mcp_servers.journal` — the same 3-line block, inserted after each profile's existing `okf:` block under `mcp_servers:`. Verify per profile with `yaml.safe_load(config)["mcp_servers"]["journal"]`. MCPs load per-session, so a registered profile gets the tools from its NEXT session (no gateway restart needed).
- **Journal is FOREVER (Michael's decision, 2026-08-21):** no retention pruning, ever — "I can always get more storage." The 90d code prune (`journal.py` `_days_ago(90)`) and all 400-day governance references are invalidated; **removal LANDED in PE #434 (`fef004cb`, GRO-4825/4826, merged 2026-08-21)** — collector now on PE `main`, prune gone (`# no retention — journal is forever` at `journal.py` L863). Any new retention/400-day language in docs or dashboards is WRONG.
- **G8 critical path (Michael's dashboard ask, GRO-4829):** unblock PR #382 (build-gate) → GRO-4189 read API → GRO-4190 fixtures → PE dashboard Logs→Journals tab (Timeline / Cron & Collectors / Raw Evidence / Retention & Privacy). Retention view says **forever**.

Status table (surface → working/stale/broken + evidence), 🚩 gaps, then numbered next-step options with the zero-risk default first. Include the exact `last_run` timestamps — Michael wants proof of freshness, not claims.

## Session detail
- **Linear (issue query + transition) recipes:** the working Linear GraphQL shapes are in `references/linear-api-graphql-recipes.md` (auth has NO `Bearer`; `issue(id:)` accepts the human id; states via `team { states { nodes } }`; transition = `issueUpdate(id:, input:{stateId:})`, comment = `commentCreate`; target the final "Done" state, not "Done - Doc Pending"). Use it before re-deriving — 2026-08-21 took 5+ failed attempts to close GRO-4828 without it.
- **Verifying claimed/merged PRs (post-hallucination audit):** when Michael says "I merged #39/#41/#42" + doubts the agent, re-verify every artifact from scratch with the 7-step ladder + full-repo phantom-PR census. 2026-08-21 run: #39 + #41 REAL (OKF hub, re-verified against live `event_router.db`), #42 **PHANTOM** (no such PR; real artifact was PE #434 G1+G3). Also captured: G5 was already resolved (audit stale), G2 seam = measured first file with `idempotency_key` (`events-2026-07-24.json`, not the assumed 07-09), G6 quarantine = 27 files/5.2MB. Recipe + findings table: `references/merged-pr-verification-ladder-2026-08-21.md`.
- 2026-08-21 (execution): Michael's gap resolutions executed. G4 DONE: journal MCP registered on all 6 active profiles (kai/fred/george/ned/orchestrator/autobot), verified OK each. G7 DONE pending merge: PR #41 promotes 2 PE verification-gap audits (2026-06-29 evidence+rootcause) from ned journal dir to okf/audits/; orphan dirs deleted (ned/journals, kai/home/.../journals, george stale .state). Linear tasks created in "Journal Continuity Audit" project: GRO-4825 G1 forever-retention (Todo, Fred), GRO-4826 G3 pin-collector (Backlog), GRO-4827 G4 (Done), GRO-4828 G7 (In Review), GRO-4829 G8 dashboard visibility (Todo, Fred, critical path), GRO-4830 G2+G5+G6 bundle (Backlog). G1 decision = journal is FOREVER, no pruning; code prune to remove in prismatic/journal.py ~L586-590.
- 2026-08-21 (E2E audit): full journal-system + MCP audit, every claim verified live. Report: `okf/audits/journal-system-and-mcp-audit-2026-08-21.md` (PR #39). 9 gaps G1–G9; headline = G1 retention 90d(code)/400d(governance) conflict [HIGH], G3 collector source-of-truth lives in feature-branch checkout `prismatic-pwp-ubersuggest-auth` [MED], G4 journal MCP registered on kai only (other 5 active profiles can't query) [MED]. Verified: journal MCP JSON-RPC handshake + tools/list + tools/call all pass; okf-mcp active+401-without-token; hd ping ready; all 7 cron jobs ok. Note: journal.py `_days_ago(90)` prune at L588; master `.index/events.json` is the 90d-pruned index.
- 2026-08-20 (build): journal MCP shipped + registered in kai config (live from next session); six-layer split standard extended via PR #37 (content/journal-mcp-layer). Over-cap memory files (fred/USER.md 163% etc.) still to prune — writes rejected on those profiles.
- 2026-08-20 (audit): full audit (first for Kai). All 7 cron jobs green, today's recap high-quality (caught Autobot Telegram HTML-escape bug root cause). Findings: 9 memory files over cap causing silent memory-write rejection; 7 profiles orphaned in legacy memory.jsonl format; orphan journal dirs (`ned/journals/` 2 evidence files, empty becca inbox copies). See `references/boundary-model-2026-08-20.md`.
