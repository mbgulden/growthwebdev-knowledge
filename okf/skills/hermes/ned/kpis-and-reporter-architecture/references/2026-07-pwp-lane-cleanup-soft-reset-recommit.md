# 2026-07-29 — Lane-cleanup soft-reset + re-commit workflow

## Trigger

Two or more local commits have already been made on a Ned branch (e.g.
`ned/pwp-publish-kpi-tracker`) but the **push-time lane gate** rejects
the push because some files in those commits live outside Ned's lane
(`['scripts/', 'prismatic/', 'plugins/']`). The most common offenders
for PWP work are:

- `config/seo_sites.json` — owned by the registry lane; Ned's adapter
  reads it but does not write it.
- `schemas/*.schema.json` at the repo root — owned by another lane;
  Ned's schemas must live under `plugins/<plugin>/capabilities/<capability>/schemas/`.

## Why a soft reset (not a revert) is the right tool

The two commits are local-only and not pushed. `git revert` would create
extra commits just to undo work. A soft reset (`git reset --soft <last_good>`)
puts everything back as **staged changes** in the index, ready to be
re-staged at the right paths and committed fresh. The branch pointer
moves back; the index and working tree carry everything forward.

The result: one clean commit at the right paths, no revert noise, the
existing commit messages are *replaced* (since the soft reset discarded
them) — but you can copy them out before resetting if you want to
preserve exact wording.

## The seven-step workflow

```
# 1. Confirm current state
git status --short
git log --oneline -3

# 2. Soft-reset to the last good commit (preserves all work as staged)
git reset --soft <last_good_sha>

# 3. Drop lane-violating files from the index (keeps them on disk)
git rm --cached config/seo_sites.json
git rm --cached schemas/<offending_schema>.json

# 4. Revert working-tree changes to the registry file (registry owner
#    keeps authority; Ned's hd-engine addition was an overreach)
git checkout -- config/seo_sites.json

# 5. Move out-of-lane schemas into the in-lane location
mv schemas/<schema>.json plugins/<plugin>/capabilities/<capability>/schemas/
# (rmdir schemas/ only if empty afterward — usually not, since other
# lanes own schemas/ files)

# 6. Update the loader's _resolve_schema_path() to point at the new
#    in-lane location
```

```python
def _resolve_schema_path() -> Path:
    env_root = os.environ.get("PWP_REPO_ROOT")
    root = Path(env_root) if env_root else REPO_ROOT
    return (
        root
        / "plugins" / "pwp" / "capabilities" / "publish_kpi_tracker"
        / "schemas" / "kpi-registry.schema.json"
    )
```

```
# 7. Stage via the symlink-target path (git add through plugins/ fails
#    with "pathspec ... is beyond a symbolic link")
git add prismatic/shipped_plugins/pwp/capabilities/<capability>/schemas/<schema>.json

# 8. Run pytest + ad-hoc verifier; both should pass with the same
#    counts as before the lane cleanup
PYTHONPATH=plugins pytest -q plugins/<plugin>/capabilities/<capability>/tests/
python3 /tmp/hermes-verify-<scope>.py

# 9. Single fresh commit with a lane-clean diff
git commit -m "..."

# 10. Push; the lane gate should now report "0 violations"
git push origin <branch>
```

## The symlink-trap detail

`prismatic-pwp-ubersuggest-auth` has `plugins/` as a git symlink to
`prismatic/shipped_plugins/`. Two consequences:

- `git add plugins/.../foo.py` errors with "pathspec ... is beyond a
  symbolic link". Stage via the canonical path
  `prismatic/shipped_plugins/.../foo.py`.
- The same file is reachable at two paths. A `git rm --cached` on one
  path leaves the file at the other path untracked. Adding it via the
  symlink-target path is the consistent way.

When the soft-reset puts `plugins` itself in the `D` state in the
index (because `git reset` saw it as part of a rename), `git restore
--staged plugins` reconstitutes it. Verify with `ls -la plugins` that
the symlink is intact before continuing.

## When NOT to use this workflow

- **The offending commit has been pushed.** Use `git revert` to create
  a clean revert commit instead. The soft-reset rewrites history, which
  a pushed commit must not do.
- **The lane violation is a handoff, not a relocation.** If the file
  truly belongs to another agent (not just to a different path Ned
  owns), follow `references/lane-rejection-owner-routing.md` instead.
  Schema relocation is a Ned-resolvable case; a config-file edit is
  a handoff case.
- **The offending commit carries a published commit message that the
  user or Linear references.** Copy the message before the soft-reset
  if exact wording must be preserved.

## Why not just edit the file paths in-place?

`git mv` from `schemas/foo.json` to `plugins/.../schemas/foo.json`
followed by `git add` to the new location works for a single file but
leaves `git status` in a confusing state when the symlink is in play.
The cleanest path is: drop the index entries, move the files on disk
to the canonical in-lane location, then `git add` the new locations.
The symlink target is the canonical staging path.

## Live evidence from this session

After soft-reset + relocate + re-commit + push:

```
✅ [Prismatic Engine] Pre-push OK: ned → ned/pwp-publish-kpi-tracker
   Files: 20 changed, 20 in-lane, 0 violations
To https://github.com/mbgulden/prismatic-engine.git
   fbd23f70..3d841694  ned/pwp-publish-kpi-tracker -> ned/pwp-publish-kpi-tracker
```

Tests + ad-hoc verifier stayed green (64/64 pytest, 12/12 ad-hoc).
The dashboard continued to render 2 per-site rows because the
file-system scan in `list_sites()` discovers per-site `*.kpi.json`
files regardless of the registry content.

## The "stale working-tree edit" trap

A subtle gap surfaced in the next session after this workflow
landed: the `_resolve_schema_path()` function in the committed code
still pointed at `schemas/pwp-kpi-registry.schema.json` (the old,
out-of-lane location). The working tree had the corrected version,
but it was an unstaged edit that didn't make it into the
soft-reset / re-commit.

The trap: the existing tests all pass because `load_schema()` is
called with explicit paths in tests. The default
`_resolve_schema_path()` is never exercised, so the broken path
ships silently. A `PYTHONPATH=plugins python3 -c "from
plugins.pwp.capabilities.publish_kpi_tracker.pwp_kpi_site_registry
import _resolve_schema_path, load_schema; load_schema()"` would
catch it with `FileNotFoundError`.

**Two-stage verification for any soft-reset + relocate workflow:**

1. Run the canonical pytest (verifies the in-tree code paths).
2. **Smoke-test the default-path loader explicitly** —
   `_resolve_schema_path()` returning a path that exists when
   used by `load_schema()` with no path override. This catches the
   case where a function edited on disk never made it into the
   commit.

The fix is mechanical: re-apply the missing edit, run the smoke
test, amend the commit. Don't trust `git status` to be empty — it
often isn't after a soft-reset, and the noise hides the
"this edit never landed" pattern.

## Lane-cleanup skill invariants to encode for next time

- **The push is the gate, not the commit.** A clean local commit
  can still be a blocked push. Don't conflate the two failure
  modes.
- **The registry file (`config/seo_sites.json`) is read-only for
  Ned.** The PWP plugin's adapter reads it but doesn't write;
  per-site `*.kpi.json` files in Ned's lane are the source of
  truth for the dashboard via the file-system scan in
  `list_sites()`.
- **Schemas live with the plugin.** Always at
  `plugins/<plugin>/capabilities/<capability>/schemas/`. Never at
  the repo root `schemas/` directory.
- **`_walk_to_pwp_repo()` over `parents[N]`.** Symlink paths give
  different `parents[N]` for the same file. Walk up looking for
  the canonical anchor file (`config/seo_sites.json`).
- **Smoke-test default-path loaders explicitly after lane cleanup.**
  `load_schema()` with no path override must succeed. If it
  raises `FileNotFoundError`, the loader edit didn't make it into
  the commit and needs to be re-applied + amended.