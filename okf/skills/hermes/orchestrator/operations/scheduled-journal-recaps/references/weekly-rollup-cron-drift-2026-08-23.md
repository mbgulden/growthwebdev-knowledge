# Weekly Rollup Drift — 2026-08-23 (13th overall, 3rd weekly-side)

## What happened

Cron: "Generate a weekly rollup from the last 7 days of Hermes daily journals" with the SILENT-WHEN-CLEAN contract, prompt path `$PRISMATIC_HOME/work/Hermes-Research/journals`.

Sequence of record:

1. First tool call: `find` on the prompt path (no `skill_view` — 13th skip-skill event).
2. `$PRISMATIC_HOME` expanded to `/home/ubuntu/work`, so the prompt path became `/home/ubuntu/work/work/Hermes-Research/journals` — a stale duplicate root with exactly one file (2026-06-26). The live corpus is at `/home/ubuntu/work/Hermes-Research/journals` (one level up).
3. Cross-checked via `mcp_journal_journal_freshness`: `corpus_path: /home/ubuntu/work/Hermes-Research/journals`, `last_weekly: 2026-W33`, `daily_recaps: 65`. This one call settles the root ambiguity.
4. Read the 7 most recent dailies (08-15, 08-16, 08-19, 08-20, 08-21, 08-22, 08-23 — 08-17/18 absent from the index) via `execute_code` section extraction (kept context lean by dropping cron tables and truncating sections).
5. Wrote `weekly/2026-W34.md` (399 words after trims) and pulled the required action line from `~/.hermes/profiles/orchestrator/state/current.json` (the switchover one-liner).
6. **The clobber:** `cp weekly/2026-W34.md latest-weekly.md` — `latest-weekly.md` was a symlink → `weekly/2026-W33.md`. `cp` wrote THROUGH the symlink: W33's file content became the W34 rollup. The symlink itself stayed intact (unchanged mtime, `lrwxrwxrwx`), so `islink` checks pass. Caught by re-running `ls -la` (mtime jump) + `head` showing W34 content at the W33 path.
7. **Recovery:** `session_search(query='\"W33\" \"Week in Review\"')` → the Aug 16 cron session (`cron_7f5fff8702bc_20260816_100027`) carried the complete verbatim W33 rollup in its final assistant message. Rewrote `weekly/2026-W33.md` from that content (added the `# Weekly Rollup — 2026-W33` title header for style parity with W34), then `rm latest-weekly.md && ln -s weekly/2026-W34.md latest-weekly.md`.
8. Word count: first draft 413 words → two patch trims → 399. `wc -w` counts markdown headers, bullets, and the ops-note line; budget ~380 for safety with an action line + footer note.

## Lessons encoded in SKILL.md

- **Prompt-path double prefix:** when a cron prompt's `$PRISMATIC_HOME/work/...` resolves to a root with suspiciously few recent files, verify against the journal MCP's `corpus_path` before trusting either root. The stale `work/work` root contains one old journal and will mislead any `find ... | tail -7` run.
- **cp-through-symlink write-through (variant 2):** `cp new latest-X.md` where `latest-X.md` is a symlink → old artifact = old artifact destroyed, symlink intact. Distinct from the 08-16 variant (symlink replaced by regular file). Only `ln -sfn` is safe. Post-update verification must check target CONTENT against the new label, not just `islink`.
- **Session DB is the first-choice restore source** for clobbered cron-delivered artifacts: the artifact text was the cron session's final response, so `session_search` returns it verbatim. Dailies-reconstruction is the fallback (lossy, slower).
- **`--snapshot-prev` ordering:** capture the prior-week baseline hash BEFORE any write into the journals tree. A post-write baseline hashes the already-clobbered file and makes the "previous week preserved" check trivially pass.
- **Pre-write word count is mandatory** (workflow step 4): 413→399 took two trim cycles that one pre-write count would have avoided.

## Files

- Restored: `weekly/2026-W33.md` (from session `cron_7f5fff8702bc_20260816_100027`, message id 509910)
- Written: `weekly/2026-W34.md` (399 words, 2,984 bytes, mode 600 to match siblings)
- Symlink: `latest-weekly.md -> weekly/2026-W34.md` (relative target)
