# Bash Heredoc + Backtick Pitfall — Ned GraphQL Mutation Bodies

**Recurrence:** GRO-537 09:33Z pass (17th pass) — re-confirmed the pitfall.
**Parens variant:** 2026-06-30 ~04:50Z (this session — GRO-143 lane-discipline relabel).

## The failure mode

```bash
source /home/ubuntu/.hermes/profiles/ned/.env && python3 << PY
body = """Picked up via `agent:ned` label, ran `finalize_task.sh`..."""
# ...
PY
```

Run via `bash -c '...'`:

```
bash: line 1: agent:ned: command not found
bash: line 1: finalize_task.sh: command not found
Traceback (most recent call last):
  ...
urllib.error.HTTPError: HTTP Error 401: Unauthorized
```

## Why it fails

The outer bash shell interprets backticks in the heredoc body as **command substitution**. It tries to execute `agent:ned`, `finalize_task.sh`, etc., fails with "command not found", and the backtick expression is REPLACED WITH EMPTY in the heredoc body before python sees it. The Python script then sends a malformed GraphQL body to Linear (empty fields where the dequeue labels should be), and the body length / content makes auth fail.

The heredoc body is technically quoted (PY is the delimiter), but bash still does command substitution on backticks before passing the literal to python. Only `$var` expansion is suppressed by heredoc-without-expansion (`<< 'PY'`). Backticks are ALWAYS expanded.

## The fix (always)

```python
# 1. write_file to /tmp/ned_<task>.py with the full body
write_file /tmp/ned_gro537_comment.py "..."
# 2. run with env loaded
source /home/ubuntu/.hermes/profiles/ned/.env && python3 /tmp/ned_gro537_comment.py
```

The Python file is a real file with literal bytes — no shell quoting layer can mangle the backticks.

## When the inline pattern IS safe

`bash -c '... python3 << PY ... PY'` is safe ONLY when the heredoc body has:
- Zero backticks (\`...\`)
- Zero `$` characters (or use `<< 'PY'` and reference env via `os.environ` inside Python)
- No single-quote characters (`'`)
- No escaped double-quotes inside Python strings (the outer `bash -c '...'` would terminate the single-quoted argument)

If any of those conditions fail, write to `/tmp/<name>.py` and run with `python3`.

## Variant: heredoc + parentheses (NOT just backticks)

**Captured:** 2026-06-30 ~04:50Z (GRO-143 lane-discipline relabel — AOT interview).

Even with all backtick precautions satisfied, a heredoc body containing literal
parentheses `()` triggers a different shell parse error:

```bash
bash -c 'cat > /tmp/gro143_comment.json << "EOF"
{
  "body": "Owner: kai-content (when prioritized)."
}
EOF
'
# => bash: line N: syntax error near unexpected token `('
```

**Why:** even inside a quoted heredoc (`<< "EOF"`), bash interprets unbalanced
parens at certain positions in the outer `bash -c '...'` argument as subshell
syntax. The error surfaces at *heredoc write time*, not at python parse time,
so it can be confusing — the shell refuses to write the file at all.

**Triggers seen:**
- Prose like "(when prioritized)", "(see below)", "(optional)" inside JSON
  string values.
- Markdown parenthetical asides.
- Commit messages like `git commit -m "[Ned] foo (GRO-123)"`.
- Issue IDs cited in prose like "GRO-143 (AOT Interview)".

**Fix:** `write_file /tmp/x.json "..."` (the Hermes `write_file` tool writes the
literal bytes with no shell-quoting layer), then `curl -d @/tmp/x.json`. This
sidesteps the bash heredoc parser entirely.

**Why not just use `python3 -c "..."` ?** Same parens trap on `bash -c`. The
`write_file` path is the cleanest escape hatch for Linear comment bodies and
GraphQL mutations that contain prose.

**Rule of thumb:** if the JSON body has any of `()\``$` or unbalanced single
quotes, always use `write_file` to author the JSON payload — never bash heredoc.

## Alternative: `python3 -c` with subprocess

For shorter bodies, the recipe file's pattern also works:

```python
python3 -c "
import json, subprocess
body = '''Picked up via \`agent:ned\` label...'''  # escape backticks with \
print(subprocess.run(['echo', body], capture_output=True).stdout.decode())
"
```

Backticks must be backslash-escaped inside the `python3 -c` argument, which is error-prone for long bodies. The `/tmp/<name>.py` pattern is preferred.

## Detection signals in tool output

If you see:
- `bash: line 1: <word>: command not found` followed by Python traceback → backtick pitfall
- `bash: line N: syntax error near unexpected token `('` → parens pitfall (this variant)
- HTTP 401 from Linear (empty body or malformed body) → likely one of the above
- Python `SyntaxError` on a line that looks valid → likely one of the above

The fix is always: stop using inline heredocs with shell-sensitive characters; switch to `write_file` for the JSON payload + `curl -d @file.json` for the Linear mutation.

## Reference

- GRO-537 09:33Z cron pass — this file's primary trigger (backtick variant)
- GRO-537 12th pass (2026-06-28 ~05Z) — earlier re-occurrence documented in skill SKILL.md "Linear API footguns"
- GRO-143 lane-discipline relabel (2026-06-30 ~04:50Z) — parens variant, this session
- `references/linear-dequeue-graphql-recipe.md` — primary GraphQL mutation recipe (uses subprocess + json.dumps; compatible with this pitfall by avoiding heredocs)