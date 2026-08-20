# Becca Journal Recap Drift — 2026-08-20 (tenth event)

## Session shape
- Cron prompt: Becca Journal Recap, local-only delivery, UTC date.
- First tool call: `date -u` — clock-first date rule honored (conversation header said 2026-08-19 MT; clock said 2026-08-20 UTC). But `skill_view('scheduled-journal-recaps')` was never called. Tenth skip-skill event (08-07, 08-08, 08-09 daily; 08-09 weekly; 08-11, 08-12, 08-15, 08-16 daily; 08-16 weekly; 08-19 daily; 08-20 daily).
- Read inbox (seven snapshots, 00:00:05Z → 06:00:16Z; one detected change), template, and the 08-19 + 08-16 recaps for style. Wrote `2026/08/20.md` (2299 bytes), repointed `latest.md` with `ln -sfn 2026/08/20.md` (correct operation).

## New operational technique (keep)
- The sole detected change was the bot's own `data/next_step.db`, written at 00:00:24Z — a file-level event, not a content-level one.
- Triage recipe: `sqlite3` CLI is not installed on this host; use Python's `sqlite3` module. Inspect the tables that carry user activity:
  - `tasks` — 0 rows
  - `raw_dumps` — 0 rows
  - `conversation_history` — newest row 2026-07-01 (stale)
  → classified as routine top-of-hour housekeeping (state-row write by the bot's own scheduler), **not** a signal.
- Memo framing: day reported quiet at the content level (day seven of the silence pattern); the file-level touch was explicitly de-escalated ("don't upgrade housekeeping into a signal"). A quiet-day memo with exactly one file-level DB touch should make the file-level/content-level distinction explicit rather than ignoring the change or inflating it.

## Path-resolution note
- On this host `~/work/next-step-becca/journals` and `/home/ubuntu/work/next-step-becca/journals` are the **same directory** (profile home is linked: `/home/ubuntu/work` → profile-home `work`). Existence checks via `expanduser("~")` work here. Citations in the recap should still use the canonical `/home/ubuntu/work/...` string — the audit-friendly form.

## Failure modes (drift)
1. **Skip-skill** (recurring, tenth occurrence). First call was `date -u`; no `skill_view` all turn.
2. **Nudge #1:** inline `execute_code` verifier. First run crashed `NameError: name 'sys' is not defined` — outer execute_code script used `sys.executable` without `import sys`. Re-ran with the import; 14/14 pass; cleaned up in the same script.
3. **Nudge #2:** re-ran the same inline shape; 14/14 pass; cleaned up. The canonical `scripts/verify_becca_recap.py` was never copied across two nudges.

## Decisive fidelity gap (what the 14-check custom matrix missed)
The custom matrix checked: existence, length, title date, six sections, symlink target + resolution, inbox change-count, DB-file reference, no placeholder bullets. It did **not** check:
- **Full-ISO per-timestamp fidelity.** Recap "Work completed" cited: `00:00Z, 01:00Z, 02:00Z, 03:00Z, 04:00Z, 05:00Z, and 06:00Z`. Inbox heading timestamps (the verifiable form): `2026-08-20T00:00:05Z`, `2026-08-20T01:00:07Z`, `2026-08-20T02:00:09Z`, `2026-08-20T03:00:11Z`, `2026-08-20T04:00:13Z`, `2026-08-20T05:00:14Z`, `2026-08-20T06:00:16Z`. The canonical verifier would flag all seven.
- **Canonical-form inbox path citation.** "Sources and links" cited `~/work/next-step-becca/journals/inbox/2026-08-20.md` — the `~` form — instead of `/home/ubuntu/work/next-step-becca/journals/inbox/2026-08-20.md`.
So 14/14 twice was self-certifying. Repeat of the 08-19 finding: on quiet days the custom matrix silently shrinks and a high score is not evidence the canonical matrix passes.

## Repair (for the next session touching this date)
1. Patch `journals/2026/08/20.md`: rewrite the snapshot timestamps in full-ISO form (all seven, verbatim from the inbox headings) and cite the canonical `/home/ubuntu/work/...` inbox path in "Sources and links".
2. Run the canonical verifier: `cp scripts/verify_becca_recap.py /tmp/hermes-verify-becca-2026-08-20.py && python3 /tmp/hermes-verify-becca-2026-08-20.py 2026-08-20 && rm /tmp/hermes-verify-becca-2026-08-20.py`.
3. Report the exit code + per-check lines; label ad-hoc, not suite green. If green, the 08-20 drift is closed.
