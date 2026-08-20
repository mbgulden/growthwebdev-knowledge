# Prismatic OKF Batch 3 Archive/Quarantine Pattern — 2026-07

Use this reference when a treasure-hunt/classification pass has already separated current canonical records from historical/archive families and the next step is to preserve historical provenance without importing a monster archive or enabling cleanup.

## Trigger

- Current canonical project records are already landed.
- Remaining families are historical/archive or quarantine: e.g. Ned scan-triage, AGY audits, canonical merge winner maps, plugin ecosystem, residual project docs, unsafe/private.
- User explicitly says no cleanup/deletion and no unsafe/private promotion.

## Required sequence

1. **Create source-selection manifest first** — do not write archive docs yet.
   - Path pattern: `/tmp/<project>-treasure-hunt/manifests/batch3-selected-archive-records.json`.
   - Include every queued family, even if selected source count is zero/deferred.
   - Preserve counts: total candidates, selected representative sources, duplicate group refs, cleanup status.
   - For unsafe/private candidates, record all candidates but redact paths/titles/content.

2. **Verify the manifest before docs.**
   - Fresh `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)` verifier.
   - Check required families, selected counts, all unsafe/private candidates represented, redaction markers, no secret assignments, cleanup blocked.

3. **Use a clean OKF worktree.**
   - `git worktree add /tmp/<batch-worktree> origin/main`
   - `git switch -c feature/<project>-okf-archive-batch3`
   - Never edit the dirty primary checkout.

4. **Write curated archive docs, not raw branch dumps.**
   - Recommended paths:
     - `okf/projects/<project>/archive/index.md`
     - `archive/<family>-history.md`
     - `archive/unsafe-private-quarantine.md`
   - Include frontmatter, historical/current boundary, provenance table, duplicate handling, cleanup status, verification boundary.
   - Archive docs preserve provenance; they do not make hidden branch behavior current.

5. **Unsafe/private quarantine rules.**
   - Do not copy raw content.
   - Redact paths/titles if they might leak sensitive names.
   - Use hash prefixes only for duplicate tracking.
   - Status should be `quarantine` or `needs-review`, never `current`.
   - State manual review required before publish/delete/redaction decisions.

6. **Index reachability.**
   - Link archive index from the canonical project index.
   - If relevant, update drift/recovery docs with archive status links.
   - Do not change unrelated master indexes unless the archive needs top-level discoverability.

7. **Pre-merge verification.**
   - Check docs exist, required frontmatter, `resource`/`git_path` match, local links resolve, provenance tables exist, cleanup-blocked markers exist, unsafe/private is redacted, no secret assignments.
   - Label: `Ad hoc targeted OKF verification: PASS` and `not full docs-suite green`.

8. **Clean PR + post-merge readback.**
   - Commit format: `[Fred] Add <Project> OKF archive records (#ISSUE)`.
   - PR body must include summary, files changed, source-selection manifest, unsafe/private handling, cleanup boundary, verification evidence.
   - Merge only if clean.
   - Verify from `origin/main` in a fresh worktree or via `git show origin/main:<path>`.
   - Remove temp verifier, temp worktrees, and generator scripts.

## Pitfalls

- Do not treat branch-summed counts as unique docs.
- Do not select only unique unsafe/private hashes; record every unsafe/private candidate redacted so the review count matches classification.
- Do not let archive docs imply cleanup is safe. Cleanup requires a separate final cleanup manifest and explicit user approval.
- Do not omit archive/quarantine links from the canonical project index; archive docs must be discoverable.
- Do not publish raw duplicate paths in unsafe/private duplicate tables if path names might be sensitive.
