# Three verifier pitfalls from a 2026-07-29 provision_site Phase 1 audit

This is a session-specific reference captured during the build of
the `provision_site` capability under `prismatic-pwp-ubersuggest-auth`.
The pitfalls surfaced by the fresh
`/tmp/hermes-verify-provision-site.py` script run after the commit
gate accepted the work. Reading in order shows how verifier
discipline catches both verifier self-bugs and genuine production
issues in the same run.

## A. Inline `subprocess.run([python3, "-c", code])` needs its own imports

**Symptom.**

```
[FAIL] ORDER:OK  (present in verifier output)
[FAIL] STOP_ON_FAIL:OK  (present in verifier output)
[FAIL] RESUME:OK  (present in verifier output)
```

The embedded `python3 -c "..."` block referenced `Path(...)` but
only the **outer** script had `from pathlib import Path`. The
embedded block runs in a fresh interpreter with no enclosing
namespace, so any name used inside it must be imported inside
the block:

```python
# outer (top of /tmp/hermes-verify-provision-site.py)
from pathlib import Path

rc, out, _ = run([
    sys.executable, "-c", """
from pathlib import Path     # <-- REQUIRED inside the embedded block
import sys
sys.path.insert(0, '/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/plugins')
# ... uses Path(...) ...
"""],
)
```

**Fix.** Add the import inside the embedded block. Anything
reachable in the outer script is **not** reachable inside the
embedded block. This is the most common silent verifier bug when
the verifier mixes inline subprocess calls with real Python
assertions. Other names hit by the same trap: `datetime`, `json`,
`re`, `os`, `sys`, anything from a third-party import.

## B. Tautological checks always pass — assert concrete expected values

A group-1 check for the env-var-only contract originally read:

```python
check(
    "Both sites report tracking_property_source=env (not literal)",
    all(
        by_slug.get(s, {}).get("tracking_property") and "env" in str(
            by_slug.get(s, {}).get("tracking_property")
        )
        for s in ("active-oahu", "hd-engine")
    ),
    "env-var-only contract holds",
)
```

The check looks robust but is a **tautology**:

- `<the value>` is the GA4 measurement ID (e.g. `"G-PRRRLMBR8Z"`).
- `"env" in str("G-PRRRLMBR8Z")` is `False`.
- The `and` therefore evaluates to `False` — failing the
  assertion for the wrong reason.
- The actual contract under test (env-var resolved the right ID)
  is not what this check measures.

**Fix.** Assert concrete expected values:

```python
check(
    "Both sites resolve via env to the right GA4 IDs",
    by_slug.get("active-oahu", {}).get("tracking_property") == "G-PRRRLMBR8Z"
    and by_slug.get("hd-engine", {}).get("tracking_property") == "G-Q6TPL08VM7",
    f"aot={by_slug.get('active-oahu', {}).get('tracking_property')} hde={...}",
)
```

**Rule of thumb.** Every `assert` should fail loudly when the
contract is wrong. If a check can pass for reasons unrelated to
the contract being tested, it is a tautology and must be
rewritten.

Common tautology shapes to watch for:

- `all(X and "marker" in str(X) for ...)` where `X` is a non-string.
- `ok(len(result) > 0 and result)` — the second clause is redundant.
- `ok(result == result)` — always passes.
- `ok(some_dict.get("key"))` — passes even when the value is `None`
  and `None` is not a valid success state.

## C. The verifier is a bug-finder — let it surface production defects

The provision_site verifier surfaced a different class of bug
than the cron-orchestrator one. The orchestrator's
`step_verify_domain` was wired with a circular import that
silently broke at runtime:

```
ImportError: cannot import name 'StepResult' from partially
initialized module 'plugins.pwp.capabilities.provision_site.orchestrator'
(most likely due to a circular import)
```

**The diagnosis.** `orchestrator.py` imported `from . import steps
as step_module` for the lazy step-fn lookup. `steps/__init__.py`
imported `from ..orchestrator import StepResult` for its return
type. Python's import machinery handled the cycle but
`StepResult` was a `None` placeholder inside `steps/__init__.py`
at the moment the first `StepResult(name=..., status="complete")`
was constructed.

**The fix.** Extract shared dataclasses to `types.py`:

```python
# types.py
@dataclass
class StepResult: ...
@dataclass
class ProvisionRun: ...

# orchestrator.py
from .types import ProvisionRun, StepResult  # both directions resolve
from . import steps as step_module

# steps/__init__.py
from ..types import StepResult
```

The rule for any new PWP capability: if the orchestrator
references dataclasses that step functions also reference, the
shared types go in `types.py`. Orchestrator and steps import from
`types.py` only — never from each other.

This bug never appeared in pytest because every test in
`test_provision_site.py` constructed `StepResult` directly with
the dataclass — there was no chain of imports through
`steps/__init__.py`. The full pipeline (`orchestrator.run()` →
`_run_step()` → `steps.step_<name>()` → `StepResult(...)`) is
what exposed the partial-init state.

## D. Commit gate catches path portability, not the verifier

The provision_site work also surfaced a class of bug that lives
**outside the verifier's reach**: the **Prismatic Commit Gate**
runs before the verifier ever sees the change.

```
❌ Path Portability Failure: Absolute path '/home/ubuntu' found
   in prismatic/shipped_plugins/pwp/capabilities/provision_site/steps/migrate.py
🚨 Commit aborted. Hardcoded paths detected.
```

The agent had written:

```python
# BAD — gate aborts the commit.
return Path("/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/config/seo_sites.json")
appendix = Path("/tmp/pwp-provisioning/sites.json")
```

The fix is to use env-var fallbacks:

```python
# GOOD
return Path("config/seo_sites.json")  # relative, walks up
appendix_env = os.environ.get("PWP_PROVISIONING_ROOT", "").strip()
appendix = Path(appendix_env) / "sites.json" if appendix_env else Path("/tmp/pwp-provisioning/sites.json")
```

When the gate fires, the error names every offending file path.
Fix all of them in one commit; the gate will pass on retry without
re-running the test suite. The verifier should also include a
literal scan that asserts no test fixture or stub path contains
`/home/ubuntu/` — so the verifier catches the same class of bug
the gate catches, independently of which one runs first.

## E. The `plugins/` symlink trap

In `prismatic-pwp-ubersuggest-auth`, `plugins/` is a git symlink
to `prismatic/shipped_plugins/`. The following error fires when
the agent stages through the symlink:

```
fatal: pathspec 'plugins/pwp/capabilities/provision_site/__init__.py'
is beyond a symbolic link
```

The canonical path is `prismatic/shipped_plugins/...` — `git
add` follows the symlink at the index level. For terminal writes
(`cat > file`), use the absolute path under
`prismatic/shipped_plugins/` so the write lands on the inode git
sees.

This was a fresh pitfall surfaced by the provision_site work;
the previous cron-orchestrator and KPI-tracker turns avoided it
because their files were already in place before this session
started.

## Diagnostic recipe recap (extended)

| Failure shape | Class | Action |
|---|---|---|
| `NameError: name 'X' is not defined` in `subprocess.run([python3, "-c", ...])` | (A) verifier import bug | Add the import inside the embedded block |
| `assert ok_(...)` with a passing/failing `all(X and "marker" in str(X) ...)` | (B) tautological check | Rewrite to assert concrete expected values |
| `AttributeError: 'str' object has no attribute 'X'` from production code | (C) real bug (production) | Patch production code, widen the type, add a regression test |
| `ImportError: cannot import name 'X' from partially initialized module` when wiring orchestrator + steps | (D) circular import | Extract `X` to `types.py`, both modules import from it |
| Commit gate aborts with "Path Portability Failure: Absolute path '/home/ubuntu'" | (E) hardcoded path | Replace with env-var fallback or relative `Path(__file__).parent` |
| `git add plugins/.../foo.py` errors with "pathspec ... is beyond a symbolic link" | (F) symlink trap | Stage via `prismatic/shipped_plugins/...` instead |

The discipline: every verifier failure is a hypothesis. Classify
first, then patch.

## Related files in this skill

- `references/2026-07-python-312-isoformat-and-here-parents-pitfalls.md`
  — three earlier pitfalls from a 2026-07-28 KPI tracker verification
  (the verifier as bug-finder for `isoformat(timespec='seconds')`,
  `HERE.parents[N]` path brittleness, and `write_file` tokenizer
  corruption of f-string interpolated paths).
- `references/2026-07-cron-orchestrator-str-path-and-tautological-checks.md`
  — three patterns from a 2026-07-29 KPI Hub cron orchestrator audit
  (the cron-orchestrator `Path`/`str` bug, the verbose `subprocess.run`
  embed, the tautology-vs-assertion shape).