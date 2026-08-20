# Darius stale PR rescue + safe push guard — 2026-07-10

## Trigger
Michael wanted Ned to keep going until Darius work was reviewed, rescued, and brought cleanly into `master`, while also preventing Ned from overwriting other agents' GitHub branches.

## Durable workflow

### 1. Prevent branch damage before rescue work
Install/use Ned's safe-push guard before doing GitHub cleanup:

- Hook: `/home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push`
- Installer: `/home/ubuntu/.hermes/profiles/ned/scripts/install_git_push_guard.sh`
- Global config:
  - `core.hooksPath=/home/ubuntu/.hermes/profiles/ned/git-hooks`
  - `push.default=current`

The hook blocks protected branch pushes, branch deletes, non-fast-forward overwrites, branch renames, and for repo-local `hermes.agent=ned` + `hermes.enforceBranchPrefix=true`, any remote branch outside `ned/...`.

Important nuance: repo-level Prismatic pre-push lane rules may be stricter than the global safe-push hook. If a branch prefix is rejected, rename to the correct lane prefix and/or split the rescue by lane.

### 2. Never directly merge unrelated-history stale PRs
For Darius, stale PRs #4–#17 targeted an unrelated-history `main` branch. They were technically “mergeable” but unsafe: branch diffs showed thousands of changes and mass deletions of assets/configs. The correct move was **not** merge. It was:

1. Inspect open PRs with `gh pr list` / `gh pr view`.
2. Compare against current `origin/master`, not stale `main`.
3. Identify safe artifacts worth rescuing.
4. Create clean rescue branches from `origin/master`.
5. Cherry-pick/copy only the safe paths into the proper lane.
6. Verify locally and through Cloudflare Pages.
7. Merge the clean rescue PRs.
8. Close the stale unsafe PRs with comments pointing to the rescue PRs.

### 3. Split by lane
A single rescue branch that mixed `docs/` and `tools/` failed lane checks. The successful split was:

- `agy/rescue-open-pr-docs` — docs/reference media only, under `docs/`.
- `ned/rescue-sprite-slicer` — tooling only, under `tools/`.

Root-level stale files (`AGY-REVIEW.md`, `PHASE2-AUDIO-PLAN.md`, `REPORT.md`) were moved under `docs/rescued-open-prs/` to keep the AGY branch inside its lane.

### 4. Preserve before mutating binary assets
Before deciding what to do with dirty VFX assets, archive both HEAD and working-tree versions plus a binary patch and checksums:

- `git diff --binary -- <paths> > archive.patch`
- copy current files and `git show HEAD:<path>` versions
- write `SHA256SUMS`
- optionally generate a visual before/current/diff contact sheet

Then promote intentional assets through a feature branch/PR, not as silent workspace dirt.

### 5. Verification used
For Darius rescue PRs:

```bash
python3 -m py_compile tools/sprite_slicer.py
python3 -m json.tool docs/mission-briefings.json
python3 -m json.tool docs/veo_vs_imagen_results.json
python3 scripts/verify_syntax.py   # expected: 46/46 passed
gh pr checks <PR> --repo mbgulden/darius-star  # Cloudflare Pages pass before merge
```

For VFX assets:

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image
files=sorted(Path('assets/sprites/vfx').glob('explosion_[0-3]_[0-3].png'))
assert len(files)==16
for p in files:
    im=Image.open(p)
    assert im.size == (512,512)
    assert im.mode == 'RGBA'
    assert im.getchannel('A').getextrema() == (0,255)
print('image_asset_check=pass files=16 mode=RGBA size=512x512 alpha=0..255')
PY
```

## Successful rescue outcome in this session
- PR #18 merged transparent VFX assets into `master`.
- PR #19 merged rescued docs/reference media into `master`.
- PR #20 merged rescued sprite slicer tooling into `master`.
- PRs #4–#17 were closed after comments explaining why direct merge was unsafe and where the rescue landed.

## Pitfalls
- `gh pr create --base main` can fail when the repo's living branch lineage is actually `master`; inspect merge-base/history before assuming GitHub's default branch is the operational base.
- `gh pr view` can report `MERGEABLE` on a PR that is still operationally unsafe because the diff is from an unrelated-history branch with mass deletions.
- Do not use broad `git merge` for stale agent branches. Extract artifacts path-by-path into a fresh branch from current `origin/master`.
- Do not push mixed-lane rescue branches. Split docs/assets vs tools/code by lane before pushing.
