# HDE repo hygiene cleanup incident — 2026-07-17

## Trigger

During HDE repo hygiene cleanup after a staging theme fix, the workspace had a large mix of tracked edits, untracked source/docs/tests, generated PWP/Lighthouse output, runtime-ish files, and a stale clean worktree.

## What to preserve vs clean

Safe cleanup targets:

- generated report output: `.lighthouseci/`, `test-results/`, `okf/output/` — archive first, then remove from repo status;
- reproducible caches: `__pycache__/`, `.pytest_cache/`, `.astro/`;
- stale temp worktree only when clean and `HEAD` is ancestor of its matching remote branch.

Preserve or restore:

- source/docs/tests needed by the active proof path, such as `docs/hde-light-theme.css`, `.pwp/routes.json`, `playwright.config.ts`, `lighthouserc.json`, `tests/a11y/`, `tests/visual/`, `tests/flows/`;
- ambiguous tracked modifications and active untracked source files;
- env/db/runtime/customer data.

## Pitfall discovered

Do not write Markdown manifests with unquoted heredocs when the text contains backticked commands. Backticks inside `<<PY` or `<<EOF` are still shell command substitution before Python sees the string. In this session, prose containing `git clean -fdx` executed that command. Use one of:

```bash
cat > "$manifest" <<'EOF'
# literal markdown here; backticks are safe
EOF
```

or write the file from a checked-in script / Python file that is not embedded in an expanding shell heredoc.

## Recovery pattern if a cleanup foot-gun fires

1. Stop further deletion immediately.
2. Inspect `git status` and archive directory contents.
3. Restore required proof/source files from live dist, backups, or known-good scaffolds.
4. Reinstall generated dependencies if `node_modules` was removed.
5. Rerun canonical verification (`npm run pwp:verify` for HDE theme/PWP work).
6. Record the incident in the manifest; do not report a sanitized success story.

## Verification shape

For this class of cleanup, final proof should include:

- `git status --short --branch` after cleanup;
- `git worktree list --porcelain` after cleanup;
- archive manifest exists and contains before/final status snapshots;
- secret scan of the manifest/report text;
- canonical build/PWP verification if source/proof files were touched or restored.
