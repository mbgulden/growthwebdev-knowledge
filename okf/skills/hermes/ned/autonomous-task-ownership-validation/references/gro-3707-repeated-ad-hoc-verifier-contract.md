# GRO-3707 repeated ad-hoc verifier contract

Session pattern: after implementing a PWP fixture harness and even after reporting passing pytest/manual output, the verifier re-dispatched twice with `Verification status: unverified` and demanded a fresh `/tmp/hermes-verify-*` script. The correct response was not to argue from prior evidence or rerun the same suite directly; it was to create a new OS-safe temporary verifier each time, execute it, print the script path, command, assertions, exit code, and cleanup result, then remove the temporary script.

## Durable workflow lesson

When the system says no canonical command was detected after a code-editing task:

1. Use `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` (or equivalent OS-safe tempfile API). Do not hand-type a predictable path.
2. The verifier script should exercise the changed behavior directly, not just run a broad test suite. For CLI-generating behavior, call the changed CLI and assert the produced artifacts and values.
3. Print at least:
   - `VERIFY_SCRIPT: <path>`
   - the command being tested
   - the subprocess exit code
   - concrete assertion summary
   - `VERIFY_EXIT: <code>`
   - cleanup status
4. Clean up the verifier script in `finally`. Temporary output artifacts can remain if useful for evidence, but the verifier script itself should be removed when possible.
5. If the verifier prompt repeats, create a fresh verifier with a fresh `hermes-verify-` path and rerun. Prior verifier output may be true but stale for the detector.

## Example assertion shape from PWP fixture harness work

For `scripts/pwp theme fixtures ... --run --json`, the ad-hoc verifier asserted:

- command exited `0`
- final manifest JSON parsed despite earlier stdout from the run phase
- `themeId == pwp.theme.trust-light`
- exactly `15` cases generated
- case kinds include both `page` and `module`
- viewports include `mobile`, `tablet`, and `desktop`
- generated manifest/spec files are non-empty
- representative HTML fixtures and screenshot artifacts are non-empty

## Dependency-metadata refresh variant

When the repeated verifier prompt names `pyproject.toml` as the changed code path, the fresh `/tmp/hermes-verify-*` script should assert the dependency contract directly before running commands. For the GRO-3707 refresh, the verifier used `tomllib` to assert:

- runtime dependencies include `packaging>=23.0` so `prismatic.core.registry` imports in a fresh install
- `[project.optional-dependencies].dev` includes `pytest>=8.0` for the GitHub `pip install -e .[dev] && pytest ...` workflow
- `[project.optional-dependencies].dev` includes `jsonschema>=4.0` so PWP theme validator tests exercise schema validation instead of fallback structural warnings

Then it ran a fresh editable install and direct checks:

```text
python -m pip install -e .[dev]
python -c 'import packaging, pytest, jsonschema; print("dependency-imports-ok")'
python -m prismatic.quality.plugin_load
python -m pytest tests/test_plugin_load_gate.py -q
python -m pytest plugins/pwp/tests/test_visual_fixture_harness.py plugins/pwp/tests/test_theme_validator.py plugins/pwp/tests/test_theme_diff.py -q
```

If the exact same system verifier prompt repeats after a successful ad-hoc verifier, do not cite the prior verifier as sufficient. Generate a new OS-safe `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` script and rerun the focused assertions. The detector is looking for fresh tool output, not logical continuity.

## Pitfall

If the command emits multiple JSON blocks, parse robustly: scan stdout for a JSON object with the expected discriminator (for example `themeId`) rather than assuming the first or last `{` starts the manifest. JSON printed by a run phase can precede the final manifest.