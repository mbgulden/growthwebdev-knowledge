# AOT Meta Tag Attribute Ordering + Hreflang Patterns

## Meta tag attribute order: site-wide inconsistency

The AOT static export has **two distinct meta description tag formats**:

### Format A: name before content
```html
<meta name="description" content="Experience the best kayaking..."/>
```

### Format B: content before name
```html
<meta content="Self-guided kayak tour..." name="description"/>
```

Format B appears on pages that had long description values that wrapped across lines in the static export. Both are valid HTML but require regex patterns that don't assume attribute order.

### Safe pattern for meta tag manipulation
```python
import re

# Matches BOTH name-before-content AND content-before-name
# Uses [^>]* to match any attributes in any order
pattern = r'<meta[^>]*name=["\']description["\'][^>]*>'
```

### Meta description spanning multiple lines
Long `<meta content="..." name="description"/>` values can wrap across physical lines in the static HTML. Always use `re.DOTALL`:
```python
new_content, count = re.subn(
    r'<meta[^>]*name=["\']description["\'][^>]*>',
    replacement,
    content,
    count=1,
    flags=re.DOTALL  # critical for multiline meta tags
)
```

## hreflang tag attribute order

hreflang tags on AOT use consistent attribute order:
```html
<link rel="alternate" hreflang="en" href="https://activeoahutours.com/..." />
```

But the surrounding `<link rel="canonical">` has **two variants**:
```html
<!-- Variant 1: rel before href -->
<link rel="canonical" href="https://activeoahutours.com/..." />

<!-- Variant 2: href before rel -->
<link href="https://activeoahutours.com/..." rel="canonical"/>
```

### Safe hreflang insertion pattern
```python
# Insert hreflang tags after canonical — handles both attribute orderings
canon_pattern = r'<link[^>]*rel=["\']canonical["\'][^>]*>'
match = re.search(canon_pattern, content)
if match:
    insert_pos = match.end()
    new_content = content[:insert_pos] + hreflang_tags + content[insert_pos:]
```

## Module import caching gotcha

When iteratively fixing a script (`/tmp/fix_meta_keywords.py`) and re-running it with `python3 script.py`, Python caches the compiled `.pyc` bytecode. If you import the script as a module (`sys.path.insert(0, '/tmp'); import fix_meta_keywords`) in the same session, changes to the source file on disk are **not** picked up — the cached bytecode is used instead.

**Symptom:** `add_keywords_to_file()` returns `changed=False` even though the file on disk has the problem you're trying to fix.

**Fix:** Always run the script as a subprocess (`python3 /tmp/script.py`) rather than importing it as a module when testing fixes. If you must import, use `importlib.reload(module)` or start a fresh Python process.

## git checkout -- on uncommitted new files

`git checkout -- <path>` restores a file to its state in the **last committed HEAD**. For new files that have never been committed, this fails with:
```
error: pathspec '<file>' did not match any file(s) known to git
```

**Workaround:** For new uncommitted files, just rewrite the file normally. `git checkout --` only works for tracked files.

## Session context (2026-07-27)
- HIGH-05 meta keywords script needed 3 iterations to handle: (1) attribute order, (2) multiline descriptions, (3) module cache
- HIGH-06 hreflang script needed 2 iterations to handle: (1) only `rel="canonical"` before `href=`, (2) `href=` before `rel="canonical"`
