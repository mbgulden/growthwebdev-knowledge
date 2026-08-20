# Clean wheel install provenance for exact-byte Prismatic review

Use this reference when a Prismatic exact-byte packet claims wheel/package install proof. The durable lesson is not that pip failed; it is that install proof can be ambiguous if the verification runs from the source tree or with source metadata/PYTHONPATH visible.

## Failure shape

A wheel smoke may appear to install and import successfully while pip reports some form of same-version/source-tree shortcut, or while Python imports from the candidate source checkout instead of the installed wheel. That evidence is insufficient for an acceptance packet because it does not prove packaged bytes can run after installation.

## Required clean install pattern

1. Build the wheel from the candidate/reconstruction bytes.
2. Create a fresh temporary venv outside the source checkout.
3. Run `pip install --force-reinstall --no-cache-dir <wheel>` from an unrelated directory, not from the source tree or archive root.
4. Run the smoke from that unrelated directory with `PYTHONPATH` removed.
5. Inspect the pip install log and assert:
   - it contains a successful install of the target package/version;
   - it does **not** contain an `already installed with the same version` shortcut or equivalent same-version skip.
6. In the smoke, assert the imported module path is under the fresh venv `site-packages`, not the worktree/archive.
7. Hash the installed module bytes and compare to the candidate source/module hash when exact-byte provenance matters.
8. Run the required behavioral smokes from the installed package, then write a concise proof log with the wheel hash, install mode, module path, installed-module hash, and behavioral markers.

## Minimal proof markers

```text
INSTALL_MODE=non-editable-force-reinstall
SOURCE_PYTHONPATH_VISIBLE=false
PIP_CONFIRMED_<PACKAGE>_INSTALL=true
PIP_ALREADY_INSTALLED_SHORTCUT=false
INSTALLED_MODULE_PATH=<fresh-venv>/lib/.../site-packages/<module>.py
INSTALLED_MODULE_SHA256=<sha256>
CANDIDATE_MODULE_SHA256=<sha256>
WHEEL_SHA256=<sha256>
RESULT=PASS
```

## Pitfalls

- Do not run the install smoke from the source checkout and then treat `import package` as installed-package proof.
- Do not rely only on `pip install` exit code; read the install log for same-version shortcuts.
- Do not assume `python -m build` wheel bytes equal the imported module; bind the installed path and hash.
- If a smoke fails because it called the wrong public function or asserted the wrong response shape, inspect the installed API and rerun the installed-package smoke without changing candidate source.
