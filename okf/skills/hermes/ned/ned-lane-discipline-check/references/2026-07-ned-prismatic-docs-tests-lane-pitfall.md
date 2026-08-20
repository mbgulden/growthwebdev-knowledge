# Ned lane pitfall: docs/tests outside owned paths

Session lesson from Prismatic Engine core worktree-janitor implementation:

- Ned's Prismatic lane allows writes under `scripts/`, `prismatic/`, and `plugins/`.
- A feature implementation that initially modified root `README.md` and root `tests/` passed local checks but was blocked by the Prismatic pre-push lane guard.
- For Ned-owned PE implementation work, place feature docs under `prismatic/docs/` and feature tests under `prismatic/tests/` unless another lane owner explicitly authorizes root docs/tests.
- If the feature genuinely requires root README or root tests, stop and coordinate/hand off rather than bypassing the guard.
- Re-run verification after moving files; path moves can invalidate prior test command paths.

This preserves the documentation-in-same-commit rule while staying inside Ned's write lane.
