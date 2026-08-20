# Prismatic OKF Treasure Hunt + Reconciliation Pattern (2026-07)

Use when a project repo appears to lack current OKF docs but branch history / backup refs / hub branches may contain stranded documentation. This came from the Prismatic Engine OKF cleanup where `deploy-fresh` had no first-class `okf/` tree, but backup and Ned branches contained large OKF trees.

## Trigger

- Current project repo lacks `okf/` or has only a breadcrumb map.
- User suspects docs are hidden/stranded, not absent.
- There are backup branches, stale remotes, moved worktrees, or dirty knowledge-hub branches.
- Goal is reconciliation/classification, not immediate promotion.

## Source inventory requirements

Inventory all possible sources, not just the current checkout:

1. Project repo local branches.
2. Project repo `origin/*` branches.
3. Secondary/stale remotes such as `dev-repo/*` that may fail fresh fetch but still have local refs.
4. Attached worktrees from `git worktree list --porcelain`.
5. Knowledge hub local/origin branches.
6. Archived local `okf/` directories under `/home/ubuntu/work`, especially moved worktree cleanup dirs.

Capture branch records with this shape:

```json
{
  "repo": "prismatic-engine",
  "branch": "backup/gro-3515-full-okf-blocked",
  "head": "<sha>",
  "okf_file_count": 301,
  "markdown_file_count": 900,
  "prismaticish_markdown_count": 444,
  "sample_paths": ["okf/audits/..."],
  "reachable_from_remote": true,
  "notes": []
}
```

Capture local OKF directories with this shape:

```json
{
  "path": "/home/ubuntu/work/.../okf",
  "git_repo_root": "<nearest .git root or null>",
  "file_count": 0,
  "prismaticish_count": 0,
  "sample_paths": [],
  "is_archived_worktree": true
}
```

## Extraction rule

Do **not** checkout polluted historical branches in the main worktree. Use:

```bash
git ls-tree -r --name-only <branch>
git show <branch>:<path>
```

For each candidate file, extract metadata:

```json
{
  "source_repo": "prismatic-engine",
  "source_branch": "backup/gro-3515-full-okf-blocked",
  "source_head": "<sha>",
  "path": "okf/audits/canonical-merge-winner-map-2026-07-06.md",
  "title": "...",
  "type": "Audit",
  "linear_issue": "GRO-...",
  "timestamp": "...",
  "status": "current|stale|unknown",
  "frontmatter_valid": true,
  "content_sha256": "...",
  "exists_in_current_hub": false,
  "exists_in_current_prismatic": false,
  "recommendation": "promote|merge|archive|ignore|needs-review"
}
```

## Dedupe + classification

Deduplicate on two axes:

1. Exact `content_sha256`.
2. Concept similarity by title/path/Linear issue/date.

Useful concept families from Prismatic:

- Dispatcher incident
- Webhook / Linear security
- Tier 7 hardening
- OKF drift / recovery
- Governance dashboard
- Prismatic plugin ecosystem
- Ned scan-triage OKF
- AGY audit
- Canonical merge winner maps

Use these classes:

| Class | Meaning | Action |
|---|---|---|
| `canonical-current` | Already indexed and accurate | keep, maybe cross-link |
| `canonical-stale` | Indexed but needs update | create update task/doc patch |
| `hidden-useful` | Not indexed/current, contains still-useful facts | promote or merge |
| `hidden-historical` | Useful as history/provenance only | archive/index as historical |
| `duplicate-superseded` | Same content or obsolete version | do not promote; record duplicate family |
| `unsafe/private` | Contains secrets/private data/client-sensitive material | quarantine; do not publish |
| `noise` | Generated filler or irrelevant | ignore after manifesting |

## Report minimum sections

A treasure-map report should include:

1. Executive summary.
2. Source inventory counts.
3. Hidden branches/worktrees with OKF docs.
4. Top 20 high-value hidden docs.
5. Duplicate families.
6. Recommended canonical structure.
7. Promotion plan.
8. Risks/blockers.
9. Exact cleanup candidates safe after promotion.
10. Verification evidence.

## Cleanup safety rule

Default cleanup answer is **yellow: no cleanup is safe now** until:

- hidden useful docs are promoted or explicitly queued;
- historical families are summarized/indexed;
- unsafe/private candidates are reviewed;
- duplicate/superseded docs are recorded.

Do not delete branches/worktrees just because the report exists.

## Verification guard lesson

The stale-verification guard may repeat old messages even after a pass. Respond by running a fresh `/tmp/hermes-verify-*` script scoped to the exact changed paths named by the guard, using `tempfile.NamedTemporaryFile(prefix="hermes-verify-", dir="/tmp")`, and explicitly clean it up. Do not argue with the guard or cite earlier unrelated verification.
