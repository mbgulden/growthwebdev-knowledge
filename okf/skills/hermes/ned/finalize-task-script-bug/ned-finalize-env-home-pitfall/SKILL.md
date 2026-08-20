---
name: ned-finalize-env-home-pitfall
description: Use when running Ned's finalize_task.sh after sourcing profile .env files; prevents HOME/tilde path expansion failures.
---

# Ned finalize env HOME pitfall

## Trigger

You source Linear credentials or profile env files before calling Ned's `finalize_task.sh`, especially with:

```bash
set -a
source /home/ubuntu/.hermes/profiles/orchestrator/.env
# or source /home/ubuntu/.hermes/profiles/ned/.env.bak
set +a
```

## Rule

**Ned's terminal runs with `HOME=/home/ubuntu/.hermes/profiles/ned/home` (the profile sandbox) — always, not just after sourcing env.** So `~` in Ned's shell expands into a *nested sandbox copy* of the tree (`/home/ubuntu/.hermes/profiles/ned/home/.hermes/...`), not the real one. `ls ~/.hermes/profiles/` returns only sandbox contents (often just `orchestrator`), and `~/.hermes/profiles/ned/` looks empty — both are wrong. **Always address real Hermes paths with absolute `/home/ubuntu/.hermes/...`** (real profile tree at `/home/ubuntu/.hermes/profiles/<p>/`), never `~`, for any read *or* write — regardless of whether you sourced anything. This silently produced empty/wrong results until switched to absolute paths.

Concretely, do **not** invoke finalize via `~/.hermes/...` after sourcing env files (some profile envs redefine `HOME` too), because shell expansion can produce paths like:

```text
/home/ubuntu/.hermes/profiles/ned/home/.hermes/profiles/ned/scripts/finalize_task.sh
```

and fail with `No such file or directory`.

**Always use absolute paths for critical scripts.** Especially for scripts like `finalize_task.sh` that are called as part of a structured workflow (e.g., from `autonomous-task-skeleton.md`), always use the full, absolute path (e.g., `/home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh`) to avoid any ambiguity or environment-dependent path resolution issues, particularly in cron environments.

## Safe command

Use the absolute path:

```bash
PRISMATIC_REPO_ROOT=/path/to/worktree \
FINALIZE_LOCK_FILES='api/main.py scripts/foo.py docs/bar.md' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

## Invocation safety

`finalize_task.sh` is an executable workflow, not a conventional CLI parser. Never call it with `--help` or another fake issue merely to discover usage: that can run default commit/unlock/Linear-comment steps against the literal argument. Read the script instead, or use `--dry-run` only with a real issue identifier and explicit `PRISMATIC_REPO_ROOT` plus `FINALIZE_LOCK_FILES`.

For a newly created empty GitHub repository, verify `defaultBranchRef` after the first branch push. If `main` is still unborn, PR creation will fail with `Base ref must be a branch`. Do not fix this by directly pushing the task branch to `main`; report the exact guardrail/bootstrap blocker and leave default-branch establishment to the authorized repository-setup work.

## Verification

Finalize's transcript is necessary but not sufficient. Treat finalize as succeeded only after all of these hold:

- output includes `STEP 1: committing any pending changes`
- output includes `STEP 3: transitioning GRO-XXXX to 'In Review' state`
- output includes `STEP 4: posting final evidence to Linear comment thread`
- final report block includes `Finalized: <timestamp>`
- a follow-up Linear query shows the issue is actually `In Review`
- a follow-up Linear comment query confirms the finalizer comment exists; if `comments(last: 1)` appears stale, query a wider window (`comments(first: 50)` or paginated) and sort by `createdAt` before concluding the finalizer failed — Linear comment connection ordering can be surprising in Ned cron verification
- stale scanner labels such as `dispatch:ready` are removed when this is a redispatch refresh
- the local `/tmp/issue-batches/<ISSUE>_RESULT.md` is rewritten after finalize/manual cleanup so it records actual final state, not pre-finalize intent (see `finalize-task-script-bug/references/ned-redispatch-result-finalization-rewrite.md`)
- `node /home/ubuntu/.antigravity/swarm.js status` shows no residual locks

Lock-shape pitfall: if locks were acquired with a different namespace/owner shape than `finalize_task.sh` uses, the script may print successful-looking unlocks while locks remain. This includes both simple-owner locks (`swarm.js lock <path> ned`) and non-`prismatic-engine` repo namespaces such as `swarm.js lock <path> sentinel-it-asset-logistics ned`; finalize currently unlocks as `prismatic-engine`. Re-run `swarm.js status`; unlock leftovers with the exact same namespace/owner form used to acquire them (`swarm.js unlock <path> ned` or `swarm.js unlock <path> sentinel-it-asset-logistics ned`). Session-specific details: `finalize-task-script-bug/references/ned-gro-3993-redispatch-finalize-lock-shape.md` and `references/ned-gro-4016-sial-closeout-finalize-lock-label-refresh.md`.

Parent-epic redispatch pitfall: if a parent epic already has an existing `ned/...` branch/PR/result and scanner redispatches it from `Backlog` only because `dispatch:ready` reappeared, do not rebuild. Query Linear comments/children, verify the existing branch in a clean temp worktree, rerun finalize with absolute script path + explicit `PRISMATIC_REPO_ROOT`/`FINALIZE_LOCK_FILES`, then remove stale `dispatch:ready` and verify state/labels/locks. Keep the epic non-green if children remain unmerged, child gates remain open, or the live verifier is still red. If a fresh Node/Astro worktree lacks `node_modules`, run the lockfile install (`npm ci`) before `npm run build`; `astro: not found` is dependency setup, not code evidence. If the live verifier is designed to exit nonzero while `green:false`, capture that expected exit/output as evidence rather than treating it as a repair blocker. If finalize leaves simple-owner locks behind, unlock with the same simple form used to acquire them. Detailed recipes: `finalize-task-script-bug/references/ned-gro-3992-parent-epic-redispatch-refresh.md`, `finalize-task-script-bug/references/ned-gro-4010-parent-epic-redispatch-refresh.md`, and `references/parent-epic-redispatch-refresh.md`.

Safe-delete / duplicate-cleanup redispatch pitfall: if an already-finalized ops-safety task reappears with an open PR and mixed checks, verify from a clean detached worktree and assert the durable safety contract (`safe_delete_candidate_count == 0`, `deleted == []`) rather than exact historical candidate counts; counts may drift as the repo changes. Rerun finalize with `PRISMATIC_REPO_ROOT`/`FINALIZE_LOCK_FILES`, remove stale `dispatch:ready`, keep Linear `In Review` while any remote proof check is red, and return `[SILENT]` when no new blocker exists. Detailed recipe: `finalize-task-script-bug/references/ned-gro-3985-safe-duplicate-redispatch-refresh.md`.

Already-implemented SEO/static-build redispatch pitfall: if Linear comments already contain PR/evidence for the same `ned/...` branch, verify the remote branch in a clean detached worktree instead of touching a dirty primary worktree; run dependency install in the clean worktree if needed before the build; prove sitemap/redirect/noindex contracts deterministically; rerun finalize with absolute script path + explicit `PRISMATIC_REPO_ROOT`/`FINALIZE_LOCK_FILES`; remove stale `dispatch:ready`; keep Linear `In Review` while remote Cloudflare/Workers checks remain red. Detailed recipes: `finalize-task-script-bug/references/ned-gro-3999-seo-redispatch-refresh.md` and `references/ned-gro-4001-og-social-redispatch-refresh.md` (OG/social image variant: build + generated HTML meta-tag verifier; verify new Linear comment via `comments(first:50)` sorted by `createdAt` because `comments(last:N)` may omit newest comments).

HD Platform CLS/layout redispatch pitfall: if Linear already has branch/PR/live Lighthouse proof for a frontend layout task, verify the remote `ned/...` branch in a clean temp worktree, run build/flow/preview HTTP/live Lighthouse, clean Playwright/Lighthouse artifacts before finalize, rerun finalize with absolute path + explicit `PRISMATIC_REPO_ROOT`/`FINALIZE_LOCK_FILES`, then remove stale `dispatch:ready` manually. Keep the issue `In Review` while `Workers Builds: hd-platform` remains red even if Pages/live CLS proof is green. Detailed recipe: `references/ned-gro-4006-cls-redispatch-refresh.md`.
