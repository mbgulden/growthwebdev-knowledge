# Tempfile detector residue and exact failure parity

Use this when a post-edit guard repeatedly lists a disposable `/tmp/hermes-verify-*` probe as a changed path, or when a baseline-red canonical suite must be compared between immutable base and candidate.

## Detector residue pattern

A valid guard-compatible repair verifier can still trigger a follow-up detector warning if the tool layer records the temporary probe as a modified path before it notices cleanup. The safe response is not to argue from memory first:

1. Allocate the probe with `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`.
2. Run it through a recognizable top-level command such as `python -m pytest -q /tmp/hermes-verify-*.py` or project-venv `pytest -q /tmp/hermes-verify-*.py`.
3. Run at least one direct focused project command against the real changed files (`pytest`, `ruff`, build, compile, or `git diff --check` as appropriate).
4. Remove the disposable probe, then assert `test ! -e /tmp/hermes-verify-*.py` in the final proof command.
5. Keep logs, not the disposable probe; hash the logs.
6. If the same warning repeats after a visible current-turn compliant rerun, classify it as detector ingestion stale/blocker and stop looping. If the current user task forbids non-skill tools, do not violate that boundary; save this lesson and state no verifier rerun was attempted.

## Canonical baseline-red parity

When the canonical suite is red on both immutable base and candidate, compare exact failure identities before claiming zero new regressions.

Avoid lossy extraction such as `^FAILED ([^ ]+)` if pytest failure lines include parametrized cases, expanded descriptions, or suffixes that distinguish failures. Prefer complete line capture:

```python
import re
from pathlib import Path

def failed_lines(log: Path) -> list[str]:
    return sorted(re.findall(r"^FAILED (.+)$", log.read_text(), re.M))

base = failed_lines(Path("/tmp/base.log"))
candidate = failed_lines(Path("/tmp/candidate.log"))
assert len(base) == len(candidate)
assert base == candidate
```

Report this as failure-set parity only, not canonical green:

```text
CANONICAL_SUITE=<passed>,<failed>,<skipped>
IMMUTABLE_BASE_FAILURES=<N>
FAILED_LINE_MULTISET_PARITY=PASS
AD_HOC_OR_CANONICAL=canonical suite run, baseline-red parity only
NOT_CLAIMING=canonical full-suite green
```
