# Session reference: 2026-07-28 `write_file` token corruption + `ruff --fix` scope pitfall

Two tooling patterns bit hard enough to be worth writing down once.

## 1. `write_file` / `patch` silently neutralizes literal strings

Symptom: a Python source file produced via `write_file` contained
`b"Authorization: *** ${auth}"` where the literal token string was
expected to be `"Authorization: …"`. The file renders as ASCII but the
literal string is mangled in a way that survives every Python-side
`str.replace` you try.

Recovery:

- `cat -v` and `grep -n 'Authorization'` show the line is intact *as
  characters* — but the substituted token is gone. So you can't patch
  with `data.replace('old', 'new')`.
- Use **byte-level** `replace` with `data.encode()` / `data.replace()`:
  ```python
  data = open(path, 'rb').read()
  needle = b'Authorization: *** ${auth}\` }'
  data = data.replace(needle, b"\"Authorization\": \"Bearer \" + auth")
  open(path, 'wb').write(data)
  ```
- If the corrupted literal is the same token-shaped string that the
  platform redacts, the bytewise replacement will fail when the source
  itself has been mangled. In that case, rewrite the **entire file** with
  `write_file` (don't patch) and avoid the literal altogether — build
  the string from variables.

Diagnostic that almost always pinpoints the issue:

```python
data = open(path, 'rb').read()
idx = data.find(b'<expected literal>')
print(f'offset: {idx}')
print(data[max(0,idx-50):idx+50])
```

If `idx == -1`, the literal is not in the file — your `replace` failed
because the source was already mangled by `write_file`.

Cleaner pattern: never write a literal token-shaped string in source.
Compose it at runtime:

```python
# Avoid: literal in source
headers = {"Authorization": "Bearer " + token}
# Avoid: literal in JSON dumped to file
# Instead: parameterized JSON
```

## 2. `ruff check --fix` and `ruff format` are scope-blind

Symptom: in a lane-locked repo (e.g. `prismatic-pwp-ubersuggest-auth`),
running `ruff check --fix` without `--exclude` or a path argument
reformats **hundreds of unrelated files** (most of `prismatic/`, `bin/`,
`portable-skills/`, plugin-blueprints). The next commit attempt then
fails with class-level checks:
- `Path Portability Failure: Absolute path '/home/ubuntu' found in
  <file>…` — for files I never touched.
- `🚨 Commit aborted. Hardcoded paths detected.`

The critical lesson: **`ruff --fix` walks the whole repo by default.** It
will fold and break dependency on `imports/` outside the agent's lane.

Safe pattern:

```bash
# Run on the new files only — exactly the lane.
ruff check --fix plugins/pwp/capabilities/publish_kpi_tracker/
ruff format  plugins/pwp/capabilities/publish_kpi_tracker/

# If a repo-wide sweep is unavoidable, **commit before** the sweep so
# `git restore` is one step away.
git add -A && git commit -m "..."
ruff check --fix .
# Then immediately:
git status --porcelain | awk '{print $2}' | grep -v '<expected lane>' | xargs -r git checkout --
```

The `git checkout --` step is the recovery hatch. Without it, the
unrelated reformatting ends up in the diff and the lane guard produces
fresh failures on the next commit.

## 3. Pre-commit gate hierarchy — two layers, easy to confuse

In lane-locked repos the commit gate is two checks:

1. **Path portability gate** — fails on `Absolute path '/home/…' found in
   <file>`. This is per-file, regex-based, and *additive*: a single
   stray literal anywhere in the working tree aborts the commit.
2. **Lane guard** — fails on `Engine] Lane violation by <agent>: <files>,
   owned directories: [...]`. This is per-agent-per-file: the agent's
   lane (e.g. `scripts/`, `prismatic/`, `plugins/`) dictates which files
   the agent can add. A single file outside the lane aborts the commit.

Both gates fail independently. When a commit fails, check which
message was the actual abort:

- "Path Portability Failure" → find the offending literal.
- "Lane violation" → `git restore` the file outside your lane.

The same commit can pass gate 1 and fail gate 2 (or vice versa). Read
the abort message carefully; the lane-violation message lists owned
directories explicitly.
