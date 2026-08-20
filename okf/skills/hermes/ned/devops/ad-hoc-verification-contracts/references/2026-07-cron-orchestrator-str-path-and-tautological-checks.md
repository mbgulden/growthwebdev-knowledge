# Three verifier pitfalls from a 2026-07-29 KPI Hub cron orchestrator audit

This is a session-specific reference captured during an audit of the
PWP plugin's cron orchestrator and GA4 resolution. Each pitfall was
surfaced by the same fresh `/tmp/hermes-verify-gap5-gap7.py` script
that the platform demanded after a push.

The first two pitfalls are **verifier bugs** that produced false
fails. The third pitfall is a **production bug** that the verifier
caught because pytest missed it. Reading all three in order shows how
verifier discipline turns into shipped code fixes.

## A. Inline `subprocess.run([python3, "-c", code])` needs its own imports

**Symptom.**

```
[FAIL] dispatch command runs  (rc=1: Traceback (most recent call last):
  File "<string>", line 39, in <module>
NameError: name 'Path' is not defined
)
```

The embedded `python3 -c "..."` block referenced `Path(...)` but only
the **outer** script had `from pathlib import Path`. The embedded
block runs in a fresh interpreter with no enclosing namespace, so any
name used inside it must be imported inside the block:

```python
# outer (top of /tmp/hermes-verify-gap5-gap7.py)
from pathlib import Path

dispatch_check = subprocess.run(
    [sys.executable, "-c", """
from pathlib import Path     # <-- REQUIRED inside the embedded block
import sys
sys.path.insert(0, '/path/to/worktree')
# ... uses Path(...) ...
"""],
    capture_output=True, text=True,
)
```

**Fix.** Add the import inside the embedded block. Anything reachable
in the outer script is **not** reachable inside the embedded block.

This is the most common silent verifier bug when the verifier mixes
inline subprocess calls with real Python assertions. Other names hit
by the same trap: `datetime`, `json`, `re`, `os`, `sys`, anything
from a third-party import.

## B. Tautological checks always pass — assert concrete expected values

**Symptom.** A group-1 verifier check for the env-var-only contract
read:

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
- The `and` therefore evaluates to `False` — failing the assertion
  for the wrong reason.
- The actual contract under test (env-var resolved the right ID) is
  not what this check measures.

**Fix.** Assert concrete expected values:

```python
check(
    "Both sites resolve via env to the right GA4 IDs",
    by_slug.get("active-oahu", {}).get("tracking_property") == "G-PRRRLMBR8Z"
    and by_slug.get("hd-engine", {}).get("tracking_property") == "G-Q6TPL08VM7",
    f"aot={by_slug.get('active-oahu', {}).get('tracking_property')} hde={...}",
)
```

**Rule of thumb.** Every `assert` should fail loudly when the contract
is wrong. If a check can pass for reasons unrelated to the contract
being tested, it is a tautology and must be rewritten.

Common tautology shapes to watch for:

- `all(X and "marker" in str(X) for ...)` where `X` is a non-string.
- `ok(len(result) > 0 and result)` — the second clause is redundant.
- `ok(result == result)` — always passes.
- `ok(some_dict.get("key"))` — passes even when the value is `None`
  and `None` is not a valid success state.

The platform's verifier discipline explicitly calls this out: "the
verifier may not reproduce the same harness ... as the real test." A
verifier that reproduces the wrong contract is worse than no
verifier — it gives a false-positive signal that the change is fine.

## C. The verifier is a bug-finder — let it surface production defects

The same verifier that false-failed on (A) and (B) then crashed on
the **next** group with:

```
Traceback (most recent call last):
  File "<string>", line 36, in <module>
  File ".../cron_orchestrator.py", line 222, in run
    publish_root.mkdir(parents=True, exist_ok=True)
    ^^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'mkdir'
```

This was a **real production bug**, not a verifier bug. The function
signature said `publish_root: Optional[Path] = None`, but `argparse`
passes strings — and `publish_root or Path(...)` short-circuits on a
non-empty string, leaving `publish_root` as a `str`. The next line
called `.mkdir()` on it.

The canonical pytest suite missed this because every test passed a
`Path` directly to `run()`. The string path was only reachable
through `argparse`, which the tests did not exercise.

**The fix (three parts).**

1. Widen the type signature: `publish_root: Optional[PathLike] = None`
   where `PathLike = Union[Path, str]`. Same for `registry_path` and
   `launcher`.
2. Coerce at the function entry, not at every call site:

   ```python
   if publish_root is None or publish_root == "":
       publish_root_path = Path("/tmp/pwp-kpi-runs") / kind
   else:
       publish_root_path = Path(publish_root)
   publish_root_path.mkdir(parents=True, exist_ok=True)
   ```
3. Add a regression test that **passes a string** to lock the
   coercion behavior in:

   ```python
   def test_run_coerces_string_publish_root(tmp_path, monkeypatch):
       publish_root_str = str(tmp_path / "string-publish-root")
       manifest = orch.run(
           kind="daily",
           publish_root=publish_root_str,  # str, not Path
           launcher=tmp_path / "stub_launcher.py",
       )
       assert manifest["publish_root"] == publish_root_str
       assert (tmp_path / "string-publish-root").is_dir()
   ```

**Why this matters.** The "release-time" verifier pattern (canonical
command + fresh `/tmp/hermes-verify-*` script) is the durable place
to catch CLI/argparse boundary bugs that unit tests typically pass
through as `Path` instances. A unit test that calls the function with
`Path("/tmp/...")` will never reproduce what happens when `argparse`
hands the function `"--publish-root /tmp/..."` as a string.

This is the **highest-value outcome** of running a fresh ad-hoc
verifier after a push: it exercises paths the test suite did not,
including the boundary between the CLI parser and the function under
test. Three real lessons in one verifier run: the path-coercion bug
was the actual product fix; (A) and (B) were verifier self-bugs that
the platform rightly flagged before the verifier could surface (C).

## Diagnostic recipe recap

When a verifier fails on the first run, classify the failure
*before* changing the production code:

| Failure shape | Class | Action |
|---|---|---|
| `NameError: name 'X' is not defined` in `subprocess.run([python3, "-c", ...])` | (A) verifier import bug | Add the import inside the embedded block |
| `assert ok_(...)` with a passing/failing `all(X and "marker" in str(X) ...)` | (B) tautological check | Rewrite to assert concrete expected values |
| `AttributeError: 'str' object has no attribute 'X'` from production code | (C) real bug | Patch production code, widen the type, add a regression test |
| `ImportError: cannot import name 'X' from partially initialized module` when wiring orchestrator + steps | (D) circular import | Extract `X` to `types.py`, both modules import from it |
| Commit gate aborts with "Path Portability Failure: Absolute path '/home/ubuntu'" | (E) hardcoded path in new code | Replace with env-var fallback or relative `Path(__file__).parent` |
| `git add plugins/.../foo.py` errors with "pathspec ... is beyond a symbolic link" | (F) symlink trap | Stage via `prismatic/shipped_plugins/...` instead |

The discipline: every verifier failure is a hypothesis. Classify
first, then patch.

## Related files in this skill

- `references/2026-07-python-312-isoformat-and-here-parents-pitfalls.md`
  — three earlier pitfalls from a 2026-07-28 KPI tracker verification
  (the verifier as bug-finder for `isoformat(timespec='seconds')`,
  `HERE.parents[N]` path brittleness, and `write_file` tokenizer
  corruption of f-string interpolated paths).