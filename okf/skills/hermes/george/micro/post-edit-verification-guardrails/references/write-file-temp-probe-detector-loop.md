# Disposable `/tmp` probe written through `write_file` can create a detector loop

## Trigger

A post-edit guard asks for a focused temporary verifier under `/tmp` with an OS-safe `tempfile` path and a `hermes-verify-` prefix. If the agent creates the tempfile path with `tempfile.mkstemp` but then writes the probe using the Hermes `write_file` tool, the workspace-change detector may record the disposable probe itself as a changed path. A repeated guard can then include both the real source files and `/tmp/hermes-verify-*.py` in `Changed paths`, even if the source worktree is clean.

## Durable lesson

For disposable verifier source, prefer a single `terminal` transcript that:

1. creates the path via Python `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`;
2. writes the probe body from within the same shell/Python command;
3. runs the probe with the project venv, preferably `python -m pytest -q /tmp/hermes-verify-*.py`;
4. runs direct top-level focused commands the detector recognizes (`python -m pytest`, `ruff check`, `ruff format --check`, build/package, `git diff --check` as relevant);
5. removes the disposable probe;
6. asserts both the new temp path and any previously listed stale temp paths are absent;
7. keeps only the durable proof log under `/tmp/hermes-verify-*` and reports its SHA-256.

## Non-claim

This pattern is not canonical suite green. Report it as `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the repository's canonical suite actually ran and passed.
