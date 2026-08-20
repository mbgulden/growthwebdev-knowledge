# OKF SSOT Dirty Worktree Cleanup Pattern (2026-07)

Use when the OKF hub checkout is on a stale/dirty feature branch and the goal is a Prismatic-style single source of truth without losing useful stranded docs.

## Trigger

- `growthwebdev-knowledge` active worktree is not on `main`/`origin/main`.
- Dirty/untracked OKF files mix current docs, duplicate mirrors, archive dumps, client/private inputs, and transient results.
- User asks to clean OKF branches/worktrees or get to a single source of truth.

## Pattern

1. **Declare the canonical target first**
   - Canonical source is `origin/main`.
   - Treat every dirty file, branch, PR, and worktree as a source candidate until classified.
   - Do not delete branches/worktrees at this stage.

2. **Manifest before promotion**
   - Write a local source manifest under `/tmp`, e.g. `/tmp/okf-hde-cron-source-manifest.json`.
   - For every dirty/untracked path record: path, git status, sha256, frontmatter title/type, whether it exists on `origin/main`, classification, and recommendation.
   - Useful classes: `okf-candidate`, `plugin-report-candidate`, `prismatic-artifact-candidate`, `website-dev-current-candidate`, `transient-noise`, `unsafe/private`, `duplicate-superseded`.

3. **Promote only selected current records via a clean worktree**
   - Create a temporary worktree from `origin/main`, not from the dirty branch.
   - Copy only selected docs.
   - Update only current indexes; do not copy dirty index files wholesale when `origin/main` has newer canonical structure.
   - Normalize frontmatter to required OKF fields (`resource` and `git_path` should be repo-relative OKF paths, not GitHub URLs, unless intentionally external).
   - Fix broken links discovered by verifier before commit.

4. **Verify selected promotion before commit**
   - Use `/tmp/hermes-verify-*` tempfile verifier.
   - Check required frontmatter, index reachability, local Markdown link resolution, exact changed scope, and `cleanup_executed=false` for source cleanup.
   - Report as ad hoc targeted verification, not docs-suite green.

5. **Merge, remote-readback, then clean only temp artifacts**
   - Merge the clean promotion PR.
   - Verify promoted docs and indexes from `git show origin/main:<path>`.
   - Remove only the temporary worktree/branch created for that promotion.

6. **Scoped dirty source cleanup after canonical proof**
   - Remove only untracked duplicates whose content is now canonical on `origin/main` or proven duplicate-superseded.
   - Revert dirty index edits only when they duplicate already-promoted links or conflict with newer canonical indexes.
   - Leave the stale source branch intact unless Michael explicitly approves branch deletion.

7. **Handle plugin mirrors by normalized content, not filename alone**
   - Uppercase or alternate filename plugin mirrors may differ in frontmatter/Markdown escaping while carrying the same body.
   - Compare normalized body/token overlap against canonical lowercase docs before removal.
   - If any unique content remains, preserve or merge-review; if only tokenization/formatting differs, mark duplicate-superseded.

8. **Quarantine raw archive/private source dumps before cleaning the active checkout**
   - For AGY/drive eval directories, preserve raw material outside the repo under a profile state quarantine path, e.g. `~/.hermes/profiles/orchestrator/state/okf-source-quarantine/<date>-dirty-hub-closeout/`.
   - For client/intake/private-ish docs, create a redacted manual-review manifest with `[REDACTED_PATH_###]`; do not publish raw paths/content in OKF.
   - Remove transient `result.md`-style files only after manifesting them as noise.

9. **Return the active hub checkout to canonical main**
   - Once dirty source material is promoted, removed as duplicate/noise, or quarantined, switch the active hub checkout to `main` and hard reset to `origin/main`.
   - Verify `git status --short --branch` is exactly `## main...origin/main` and `HEAD == origin/main`.

## Pitfalls

- Do not bulk-merge a dirty branch just because some files are useful.
- Do not promote raw AGY/drive folders as current truth; archive/roll up or quarantine them.
- Do not publish client intake/source files without manual review.
- Do not delete stale feature branches as part of the same cleanup unless Michael explicitly approves; preserve them behind an approval-only cleanup manifest.
- Do not trust dirty branch index files over newer `origin/main` index structure.
- Do not claim canonical cleanup from local status alone; prove canonical docs from `origin/main` readback.

## Verification packet shape

```text
AD_HOC_VERIFICATION=PASS
SCOPE=OKF dirty hub worktree cleanup after selected promotions
canonical_worktree=/home/ubuntu/work/growthwebdev-knowledge
worktree_branch=main
head_equals_origin_main=true
worktree_clean=true
promoted_docs_on_origin_main=true
quarantine_manifest=<path>
branch_deleted=false
worktree_deleted=false
AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite green
```
