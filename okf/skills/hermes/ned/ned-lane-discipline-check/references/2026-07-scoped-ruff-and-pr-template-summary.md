# Scoped ruff + lane-aware PR template (Prismatic Engine)

This is a short reference distilled from a 2026-07-28 PR (#410) into the
prismatic-pwp-ubersuggest-auth repo. It bundles two failure modes that
share a fix: (1) `ruff check --fix` and `ruff format` operate on the
**whole repo** by default with no scope guard, and (2) Ned's owned lanes
are `scripts/`, `prismatic/`, `plugins/` — so files at repo root are
rejected by the lane pre-push hook.

## 1. Scoped ruff

`ruff check --fix` and `ruff format` walk the whole repo, not just your
files. When you run them on a Prismatic Engine working tree, they mutate
~280 unrelated files (lint fixes, import ordering, formatter reflow)
and trigger the path-portability guard on files that contain hard-coded
example paths.

**Always scope ruff to the files you authored.** Maintain a list of
owned paths before running lint:

```python
# ruff-check / format scope. Update this whenever the change set changes.
OWNED = [
    "prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/",
    "plugins/pwp/capabilities/publish_kpi_tracker/",  # if symlinked
    "tests/publish_kpi_tracker/",
    "scripts/kpis/",
    "docs/pwp/",
]
subprocess.run(["ruff", "check", "--fix", *OWNED], check=False)
subprocess.run(["ruff", "format", *OWNED], check=False)
```

If ruff reformats a file outside `OWNED`, `git restore -s origin/main`
that file before staging. The pre-push hook will block
hard-coded-path reformats separately.

## 2. Lane ownership and repo-root files

Ned's owned dirs are `scripts/`, `prismatic/`, `plugins/`. The following
files are at repo root and trigger the lane guard:

- `pyproject.toml`
- `pytest.ini`
- `conftest.py`
- `setup.cfg`

If you only need to *configure* test discovery for a new plugin, do it
via `[tool.pytest.ini_options]` in `pyproject.toml` — but pyproject.toml
itself is at root. Workarounds:

1. **For test discovery**, ship a `pytest.ini` (or `conftest.py`) inside
   the plugin directory (`plugins/pwp/pytest.ini`) and run pytest with
   `cd` rooted at that plugin directory. The pre-push hook only walks
   the diff-vs-remote changed-file list, so a repo-root file only
   counts if you changed it.
2. **For plugin config**, do not touch `pyproject.toml`. The CI matrix
   reads `pyproject.toml` once; if you change it, your plugin activation
   changes for the entire repo, which the lane guard will reject.
3. **For the commit gate**, the path-portability check is a separate
   `grep -n '/home/ubuntu'` against changed files. Hard-coded example
   paths inside docstrings or fixture examples trip this. Replace
   `/home/ubuntu/work/<repo>/<subpath>/` with `<repo>/<subpath>/` or
   remove the path entirely.

## 3. PR template (lane-aware)

Pull the PR template from `prismatic-pwp-ubersuggest-auth/.github/PULL_REQUEST_TEMPLATE.md`
or scaffold one with these fields:

```
## What changed
- verbatim bullet list of files added or modified

## Why
- 1–2 sentences linking the change to a Linear issue or domain

## Canonical verification
- `python3 -m prismatic.quality.plugin_load` → exit 0 / PASS
- `pytest path/to/tests/test_*.py -q` → N/N PASS
- for KPI metrics: `npm run kpi:daily` (or the Python launcher) → exits 0

## Manual reproduction
- environment setup (venv / npm install)
- commands to demo the change locally

## Linked Linear
- identifier + URL

## Lane check
- All changes are inside `scripts/`, `prismatic/`, or `plugins/`.
- No `pyproject.toml`, `pytest.ini`, or `conftest.py` at repo root.

## Docs touched
- if the manifest / schema / lookup table changed, list the doc path.
```

## 4. Companion: docs/provider-neutral-receipt-validation.md is also Ned's lane

The lane guard rejected an unrelated write to `docs/` during the KPI
verification. The `docs/` directory is owned by other agents. If the
change needs documentation, file a separate PR against the docs lane
and link it in the body. Do not edit `docs/` from a Ned branch.

## 5. Recovery recipe

If you accidentally triggered a red lane guard (or hit
`ruff --fix` reformatted ~280 files), the recovery shape is:

1. `git stash` your work-in-progress.
2. `git reset --hard origin/main` to clear the stray reformats.
3. `git stash pop` to restore your authored files.
4. Run ruff **scoped** to your owned paths.
5. Commit with an explicit \"fixes reformatted X files reverted in
   origin/main style\" message if the commit gate is still angry.
