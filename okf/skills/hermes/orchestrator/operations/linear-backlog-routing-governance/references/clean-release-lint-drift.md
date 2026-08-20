# Clean release-environment lint drift

## Trigger

A PR’s CI lint matrix fails in files outside the PR diff, while local lint passes.

## Reliable diagnosis

Ambient development tools may read user configuration or resolve a different dependency graph. Reproduce the CI install surface instead:

```bash
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
python3 -m venv "$TMP/venv"
"$TMP/venv/bin/pip" install -e '.[release]'
"$TMP/venv/bin/python" -m ruff --version
"$TMP/venv/bin/python" -m ruff check <the exact CI file list>
"$TMP/venv/bin/python" -m ruff format --check <the exact CI file list>
```

Then run the focused feature tests using that same venv.

## Safe remediation

If the clean release environment resolves a newer Ruff release that introduces rules against existing unrelated targets:

1. Confirm the PR diff does not touch the reported failure paths.
2. Pin the dev/release Ruff range below the newly incompatible release (for example, `ruff>=0.5,<0.16`) rather than mass-formatting unrelated files in the feature PR.
3. Re-run the exact CI lint and format target lists in a new clean venv; record the resolved Ruff version.
4. Push the narrow dependency constraint, then wait for CI on the new head. Do not call CI green until GitHub reports it.

This preserves feature scope while making the workflow reproducible; schedule a separate hygiene task to adopt the newer Ruff rules deliberately.
