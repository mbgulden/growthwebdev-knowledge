# Weekly Rollup Cron — Drift Notes

## Session drift — 2026-08-09 Hermes-Research weekly rollup (skip-skill pattern)

Concrete drift on 2026-08-09, captured here so the next weekly-rollup session doesn't repeat it:

- The cron prompt for "weekly rollup from last 7 daily journals" fired. The session opened with the FIRST-REPLY REQUIREMENT state dump (one-line + next-action + in-flight + pending-decisions), then proceeded to read 7 journal files via `read_file` calls — and **never called `skill_view('scheduled-journal-recaps')`**. The skill ships a canonical `scripts/weekly_rollup_verify.py` that was one `cp`/`run`/`rm` away and was never consulted.
- Verification was rolled ad-hoc: `wc -w` + `ls -la` + `readlink` shell checks via `terminal` calls, no `/tmp/hermes-verify-weekly-*.py` file written at all. Same shape as the Becca daily drift, different cron.
- The 7-file window spanned **two ISO weeks** (Aug 2 in W31, Aug 3–9 in W32) and the rollup header said `2026-08-03 to 2026-08-09` — correct date range — but didn't surface the W31/W32 boundary explicitly. The "7 journals found; Aug 4 absent" gap was noted in the body but not the header.
- The rollup content was actually correct in shape (six sections, ≤400 words, ≥7 unique daily citations, `latest-weekly.md` relative symlink repointed). What it lacked was the canonical verifier's per-check `OK`/`FAILURE` evidence that the audit hook expects, and the prior-week `--snapshot-prev` baseline that protects against the previous weekly being overwritten.
- Concrete corrections for the next session that opens a weekly-rollup cron prompt:
  1. **First tool call**: `skill_view(name='scheduled-journal-recaps')`. Not optional. Not conditional. The skill name is the loader hook; if it loads, follow it.
  2. **Discover the 7 files**, then **compute ISO week labels** for all 7 with `for d in <dates>; do date -d "$d" +"%Y-W%V"; done | sort -u`. If more than one label appears, the window straddles a week boundary — surface that in the rollup header's date range.
  3. **Word-count the draft before writing it.** First drafts run 25-50 words over the 400 limit because the body sections expand naturally. Trim in place; do not write a too-long file and assume the verifier will pass.
  4. **Write the real file first** via `write_file` on `weekly/YYYY-Www.md` (where YYYY-Www is the ISO week of the **end date**, not today's clock). **Never** `write_file` through `latest-weekly.md` — it's a symlink and `write_file` follows symlinks, overwriting the previous weekly artifact. Use `ln -sfn weekly/YYYY-Www.md latest-weekly.md` to repoint atomically.
  5. **Last tool call before final response**: capture the baseline and run the canonical verifier, both as separate `python3` invocations of the same script:

     ```bash
     python3 ~/.hermes/profiles/orchestrator/skills/operations/scheduled-journal-recaps/scripts/weekly_rollup_verify.py /home/ubuntu/work/Hermes-Research/journals 2026-W32 --snapshot-prev
     python3 ~/.hermes/profiles/orchestrator/skills/operations/scheduled-journal-recaps/scripts/weekly_rollup_verify.py /home/ubuntu/work/Hermes-Research/journals 2026-W32
     ```

     Report the script's exit code and per-check `OK`/`FAILURE` lines verbatim. Never replace the canonical verifier with `wc -w` + `ls -la` ad-hoc checks — same drift shape as the Becca daily recap, different cron.
  6. **Self-detection by `prismatic-journal-snapshot`** is unlikely for weekly rollups (the snapshotter watches the inbox dir, not `weekly/`), but if a future migration moves weekly rollups under a watched path, apply the same self-referential reframe recipe documented in `references/becca-journal-recap.md` for the Becca daily recap.

## ISO-week-boundary recipe (worked example, 2026-08-09)

The end date is **always** the most recent of the 7 files. The ISO week for the output file name comes from `date -d <end-date> +"%Y-W%V"`. For a window that spans two ISO weeks:

| Date       | Day | ISO Week | In 7-file window? |
|------------|-----|----------|--------------------|
| 2026-08-02 | Sat | 2026-W31 | yes (oldest)       |
| 2026-08-03 | Mon | 2026-W32 | yes                |
| 2026-08-04 | Tue | 2026-W32 | **no — file missing** |
| 2026-08-05 | Wed | 2026-W32 | yes                |
| 2026-08-06 | Thu | 2026-W32 | yes                |
| 2026-08-07 | Fri | 2026-W32 | yes                |
| 2026-08-08 | Sat | 2026-W32 | yes                |
| 2026-08-09 | Sun | 2026-W32 | yes (newest)       |

End date = 2026-08-09 → ISO week = 2026-W32 → output file `weekly/2026-W32.md`. Header text should say: *"7 journals found; Aug 4 absent; window spans ISO W31 (Aug 2) and W32 (Aug 3–9)."* The previous weekly file (`weekly/2026-W31.md`) exists in the directory and is the natural `--snapshot-prev` baseline.

If two weeks appear and the prior weekly file is missing (e.g. the journals directory's `weekly/` only has `2026-W30.md`), the canonical verifier's check #6 (`previous-week unchanged`) will skip with `INFO no previous-week baseline; skipping byte-identical check`. That is correct behavior, not a failure — capture and re-run without `--snapshot-prev` and the script still passes on checks 1–5.

## Path: weekly/ vs latest-weekly.md

The journals directory layout (`/home/ubuntu/work/Hermes-Research/journals/`) at the time of this drift:

```
journals/
├── 2026/
│   └── 08/
│       ├── 02.md
│       ├── 03.md
│       ├── 05.md
│       ├── 06.md
│       ├── 07.md
│       ├── 08.md
│       └── 09.md
├── inbox/
├── weekly/
│   ├── 2026-W23.md  ... 2026-W30.md
│   ├── 2026-W31.md  (predecessor)
│   └── 2026-W32.md  (new)
└── latest-weekly.md -> weekly/2026-W32.md
```

Canonical verifier command for the `Hermes-Research` root:

```bash
python3 ~/.hermes/profiles/orchestrator/skills/operations/scheduled-journal-recaps/scripts/weekly_rollup_verify.py /home/ubuntu/work/Hermes-Research/journals 2026-W32
```

For the `next-step-becca` root (different journals tree), substitute `/home/ubuntu/work/next-step-becca/journals` as the first argument. Same script, same exit-code semantics.