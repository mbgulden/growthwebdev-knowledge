# Memory Model — Six Layers (ratified 2026-08-20)

One-sentence rule: **memory = who/what now · skills = how to do it · journal = what happened (evidence) · OKF = what we know and decided (curated).**

| Layer | What it is | Lives in | Loaded when | Cap |
|---|---|---|---|---|
| Memory (hot) | Stable preferences + facts + pointers only | `profiles/<agent>/memories/MEMORY.md` + `USER.md` | Always (injected every turn) | ~2200 / ~1375 chars; **over-cap = writes silently rejected** |
| Handoff | Durable-but-transient state | `state/current.json` | Session start | — |
| Journal | Timestamped evidence trail with citations; append-only; never injected | `~/work/Hermes-Research/journals/` (+ Becca private) | On query | ~5 MB/day |
| Skills | Procedures re-derived each session (umbrella + 1-page micro, symlinked from orchestrator) | `profiles/<agent>/skills/` | On demand | — |
| OKF | Curated, versioned, shared knowledge: standards, decisions, reports, env facts, handoffs | `growthwebdev-knowledge` git repo | On query via okf-mcp | curated |
| Session DB | Verbatim transcripts, FTS5 | per-profile `state.db` | `session_search` | — |

## Journal ↔ OKF boundary (the new piece)

- Journal is the **raw ledger**; OKF holds the **conclusions extracted from it** plus pointers back to evidence. They are complementary, not competing.
- Journals never go *into* OKF (volume: 378 MB, ~5 MB/day → git-churn hell).
- OKF docs that cite journal findings should carry the evidence ref (date file + section), so a reader can verify.
- Existing OKF standard for memory↔skills only: `okf/standards/hermes-memory-skills-boundary-discipline.md` (2026-07-29, verified fred). The journal layer was missing from it — extension PR pending as of 2026-08-20.

## Live failure classes found 2026-08-20 (check these during any fleet audit)

1. **Memory over cap → silent write rejection.** Symptom: agent forgets / new memories don't stick; no error surfaced to user. 9 files were over cap: fred/USER.md 163%, george/MEMORY.md 100%, fred/MEMORY.md 99%, george/USER.md 99%, ned/MEMORY.md 98%. The daily swarm-journal digest reports this in its "Errors & Issues" section — read it.
2. **Orphaned legacy memory format.** 7 profiles (active-oahu, ai-consulting, autobot, google-ai-toolkit, hdengine, jules, next-step) still have `memory.jsonl`/`user.jsonl` — pre-boundary-discipline format, not injected by current memory system. Report as orphaned; don't count as live memory.
3. **Orphan journal dirs.** `ned/journals/` (2 one-off evidence files, June), `kai/home/work/next-step-becca/journals/` (empty inbox copy), george's 08-09 Hermes-Research copy under his profile. Cleanup candidate — approval required before deletion.

## Read-side architecture recommendation (pending Michael's go)

Small local MCP/HTTP service (okf-mcp pattern: systemd unit + bearer token + in-memory index over the recaps + event index) exposing: `journal_latest`, `journal_read(date)`, `journal_search(query, range)`, `journal_freshness()`, `journal_agent(agent, date)`. Makes the journal queryable for every agent without touching the live collector. Then the paused PE work (GRO-4189 read API, Logs→Journals dashboard tab, retention 90→400 fix, quarantine cleanup, legacy-index isolation) proceeds against a system with demand.
