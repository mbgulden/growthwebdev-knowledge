# Disposable verifier generation: avoid nested string/quoting failures

Session signal: while validating a Prismatic admission envelope, two generated `/tmp/hermes-verify-*.py` scripts failed before execution because newline/string escaping inside a generated Python one-liner produced `SyntaxError: unterminated string literal`. The launcher/envelope were untouched, but the failed verifier wasted review time.

Reusable pattern:

1. Treat a failed generated verifier as **no proof**, even if the log hash exists; rerun with corrected bytes and report the failed helper honestly.
2. Prefer `write_file()` for disposable verifier scripts when the script contains ordering checks, embedded newlines, or source-code string matching.
3. Use `splitlines()` and line-index checks instead of embedding literal `\n...\n` snippets inside generated Python strings.
4. Keep the verifier script temporary and remove it after successful execution, but keep the result log and its SHA.
5. Include a guard that proves the verifier itself was removed, e.g. `TEMP_VERIFIER_REMOVED=true`.

Minimal line-order idiom:

```python
lines = target.read_text().splitlines()
bootstrap = lines.index("verify_frozen_inputs()")
sys_path = next(i for i, line in enumerate(lines) if line.startswith("sys.path.insert("))
first_import = next(i for i, line in enumerate(lines) if line.startswith("from prismatic."))
assert bootstrap < sys_path < first_import
```

Do not memorialize the original syntax error as an environment/tool limitation. The durable lesson is the safer probe-writing pattern.