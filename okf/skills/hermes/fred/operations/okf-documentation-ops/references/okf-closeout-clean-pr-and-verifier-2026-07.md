# OKF closeout clean PR and verifier pattern — 2026-07

## Context

A session produced durable OKF records for HDE Stripe staging launch, HDE staging-governance repair, OpenHumanDesignMCP release hardening, and two Hermes cron alert incidents. The first OKF PR was accidentally created from an old Ned OKF branch and therefore showed ~100 inherited audit/plugin files even though the intended commit touched only the closeout bundle.

## Durable pattern

1. **Write class-level OKF records.**
   - HDE launch closeout: project report with commits, branch readback, verification scope, Stripe test-account proof, and remaining hosted-launch proof.
   - Staging governance: standard for Fred-only staging promotion and repo-local hook precedence.
   - OpenHumanDesignMCP closeout: project report for Dependabot/Ned/Fred handoff PR cleanup.
   - Cron alert output: standard plus incident reports for post-publish test debris and AGY scratchpad leakage.

2. **Patch indexes in the same change.**
   - `okf/index.md` for current governance/project closeouts.
   - `okf/projects/index.md` for project index links.
   - `okf/standards/index.md` for standards.
   - `okf/reports/index.md` for incident reports.

3. **Verify OKF structure with a tempfile script.**
   Use `/tmp/hermes-verify-*.py` to check:
   - frontmatter exists and includes required fields,
   - `resource` and `git_path` match the file path,
   - all local Markdown links resolve,
   - new docs are reachable from indexes,
   - evidence markers are present (`c247293`, `1083287`, job IDs, `37 passed`, `10 pages built`, etc.).

4. **If the PR is polluted, replace it.**
   - Inspect `gh pr view <n> --json files` or equivalent.
   - If it includes unrelated inherited files, close it as superseded.
   - Create a clean worktree from `origin/main`:
     ```bash
     git fetch origin
     git worktree add -B feature/fred-okf-<topic>-clean-YYYYMMDD /tmp/<clean-worktree> origin/main
     ```
   - Copy only intended OKF docs into the clean worktree.
   - Reapply targeted index edits against the actual `origin/main` index text, not stale local markers.
   - Re-run the verifier on the clean worktree.
   - Commit/push/open/merge the clean PR.

5. **Post-merge readback.**
   - Verify PR state is `MERGED` and `origin/main` points at the merge commit.
   - Run a post-merge verifier against the merged worktree or a fresh clone of `origin/main`.
   - For guard messages that name one changed file, create a fresh verifier scoped to that path and clone/read `origin/main` so old dirty worktrees cannot contaminate the result.
   - Clean the temp worktree and `/tmp/hermes-verify-*` script.

## Pitfalls found

- A small local commit can still create a polluted PR if the branch base is old. Always inspect PR file count before merging docs.
- Do not link to a standard that exists only in a dirty/unmerged local worktree. Mention it as pending or wait until it is on `main`.
- Private bundle links should use durable repo URLs unless the target exists inside the hub repo.
- Guard-requested verification may repeat. Treat each request as requiring a fresh `/tmp/hermes-verify-*` script and summarize as ad hoc targeted verification.
