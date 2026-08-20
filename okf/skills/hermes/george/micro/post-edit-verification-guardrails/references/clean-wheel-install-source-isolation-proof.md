# Clean-wheel install/source-isolation proof

Use when a Prismatic review blocks evidence because an installed-wheel check may have imported or short-circuited from source-tree metadata instead of proving the packaged artifact.

## Pattern

1. Build from a clean reconstruction/source tree into a separate `dist/` directory.
2. Create a fresh venv and an unrelated outside working directory.
3. From the outside directory, run pip with source import paths removed:
   - `env -u PYTHONPATH <venv>/bin/pip install --no-cache-dir --force-reinstall <wheel>`
4. Fail the proof if pip reports the source shortcut:
   - `! grep -q 'already installed with the same version' <log>`
5. Assert the expected install marker appears:
   - `grep -q 'Successfully installed .*<package>' <log>`
6. From the same outside directory with `PYTHONPATH` unset, import the target module and assert:
   - `Path(module.__file__).resolve()` lives under the fresh venv/site-packages path, not the source tree.
   - The installed module SHA equals the candidate source SHA.
   - Required behavior smokes pass from the installed wheel.
7. Record wheel SHA, installed-module SHA/path, log path/SHA, install mode, and explicit non-claims.

## Proof packet fields

```text
WHEEL_SHA256=<sha256>
INSTALL_MODE=non-editable-force-reinstall
SOURCE_PYTHONPATH_VISIBLE=false
PIP_ALREADY_INSTALLED_SHORTCUT=false
INSTALLED_MODULE_PATH=<fresh-venv-site-packages-path>
INSTALLED_MODULE_SHA256=<sha256>
CANDIDATE_MODULE_SHA256=<sha256>
BEHAVIOR_SMOKE=<PASS|FAIL>
LOG=<path>
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted packaging proof
NOT_CLAIMING=canonical suite green
```

## Pitfalls

- Running `pip install <wheel>` while the current directory is the source/archive root can produce misleading "already installed with the same version" evidence. Treat that as blocked evidence and rerun from an unrelated directory.
- Removing `PYTHONPATH` alone is not enough if the interpreter/venv already has the package installed. Use a fresh venv and assert `module.__file__`.
- Do not invent convenience API calls for wheel smoke tests. Inspect the actual public API/return shape, then smoke a minimal real behavior path.
- If source bytes are unchanged but evidence was flawed, preserve the inaccurate packet as blocked provenance and freeze a new packet with corrected evidence only.
