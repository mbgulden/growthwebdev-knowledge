# Safe GitHub rescue checklist

Use this when cleaning up noisy/stale agent PRs and rescuing useful work without merging dangerous branch history.

## Preflight
- [ ] Fetch current remote refs.
- [ ] Identify the real operational base (`origin/master`, `origin/deploy-fresh`, etc.); do not assume `main`.
- [ ] Confirm safe-push guard is installed or active.
- [ ] List open PRs and note head/base branches.
- [ ] For each stale PR, compare against current operational base, not only the PR's declared base.

## Triage each PR
- [ ] Is the PR from unrelated history?
- [ ] Does its diff include mass deletion of assets/configs?
- [ ] Are there safe standalone artifacts to rescue? Examples: docs, reference media, small tools, intentionally generated assets.
- [ ] Are broad code refactors already superseded by current master?

## Rescue safely
- [ ] Create a new branch from current `origin/<base>`.
- [ ] Copy only selected safe paths from source branches using `git checkout origin/<source> -- <path>` or `git show`.
- [ ] Split branches by lane (`agy/...` for docs/assets, `ned/...` for tools/scripts/code lanes as allowed).
- [ ] Add a manifest mapping rescued path → original path/source PR/source branch.
- [ ] Do not merge stale PR branches directly.

## Verify
- [ ] Run syntax/build checks relevant to the repo.
- [ ] Validate JSON or generated docs if present.
- [ ] For binary assets, verify dimensions/mode/alpha and preserve originals first.
- [ ] Push only matching branch name → same remote branch.
- [ ] Wait for required GitHub/Cloudflare checks.

## Close stale PRs
- [ ] After rescue PRs are merged, comment on each stale PR with what was rescued and why direct merge was unsafe.
- [ ] Close the stale PRs so they cannot be accidentally merged later.
- [ ] Verify open PR count is zero or expected.
