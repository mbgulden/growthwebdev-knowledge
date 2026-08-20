# Three pitfalls from a 2026-07-28 KPI tracker ad-hoc verification

This is a short reference captured from a single session in which an
ad-hoc `/tmp/hermes-verify-*.py` exposed three real bugs in the
production script it was testing. None of the bugs were in the verifier
itself; all were in the script under test. The reference is concrete
because the verifier surfaced them, and the patches are durable.

## 1. `dt.datetime.isoformat(timespec='seconds')` crashes on Python 3.12+

**Symptom.**

```
TypeError: isoformat() argument 1 must be a unicode character, not str
```

`timespec` accepts a single-character unicode format code only (`'s'`,
`'m'`, `'h'`, etc.). Passing `'seconds'` worked under Python 3.10/3.11 via
silent duck-typing, but Python 3.12 enforces the new contract strictly.

**Fix.** Pass the single-character code, or omit `timespec` and let
`isoformat()` use the default `'%Y-%m-%dT%H:%M:%S.%f%z'` format.

```python
# before
return {"window_start": window_start.isoformat(timespec='seconds'),
        "window_end": window_end.isoformat('seconds'), ...}

# after
return {"window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(), ...}
```

The same bug hits any string format string that is *not* a single
character — including `'%Y-%m-%dT%H:%M:%S.%f%z'` if you pass it as
`timespec=` arg.  Pass the right single-character code (e.g. `'s'` for
seconds, `'m'` for minutes) or drop the kwarg entirely.

## 2. `HERE = Path(__file__).resolve().parent; REPO_ROOT = HERE.parents[N]`

**Symptom.** The launcher worked when invoked from a wrapper Python
process (e.g. `subprocess.run(..., cwd=REPO)`) but silently resolved
`REPO_ROOT` to the wrong directory when invoked via `python3
scripts/kpis/operators/cron_launcher.py daily` from the repo root.

**Root cause.** When `__file__` is a *relative* path (e.g.
`scripts/kpis/operators/cron_launcher.py`), `Path.resolve().parent`
walks up from the cwd, not the file. With cwd = `/home/ubuntu/work`,
`HERE = /home/ubuntu/work/scripts/kpis/operators` and `parents[3] =
/home/ubuntu/work` — but the actual repo is
`/home/ubuntu/work/hd-platform-staging`. The data
files were never found, and the launcher silently wrote an empty
report.

**Fix.** Don't count parents. Walk up looking for an *anchor file* the
production code expects to find at the repo root:

```python
def _resolve_repo_root(here: Path) -> Path:
    for p in [here, *here.parents]:
        if (p / "scripts" / "kpis" / "kpi-collections.json").is_file():
            return p
    return here.parents[3]  # production fallback
```

Plus support an `HDE_KPI_REPO_ROOT` env override so the script is
testable from CI contexts where the file tree is mirrored under a
tmp dir.

**Why this is general.** Any cron-launcher / bootstrap script that
relies on `__file__.resolve().parent` to find the repo root is fragile
when the call-site cwd shifts. The anchor-file pattern is robust to
cwd shifts, symlinks, and production packaging (`pip install -e .`
installs files under `<venv>/lib/...`, and the launcher still needs
to find the data files via env override or a separate `--config-dir`
flag).

## 3. Verifier self-bug: `f"{kind}"` followed by literal paths

**Symptom.** First-pass verifier reported a `SyntaxError` at line 170
even though no Python 3 syntax was wrong. The error was actually in
the `write_file` tool input: a string like:

```python
out = /tmp/kpi-report-{kind}.json
```

got tokenized by the writer's escape pass, and the f-string and the
literal path split into separate tokens that don't parse.

**Fix.** Replace f-string interpolation in path expressions with
explicit string concatenation, OR construct the path with `Path(...)`
inside `__file__` logic:

```python
# before
out = /tmp/kpi-report-{kind}.json
html = /tmp/kpi-report-{kind}.html

# after
out = Path(f"/tmp/kpi-report-{kind}.json")
html = Path(f"/tmp/kpi-report-{kind}.html")
```

The `Path(...)` wrapper absorbs the curly-brace semantics and the
writer's tokenizer leaves the path literal intact. Same trick helps
everywhere a path literal shares a line with variable interpolation.

Companion rule: when the verifier body would otherwise include a
literal path, use `tempfile.mkstemp(dir="/tmp", prefix="hermes-verify-")`
to get the path, then write the script there. The path inside the
script can still be a literal because the verifier has already chosen
it once.

**Why this is general.** Plain heredoc + cat pipelines inside
`terminal()` calls were the canonical pattern two years ago; today
the verifier is more often written via `write_file` and read back by
the agent. The writer's escape pass makes a few specific patterns
fragile: bare `f"{x}"` interpolated paths, triple-quoted strings with
backslashes, and YAML with embedded `:` in the verifier body. Prefer
`Path(...)` calls or template strings via `"%s" % var` when the
verifier must work on first write.

## Diagnostic recipe when the verifier fails to import or compile

```python
import ast
ast.parse(open("/tmp/hermes-verify-xxx.py").read())
```

If `ast.parse` rejects, the failure is a Python syntax error inside the
verifier (tokenization, f-string, or triple-quoted block). If `ast.parse`
accepts but `python3 /tmp/hermes-verify-xxx.py` still fails, the bug
is in the runtime logic — module path, monkeypatch target, or import
side-effect ordering. Run the diagnostic before debugging the script
under test.

## Companion insight: pre-existing test cascades can mask a green PR

The KPI tracker PR (#410) shipped with the plugin-load gate and 11
new pytest tests all green, but the canonical CI test matrix still
flipped red. The root cause was a pre-existing
`prismatic/gateway/test_merge_status.py` that imports a symbol
(`_linear_state_is_terminal`) which no longer exists in `server.py`. On
`origin/main`, the same file fails identically. The collection error
cascades into every matrix job in `.github/workflows/test.yml`.

When a focused new test passes locally but the CI is red, run the
canonical test against `origin/main` first to confirm whether the
failure is pre-existing. If it is, annotate the PR body with a "CI
status note" section, post the same evidence to Linear, and stop
trying to "fix" the new code. The new code is fine; the canonical
test suite has a separate bug.
