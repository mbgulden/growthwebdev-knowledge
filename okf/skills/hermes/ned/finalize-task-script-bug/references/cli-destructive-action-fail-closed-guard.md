# CLI destructive-action fail-closed guard

Some CLIs can print an error to stderr while exiting `0`, especially when an unsupported subcommand is parsed by a parent command. Treating exit code alone as success can falsely report a destructive action as completed.

Validated pattern from GRO-3571 (Jules stalled-session purge, 2026-07-07):

- Acceptance asked for `jules remote delete --session <id>`.
- Installed Jules CLI v0.1.42 did not advertise a `remote delete` subcommand.
- A direct attempt printed `Error: unknown flag: --session` while returning exit code `0`.
- Fix: feature-probe the command surface before attempting deletion and classify stderr/stdout containing `error:`, `unknown command`, or `unknown flag` as failure even when return code is zero.

Reusable implementation shape:

```python
def supports_delete(bin_path: str) -> bool:
    result = run_cmd([bin_path, "remote", "--help"])
    return bool(re.search(r"^\\s+delete\\s+", result.stdout + result.stderr, re.MULTILINE))


def command_failed(result: subprocess.CompletedProcess[str]) -> bool:
    text = (result.stdout + result.stderr).lower()
    return (
        result.returncode != 0
        or "error:" in text
        or "unknown command" in text
        or "unknown flag" in text
    )
```

Use this for any cleanup/purge/delete/cancel automation: prove the destructive command exists first, then verify both exit code and output semantics before reporting success.