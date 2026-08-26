---
name: tool-parameter-required-fields-checklist
description: When invoking tools that have modes (patch, edit, write_file) or that require path parameters, run a mental checklist of REQUIRED fields before every call. The patch tool's `mode='replace'` and `mode='patch'` are different invocations; omitting `path` (or using the wrong mode) silently no-ops or fails without a helpful error. Use when calling `patch`, `edit`, `write_file`, or any tool that takes both a `mode` and a `path` parameter. Applies across all Hermes agents.
tags:
  - tools
  - patch
  - ergonomics
---

# Tool Parameter Required-Fields Checklist

## The trap

Tools with `mode` + `path` parameters silently fail in unhelpful ways when a required parameter is missing. The three most common failure modes I have hit repeatedly:

### 1. `patch` with `mode='replace'` requires `path`

```python
# ❌ WRONG — fires the "path required" error message 6 times in a row
patch(mode='replace', old_string='foo', new_string='bar')

# ✅ CORRECT — explicit path
patch(mode='replace', path='/abs/path/to/file.txt', old_string='foo', new_string='bar')
```

The error message is `"path required"` — not "you forgot to include path" or any helpful pointer. The agent reads the error, thinks it's another transient failure, and retries identically. Each retry burns a tool iteration.

### 2. `patch` with `mode='patch'` is **V4A multi-file patches**, not a synonym for `replace`

```python
# mode='replace' (default) — single-file find-and-replace using old_string/new_string
# mode='patch'       — V4A multi-file patch format using `*** Begin Patch ... *** End Patch`
# These are TWO DIFFERENT INVOCATIONS.
```

Passing `old_string`/`new_string` while `mode='patch'` silently treats `new_string` as the entire patch body — your find-and-replace diff gets corrupted.

### 3. `write_file` requires `path` and `content`; missing `path` is also a "path required" error

Same failure shape as `patch`. Same wrong retry pattern.

### 4. `memory` tool: the `operations` array shape corrupts long escaped strings

Batch `operations=[{action, old_text, content}]` calls are prone to **generation-side corruption** when the payload contains long strings with escaped quotes, em-dashes, or parens — the tool reports `content is required` (payload field didn't survive intact) or `No entry matched` (old_text mangled), and the loop detector flags you after 3-4 identical retries. Hit this 4× in one session.

- For a single change, use the **single-op shape** (`action`/`target`/`content`/`old_text` as top-level fields) — it survived where the ops array did not.
- Use a **short unique anchor** for `old_text` (e.g. `Local Qwen27B is blind`) instead of pasting the entire existing entry.
- If an ops-array attempt fails with "content is required", **do not retry it** — the payload did not survive generation. Switch shape immediately.
- Batch shape is still worth it for multi-change updates (atomic, char-limit checked once) — but keep each entry's strings short.

### 5. `read_file` has a per-call size cap — check file size BEFORE reading

In some profiles `read_file` refuses any single read that would produce more than ~2,000 characters: `Read produced 5,320 characters which exceeds the safety limit (2,000 chars). Use offset and limit to read a smaller range.` (The stock tool description cites ~100K — trust the actual error message for the cap in YOUR profile.) Observed failure pattern: repeated whole-file reads of 5–8KB files (a JSON schema, an OKF doc, a Python harness) → 3–4 identical failures → loop detector fires → the session's tool-iteration cap is consumed before the real task progresses.

**Fix, in order of preference:**
1. Size-check first (`wc -c`, `stat`, or the `total_lines`/`file_size` fields in the error itself) and pick the access strategy before reading.
2. Chunk with `offset`/`limit` for medium files.
3. For local files, `terminal` (python3, grep -n) has no such cap and is usually faster when you only need specific lines.
4. For OKF hub docs, prefer `mcp_okf_read` (live disk read, truncates at 60KB) over `read_file` on the checkout path.
5. `execute_code`'s `read_file` wrapper inherits the same cap, and on failure returns an **error dict with no `content` key** — `result["content"]` raises `KeyError: 'content'`. Check `result.get("error")` before indexing, and do NOT retry the same read (that's what trips the loop detector).

## Checklist (run before calling `patch` or `write_file`)

Before EVERY invocation:

```
[ ] Do I have a `path` parameter set?
[ ] If using patch: is `mode` correct? (replace for find/replace, patch for V4A)
[ ] If mode='replace': do I have `old_string` AND `new_string`?
[ ] If mode='patch': do I have `patch` (the multi-file patch body)?
[ ] Is `path` absolute? Relative paths get resolved against session cwd.
```

When you see `"path required"`: STOP. The tool call had no path parameter. Re-read the parameters, do not retry identically.

## What to do when the failure repeats

- After TWO identical failures of the same tool call, **stop and re-inspect the tool's parameters**. Don't paste-and-pray a third time.
- Print the parameters you are about to send before sending them. `mode=...` and `path=...` should be the first two.
- If you keep omitting `path`, switch tools. `write_file` with a full body, or a Python `sed`/`with open() as f: f.write(...)` script via `execute_code`, may be less error-prone than `patch`.

## Recovery when work is stuck

If you have already burned several iterations hitting the same tool failure:

1. **Don't keep retrying.** Each retry burns an iteration without making progress.
2. **Switch tools.** If `patch(mode='replace', old_string, new_string)` keeps failing on a long file, use `write_file(path, full_content)` or a Python `with open() as f: f.write(...)` script via `execute_code`.
3. **Use scripts for bulk edits.** When editing multiple specific blocks in different files, write a small Python file under `execute_code` that does the search-and-replace. Much more reliable than `patch` for bulk work.
4. **`execute_code` pattern for the "bulk CSS/HTML edits" case (Astro shell scripts).** When you have 5+ CSS rule replacements across 2-3 files, write a Python helper script and run it from `execute_code`:

   ```python
   import subprocess
   script = '''
   import re
   path = "src/components/shell/PrimaryNav.astro"
   with open(path) as f: content = f.read()
   old = """  .nav-link {
       display: flex;
       align-items: center;
       padding: 1rem 1.125rem;"""
   new = """  .nav-link {
       display: flex;
       align-items: center;
       padding: 10px 16px;
       color: #fdf5e3;"""
   if old not in content: print("NOT FOUND")
   else:
       content = content.replace(old, new)
       with open(path, "w") as f: f.write(content)
       print("OK")
   '''
   print(subprocess.run(["python3", "-c", script], capture_output=True, text=True).stdout)
   ```

   This pattern was used 4+ times in a single session when `patch` kept failing with "path required" — and worked first try each time because the python script doesn't have to remember which tool mode/path combination to use.

## Related Skills

- `compact-verification-output` — for when tests/scripts output too much to keep in context.
- `corrections-lead-with-recipe` — for correcting generated artifacts (different scope).
- `directive-then-execute` — execute, don't narrate (different scope).

## Why this skill exists

I have personally re-encountered the `patch` "path required" loop three times in the same session before writing this. The error message is too generic to debug from the error alone, and the tool is otherwise useful enough that I don't want to abandon it. The checklist is the cheapest fix.
