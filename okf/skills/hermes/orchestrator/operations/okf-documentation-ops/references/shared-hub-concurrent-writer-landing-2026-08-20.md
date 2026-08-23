# Shared OKF hub with a concurrent auto-regen writer: safe landing (2026-08-20)

The `growthwebdev-knowledge` hub is a **multi-writer repo**. Besides human/agent
feature branches, an **OKF skill-hub auto-regen / drift-reconciliation process**
commits to it on its own cadence (2026-08-20: `content/kai-skill-hub-drift-2026-08-20`
branch, `okf/skills: auto-regen …` commits, `skill drift reconciliation` commits, and
a `rescue/ned-gro4797-<sha>` rescue ref it created). Working in this repo means your
branch and the remote can move **under you** between a `fetch` and a `push`. The
2026-08-20 session hit this repeatedly and it took several failed pushes / cherry-pick
failures / a rescue branch to land cleanly. This is the safe sequence.

## The failure modes that actually happened (avoid these)

1. **Committing to a stale base.** The feature branch was created from an
   `origin/main` that was several auto-regen commits behind. The remote tip (an older
   base) and my tip (newer base) **diverged** → plain `git push` rejected as
   non-fast-forward, and the remote tip was missing the new `okf/skills/` subtree
   entirely.
2. **Cherry-pick failing mid-flight** because a concurrent commit moved the working
   tree / target branch between steps. Symptom: `git cherry-pick` hints to abort,
   "needs merge" on checkout, a commit silently landing on a branch I didn't mean.
3. **Committing on whatever branch the hub checkout happened to be on** (a peer's
   unpushed `content/…` branch) → `git push origin main` lands nothing and muddies
   the peer's WIP. (Also captured as a SKILL.md pitfall.)
4. **`git config user.name` in the hub checkout is another agent's** (it was "Ned").
   The pre-push lane-ownership hook keys off the **branch prefix**, not the commit
   author, so `feature/*` → fred → `owner: ["*"]` regardless of the author name.
   Don't be misled by the author field when a lane error appears.

## The safe landing sequence

```bash
cd /home/ubuntu/work/growthwebdev-knowledge
git fetch origin

# 1. ALWAYS rebuild the working branch from FRESH origin/main — never from a branch
#    you created earlier that may now be stale. Re-apply the intended files (from the
#    live source / a saved copy), never assume the earlier commit is still valid.
git checkout -B feature/<agent>-<slug> origin/main
# ... cp the runbook, apply the index line, re-sync the skill mirror from live, ...
git add -A
git commit -m "[Fred] <summary> (#GRO-xxxx)"
MINE=$(git rev-parse HEAD)

# 2. If push is non-fast-forward, the remote moved. Do NOT merge blindly. Diagnose:
git fetch origin
REMOTE=origin/feature/<agent>-<slug>
git merge-base --is-ancestor $REMOTE $MINE && echo "remote is ancestor of mine -> plain push" \
  || echo "DIVERGED -> verify superset before force"
git merge-base --is-ancestor origin/main $MINE  && echo "mine on latest origin/main" \
  || echo "MINE ON STALE BASE -> rebuild from origin/main (step 1)"
git merge-base --is-ancestor origin/main $REMOTE && echo "remote on latest main" \
  || echo "remote on STALE main (it predates the auto-regen commits)"

# 3. Before ANY force-push, prove your tip is a SUPERSET of the remote tip: the
#    remote's content must be a strict subset of yours (identical or older base +
#    your additions). Diff the two tips; every file the remote has must be present in
#    yours at equal-or-newer content.
git diff --stat $REMOTE $MINE            # expect: your additions; no remote-only loss
# Spot-check the files the remote had (runbook, index line, mirror refs):
git diff <(git show $REMOTE:<path>) <(git show $MINE:<path>)

# 4. Only then force-with-lease on YOUR OWN feature branch (never a shared/peer branch).
git push --force-with-lease origin feature/<agent>-<slug>

# 5. Read back from origin (not the local checkout):
git fetch origin
git ls-remote origin feature/<agent>-<slug>
git show origin/feature/<agent>-<slug>:<path>   # confirm the content is what you think
```

## Rules of thumb

- **A non-fast-forward push in this hub is expected, not alarming.** The auto-regen
  writer means the remote branch will often have moved. The question is never "should
  I force?" but "is my tip a verified superset of the remote tip, and is it on a
  current base?" If yes → `--force-with-lease` on your own feature branch is correct.
- **`--force-with-lease`, never bare `--force`.** The lease fails the push if the
  remote moved again between your check and your push, which is exactly the
  concurrent-writer hazard.
- **Never force a peer's or shared branch** (`content/*`, `main`, another agent's
  feature). Force only the `feature/<you>-*` branch you own.
- **If you can't confirm superset, stop and land a NEW branch** from fresh
  `origin/main` instead of forcing. A redundant-but-clean feature branch is always
  safer than a force you can't fully verify.
- **Rebuild from `origin/main` every time** rather than reusing a feature branch you
  built 30 minutes ago — the auto-regen writer may have advanced `origin/main`.
- **Read back from `origin/`, not the working tree.** The working tree in this hub is
  unreliable mid-session (concurrent checkouts, auto-checkpoints). `git show
  origin/<branch>:<path>` is the source of truth for "did it actually land."
- **Rescue refs are the hub's own safety net, not another agent you're fighting.**
  `rescue/<agent>-gro<#>-<sha>` refs are created by the repo's tooling to preserve a
  commit when a push fails. If you see one with your SHA in it, the commit is safe —
  you don't need to "recover" it; you just need a clean branch from current
  `origin/main` carrying the same content.

## Why this is its own class

Any multi-agent knowledge hub with a background auto-regen / snapshot process has this
property: the remote is a moving target. The reusable lesson is not "git gotcha N" but
a discipline — **rebuild from fresh main, verify superset, force-with-lease on your
own branch only, read back from origin**. The 2026-08-20 session proves the cost of
skipping it: ~5 failed push/cherry-pick cycles and a tangled reflog before a clean,
verified landing.
