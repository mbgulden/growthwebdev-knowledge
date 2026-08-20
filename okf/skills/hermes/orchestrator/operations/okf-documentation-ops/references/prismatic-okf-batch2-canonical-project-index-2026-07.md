# Prismatic OKF Batch 2 — canonical project index promotion pattern

Use this reference when a treasure-hunt/reconciliation phase has already inventoried hidden OKF/docs and the next task is to promote **current canonical project records** without merging polluted historical branches.

## Trigger

After an OKF treasure map exists with candidate manifests, promote a small Batch 2 into the hub:

- one canonical project index;
- a small set of current synthesized records;
- compatibility/index pointers;
- provenance preserved;
- historical/archive/noise families queued, not blindly copied;
- no cleanup/deletion yet.

## Inputs

Expected manifest workspace:

```text
/tmp/prismatic-okf-treasure-hunt/manifests/
```

Useful files:

```text
priority-candidate-docs.json
priority-concept-families.json
priority-exact-duplicate-groups.json
phase2-6-summary.json
```

Create a Batch 2 source-selection manifest before writing docs:

```text
batch2-selected-canonical-records.json
```

Suggested selection schema:

```json
{
  "family": "Governance dashboard",
  "target_path": "okf/projects/prismatic-engine/governance-dashboard-history.md",
  "promotion_mode": "synthesize",
  "selected_sources": [
    {
      "source_repo": "prismatic-engine",
      "source_branch": "backup/gro-3515-full-okf-blocked",
      "source_head": "...",
      "path": "okf/...md",
      "content_sha256": "...",
      "classification": "hidden-useful",
      "recommendation": "promote or merge"
    }
  ],
  "duplicate_group_refs": [],
  "notes": []
}
```

## Clean worktree pattern

Use a clean hub worktree; do not edit the dirty primary checkout:

```bash
cd /home/ubuntu/work/growthwebdev-knowledge
git fetch origin --quiet
rm -rf /tmp/okf-prismatic-project-index
git worktree add /tmp/okf-prismatic-project-index origin/main
cd /tmp/okf-prismatic-project-index
git switch -c feature/fred-prismatic-okf-project-index
```

## Batch shape that worked

For Prismatic, Batch 2 landed:

```text
okf/projects/prismatic-engine/index.md
okf/projects/prismatic-engine/tier-7-journey.md
okf/projects/prismatic-engine/tier-7-architecture.md
okf/projects/prismatic-engine/dispatcher-incident-history.md
okf/projects/prismatic-engine/governance-dashboard-history.md
okf/projects/prismatic-engine/okf-drift-and-recovery-history.md
okf/projects/prismatic-engine.md
okf/projects/index.md
okf/index.md
```

`okf/projects/prismatic-engine.md` became a compatibility shim pointing to `./prismatic-engine/index.md` while preserving the caveat that `prismatic-engine/deploy-fresh` has no first-class `okf/` tree.

## Required doc content

Every promoted/synthesized current record should include:

1. Required OKF frontmatter.
2. Current-vs-historical boundary.
3. What is **not** current operational truth.
4. Batch 3 queue, if applicable.
5. Provenance table with this exact shape so verifiers can detect it:

```markdown
| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
```

6. Verification boundary text:

```text
Ad hoc targeted OKF verification only — not full docs-suite green.
```

## Batch 3 / cleanup boundary

Explicitly queue historical/archive families instead of promoting everything:

- Ned scan-triage OKF
- AGY audit
- Canonical merge winner maps
- unsafe/private quarantine

Do not delete branches, archived worktrees, or refs in Batch 2. State: **no cleanup is safe yet**.

## Verifier checks that caught real gaps

The first verifier failed because the canonical project index lacked:

- the provenance table shape;
- exact verification-boundary wording.

Make the verifier check all new docs, including the index, for:

- required frontmatter;
- `resource` and `git_path` matching the path;
- local Markdown links resolving;
- project/master indexes reaching the canonical project index;
- compatibility shim reaching the canonical project index and preserving no-first-class-spoke caveat;
- Batch 3 queue markers;
- provenance table;
- no assignment-shaped secret markers;
- temp verifier cleanup.

## PR and post-merge

Commit example:

```text
[Fred] Add canonical Prismatic OKF project index (#GRO-3721)
```

After merge, verify from `origin/main` in a fresh worktree and clean temp worktrees/scripts.

Report boundary:

```text
Ad hoc targeted OKF verification — not full docs-suite green.
```