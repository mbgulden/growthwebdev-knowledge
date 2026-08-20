# Canonical Journal Runtime Release

## When this applies
An active Hermes journal cron has been hot-patched in the installed `prismatic` package, while the canonical Prismatic Engine source lacks the same behavior or the active import path is ambiguous.

## Durable repair pattern

1. Locate the cron entrypoint and inspect the module it imports at runtime with `inspect.getfile()`; do not infer it from a repository checkout.
2. Create a clean `feature/` worktree from `origin/main`. Patch the canonical `prismatic/journal.py` contract, not only a site-packages copy:
   - read the *tail* of long logs using a bounded byte read and discard the partial first line;
   - parse line timestamps and include only a declared freshness window;
   - suppress `git` stderr for non-repositories instead of generating fake Git events.
3. Add regressions for: stale head vs current tail, out-of-window timestamps, and non-Git workspaces. Keep the existing journal regression tests in the focused test command.
4. Run `py_compile`, `ruff check`, focused pytest, `git diff --check`, then commit with the required issue prefix.
5. Install/release the canonical build into the *actual active Hermes runtime*, then re-check `inspect.getfile()` and behavior markers. Run the affected scheduler job through Hermes; a source-only test is insufficient.
6. Push a feature branch/open a review PR. Do not merge around CI or required-review gates. Report CI as pending/blocked separately from local targeted proof.

## Verification language

Use **ad hoc targeted verification** and name its exact layers: fixture, focused pytest, runtime-import readback, and fresh scheduler run. Do not call it full suite, production deployment, or merged release unless those happened.

## Pitfall

A formatter can create a large unrelated diff in old source files. Before amending a commit, compare against the intended base and restore/reapply the narrow functional patch if formatting expanded the review surface.
