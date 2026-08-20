# Prismatic OKF next-batches pattern — archive, standards, repo-local map

Session pattern from the Prismatic Engine OKF treasure hunt after Batch 2 canonical project records landed.

## When to use

Use this after an OKF treasure hunt has already produced:

- a canonical project index/current records batch;
- classified hidden docs;
- unsafe/private candidates;
- a repo-local breadcrumb map that may need finalizing.

This pattern covers:

1. Batch 3 historical/archive rollups;
2. Batch 3.5 reusable standards/decision extraction;
3. Batch 4 repo-local breadcrumb map update;
4. stale-verification guard handling when temp worktrees/scripts were intentionally cleaned.

## Batch 3 — archive/quarantine rollups

Before writing archive docs, create an explicit selection manifest:

```text
/tmp/prismatic-okf-treasure-hunt/manifests/batch3-selected-archive-records.json
```

Recommended families:

- Ned scan-triage OKF;
- AGY audit;
- Canonical merge winner maps;
- Prismatic plugin ecosystem;
- Other Prismatic docs;
- unsafe/private.

Rules:

- Historical/archive docs are curated rollups, not raw branch dumps.
- Unsafe/private candidates are not published or promoted; create a redacted quarantine record only.
- Record all unsafe/private candidates, even if duplicate hashes collapse them conceptually.
- Redact unsafe/private paths/titles in published docs and use safe hash prefixes only.
- Cleanup remains blocked; no branch/ref/worktree/local-dir deletion.

Archive docs should include:

- frontmatter with matching `resource` and `git_path`;
- why the archive exists;
- current-vs-historical boundary;
- provenance table;
- duplicate/superseded handling;
- cleanup status;
- exact boundary: `Ad hoc targeted OKF verification only — not full docs-suite green.`

## Batch 3.5 — reusable standards/decisions

Only extract standards/decisions when Batch 3 reveals a reusable rule beyond the project record.

Prismatic examples:

```text
okf/standards/prismatic-dashboard-live-proof.md
okf/standards/okf-worktree-reconciliation.md
okf/decisions/prismatic-okf-hub-and-spoke-map.md
```

Key markers to verify:

- dashboard standard includes `live API status/body sample`;
- reconciliation standard includes `git ls-tree`, `git show`, `Cleanup remains blocked`, and unsafe/private quarantine language;
- hub/spoke decision names canonical hub path and repo-local breadcrumb path;
- standards, decisions, and master indexes link the new docs.

## Batch 4 — repo-local breadcrumb map finalization

When the project repo lacks a first-class `okf/` tree, update the repo-local map after the hub has landed canonical/archive/standards docs.

For Prismatic:

```text
prismatic-engine/docs/okf-map.md
```

Verify against durable remotes, not dirty local checkouts:

- `prismatic-engine origin/deploy-fresh:docs/okf-map.md`;
- `growthwebdev-knowledge origin/main:<hub-path>` for every referenced hub record.

The map should explicitly state:

- `deploy-fresh` does not currently keep a first-class `okf/` tree;
- canonical project index path;
- archive index path;
- treasure-map report path;
- unsafe/private quarantine boundary;
- cleanup remains blocked;
- relevant standards/decisions.

## Stale verification guard pattern for cleaned temp paths

If a stale guard lists temp paths that were intentionally cleaned, do **not** recreate fake temp artifacts. Instead run a fresh `/tmp/hermes-verify-*` script whose `changed_paths_checked` includes the exact stale paths and explains:

- durable replacement verified on `origin/main` or `origin/deploy-fresh`;
- temp worktree/script is intentionally absent;
- generated durable docs/indexes exist;
- merge commits are present;
- verifier itself was removed.

Example checked-path wording:

```json
{
  "changed_paths_checked": [
    "/home/ubuntu/work/prismatic-engine/docs/okf-map.md",
    "/tmp/okf-prismatic-standards-decisions/okf/standards/prismatic-dashboard-live-proof.md",
    "/tmp/write_batch35_okf.py"
  ],
  "durable_replacements_checked": [
    "prismatic-engine origin/deploy-fresh:docs/okf-map.md",
    "growthwebdev-knowledge origin/main:okf/standards/prismatic-dashboard-live-proof.md",
    "growthwebdev-knowledge origin/main Batch 3.5 generated docs/indexes"
  ]
}
```

## Commit/PR hygiene

- Use clean worktrees from `origin/main` / `origin/deploy-fresh`.
- Do not edit dirty primary checkouts in place.
- If Hermes auto-checkpoints a WIP commit, `git reset --soft <base>` and recommit with the required `[Fred] ... (#ISSUE)` message.
- For Prismatic repo edits, lock files before editing and unlock after merge.
- Keep PRs small: archive batch, standards/decision batch, repo-local map batch.
