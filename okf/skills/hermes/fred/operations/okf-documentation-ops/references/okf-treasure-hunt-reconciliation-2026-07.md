# OKF Treasure-Hunt and Reconciliation Pattern

Use this pattern when a project appears to have missing OKF/docs, but branch names, backup refs, archived worktrees, or hub records suggest docs were stranded rather than absent.

## Trigger signals

- Current project branch has no first-class `okf/` tree, but older indexes point to one.
- User says variants of “make a map to where it exists” or “don’t stop at not found.”
- Branches include names like `*okf*`, `*docs*`, `*knowledge*`, `*closeout*`, `backup/*full-okf*`, `tier-5a-okf-pilot`, `GRO-2445-okf-drive-drift*`, or `GRO-3520-local-okf-full`.
- Archived worktree directories contain `*/okf` trees.

## Required behavior

1. **Inventory before editing.** Use `git branch -a`, `git worktree list --porcelain`, `git ls-tree -r --name-only <ref>`, and local `find ... -type d -name okf` to discover sources. Prefer read-only `git show`/`git ls-tree`; do not check out polluted historical branches in the main worktree.
2. **Preserve provenance.** For every candidate, capture repo, branch/ref, head SHA, path, title/frontmatter, content hash, current-base existence, and recommendation.
3. **Use a scratch workspace.** Put manifests under `/tmp/<project>-okf-treasure-hunt/{manifests,reports,extracts}`.
4. **Deduplicate.** Group exact content hashes first; then group concept families by title/path/Linear issue.
5. **Classify.** Use: `canonical-current`, `canonical-stale`, `hidden-useful`, `hidden-historical`, `duplicate-superseded`, `unsafe/private`, `noise`.
6. **Land a report before promotion.** First durable PR should usually be an indexed OKF report summarizing the inventory, not a giant promotion PR.
7. **Promote in batches.** Use clean hub worktrees from `origin/main`; never merge historical branches directly.
8. **Keep project breadcrumbs current.** If the project repo lacks `okf/`, add/update a repo-local map such as `docs/okf-map.md` and link it from README.

## Manifest outputs

Typical outputs:

```text
/tmp/<project>-okf-treasure-hunt/manifests/summary.json
/tmp/<project>-okf-treasure-hunt/manifests/<repo>-branches.json
/tmp/<project>-okf-treasure-hunt/manifests/local-okf-directories.json
/tmp/<project>-okf-treasure-hunt/manifests/candidate-docs.json
/tmp/<project>-okf-treasure-hunt/manifests/candidate-docs.csv
/tmp/<project>-okf-treasure-hunt/manifests/duplicate-content-groups.json
/tmp/<project>-okf-treasure-hunt/manifests/high-value-candidates.json
/tmp/<project>-okf-treasure-hunt/reports/<project>-okf-treasure-map.md
```

## Report sections

Minimum report structure:

1. Executive summary.
2. Source inventory counts.
3. Highest-signal hidden branches/worktrees.
4. Top high-value hidden docs.
5. Duplicate exact-content groups.
6. Local OKF directories with project signal.
7. Initial classification read.
8. Recommended next batches.
9. Risks/blockers.
10. Manifest file list.
11. Verification boundary.

## Verification

Use a fresh `/tmp/hermes-verify-*` script. Check:

- manifests exist;
- JSON parses;
- CSV row count matches candidate JSON;
- expected high-signal branches are present;
- report contains required sections and branch markers;
- project breadcrumb map exists when relevant;
- temp verifier is cleaned up.

Report as:

```text
Ad hoc targeted OKF verification: PASS
Scope: OKF treasure-hunt inventory / promotion batch only — not full docs-suite green.
```

## Pitfalls

- Do not treat a missing current `okf/` tree as proof of no documentation.
- Do not fetch all remotes blindly if archived sandbox remotes are broken; fetch `origin` and inspect existing refs.
- Do not run expensive per-file `git log` over thousands of files in the first pass; start with branch/file counts and only extract high-value candidates.
- Do not delete backup branches/worktrees until the inventory and high-value docs are indexed or backed up.
