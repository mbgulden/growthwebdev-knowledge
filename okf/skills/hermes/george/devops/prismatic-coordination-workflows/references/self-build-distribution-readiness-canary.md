# Self-build distribution-readiness canary

Session-derived pattern for continuing Prismatic self-build when the planned product canary is blocked by tracker/dependency truth, but a narrow infrastructure readiness defect is available.

## Trigger

Use this pattern when:

- the next planned issue is blocked by phase-order dependencies or contradictory tracker state/labels;
- current main has a narrow distribution/readiness verifier defect that blocks portability proof;
- the defect can be isolated to one or two non-production paths; and
- Michael has authorized supervised Prismatic self-build / merge-worthy PRs, but not production deploys, Linear mutations, cap increases, or generic dispatch.

## Coordination rule

Do **not** launch a planned canary when live source truth contradicts its policy or prerequisites. Treat labels such as `dispatch:ready` and parent `Done` states as untrusted if children are still active or the issue description says not to mark ready yet.

If a safe infrastructure blocker exists, continue the self-build loop with a bounded readiness repair instead of idling or forcing the blocked product canary.

## Producer contract shape

A good cap-1 readiness-repair task contract includes:

```text
TASK=<self-build slice id>
PURPOSE=<single verifier/readiness defect>
BASE=<current origin/main SHA>
WORKSPACE=<clean worktree>
BRANCH=<focused branch>
PRODUCERS=1
ALLOWED_CHANGED_PATHS=<exact list, usually script + test>
FORBIDDEN=<commit/push/PR/merge/deploy/restart/Linear/generic dispatch/cap raise>
```

Require the producer to report real command results and remaining readiness failures separately from the repaired traceback/defect.

## PEP 639 project.license normalization pitfall

Distribution-readiness scripts must accept current PEP 639 string-form metadata:

```toml
license = "AGPL-3.0-only"
```

If legacy compatibility is needed, accept only exact built-in table form with exact built-in string `text`:

```toml
license = { text = "AGPL-3.0-only" }
```

Do not assume `project.license` is a dict and call `.get("text")` directly. Use one pure normalizer shared by all call sites.

Security/test expectations for the normalizer:

- exact built-in `str` returns stripped value;
- exact built-in `dict` with exact built-in string `text` returns stripped value;
- missing, bool, list, file-only table, malformed table, non-string text, custom `str` subclass, and custom `dict` subclass return empty string without raising;
- exact built-in dicts with custom string-subclass keys must also return empty string without invoking `__eq__` or other comparison hooks;
- no license-file reads, SPDX inference, metadata rewrites, weakened required-license checks, or Docker-label semantic changes;
- importing the script as a module has no command execution or filesystem-write side effect.

Implementation trap: do not use `.get("text")`, `"text" in table`, `set(table)`, sorted keys, or any comparison-driven lookup on untrusted dictionary keys. For the legacy table case, first require `type(value) is dict and len(value) == 1`, pull the sole `(key, text)` with `next(iter(value.items()))`, require `type(key) is str`, and only then compare `key == "text"`. Add a hostile `str`-subclass key whose `__eq__` raises to prove the hook never executes.

## Python-version compatibility pitfall

Distribution-readiness helpers are exercised by the declared GitHub CI Python matrix, not only the local interpreter. If a new test imports a script that reads `pyproject.toml`, Python 3.10 will fail on unconditional `import tomllib` even when local Python 3.11/3.12 passes.

Use the standard fallback pattern when Python 3.10 remains supported and `tomli` is already declared:

```python
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised through import-hook regression
    import tomli as tomllib  # type: ignore[no-redef]
```

Add a regression that forces `tomllib` unavailable through an import hook and proves the module uses the `tomli` fallback. Treat CI failure on this as a same-slice Repair-1: prior CI/review evidence is stale after the repair commit, so refresh exact-head CI and exact-head independent review before merge.

## Verification packet

Label these separately:

```text
COMMAND=python3 -m py_compile <script> <test>
RESULT=<PASS|FAIL>
AD_HOC_OR_CANONICAL=ad-hoc focused

COMMAND=uvx ruff check <script> <test>; uvx ruff format --check <script> <test>
RESULT=<PASS|FAIL>
AD_HOC_OR_CANONICAL=ad-hoc focused

COMMAND=PYTHONPATH="$PWD" python3 -m pytest -q <focused test>
RESULT=<PASS|FAIL>
AD_HOC_OR_CANONICAL=ad-hoc focused

COMMAND=PYTHONPATH="$PWD" python3 -m pytest -q tests/
RESULT=<PASS|FAIL>
AD_HOC_OR_CANONICAL=canonical suite

COMMAND=python3 scripts/distribution_readiness_smoke.py
RESULT=<PASS|FAIL|BLOCKED>
AD_HOC_OR_CANONICAL=distribution readiness smoke
NOT_CLAIMING=clean-room portability unless the full clean-room install/boot/dashboard/canary/backup/rollback proof also passed

COMMAND=python3 scripts/release_check.py; uvx --from build pyproject-build --outdir <tmp>
RESULT=<PASS|FAIL>
AD_HOC_OR_CANONICAL=release/package proof
```

If the readiness smoke exits non-zero after the parser crash is fixed, preserve the failure as a remaining readiness issue; do not weaken readiness checks to produce green output.
