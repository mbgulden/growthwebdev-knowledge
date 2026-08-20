# AGY post-merge immutable release closeout

Session-derived checklist from a cap-1 AGY self-build repair where multiple exact-head reviews returned `REPAIR` before the final merge.

## Trigger

Use this reference when a focused AGY/Prismatic repair PR has iterative review findings, exact-head CI, conditional merge authorization, and a required post-merge release proof before any production or Linear closeout.

## Exact-head review discipline

1. Preserve each candidate/repair commit as its own reviewable artifact.
2. Treat every independent `REPAIR` verdict as invalidating all prior `CLEAN`, CI, PR-body, and local proof claims.
3. Repair the same issue and same candidate lineage; do not launch the next issue or raise cap because an earlier head was green.
4. Re-run refreshed local proof and GitHub CI on the new exact head.
5. Dispatch final independent review only after the new exact head and checks are known; no merge unless the latest exact-head review is `CLEAN`.

## Merge preflight

Before merging a conditionally authorized focused PR:

- Re-read PR head SHA, mergeability, and check conclusions from GitHub.
- Confirm the latest head equals the reviewed commit.
- Confirm checks are green on that exact head.
- Confirm PR body marks stale evidence as stale and names the current proof boundary.
- Confirm merge authorization covers merge only; do not infer production deploy/repoint/restart or Linear closeout.

## Standalone immutable release proof

After GitHub creates a merge commit:

1. Read the actual merge SHA from GitHub/PR output.
2. Create a release checkout under `.prismatic/releases/<repo>-<merge-prefix>` pinned to the merge SHA.
3. Ensure the release is standalone:
   - detached or pinned to the merge SHA;
   - clean worktree;
   - no `.git/objects/info/alternates`;
   - no dependence on the mutable repair checkout.
4. If a local clone cannot see the new GitHub merge object, do not force a worktree from the repair checkout. Fetch the exact merge object or clone/fetch from GitHub `main` directly, then pin to the merge SHA.
5. Run post-merge proof from the release checkout, not the repair worktree.

Suggested proof classes:

```text
COMPILE=PASS
SCOPED_RUFF=PASS
SCOPED_FORMAT=PASS
FOCUSED=PASS
CANONICAL=PASS
SOURCE_EDGE_PROBES=<n>/<n> PASS
BUILD=PASS
WHEEL_INSTALL=PASS
INSTALL_SMOKE=PASS
MARKER=<issue>_POSTMERGE_IMMUTABLE_RELEASE_OK
```

## Closeout boundaries

Keep these separate in reports, handoff, control state, and Linear comments:

- `PR merged`
- `post-merge immutable release verified`
- `production files overlaid / service restarted`
- `Linear state/label closeout`
- `cap increase / generic dispatch resume`
- `next issue launch`
- `clean-room portability`

If only merge was authorized, post evidence to Linear/PR but leave issue state and labels unchanged until explicit authorization. Phrase the boundary directly: “Linear closeout and production repoint remain pending explicit authorization.”

## Common overclaim traps

- Calling prior CI green after a new repair commit exists.
- Treating a safety-filtered or blocked review as clean.
- Treating source-checkout proof as release proof.
- Treating wheel install smoke as clean-room portability.
- Reusing a mutable repair checkout as the deployed release artifact.
- Closing Linear Done or removing `dispatch:paused` because the PR merged, without explicit closeout authorization.
