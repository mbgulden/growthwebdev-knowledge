---
name: isolated-pr-from-entangled-branch
description: Land verified changes as a clean single-commit PR to main when they currently exist only as uncommitted working-tree changes on an entangled long-lived agent branch (N commits ahead). Worktree isolation, exact-path staging, real-remote detection, post-creation PR verification, CI-red root-cause via sibling PRs.
tags: [git, pr, worktree, github, staging, cleanup]
related_skills: [branch-deletion-approval, handoff-packet-independent-review, prismatic-evidence-handling, linear-handoff-build-out]
---

# Isolated PR from an Entangled Branch

Verified work is sitting as **uncommitted** changes in an agent's long-lived staging worktree, on a branch **N commits ahead of main** (unrelated work). Committing there and PR'ing would drag all N commits into main. Instead: land exactly the verified paths as one clean commit on a fresh branch off the real main.

## When to use
- A review/handoff says "commit + PR these N paths" but the paths are uncommitted on a branch with `git rev-list --count <remote>/main..HEAD` > 0, and not all of that delta is yours.
- The source worktree is dirty with the peer's unrelated changes (38 files, etc.).
- The owner approved the clean path ("branch from main, just the N paths").

## Pre-checks (all before branching)
1. **Identify the REAL remote.** `git remote -v` — `origin` may be a **local path remote** (a sibling worktree), not the upstream host. If so: `git remote add github https://github.com/<owner>/<repo>.git` and do all upstream work against `github`. A local-path `origin/main` can also be **stale** (observed 2026-08-20: local `origin/main` 4433ea6 vs GitHub main 497ae45 — different trees).
2. **Conflict-scan each path against upstream main.** `git cat-file -e github/main:<path>`. Absent on main ⇒ the PR adds it as a full new file (content = the verified build; fine, but say so in the PR body so reviewers don't mistake a full-file diff for a world rebase). Present ⇒ eyeball that the diff is only your change.
3. **Know the dirtiness.** `git status --short | wc -l` in the source worktree. If > N, you must stage explicit paths — never `-A`/`-a`.
4. **Establish commit identity.** `git config user.name` may be empty. Find the repo's established agent identity: `git log --all --grep='\[<Agent>\]' -1 --format='%an <%ae>'`, then pass `-c user.name=... -c user.email=...` on the commit command. Don't set global config.
5. **`gh auth status`** first (auth lives under the profile home). If not logged in, stop and ask — don't start an interactive login mid-task.

## Workflow
1. **Isolate in a worktree.** `git worktree add /home/ubuntu/work/<topic>-branch -b feature/<ISSUE>-<slug> github/main` (after `git fetch github main`). Never branch from inside the peer's dirty worktree — you'd inherit their dirty files and one `git add` accident away from shipping their WIP.
2. **Copy exactly the N paths** from the source worktree (`mkdir -p` parents first), then md5 both sides per path.
3. **Re-verify in the NEW worktree** — don't trust the copy: `py_compile` (or equivalent), run the tests, grep for the key symbols. Gotcha: tests with hard-coded absolute paths may actually exercise the SOURCE tree, not the copy — acceptable only because md5s are identical, and worth a line in the PR body.
4. **Stage exactly the paths** (`git add p1 p2 ...`), confirm `git diff --cached --name-only | wc -l` == N, commit with the `[Agent] … (#ISSUE)` prefix via **`-F <msgfile>`** (write the message file first). Apostrophes/em-dashes in `-m` strings break `bash -c` quoting (observed: "unexpected EOF while looking for matching `''`").
5. **Push to the real remote**, `gh pr create --repo <owner>/<repo> --base main --head feature/... --body-file <body.md>`.
6. **Verify the PR after creation** — success output is self-report: `gh pr view <n> --json state,mergeable,baseRefName,files` must show OPEN, MERGEABLE, base main, and the exact expected file set.
7. **Root-cause red CI before reporting it.** `gh pr checks <n>` — if a check fails, neither wave it away nor claim it as yours. Prove provenance two ways: (a) run the same check on sibling open PRs (`gh pr checks <sibling-pr>` — a check failing identically on 3 unrelated open PRs is pre-existing infra red), and (b) grep build config for your paths (nothing build-related referencing them ⇒ they can't be the cause). Report: "CI red is pre-existing — fails identically on PRs X/Y/Z; my paths are not build inputs" — with the evidence inline, not as an assertion.
8. **Do NOT merge** if merge is the owner's publish/staging-governor gate, and **do NOT delete the worktree/branch** — both need explicit approval (`branch-deletion-approval`). Leave the worktree in place and say so in the report.

## Pitfalls
- **`origin` can be a lie.** On this host, some repos point `origin` at a local sibling worktree (e.g. `hd-platform-staging`'s origin = `/home/ubuntu/work/hd-platform`). Every GitHub-facing op (fetch main, push, PR base) goes through the explicitly-added `github` remote.
- **Stale local main ≠ upstream main.** Always `git fetch github main` and branch off `github/main`, never a possibly-stale local ref.
- **`git add -A` / `commit -a` in a dirty peer worktree is a release incident waiting to happen.** Explicit paths only; the staged count must equal the expected count exactly.
- **Commit messages through the shell:** `-F file`, always, for multi-line or punctuation-bearing messages.
- **A full-file diff is expected when the path is new to main** — but unexplained, it looks like a rebase accident. One line in the PR body ("this file did not exist on main before; content is byte-identical to the live build `<hash>`") defuses it.
- **Red check ≠ your fault AND red check ≠ ignore.** Do the sibling-PR + build-input analysis and report the verdict with evidence.
- **Don't cherry-pick when there's nothing to pick.** If the N paths are UNCOMMITTED (not commits), there are no commits to cherry-pick — the operation is "branch from main + copy the paths + one commit." (A tempting recipe from other contexts fails here.)

## Verification
- PR exists: `gh pr view <n>` → OPEN / MERGEABLE / base main / exactly N files.
- Commit stat shows exactly N files; worktree is clean after commit (`git status --short` empty).
- Worktree copies md5-identical to the source worktree (and to the live build, if that's the claim).
- CI verdict is root-caused (sibling comparison + build-input grep), cited by PR number in the report.
- State file / handoff records the PR number, commit sha, branch, base sha, and "not merged (owner gate)".
