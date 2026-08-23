# Verifying merged agent PRs (post-hallucination audit) — 2026-08-21

**Trigger:** Michael says "I merged PRs #39, #41, #42" + expresses doubt about the
agent's results ("he started hallucinating"). Class of work: re-verify every
claimed artifact from scratch, assume nothing, and name the exact gap.

## The verification ladder (run in order, every claim needs tool output)

1. **PR exists + merged:** `gh pr view N --repo R --json number,title,state,mergedAt,headRefName,author`.
   - **Phantom-PR signal:** `Could not resolve to a PullRequest` in the expected
     repo. PR numbers are **repo-scoped** — a number that resolves nowhere in the
     expected repo was hallucinated, not "in another repo" by default. Confirm
     with a full-repo census (below) before concluding.
2. **Files landed on main:** `gh pr diff N --name-only` → for each file,
   `git cat-file -e origin/main:<path>` (after `git fetch`). Present/absent per
   file is the receipt — not the PR state, not the branch (branch may still
   exist after merge).
3. **Content is real, not a stub:** `git show origin/main:<path> | wc -l` and
   skim. 133-line audit doc ≠ hallucination; 3-line "TODO" doc = red flag.
4. **Re-verify substance against LIVE data:** re-run the artifact's headline
   numbers yourself. This session: re-queried `event_router.db`
   (635 runs all-`dispatched`, 2 review rows, 0 pipeline rows) — exact match
   with the promoted evidence doc. For file-cleanup claims: `ls` the claimed
   deleted dirs. For code claims: `git show origin/main:<code>` + grep the
   behavior (found `# no retention — journal is forever` at L863).
5. **DoD items:** read the Linear task's "Definition of done" and check each.
   Example: "confirm OKF search finds both docs" → `mcp_okf_search("...")`
   must return hits. DoD met but task still In Review → close it (state
   transition per `okf-mcp-hub` → `references/linear-api-patterns.md`).
6. **Linear state read-back:** use the plural `issues(filter:{id:{eq:"GRO-XXXX"}})`
   query — the singular `issue(id:)` with an identifier returns HTTP 500.
7. **Stray state sweep on shared checkouts:** `git status -sb` in each repo you
   touched. This session found an **unpushed commit on local `main`**
   (another agent's auto-regen, ahead 1) — nothing lost, but it must be
   reported and pushed, and it means "local main == origin/main" assumptions
   are false until checked.

## Full-repo census for a phantom PR number

```bash
for repo in <every mbgulden repo with a local checkout>; do
  gh pr view N --repo $repo --json number,state,mergedAt,title 2>/dev/null
done
```
Omitted repos = number doesn't exist there. A number that exists elsewhere with
an old mergedAt (e.g. months ago) is a **name collision**, not the claimed
merge. The real third artifact was in a *different repo* entirely (PE #434,
G1+G3) — the agent had shipped real work but mis-numbered it.

## Findings table (2026-08-21 run)

| Claimed | Reality | Evidence |
|---|---|---|
| PR #39 merged (OKF hub) | ✅ REAL | `d2c65cb` on main; DB numbers re-verified live |
| PR #41 merged (OKF hub) | ✅ REAL | `54af662` on main; orphan dirs deleted; OKF search hits both docs |
| PR #42 merged | ❌ PHANTOM | no #42 in hub; 18-repo census: only old/colliding #42s; real artifact = PE #434 |
| PE #434 (G1+G3) | ✅ REAL | `fef004cb` on PE main; prune removed, collector on main |

## G2/G5/G6 triage (the work the phantom "PR 42" was supposed to be)

Measured 2026-08-21 against live data:

- **G5 — RESOLVED (audit was stale):** every `journal_*` cron job in every
  profile (orchestrator + fred twin) now has `last_run_at` populated with
  current timestamps. No code change needed — record as verified-stale in the
  PR/Linear, don't "fix" it.
- **G2 — open, numbers measured:** legacy index rows lack `idempotency_key`.
  Seam is **measured, not assumed**: pre-07-09 files = 0 keys (33 files,
  390,582 rows); first file with keys = `events-2026-07-24.json`; 07-09→07-23
  files are mixed/partial. Recipe: date-ordered scan of `.index/events-*.json`
  for the first file containing `idempotency_key`. Backfill `"legacy": true`
  over pre-seam files; expose the flag in `journal_search` output so agents
  can say "history, not proof."
- **G6 — open:** `.quarantine/` = 27 files / 5.2 MB, no triage. Fill =
  summary (top offending sources + counts) in the monthly recap + 90-day
  rotation. Note the journal *index* is forever — only quarantine (noise)
  rotates.
- Code home: `prismatic/journal.py` on PE `main` (post-#434). Key functions:
  `update_event_index` (L839), `signal_idempotency_key` (L880),
  `write_quarantine` (L993), `build_evidence_recap` (L1237). `JournalConfig`
  is `@dataclass(frozen=True)` — adding fields breaks the 3 direct
  constructions in `tests/test_journal*.py` (add defaults).
- MCP server `~/work/journal-mcp-server/server.py` is **not git-tracked**
  (no repo) — era-flag exposure there is a local edit, coordinate separately.
- 5 journal test files exist (`tests/test_journal*.py`) — run them before
  claiming the bundle PR done.

## Reporting shape for Michael

Per claimed PR: ✅ REAL / ❌ PHANTOM + one-line evidence. Then the "what
actually shipped" list, then the exact gap (which real work has no PR yet) +
proposed next step. Never say "all verified" while a phantom number stands in
the user's own sentence — name it.
