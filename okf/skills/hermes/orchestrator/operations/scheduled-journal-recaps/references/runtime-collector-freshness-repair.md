# Runtime Collector Freshness Repair

## Problem class
A journal snapshot can be scheduler-green but narratively wrong when it treats a recently modified, long-lived log as if its entire contents happened in the current reporting window. Reading the first N bytes is especially dangerous: current appends occur at the tail while old startup/errors occupy the head.

## Correct repair
1. Add a tail reader that seeks near EOF, drops an initial partial line, and returns newest complete lines.
2. Parse timestamps line-by-line; only emit log signals inside the explicit reporting window (for example, last 24h).
3. Keep current timestamped error detection; verify a stale error is excluded and a current error remains detected.
4. Make Git helpers return empty output for a non-repository/error result. Never turn Git stderr into `git_commits` or `git_dirty` events.
5. If the current-day generated inbox/index already contains bad signals, copy it to a dated repair-backup directory first, then regenerate only those generated artifacts. Do not alter finalized historical journals without an explicit correction policy.
6. Run the scheduler after the repair, then assert the fresh inbox/index contains neither the stale dated marker nor `fatal: not a git repository`, and contains no `git_*` signal types for a non-Git journal root.

## Verification boundary
Label fixture + scheduler evidence as **ad hoc targeted verification**, not suite green. A runtime-package patch is a bridge only; create a canonical-source/release follow-up so upgrades cannot silently overwrite it.
