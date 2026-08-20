---
name: worktree-hygiene-and-cleanup-safety
description: Use when auditing, cleaning, pruning, archiving, or building automation around Git worktrees/temp checkouts in Prismatic Engine or similar multi-agent repos. Covers how to preserve good/ambiguous work, avoid superseding valid changes, and build cleanup into actual tooling rather than metadata.
---

# Worktree Hygiene & Cleanup Safety

## When to use

Use this skill when Michael asks to:
Use this skill when Michael asks to:
- Audit or clean stale Git worktrees, temp directories, or agent sandboxes.
- Build or modify a worktree janitor/cleanup tool.
- Decide whether dirty/stale work can be removed.
- Prevent agents from superseding, deleting, or losing “good” work.
- Turn cleanup workflows into Prismatic Engine core CLI/API/cron behavior.
- Get a read-only "where are we at" state-of-things report across multiple repos, branches, worktrees, PRs, Linear parents, and live services before deciding whether to clean, merge, or continue.

## Core principle

Do **not** ask the agent to infer whether work is “good.” That is how valid work gets superseded or deleted.

Instead, encode this rule in tooling:

> “Good” means “not mechanically proven safe to remove.”

A cleanup tool should only auto-remove a worktree when Git evidence proves it is disposable. If evidence is ambiguous, the tool must preserve it and mark it for manual review.

Preservation alone is not enough. The durable next layer is **proof pressure**: useful work should carry portable evidence that makes it legible, promotable, or intentionally disposable. Missing proof must create a `proof_gaps`/`preserve-needs-proof` state, not a delete signal.

## Required safety gates

Automatic removal is allowed only when all gates pass:

1. Path is **not** the canonical checkout.
2. Worktree path exists or is only missing metadata eligible for prune.
3. No unmerged/conflicted files.
4. `git status --short` is clean.
5. `HEAD` is already an ancestor of the configured base ref.
6. Worktree is older than the stale threshold.
7. The removal target is listed in a manifest generated before mutation.

If any gate fails, classify as `keep` or `manual-review`, not `safe-remove`.

## Dirty work policy

Dirty work must be protected by code, not convention.

When the goal is to checkpoint dirty live-ish work, do not clean first and do not `git add .`. Create/switch to an agent-owned branch, inspect tracked diffs and untracked sizes, exclude secret-bearing backups/runtime state/generated caches, stage only intentional files, run `git diff --cached --check` plus a staged secret scan, verify the behavior, then commit. If a lane guard blocks pushing a mixed-lane checkpoint, preserve it with a local `git bundle` and report the blocked paths instead of forcing the push or losing the checkpoint.

- Cron must **not** pass dirty-delete flags.
- Ordinary `--apply` must not delete dirty work.
- `--include-dirty` may only include dirty worktrees in the manifest and archive them.
- Actual dirty deletion requires a second deliberate signal: an exact confirmation token emitted in the manifest, e.g. `DELETE-DIRTY-WORKTREES:<base-ref>`.
- Dirty/conflicted work should be archived before any permitted destructive operation.

## Manifest contract

Before mutation, write a machine-readable manifest containing:

- repo path and base ref,
- created timestamp,
- dry-run/apply mode,
- dirty confirmation token,
- policy rules,
- every removable worktree,
- every kept/manual-review worktree,
- safety class and safety reasons for each item.

Prefer explicit classes:

- `safe-remove`
- `keep`
- `manual-review`
- `safe-prune-metadata`

## Archive contract

For dirty or ambiguous work, save recoverable evidence before removal/approval:

- `head.txt`
- `branch.txt`
- `status.txt`
- `diff.patch`
- `staged.patch`
- `untracked-files.txt`
- `untracked.tar.gz` for bounded-size untracked files

Never report a cleanup as complete without naming where archives/manifests landed.

## PE core integration pattern

When Michael asks for cleanup to be “actual tooling,” implement in Prismatic Engine core surfaces, not just session notes:

- core module for behavior, e.g. `prismatic/worktree_janitor.py`,
- CLI verbs, e.g. `prismatic worktrees ...`,
- authenticated API route, e.g. `GET /api/v1/worktrees`, `POST /api/v1/worktrees/janitor`,
- scheduler-neutral cron manifest, e.g. `prismatic crons emit/install`,
- docs under an in-lane docs path,
- focused tests proving preservation behavior.

Cron should default to silent, safe cleanup only. It should not delete dirty or ambiguous work.

## Usefulness/proof layer

When the user asks how to prove agent work is useful/indispensable, do **not** make cleanup more aggressive. Add a portable proof/provenance layer that travels with each worktree and feeds CLI/API/UI decisions.

Recommended proof files:

- `.prismatic/worktree-proof.json`
- `prismatic-worktree-proof.json`
- `.worktree-proof.json`

Recommended proof fields:

- schema/version, issue/task id, summary, agent, created_at,
- verdict: `useful`, `indispensable`, `promote`, `blocked`, `broken`, `superseded`,
- verification evidence, artifacts, and handoff notes.

Expose proof state on worktree records with fields like:

- `value_class`: `indispensable`, `preserve-needs-proof`, `broken-review`, `disposable`, `unknown`,
- `value_score`,
- `value_signals`,
- `proof_gaps`,
- `promotion_recommendation`.

Critical rule: missing documentation/proof is a **proof gap**, not a trash signal. It should preserve the work and route it to proof capture or promotion review.

## Promotion pipeline pattern

The durable solution is a three-layer system:

1. **Safety gates** — prevent accidental deletion.
2. **Proof/provenance** — make agent work legible and portable.
3. **Promotion pipeline** — route each worktree by evidence:
   - `indispensable`/`promote` → open/update PR or Linear comment,
   - `preserve-needs-proof` → assign proof-capture/review,
   - `blocked` → route to the correct agent/human lane,
   - `broken-review` → require explicit disposal review,
   - `disposable` → safe janitor target.

This avoids the lesser solution of hoarding every ambiguous worktree forever while still preventing undocumented useful work from being trashed.

## Verification expectations

Focused verification should prove behavior, not just imports:

- dirty work survives `apply` without token,
- dirty deletion occurs only with the exact token,
- clean committed work ahead of base is kept,
- conflicted work is never planned for removal,
- clean+merged+stale work is removable,
- manifest exists before mutation,
- CLI/API use the same safety gates as the core module,
- undocumented dirty/active work becomes `preserve-needs-proof`, not disposable,
- proof-backed useful work becomes `indispensable`/`promote`,
- proof template CLI/API returns portable schema fields.

If the implementation worktree is removed or Hermes cannot see canonical verification, create a `/tmp/hermes-verify-*` script that checks out current `origin/main` into a temporary worktree, exercises the merged behavior, removes the verifier script, and reports the result as **ad-hoc verification**, not full-suite green.

## State-of-things read-only reconnaissance pattern

When Michael asks a broad project question like "where are we at for X?" the goal is not to clean up. The goal is to **triangulate Git + GitHub + Linear + live services into one consistent picture** before deciding what to do. This read-only pass is the prerequisite for any subsequent cleanup, merge-train, or PR-routing work and frequently *replaces* it (the answer turns out to be "document the drift, don't act yet").

### Required probes (parallelize them in one tool batch)

1. **Git state per repo** (only repos relevant to the project, filtered by name/remote):
   - `git rev-parse --abbrev-ref HEAD` and `git log -1 --format='%h %ci %s'`
   - `git status --short --branch` — captures working-tree dirtiness
   - `git worktree list --porcelain` — captures cross-worktree state including detached HEADs and `/tmp` scratch worktrees
   - `git rev-list --left-right --count <base1>...<base2>` — quantifies divergence
   - `git branch -r --merged <base>` — flags prunable remote branches
   - `du -sh <repo>` vs `git count-objects -vH` — separates working-file bloat from git object bloat

2. **GitHub PR state** (works without `gh` auth via the REST API):
   - `GET https://api.github.com/repos/<owner>/<repo>/pulls?state=open&per_page=100`
   - Bucket by `base.ref`, `mergeable`, head/branch date
   - Cross-check each PR's head branch against local branches to find PRs whose branches no longer exist locally
   - The REST API works read-only even when `gh auth status` reports not logged in; only mutations need auth

3. **Linear state**:
   - GraphQL `issues(first:100, orderBy:updatedAt)` paginated, filtered by project/labels/title regex
   - For each parent epic, fetch children + last 3 comments to capture finalization reports
   - Classify states: Done vs Todo vs Backlog vs In Progress
   - **Explicitly flag parents that are Done while required children remain Todo/Backlog** — that is a real drift class, not a status quirk

4. **Live services**:
   - `systemctl show <svc>.service -p ActiveState -p SubState -p ExecStart` for each project service
   - `ss -ltnp` to verify what's actually listening vs what unit files claim
   - `curl -sS -o /dev/null -w 'HTTP=%{http_code}\n'` against each public URL (prod, staging, key routes, optional `/health`)
   - Note: `/health` returning 404 is a real signal, not noise — it means the route was never wired up

5. **Documentation drift**:
   - List recent `docs/operations/*.md` and `docs/vision/*.md` files
   - Read the launch audit / green-state rubric and check whether it still matches the actual Linear/PR state. If it doesn't, that's a doc-drift signal worth reporting before any cleanup.

### Output shape

Report the four-way state in one table per surface:

```md
| Repo/Branch | HEAD | Status | PRs | Linear parents | Live |
|---|---|---|---|---|---|
```

Then a separate **drift table** calling out where the four sources disagree. The user's "where are we at" question is really "where do these sources disagree?" — answering that is the value.

### Pitfalls

- Do not start mutating anything during the reconnaissance. The question is usually about state, not action.
- Do not trust a parent epic's `state.name` alone. Verify its children. Parents get auto-finalized or hand-moved without their children being done.
- Do not trust a `Done` Linear state without checking the linked PR — the PR may still be open, conflicted, or never merged.
- Do not trust a green audit doc without re-reading it against current Linear and PR state. Audits go stale fast under multi-agent work.
- Do not assume `gh auth status` failing means GitHub is unreachable. The REST API works read-only without auth.
- Do not assume a unit file's `ExecStart` is what's currently running. `ss -ltnp` is the ground truth.
- Do not report "clean working tree" without checking `git worktree list --porcelain` for other worktrees attached to the same repo. Dirt can live in a sibling checkout.
- Quantify before recommending. "There are 29 open PRs and 14 detached worktrees" beats "the PR backlog is large."

## Pitfalls

- Do not equate “dirty” with “bad.” Dirty often means valuable unfinished work.
- Do not equate “old” with “safe.” Old committed work ahead of base is still work.
- Do not equate “missing documentation” with “disposable.” Missing documentation should create a proof gap and preserve/route the work.
- Do not accept “tests fail” as proof of trash. Useful unfinished work often fails tests; require explicit broken/superseded proof before disposal.
- Do not let cron pass `--include-dirty` or equivalent destructive dirty flags.
- Do not remove worktrees before archiving dirty/untracked state.
- When generating manifests/reports from shell, use single-quoted heredocs (`<<'EOF'`) or write with Python triple-quoted strings that do not pass through shell expansion. Markdown backticks inside an unquoted heredoc can execute command substitution; in a cleanup script that can accidentally run destructive examples like `git clean -fdx`.
- When creating or editing GitHub PR bodies from shell, avoid inline double-quoted Markdown containing backticks or command examples. Write the body to a temp file with `write_file`/single-quoted heredoc and use `gh pr create --body-file` or `gh api -X PATCH ... -F body=@file`; otherwise the shell can execute backticked snippets and corrupt the PR body.
- Do not build only metadata or docs when Michael asked for actual tooling.
- Do not leave cleanup worktrees or locks behind after merging the cleanup tool.
- Do not bury Michael in raw verifier logs when explaining safety. Translate to practical trust/decision language: what is preserved, what is promotable, what needs proof, and what requires explicit approval.
- **Filenames containing literal newlines bypass `.gitignore` globs.** A buggy script that creates files like `production_database.db\n` produces paths that `ls` shows as ordinary, that shell commands cannot address directly, and that `*.db` ignores do not match (so the file appears as untracked `??`). When a flagged sensitive file does not respond to glob ignores, suspect a literal newline or other control character in the filename. Stat-only inspection (`os.listdir` + `os.lstat` + SHA-256) is the safe resolution path; never `cat`/`open` for reading. The empty-file canonical SHA-256 (`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) is a sentinel for "this file was truly zero bytes." Patch `.gitignore` with a defensive comment, never a broad new glob. See `references/2026-07-newline-filename-gitignore-bypass.md` for the full pattern.

## References

- `references/2026-07-hde-state-of-things-audit.md` — multi-repo + Linear + GitHub + services read-only audit pattern; surfaces parent-done/children-incomplete drift and four-way state disagreement without mutating anything.
- `references/2026-07-prismatic-worktree-janitor-safety.md` — session notes from hardening the PE worktree janitor after Michael challenged how to guarantee good work is not deleted.
- `references/2026-07-prismatic-worktree-usefulness-proof.md` — session notes for the proof/provenance layer that makes preserved agent work legible, promotable, or explicitly reviewable.
- `references/2026-07-hde-workspace-branch-cleanup.md` — HDE-specific cleanup pattern for live-ish app workspaces: inventory, archive secret/runtime/generator clutter, prune only local superseded branches, document a workflow map, and verify cleanup reports with `/tmp/hermes-verify-*`.
- `references/2026-07-hde-branch-worktree-cleanup-followup.md` — HDE branch/worktree cleanup follow-up: dry-run remote branch deletion, prove merge ancestry before deleting, preserve dirty/unmerged branches, archive staging runtime backups, and verify remote branches are gone.
- `references/2026-07-hde-repo-hygiene-cleanup-incident.md` — HDE cleanup follow-up capturing the unquoted-heredoc/backtick foot-gun, safe archive targets, recovery steps, and verification shape after restoring PWP/theme proof files.
- `references/2026-07-hde-golden-path-lane-guard-bundle.md` — HDE golden-path continuation pattern: split remaining dirty work into local checkpoints, verify, create a recoverable `git bundle` when Prismatic lane guard blocks push, deploy staging safely, and report GitHub governance as the remaining gate.
- `references/2026-07-hde-lane-widening-and-pr-governance.md` — follow-up pattern when Michael explicitly authorizes a temporary lane expansion: patch `PRISMATIC_ENGINE.yaml`, dry-run the pre-push hook, commit the governance change, push, open/repair/merge the PR, and redeploy the alias if merge automation serves stale preview content.
- `references/2026-07-hde-emergency-staging-rollback.md` — emergency rollback pattern for recent HDE staging regressions: identify recent bad merges, revert them on a separate Ned branch without rewriting history, prove the tree matches the known-good state, merge the rollback PR, then verify and restore the actual live staging `dist` if the hostname is served locally rather than from the fresh Cloudflare preview.
- `references/2026-07-hde-email-session-branch-worktree-cleanup.md` — HDE cleanup pattern after an active feature/email session: archive-first cleanup, remove clean non-canonical worktrees, preserve dirty/current/local-only work, delete only mechanically safe local branch copies, handle branch-deletion failures caused by late-discovered worktrees, and verify with `/tmp/hermes-verify-*`.
- `references/2026-07-hde-production-promotion-clean-worktree.md` — HDE production-promotion pattern when staging is verified but production/staging checkouts are dirty: create a clean worktree from `deploy-fresh`, cherry-pick only intended commits, move service templates into Ned's lane (`scripts/systemd/`), run a `/tmp/hermes-verify-*` production-push verifier plus `npm run build`, then push/PR without deploying.
- `references/2026-07-beyondsaas-branch-worktree-cleanup.md` — BeyondSaaS cleanup pattern after a dirty Cloudflare Pages deployment: archive dirty state, secret-scan untracked files, remove only duplicate/cache clutter, checkpoint live-ish untracked assets/source, delete only merged local branches, and preserve ahead branches for extraction/PR review.
- `references/2026-07-newline-filename-gitignore-bypass.md` — pattern for resolving a flagged sensitive file whose name contains a literal newline character (or other control characters) that bypasses `.gitignore` globs: stat-only inspection, empty-file SHA-256 sentinel, deletion/move receipt outside the tracked tree, defensive `.gitignore` comment (no new globs), and how to keep the canonical repo clean afterward.
