# OKF staging-promotion workflow — when the pre-push hook is the gate

Source session: `mbgulden/sentinelitad.com` deploy pipeline standard being promoted to `mbgulden/growthwebdev-knowledge` on 2026-07-28.

## Why this reference exists

The `prismatic-staging-governance` standard defines a pre-push hook that:
- Blocks direct pushes to `main` (production is manual-only).
- Routes staging-branch pushes to `deploy-fresh` based on **the source branch name**, not the destination branch.
- Requires source branches to match one of: `feature/`, `content/`, `research/`, `jules/`, `ned/`.

Any OKF promotion to `deploy-fresh` that hasn't read this skill will hit the hook with a "doesn't match any agent prefix" rejection. This reference documents the exact flow that works.

## The flow that works

```bash
# 1. Make your changes on a feature branch. Use the agent prefix that matches you.
cd <hub-repo>
git status                      # should be clean before you start
git checkout -b feature/fred-<topic>-<date>

# 2. Make your OKF changes (new docs, index updates).
# Verify with a focused /tmp/hermes-verify-*.py script before commit.

# 3. Commit.
git add <changed paths>
git commit -m "[Fred] <summary> (#<scope>)"

# 4. Push the feature branch (this is a worker push — should always succeed).
git push origin feature/fred-<topic>-<date>
# Expect: "✅ [Prismatic Engine] Pre-push OK: fred → feature/fred-...   Files: N changed, N in-lane, 0 violations"

# 5. Promote to deploy-fresh (the staging lane) by pushing the feature branch AS deploy-fresh.
git push origin feature/fred-<topic>-<date>:deploy-fresh
# Expect: "✅ ... To https://github.com/...  <old-sha>..<new-sha>  feature/... -> deploy-fresh"

# 6. (Operator action, you) Open PR from feature branch into main on the GitHub UI.
#    OR, if already-merged-to-main is needed urgently: locally fast-forward main to deploy-fresh,
#    open the PR via the UI. (Manual per "production is manual-only" rule.)
```

## Three flows that DON'T work — and the error each gives

### ❌ `git push origin main:deploy-fresh`
```
❌ [Prismatic Engine] Branch 'main' doesn't match any agent prefix.
   Valid prefixes:
     feature/ → fred
     content/ → kai
     research/ → agy
     jules/ → jules
     ned/ → ned
```
**Why:** the hook checks the source branch name (`main`), which doesn't match any worker prefix. Production is manual-only and `main` itself is never an acceptable source for an automated promotion.

### ❌ `git push origin main:main`
```
❌ [Prismatic Engine] Push to main is BLOCKED.
   Production deployments are manual-only.
   Use deploy-fresh for staging, then merge manually.
```
**Why:** explicit guard against accidental production pushes. Merge to `main` must be a GitHub UI PR action by a human.

### ❌ `git push origin main:deploy-fresh` after a fresh checkout with no feature branch
Same as #1 — main is the source branch and the hook rejects it.

## What if the hook is missing or disabled on a repo?

The hub repo (`growthwebdev-knowledge`) has the hook installed and active as of 2026-07-28. Other OKF repos may not. Before assuming the hook blocks, check:

```bash
# From inside the repo:
cat .git/hooks/pre-push 2>&1 | head -5    # bare repo hook
cat .git/config | grep -i hooksPath      # repo-local hook override
ls -la .git/hooks/pre-push               # file-based hook
```

If no hook is present, the promotion flow is the standard git push:

```bash
git checkout main
git pull origin main
git push origin main:deploy-fresh
# Or, if main is the deployment branch:
git push origin main
```

The pre-push hook is an opt-in safety net for staged-promotion repos. Don't assume it's there; verify.

## Why the source branch matters more than the destination branch

The hook's design (per `okf/standards/prismatic-staging-governance.md`) intentionally gates on the **source** for two reasons:

1. **Audit trail.** A promotion to `deploy-fresh` triggered from `feature/fred-...` is unambiguously a fred-controlled change. If you'd accidentally promoted from `main` (which is auto-merged-from-deploy-fresh by the human integrator), the resulting deploy-fresh head wouldn't tell you who started the change.

2. **Lane collision prevention.** A `content/` source branch signals "this is a kai document change". A `research/` source branch signals "this is an agy-research update". The hook ensures staging promotions respect lane ownership before the work even enters the queue.

Memorize: **the source branch name is the proof of who you are; the destination branch name is the proof of what you want to update.** The hook enforces both, in that order.

## Edge cases

### "What if I'm not 'fred' — what prefix do I use?"

Use the prefix that matches your agent identity:
- `feature/` — fred (orchestrator)
- `content/` — kai (content)
- `research/` — agy (research / analysis)
- `jules/` — jules (review / coding)
- `ned/` — ned (infrastructure / runtime)

If you're operating as a different agent on this session, use that prefix. The hook is the same — only the prefix changes.

### "My change isn't aligned to any one agent's lane"

Pick the agent who is the operational owner of the deliverable. The branch name doesn't have to match the change content; it just has to reflect who owns the work end-to-end.

### "I have a polluted feature branch (inherited unrelated files)"

That's a different problem (handled by `references/okf-closeout-clean-pr-and-verifier-2026-07.md`). The promotion flow itself is the same — just on a clean branch.

## Companion references

- `references/okf-closeout-clean-pr-and-verifier-2026-07.md` — how to recognize and replace a polluted PR before this flow.
- `references/okf-linear-handoff-2026-07-26.md` — the OKF docs → Linear tree promotion (different flow, same source branch discipline).
- `okf/standards/prismatic-staging-governance.md` — the canonical governance standard this flow implements.

## Worked example — sentinelitad.com deploy standard (2026-07-28)

```text
$ git -C /home/ubuntu/work/growthwebdev-knowledge checkout main
$ git status
# clean

$ git diff --stat HEAD origin/deploy-fresh
# nothing local

$ git checkout -b feature/fred-cf-pages-direct-uploads-deploy-standard
Switched to a new branch 'feature/fred-cf-pages-direct-uploads-deploy-standard'

# (wrote 4 files: 2 new docs + 2 index updates)

$ python3 /tmp/hermes-verify-okf-cf-pages-deploy-2026-07-28.py
# PASS: OKF doc verification complete (ad-hoc targeted)

$ git add okf/standards/cloudflare-pages-direct-uploads-deploy.md \
          okf/standards/references/cf-pages-direct-uploads-sentinelitad-session-2026-07-28.md \
          okf/standards/index.md \
          okf/index.md

$ git commit -m "[Fred] Add CF Pages Direct Uploads deploy standard (#sentinelitad-2026-07-28) ..."
[main 4d04a4d] [Fred] Add CF Pages Direct Uploads deploy standard ...

$ git push origin feature/fred-cf-pages-direct-uploads-deploy-standard
✅ [Prismatic Engine] Pre-push OK: fred → feature/fred-cf-pages-direct-uploads-deploy-standard
   Files: 88 changed, 88 in-lane, 0 violations
 * [new branch] feature/fred-cf-pages-direct-uploads-deploy-standard -> feature/fred-cf-pages-direct-uploads-deploy-standard

$ git push origin feature/fred-cf-pages-direct-uploads-deploy-standard:deploy-fresh
✅ [Prismatic Engine] Pre-push OK: fred → feature/fred-cf-pages-direct-uploads-deploy-standard
   Files: 88 changed, 88 in-lane, 0 violations
   e47517e..2b7201f  feature/fred-cf-pages-direct-uploads-deploy-standard -> deploy-fresh
```

The new standard is now on `origin/deploy-fresh`. `main` is still 13 commits behind (includes the merge-from-deploy-fresh and the new OKF commits), waiting on manual PR to make `main` include them.

Note: the pre-push hook reported "88 changed" because it walks the full diff against the prior tip, but only 4 files were in our actual commit (the index updates + 2 new docs). The "0 violations" line is what matters — none of the 88 diff'd files violate the lane contract.
