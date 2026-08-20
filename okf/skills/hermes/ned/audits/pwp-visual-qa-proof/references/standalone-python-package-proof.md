# Standalone Python Package Fresh-Clone Proof

Use this for PWP extraction/package gates where a source-layout repository must prove both distribution construction and tests without inherited monorepo imports.

## Reliable sequence

1. Create a clean clone in a parent directory with no sibling `prismatic-engine`; record `HEAD` and tree SHA.
2. Create a fresh build venv and run `env -u PYTHONPATH <venv>/bin/python -m build`. Record both artifact paths and SHA-256 values.
3. Do not run bare system `pytest` against a `src/` layout: collection may fail with `ModuleNotFoundError` even when package code is sound because the package is not installed.
4. For a fresh suite result, create another venv and run:

```bash
python3 -m venv /tmp/<proof>-test-venv
/tmp/<proof>-test-venv/bin/python -m pip install --upgrade pip
cd <fresh-clone>
/tmp/<proof>-test-venv/bin/python -m pip install '.[dev]'
/tmp/<proof>-test-venv/bin/python -m pytest tests -q
```

5. If the task specifically requires wheel-install proof, keep it separate: install `dist/*.whl` non-editably in a clean venv and import from an empty directory with `PYTHONPATH` unset. Editable/source-suite green is not a substitute.

   **Isolation hardening:** before installing the wheel, run `env -u PYTHONPATH <install-venv>/bin/python -c 'import importlib.util; assert importlib.util.find_spec("<package>") is None'`. After installation, assert that `Path(package.__file__)` is under the install venv's `site-packages` and is *not* under `<clone>/src`. Also assert that the fresh-clone parent has no sibling `prismatic-engine` directory. These three assertions rule out preinstalled-package, source-tree, and sibling-checkout false positives.
6. Preserve the exact command, exit code, test count/skips, log path, artifact checksums, candidate SHA/tree SHA, installed-module path, and explicit scope/non-claims in the result packet. If a PR is opened after the proof, re-read both its head SHA and CI checks; post concrete wheel/isolation evidence only after that readback.

## Finalization pitfall

After automated finalization and any evidence-comment mutation, re-read Linear immediately. A workflow automation can move an issue from `In Review` back to `In Progress`; correct the state only after confirming branch push, PR/readback, evidence comment, and lock release.
