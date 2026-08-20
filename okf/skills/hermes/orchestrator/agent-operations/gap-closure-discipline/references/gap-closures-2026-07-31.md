# Gap closures from 2026-07-31 — Moves 11-19 cleanup pass

This is the worked-example record for the orchestrator-scripts-repo cleanup pass. The discipline is in SKILL.md; the worked examples are here. Read this when closing a multi-move cleanup pass, when reconciling a stale handoff, when running a verification audit that surfaces bugs in the verifier itself, or when handling a direction-pivot mid-session.

## Context

Previous session (2026-07-30) shipped Moves 11/12/13 plus wrote but did not commit Move 14. Hit the 90-call tool cap mid-Move-14. State at handoff-write time was 4 commits ahead on `feature/gro-3306`, Move 14 verifier + audit done but uncommitted.

This session was opened from a cold-start greeting with a 30h-stale `state/current.json` that did NOT mention Moves 11-14. The first bounded move was **not** "resume Move 15" — it was "verify the handoff is current" → discovered staleness → recovered via `git log` + `git status` + `session_search` → wrote fresh handoff. This was the entire reason the cold-start first reply said `current.json was last written 2026-07-30T17:40`.

## The 5 moves shipped (Move 15-19)

| # | Title | Linear | Commits | Verifier result |
|---|---|---|---|---|
| 15 | Commit Move 14 verifier + OKF doc + GRO-4372 comment | [GRO-4377](https://linear.app/growthwebdev/issue/GRO-4377) | `ff88799` | 4/4 PASS |
| 16 | Classify + commit 23 critical untracked scripts + .gitignore | [GRO-4378](https://linear.app/growthwebdev/issue/GRO-4378) | `51d30c7`, `6b75b4a` | 4/4 PASS (after bug fix) |
| 17 | Reconcile ned/GRO-3310 branch | [GRO-4379](https://linear.app/growthwebdev/issue/GRO-4379) | `4fe304a` (merge) | pre-commit 9/9 PASS |
| 18 | Delete 4 stale .bak files + gc prunable worktree | [GRO-4380](https://linear.app/growthwebdev/issue/GRO-4380) | (deletions only) | 4/4 PASS |
| 19 | Final handoff refresh + counter bump + stand down | [GRO-4381](https://linear.app/growthwebdev/issue/GRO-4381) | (handoff only) | 10/10 PASS (ad-hoc Move 19 verifier) |

Plus: [GRO-4372](https://linear.app/growthwebdev/issue/GRO-4372) retroactively closed (the Move 14 task that hit the tool cap). Parent [GRO-3306](https://linear.app/growthwebdev/issue/GRO-3306) ("Google AI Ultra Toolkit & Workflow" project) has summary comment.

**Counter:** 72 → 81. Discipline: 100% throughout.

## The bugs hit during this pass — by category

### Category 1: Verifier had bugs the first time it ran (Move 14 → Move 16)

Two bugs in `verify_move14_untracked_audit.py` surfaced when the audit re-ran post-Move-16:

1. **`os.path.basename()` on a directory entry returns `""`.** `agy-oauth/` got reduced to `""`, which then matched in `git_grep_untracked("")` and polluted `code_refs`. Fix: `if os.path.isdir(path): continue` before basename extraction.

2. **The "critical" checks were designed pre-Move-16.** They asserted `"registry_writer.py" in code_refs` (i.e., "the audit found this file as untracked-and-referenced"). After Move 16 committed `registry_writer.py`, the check FAILED because the file was now tracked, not untracked. Fix: invert the check — PASS if tracked, FAIL if untracked-but-referenced (Move 16 missed one), FAIL if absent.

This is the same bug class as the verifier-as-deliverable-discipline "Critical-check assertion inverted after fix lands" pitfall — but encountered fresh in a different verifier. The recipe is universal: **when a fix moves a file from untracked to tracked, the verifier that asserted "must be in the untracked list" silently flips from PASS to FAIL.** Either change the check to accept either state, or scope the verifier to detect only the original problem (and run it once before the fix lands, archiving the result).

### Category 2: Linear API identifier-reality (Move 15)

Drafted 5 tasks as "GRO-4373..4377." Sent the issueCreate mutations. Got GRO-4377..4381 instead. Cause: GRO-4373..4376 already existed (Zapier infra tasks by another agent). Linear assigns sequential identifiers; it does not gap-fill.

**Fix pattern:** Plan by parent epic + child title; let Linear assign. Reference tasks by UUID in code, by identifier in human-readable artifacts only after the API call returns.

### Category 3: Merge-conflict indent drift (Move 17)

Three auto-merge conflicts in `agy_sandbox_event_supervisor.py`. Resolution strategy: keep HEAD signature (additive), take ned's `build_agy_command()` helper (cleaner extraction), take ned's `stdin=subprocess.DEVNULL` (the actual GRO-3310 bug fix).

But the first `patch` call to remove the conflict markers stripped one indent level from `token: str = None,`. Caught by lint. The fix was to re-patch with the original indentation. Same pattern repeated for the third conflict.

**Recipe for three-conflict-in-one-file merges:** Declare the strategy in one sentence **before** opening the file. Edit. Run `python3 -c "import ast; ast.parse(open(path).read())"` after each conflict resolution. Three conflicts is the threshold where strategy declaration + AST-parse-between-edits saves more time than it costs.

### Category 4: Handoff fact-vs-estimate mismatch (Move 19)

Final handoff claimed `feature/gro-3306 has 10 commits ahead of main`. Mental estimate from a truncated log view. **Actual count: 47 commits ahead.** Caught by the ad-hoc Move 19 verifier (check #7: `git log main..feature/gro-3306 --oneline | wc -l`). The handoff + OKF doc both said "10" until the verifier forced a re-count.

**Recipe:** any count that lands in a handoff, OKF doc, or Linear comment must come from `wc -l` / `ls | wc -l` / `git log ... | wc -l` at write time, not mental estimation. The verifier catching the miscount is what good verification looks like — but it's better to never write the wrong number in the first place.

### Category 5: Ad-hoc verifier's own bugs (Move 19)

`/tmp/hermes-verify-move19-cleanup-2026-07-31.py` first ran 8/10 with 2 false-positive FAILs:

1. `os.listdir(REPO)` returned a name (`silent_cron_detector.py`) that had been deleted; `open()` raised `FileNotFoundError`. Fix: `if not os.path.isfile(path): continue`.
2. The pre-commit hook success marker check looked for `"All gates passed"` (old marker); actual markers are `✅ Move 11 verifier: ALL CHECKS PASSED` and `All gates passed successfully`. Fix: match the actual markers in current use.

After 2 patches, re-run was 10/10. Then `rm` the script. PASS-count + findings captured in handoff + OKF + GRO-4381 comment.

## The directional pivot pattern

This session had **two direction pivots** that I'd not previously encountered in this shape:

1. User opened with "Should Fred be building the transitional sections of prismatic engine?" — a question. I responded with "yes, but scope-defining questions first" + `clarify` tool with 4 options.
2. User pivoted: "Please do cleanup and gracefully merge the work that Fred has been working on the last few days" — new directive.
3. User refined: "Please create linear tasks for each of these items and systematically resolve them one by one" — further scope.

The right move at step 2 was to **execute on the new directive**, not to ask a clarifying question. Projector discipline says "ask when ambiguous" — but the new directive was unambiguous; a clarifying question would have added noise. Acknowledge in one sentence, pick the highest-impact bounded move, execute.

## Lessons for future cleanup passes

1. **Cold-start with a stale handoff = always assume staleness, reconstruct from durable sources.** The recovery sequence is in `session-state-handoff/SKILL.md` under "Pitfall: a stale handoff is a hidden failure mode."
2. **Re-run your verifier after fixing what it detects.** The "inverted critical-check" bug only surfaces on the post-fix re-run, not on the post-write first run.
3. **Merge conflicts in same file: declare strategy first, edit second, AST-parse between edits.** Strategy-first saves more time than the cost of writing it down at three-conflict complexity.
4. **Counted values are claims, not facts, until verified.** Branch ahead/behind, file count, line count — all need `wc -l` at write time.
5. **Direction pivots are clarifications, not questions.** When the user gives a new directive, execute on the new directive. Don't ask whether to scope it.

## What this cleanup pass did NOT close

The 15 gaps surfaced in `state/okf-orchestrator-gaps-2026-07-31.md` — most notable: `state.db` is 4.7GB unvacuumed; `cron/jobs.json` is not in any git repo (no commit history on cron changes); 61 stale `.jobs_*.tmp` files in cron/; 7 additional `.bak` files in scripts/ deferred from Move 18 scope; George's 6 stale reviewer delegations (the actual George bottleneck Michael originally flagged). None of these were in scope for "Fred's last few days of work" — they're separate gaps for a future cleanup pass.

## Files touched

- `state/current.json` — refreshed (was 30h stale)
- `state/okf-move-14-untracked-audit.md` — new
- `state/okf-move-19-handoff-refresh.md` — new
- `state/okf-orchestrator-gaps-2026-07-31.md` — new
- `state/proactive-count.json` — counter 72 → 81
- `scripts/verify_move14_untracked_audit.py` — bug fixes (committed `6b75b4a`)
- `scripts/agy_sandbox_event_supervisor.py` — merge conflict resolution (commit `4fe304a`)
- `scripts/.gitignore` — `prismatic_state/*.db`, `event_bus.db`, `*.bak`, `*.bak-*` added (commit `51d30c7`)
- 23 critical scripts tracked (commits `51d30c7`)
- 4 stale `.bak` files deleted (Move 18)

Counter discipline: 81/81 = 100% throughout. No `--no-verify` on any commit. Every move was committed + Linear-comment + state-update before moving to the next.
