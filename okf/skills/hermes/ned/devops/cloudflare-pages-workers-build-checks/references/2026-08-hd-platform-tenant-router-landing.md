# 2026-08-21 hd-platform: landing a staging-only runtime file as a clean PR (#56)

Case: Michael asked to "commit the router change, get me a PR so we can push to main."
The change was `scripts/hde_tenant_router.py` in the dirty staging checkout
`/home/ubuntu/work/hd-platform-staging` (branch `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`,
12 other modified files + untracked `.bak` files).

## The topology trap

The router **did not exist on `github/main` at all** — neither did its three import
dependencies (`scripts/hde_rate_limits.py`, `hde_job_queue.py`, `hde_usage_budgets.py`).
They only ever lived on the staging line. A naive `git diff` PR would have landed a file
that cannot `import`. Discovery sequence that caught it:

```bash
git cat-file -e github/main:scripts/hde_tenant_router.py   # fatal: exists on disk, not in github/main
git ls-tree -r github/main --name-only | grep tenant_router  # nothing
# then check the router's import closure:
for f in scripts/hde_rate_limits.py scripts/hde_job_queue.py scripts/hde_usage_budgets.py; do
  git cat-file -e "github/main:$f" 2>/dev/null || echo "MISSING $f"
done
# and that main's shared/database.py exports the symbols the router needs:
git show github/main:shared/database.py | grep -cE "class (User|Invitation|BotInstance)|async_session_factory"
```

All three deps are stdlib-only (redis imported lazily inside functions) and
`shared/database.py` on main already exports everything — so the PR = router + 3 deps +
1 runtime data file, as a **pure addition**. Confirmed no conflict surface:
`git grep -l tenant_router github/main` → nothing.

## Clean-PR recipe (isolated worktree off the fetched remote main)

Never commit from a 12-file-dirty staging tree. Do this:

```bash
git fetch github
git worktree add /tmp/pr-<topic> -b ned/<topic>-<date> github/main
cp /path/to/dirty/checkout/scripts/hde_tenant_router.py  /tmp/pr-<topic>/scripts/
cp /path/to/dirty/checkout/scripts/hde_*.py              /tmp/pr-<topic>/scripts/
git -C /tmp/pr-<topic> add -A && git -C /tmp/pr-<topic> commit -m "[Ned] ... (#GRO-XXXX)"
git -C /tmp/pr-<topic> push github ned/<topic>-<date>
gh pr create --repo <repo> --base main --head ned/<topic>-<date> ...
```

The temp worktree + local branch stay behind; deletion needs Michael's approval per
`branch-deletion-approval` (state it in the reply, don't clean up silently).

## The runtime-data-file gap (caught by importing, not py_compile)

`py_compile` passed on all modules, but an **actual `import hde_tenant_router`** logged:
`Failed to load somatic_cues.json ... Using simple fallback`. The router loads
`scripts/somatic_cues.json` (360 cues) at startup via `os.path.dirname(__file__)` —
graceful fallback, but a tracked runtime data file present on staging and absent from
main. Added it to the same PR (valid JSON check), re-ran the import:
`Successfully loaded 360 somatic cues`. Lesson: `py_compile` proves syntax; **importing
the module proves the runtime closure** (data files, optional deps, env defaults).

## Verification ladder that closed the gate

1. `py_compile` on all 4 modules — pass.
2. `import` each module (deps, then router) — pass, with the somatic_cues catch above.
3. Behavior asserts: `GUEST_TURN_TIMEOUT_SECONDS == 180.0`,
   `ONBOARDING_BOT_USERNAME == 'Humandesigncompanionbot'`, welcome-rotation
   `guide_choice_prompt(42)` twice → different openers.
4. Frontend: root `docs/` (14 sibling `.md`) is NOT an Astro source (no content
   collections, routes live in `src/`), so the new doc can't break the build — but the
   harness reminder named `npm run build`, so ran exactly it: `npm ci && npm run build`
   → exit 0, `10 page(s) built`, postbuild `route-complete` 230 legacy files preserved.
5. `gh pr view 56 --json mergeable,mergeStateStatus` → `MERGEABLE` + `UNSTABLE`
   (pending CF checks, not a failure — see SKILL.md).

## Notes

- Root-level `docs/*.md` in this repo is reference material, not site content; wiring a
  route for it is separate work. Say so instead of silently assuming it renders.
- The router's hardcoded 35s POST timeout (which aborted every real ~27B-model turn)
  became `GUEST_TURN_TIMEOUT_SECONDS` (env `HDE_GUEST_TURN_TIMEOUT_SECONDS`, default
  180). Invariant to preserve: guest hermes cap (120) < router POST cap (180).
