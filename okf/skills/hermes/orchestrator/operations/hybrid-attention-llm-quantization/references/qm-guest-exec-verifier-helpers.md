# qm guest exec SSH escape helpers

When running grep/python/arbitrary commands inside a VM via `qm guest exec 230 -- bash -c '...'`,
the SSH chain wraps the inner output in JSON (`{"exitcode": N, "exited": M, "out-data": "..."}`),
which has two consequences for verifiers:

1. **Bash quoting is mangled** — single quotes inside `bash -c '...'` get stripped, breaking
   `python3 -c "print('hello')"` patterns and `awk`/`grep` with regex pipes.
2. **The JSON `out-data` value is the actual stdout** — anything else in the SSH output
   (warnings, sshpass stderr, the JSON keys themselves) is noise.

## The two helper functions that work

```python
SSH = "sshpass -p '[REDACTED]' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@192.168.1.2"


def direct_qm_grep(pattern, file="/tmp/qwen-quantize/quantize.py"):
    """Run grep via qm guest exec and extract count from JSON output.

    Uses fixed-string (-F) so regex metachars don't need escaping.
    Single quotes around the inner command survive the SSH wrapper.
    """
    inner = f"grep -cF '{pattern}' {file} 2>/dev/null || echo 0"
    inner_for_bash = "'" + inner.replace("'", "'\"'\"'") + "'"
    cmd = f"qm guest exec 230 -- bash -c {inner_for_bash}"
    full = f'{SSH} "{cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=20)
    text = r.stdout
    # Parse the JSON wrapper and extract out-data value
    if '"out-data"' in text:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            obj = json.loads(text[start:end])
            out_data = obj.get("out-data", "")
            m = re.search(r'\d+', out_data)
            return int(m.group()) if m else 0
        except Exception:
            pass
    # Fallback: any number anywhere
    m = re.search(r'\d+', text)
    return int(m.group()) if m else 0


def direct_qm_command(cmd_in_vm):
    """Run arbitrary command inside VM 230, return raw stdout from out-data."""
    inner_for_bash = "'" + cmd_in_vm.replace("'", "'\"'\"'") + "'"
    full_cmd = f"qm guest exec 230 -- bash -c {inner_for_bash}"
    full = f'{SSH} "{full_cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    text = r.stdout
    if '"out-data"' in text:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            obj = json.loads(text[start:end])
            return obj.get("out-data", "")
        except Exception:
            # JSON parse failed; extract out-data value with a tolerant regex
            m = re.search(r'"out-data"\s*:\s*"([^"]*)"', text)
            if m:
                return m.group(1).replace('\\n', '\n').replace('\\"', '"')
    return text
```

## Why naive `ssh_run` fails on real recipes

A naive `ssh_run` that does `text.find('{"')` (looking for `{"`) will silently miss the JSON
because the SSH wrapper actually emits:
```
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "2\n"
}
```
The `{` is on its own line, followed by indented keys. `text.find('{"')` returns -1, the parse
fails silently, and the verifier falls back to `re.search(r'\d+', text)` which matches the
`0` in `"exitcode": 0` — silently returning the wrong answer (0 instead of 2).

The fix is `text.find('{')` (first brace, no quote) + `text.rfind('}')` (last brace), then
`json.loads()`. The tolerance regex with `r'"out-data"\s*:\s*"([^"]*)"'` is the final fallback
when the JSON itself is malformed (e.g., the inner bash command's stdout contains literal
newlines that the wrapper didn't escape).

## When the inner command itself is the problem

Some `qm guest exec` failures are not the JSON wrapper — they're the inner bash command:

- `bash -c 'grep X Y'` works fine.
- `bash -c "python3 -c \"import X\""` silently strips inner quotes before bash sees them.
  Workaround: write the Python to a file via `wget` from a local HTTP server, then `python3 /tmp/file.py`.
- `bash -c "echo $((1+1))"` strips the `$` before bash sees it. Workaround: pass via env var
  or write the arithmetic to a script.
- `bash -c 'awk "/foo/{print $1}"'` with regex pipes inside double quotes silently breaks.
  Workaround: use `grep -F` (fixed string) instead of regex, or split into multiple commands
  joined by `&&`.

## Plan for one round of fix-and-re-verify

When writing the verifier for a quantization recipe, expect at least one round of
"verifier bug, not real bug" fixes. Common patterns:

1. `grep -cF` returns 0 when the pattern is in a comment but not in actual code.
2. `python3 -c "..."` import fails because the script path is wrong on the VM.
3. `nvidia-smi --query-gpu=memory.used` returns "1" for an idle GPU but the regex expects >1000
   for "loaded" — adjust the threshold or check `utilization.gpu`.
4. The JSON wrapper gets truncated at long log output — check the `text.rfind('}')` end position
   before `json.loads()`.

Always fix the verifier first, then re-verify. The recipe is the agent's intentional design;
the verifier is the agent's check on itself. Bugs in the verifier don't invalidate the recipe.