---
name: telegram-cron-output-check
description: Scan Telegram-bound cron scripts for forbidden stdout patterns. Detects recap paragraphs, all-clear / green-pulse markers in stdout, debug scaffolding, recurring tagged prefixes, and verbose emit patterns. Run on every cron script change. Exit 0 = clean; exit 1 = violations to fix.
---

# telegram-cron-output-check

## What this verifier checks

Every Telegram-bound cron script must follow the cron-alert-output-contract (the OKF standard, mirrored in the `telegram-cron-output-contract` micro-skill). The verifier enforces the contract mechanically by scanning for forbidden patterns.

The verifier catches:

- Recap paragraphs (multi-line output that prints even when nothing is active).
- Header-only outputs (date + counts but no action line).
- All-clear / green-pulse markers in stdout (e.g. `SILENT`, `OK`, `All hostnames locked`).
- Debug scaffolding (e.g. `Alert sent to Telegram`, `AGY exit code`).
- Recurring tagged prefixes (`[NIGHTLY-BACKLOG]`, `[CONSULTING-PIPELINE]`) that should go to stderr.
- "Top stale", "Sample next_action", "GitHub activity sample", "Projects scanned" — recap-section labels.
- Internal narrative (`Let me...`, `I will...`, `I am going to...`).
- Cross-Project Sync header (the day-of-week recap the original script emitted).

The verifier is heuristic. False positives are possible. False negatives are also possible — patterns not yet encoded won't be caught. The list grows over time as new violations appear in audits.

## Inputs

```
python3 verify.py <path-or-dir>
```

- Single file: pass the path. Verifier scans one file.
- Directory: pass the dir. Verifier walks recursively, scanning every `.py` and `.sh`.

## Exit codes

- **0**: no forbidden patterns found. The directory or file is contract-clean.
- **1**: violations found. The output lists each file, line number, pattern name, and a 100-char excerpt.
- **2**: usage error (wrong number of args, path not found).

## What is excluded

- Lines that print to stderr (`file=sys.stderr` or `file=sys`) are skipped. Scaffolding belongs there.
- The verifier itself (the file with `telegram-cron-output-check` in its path) is excluded.
- Broken symlinks are skipped (they'd cause FileNotFoundError on open).

## When to use this verifier

Per `verifier-as-deliverable-discipline/SKILL.md`, this verifier ships alongside any artifact that touches Telegram-bound cron scripts. Run it before claiming a script is correct.

Specific triggers:

- After editing any `scripts/*.py` or `scripts/*.sh` file referenced by a cron job.
- After enabling a paused cron (`hermes cron enable <id>` or via `jobs.json` edits).
- After adding a new cron job.
- As a final pass before claiming a gap-7-style "Telegram is too chatty" fix is done.

## Known limitations

- The pattern list is hand-curated from real audits. New violation shapes won't be caught.
- The verifier does not check whether the script's cron deliver setting causes double-delivery (this requires cross-referencing `cron/jobs.json`).
- The verifier does not check whether `--quiet` is wired up correctly in the cron wrapper. That requires reading both the script and the `*.sh` wrapper that invokes it.
- The pattern `print\([^,)]*\[NIGHTLY-BACKLOG\]` uses `[^,)]` to avoid matching positional arguments; this is heuristic and may miss multi-line tagged-prefix prints.

## Adoption status

Shipped 2026-07-29 with the gap-7 Telegram-cron-output-contract discipline. Currently scans the orchestrator's `scripts/` directory clean. Symlinked onto 5 other profiles (george, kai, ned, autobot, next-step).

## Related work

- Micro-skill: `skills/micro/telegram-cron-output-contract/` — the contract itself, including forbidden patterns and implementation requirements.
- OKF standard: `okf/standards/cron-alert-output-contract.md` — the canonical contract.
- Umbrella: `skills/agent-operations/verifier-as-deliverable-discipline/` — the four named verifiers and the counter.
