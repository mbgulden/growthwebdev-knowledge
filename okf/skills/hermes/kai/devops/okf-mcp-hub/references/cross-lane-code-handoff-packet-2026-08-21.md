# Cross-lane code handoff packet (verified 2026-08-21)

When you build code that is **outside your lane** and the pre-push hook
correctly blocks you (PE: `prismatic/`+`scripts/`+`tests/` = Ned's lane /
Fred's `*`; Kai owns `content/`+`active-oahu/` only), do NOT rename the branch
to slip past the guard and do NOT force it. This is the durable "commit
locally + hand off in-lane" pattern (resolution path (e) in the lane-gate
list), executed end-to-end for the G2+G6 journal bundle:

## Why not just push
The lane guard exists to prevent cross-lane contamination. Renaming
`content/x` → `feature/x` to attribute the push to Fred, or `git -c
core.hooksPath=/dev/null push`, defeats the control. If the code genuinely
belongs to another agent's lane, the *landing* belongs to that agent — your
job is to make their landing a 2-minute mechanical step, not a re-do.

## The 5-step pattern

1. **Commit locally on your branch** (push will be blocked — that's expected).
   - `git reset -q` then `git add <only your files>` — on a shared box,
     `git add -A` sweeps in foreign untracked files (swarmlock research,
     dashboard PNGs). Stage exactly the intended files and verify with
     `git diff --cached --name-only | grep -vE '<expected>'` → empty.
   - Fix lint hygiene (unused imports, `ruff format`) before commit so the
     handoff is clean.
   - Cite the CORRECT Linear issue in the commit subject — verify the issue
     → gap mapping first (this session: the commit cited GRO-4829, but 4829
     was actually G8; the real bundle issue was GRO-4830). Amend if wrong.

2. **Generate the patch + verify it is byte-identical to the commit.**
   ```bash
   git -C <repo> format-patch -1 <commit-sha> --stdout > /tmp/handoff.patch
   # or: git show --format= <commit-sha>  (unified diff, no commit header)
   ```

3. **Write the handoff packet doc IN YOUR LANE** (Kai: `okf/audits/`,
   `okf/hubs/`, `okf/standards/`). It must be self-contained so the landing
   agent needs no other context:
   - What was built (gap → code mapping), what's verified (test counts,
     idempotency proof, live smoke tests), what's already applied (side
     effects like a run backfill or a patched live server — "do NOT redo").
   - **Exact landing commands** (branch name, `git apply` path, the exact
     pytest invocation, commit message, PR base).
   - **The full patch embedded** in a ` ```diff ` fence (self-contained —
     the landing agent copies it out, no access to your unpushed commit).
   - Out-of-scope markers (sibling issues that are NOT part of this bundle).

4. **Branch + PR the doc** from `origin/main` (NOT from a branch that's an
   open PR). The doc is in your lane so the push is clean. Verify the PR
   shows exactly the one doc file (the `git checkout <sha> -- .` trick to
   pull a file can drag in foreign files — `git reset -q` and re-stage only
   the doc).

5. **File a Linear child task** for the landing (see
   `linear-api-patterns.md` for the create + `commentCreate` +
   `issueUpdate(parentId:)` shapes):
   - Title: `<bundle>: apply verified patch in-lane + open <repo> PR`.
   - Description: context (why done-but-unpushed), the handoff PR link,
     copy-paste landing steps, "already done / do NOT redo", out-of-scope,
     acceptance criteria (exact file list, test count, issue → In Review).
   - Set parent to the bundle issue via `issueUpdate(parentId:)`.
   - Post a pointer comment on the bundle issue.
   - Leave it **unassigned** if you're unsure which agent; let Michael route.
     (Do not guess — the app key can't assign to the PE bot anyway.)

## Verification (the part that makes it trustworthy)

Ad-hoc, not suite green — the deliverable is a markdown doc, so the load-
bearing check is: **does the embedded patch apply cleanly to a pristine base
and reproduce the commit byte-for-byte?**
```python
# in a temp worktree of pristine origin/main:
git apply --check embedded.patch          # clean?
git apply embedded.patch
git add -A
assert (git diff --cached) == (git show --format= <commit>)   # byte-for-byte
# then run the target test suite on base+patch
```
- `git diff` (no `--cached`) MISSES untracked files the patch added — use
  `git add -A` then `git diff --cached`, else the comparison silently
  under-counts and "fails" on a false mismatch.
- Verify the doc's factual claims too (commit sha present, issue id present,
  addendum present) so the landing agent isn't misled.
- Clean up the temp worktree + verify script after.

## This session's actuals (G2+G6 journal bundle)
- Code: PE `content/journal-g2-g6-20260821` @ `9c43e44a` (unpushed, lane-blocked).
- Packet: OKF `okf/audits/g2-g6-handoff-packet-2026-08-21.md` → PR #42 (Michael
  merged it; doc now on `origin/main`).
- Task: GRO-4831 (parent GRO-4830), unassigned, ready for Ned (lane owner) or
  Fred (`*`).
- Verification: 7/7 ad-hoc checks pass (patch applies to pristine main,
  byte-for-byte, 46/46 tests on base+patch); Linear read-back 6/6 pass.
