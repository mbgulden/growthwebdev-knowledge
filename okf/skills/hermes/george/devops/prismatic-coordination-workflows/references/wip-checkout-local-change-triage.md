# WIP-checkout local-change conflict-risk triage (Prismatic multi-worktree fleet)

**Trigger:** human flags "conflict risk with `<file>` needs inspection before proceeding," OR a clean-checkout/rebase of a WIP checkout is pending (e.g. native-crons `design/GRO-3837`, 89 dirty files, live crontab block running from it).

**Class:** inspect READ-ONLY, then present a disposition menu for human authorization. Never discard/stash/commit without the call.

## Why this class exists

Live cron blocks + WIP checkouts (dirty index, auto-checkpoint commits) mean a rebase or clean-checkout move will be blocked by — or silently destroy — staged local changes. The inspection must separate: (a) what the branch already committed, (b) what lives only in the index, (c) what runtime actually reads. Those three answers determine the whole risk profile.

## Recipe (all read-only unless authorized)

1. **Locate every checkout carrying the file** and which are dirty:
   ```bash
   for d in /home/ubuntu/work/*/; do
     git -C "$d" status --porcelain -- <path> 2>/dev/null | sed "s|^|$(basename $d): |"
   done
   ```
2. **Classify staged vs unstaged** — porcelain two-column read: `M ` = staged (index), ` M` = unstaged (worktree). Then split the diffs:
   - worktree vs index: `git diff -- <path>` (often EMPTY for staged-only changes — that is the trap, see pitfalls)
   - index vs HEAD: `git diff --cached -- <path>`
3. **Blob identity — who already matches whom:**
   ```bash
   git rev-parse :<path>            # staged blob
   git rev-parse HEAD:<path>        # committed
   git -C <canonical-checkout> rev-parse origin/main:<path>
   ```
   If `HEAD` blob == `origin/main` blob, the branch state is clean and the entire risk lives in the index draft.
4. **Cross-worktree match** — which drafts are identical, which are unique:
   ```bash
   for d in /home/ubuntu/work/*/; do
     b=$(git -C "$d" hash-object "$d/<path>" 2>/dev/null)
     [ -n "$b" ] && echo "$(basename $d) $b"
   done
   ```
5. **Provenance:** `git log origin/<branch>..HEAD --stat` (the ahead commit — look for `[WIP-auto-checkpoint]` author/timestamp) + `stat -c '%y' <file>` (draft age).
6. **Runtime impact:** pull the full crontab (`crontab -l`) noting the `# BEGIN/END PRISMATIC_NATIVE_CRONS` block, then `grep -rn '<file-or-dir>' scripts/` in the checkout. Usually `research/` docs → zero runtime readers → risk is git-hygiene only (blocks rebase/clean-checkout; future 3-way merge if the file later changes on main).
7. **Content assessment:** save the full diff to a file (`git diff --cached -- <path> > /tmp/george-<topic>-staged-diff.txt`), READ it, and assess what the draft changed (version bump? removed guardrails? new sections?). Attach the diff file via MEDIA — never paste a 200-line diff into chat.
8. **Present proof block + disposition menu** (one authorization decides it):
   1. **Preserve-then-clean (default recommendation):** commit the staged draft to a local tombstone branch (e.g. `wip/<topic>-<date>`, no push) → checkout is then free for the canonical clean move. Preserves draft truth, blocks nothing.
   2. **Labeled stash:** `git stash push -m "<topic> WIP <date>" -- <path>` — lighter, but the stash lives in the same checkout that may be wiped.
   3. **Discard** — only after human confirms throwaway; push back once first (real work deserves a branch tombstone).
   4. **Leave as-is** — then the clean-checkout/rebase decision stays explicitly blocked until this is resolved.

## Pitfalls

- **Staged-only changes look clean to `git diff`.** `git diff -- <path>` returns 0 lines for an index-only change; a "no diff" read is a false clean. Always start from `git status --porcelain` columns.
- **WIP auto-checkpoint commits don't cover the file.** The ahead commit may predate the file's mtime; a dirty index is NOT committed. Verify with `git status --porcelain -- <path>`, not with commit count.
- **Don't judge the draft by age.** Old + uncommitted ≠ junk; read the diff. In the 2026-09-06 instance the 7-week-old draft downgraded doc version 1.1.0 → 1.0.0 AND deleted the TBD-by-GRO-3838 guardrails → rough draft: preserve via tombstone, do NOT promote.
- **Cross-worktree hash loop:** guard with `2>/dev/null` and `[ -n "$b" ]` — some worktrees lack the file and bare `git hash-object` would pollute output.

## Executing Option 1 (preserve-then-clean) — verified plumbing recipe

When the human authorizes Option 1, commit the staged draft to a side branch **without moving the live branch's HEAD and without touching any other dirty file**. Do NOT `git commit` in the checkout (it would drag in whatever else is staged, or rewrite the live branch). Use raw plumbing with an isolated index:

```bash
cd <checkout>
BRANCH=$(git rev-parse --abbrev-ref HEAD)          # live branch, must NOT move
HEAD_TREE=$(git rev-parse HEAD^{tree})
STAGED_BLOB=$(git rev-parse :<path>)               # the staged blob to preserve
NEW_TREE=$(GIT_INDEX_FILE=$(mktemp) git read-tree "$HEAD_TREE" && \
  GIT_INDEX_FILE=$(mktemp) git update-index --cacheinfo 100644,$STAGED_BLOB,<path> && \
  GIT_INDEX_FILE=$(mktemp) git write-tree)
COMMIT=$(git commit-tree "$NEW_TREE" -p "$HEAD" -m "[wip-preserved] <topic> staged draft <date>")
git update-ref refs/heads/wip/<topic>-<date> "$COMMIT"
git restore --staged --worktree -- <path>          # free the checkout
```

(Sequence the `GIT_INDEX_FILE` steps against ONE temp index file in practice: read-tree → update-index → write-tree on the same temp index, then `rm` it.)

**Verification (run all, report as proof block):**
- `git status --porcelain -- <path>` → 0 lines (file clean).
- Dirty-file count dropped by exactly 1 (e.g. 89 → 88); branch still `ahead N` on the SAME sha.
- Worktree blob now == `origin/main:<path>` blob (`git rev-parse <path>` after restore).
- `git diff $BRANCH..wip/<topic>-<date> --stat` → exactly the one file at the original ±line count (e.g. 100+/69−).
- `git diff origin/main: <path>` vs the side branch file → line count matches the saved staged-diff file exactly (201 lines in the 09-06 instance).

Side branch stays local-only unless the human explicitly asks to push (pushing is a separate authorization).

## Instance (2026-09-06, george)

- File: `research/rubric-inventory-matrix.md` (GRO-3837 scorecard rubric, v1.1.0 on PE origin/main).
- Only dirty checkout: `/home/ubuntu/work/prismatic-pe-native-crons` on `design/GRO-3837`, ahead 1 (`[WIP-auto-checkpoint]` 2026-07-15, author Ned), 89 porcelain files total.
- Staged-only: staged blob `c3dbe122` vs HEAD blob `9a69ef51` **== PE origin/main blob** → branch state clean; index draft = 100+/69−: rewrote scoring table, version 1.1.0→1.0.0, deleted "TBD by GRO-3838"/"Target Score is 10"/evidence-actionability guardrails, added "Complete Rubric Matrix" sections A–E (rows A1–E3, fred/ned owner lanes, `scripts/plugin_architecture` + `/api/plugins/*` proof surfaces). mtime 2026-07-15 17:21.
- Runtime: 11-entry native-cron block (pwp credentials refresh + 10 seo jobs) runs from the same checkout; `grep -rn rubric-inventory scripts/` = 0 → zero runtime impact.
- **EXECUTED (authorized same session):** plumbing recipe above → side branch `wip/rubric-matrix-draft-20260715` @ `96e7ac6b` (parent `7d59a3f0`, live branch unchanged); worktree file restored to `9a69ef51`; dirty 89→88; side-branch diff = exactly 1 file 100+/69−; vs-PE-main diff 201 lines == saved staged diff. Branch local-only; push-or-keep is a separate pending decision.
