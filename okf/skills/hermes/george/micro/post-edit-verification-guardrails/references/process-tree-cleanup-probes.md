# Process-tree cleanup probes for post-edit verification

Use this reference when a code edit claims that a command runner, helper process, Git wrapper, enumerator, or subprocess timeout path does not leak descendants.

## Durable lesson

A successful parent/leader exit is not enough proof. A descendant can close stdout/stderr, survive after the leader exits 0, and leave no open pipe for the caller to notice. Guard-compatible verification should force that shape directly.

## Minimal probe shape

1. Create a disposable pytest file with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
2. In the probe, replace the runner executable with a fake script that:
   - forks a child/descendant;
   - child closes stdout/stderr;
   - child sleeps long enough to outlive the parent unless killed;
   - child writes a marker after the sleep;
   - parent prints a success token and exits 0.
3. Call the changed runner/helper with a short timeout and assert it returns the success token.
4. Sleep slightly longer than the child delay and assert the marker file does **not** exist.
5. Also assert exact HEAD/tree and clean status when the probe is reviewing an exact candidate.
6. Run the disposable pytest plus direct focused tests/lint/build in the same terminal transcript; clean up the disposable script and assert stale temp paths are absent if the detector previously listed them.

## Example assertion core

```python
marker = tmp_path / "marker"
fake.write_text(
    "#!/usr/bin/python3\n"
    "import os,time\n"
    "if os.fork()==0:\n"
    " os.close(1); os.close(2); time.sleep(.2); "
    f"open({str(marker)!r}, 'w').write('survived'); os._exit(0)\n"
    "print('ok', flush=True)\n"
)
fake.chmod(0o755)
monkeypatch.setattr(module_under_test, "_git_executable", lambda: str(fake))
assert module_under_test._git(tmp_path, "status", timeout=1.0) == "ok"
time.sleep(0.25)
assert not marker.exists()
```

## Report classification

This is **ad-hoc targeted** verification unless the repository's canonical suite also ran and passed. Report the non-claim explicitly:

```text
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green
SUCCESSFUL_LEADER_DESCENDANT_CLEANUP=PASS
TEMP_SCRIPT_CLEANED=true
```
