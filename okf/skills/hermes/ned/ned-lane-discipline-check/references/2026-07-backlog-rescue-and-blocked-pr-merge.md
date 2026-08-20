# 2026-07 backlog rescue + blocked PR merge lessons

## Darius-style stale PR rescue pattern

When a repo has a large stale PR backlog, especially branches targeting an unrelated-history base:

1. Inventory open PRs first: base/head, mergeability, changed files, status checks, branch lineage.
2. Do **not** merge broad stale PRs directly when diffs show mass deletions of assets/configs or unrelated-history ancestry.
3. Extract safe artifacts into new clean lineage branches by lane:
   - `agy/` for docs/assets/design/reference media.
   - `ned/` for scripts/tools/infra cleanup.
   - Existing feature branch only when preserving a verified feature asset already tied to that feature.
4. Add a manifest mapping rescued files back to source PR/branch when rescuing more than a couple files.
5. Verify each rescue PR independently before merge; for web repos include Cloudflare/Pages checks when present.
6. After safe rescue PRs merge, comment on stale unsafe PRs and close them so they cannot be accidentally merged later.
7. Final verification should include: open PR count, merged rescue PR links, local clean status, and relevant test/check output.

## Lane guard pitfall

If a rescue branch mixes lanes, Prismatic pre-push rejects it. Split mixed rescue work instead of bypassing:

- Docs/reference media under AGY/docs lane.
- Tools/scripts under Ned tooling lane.
- Move root-level report files under an allowed directory such as `docs/rescued-open-prs/` when appropriate.

## Blocked issue + PR merge auto-completion pitfall

GitHub/Linear can auto-move an issue to Done when a PR title/body references the issue. If the merged PR implements only a safe detector, wrapper, dry-run, or partial utility but acceptance criteria remain externally blocked:

1. Merge the safe PR only after tests/checks pass.
2. Post a Linear comment with exact verification and the remaining blocker.
3. Check Linear state after merge.
4. If auto-moved to Done incorrectly, move it back to Todo/In Progress and comment why.
5. Keep `agent:needs-human-review` when the remaining acceptance criterion depends on missing external CLI/API capability.

Example from GRO-3571: PR #182 merged the safe Jules stalled-session purge utility, but actual purge remained blocked because installed `jules` exposed only `remote list`, `remote new`, and `remote pull`; no delete/cancel command existed. The issue had to be moved back from Done to Todo after auto-completion.

## Repo bloat cleanup pattern

For asset-heavy repos, distinguish actionable local bloat from legitimate reachable asset history:

- Check `.git` size, `.git/lfs`, pack sizes, and `git count-objects -vH`.
- Prefer safe local cleanup first: `git lfs prune`, `git reflog expire --expire=now --expire-unreachable=now --all`, then `git gc --prune=now`.
- Do not rewrite remote history just to shrink reachable game/media assets unless explicitly approved.
- If watchdog thresholds were too naive, update them to alert on actionable regression rather than permanent expected baseline.
