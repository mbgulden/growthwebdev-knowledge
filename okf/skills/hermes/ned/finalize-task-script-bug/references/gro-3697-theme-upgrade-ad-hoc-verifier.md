# GRO-3697 repeated ad-hoc verifier detector pattern

Context: After implementing `pwp theme upgrade` for tenant-safe theme upgrades, the verifier detector twice reported: `Verification status: unverified` and `No canonical test/lint/build command was detected`, despite a prior pytest run and a prior ad-hoc verifier.

Durable lesson: treat each detector prompt as a fresh evidence contract. Do not argue from earlier pytest output, previous ad-hoc output, or Linear comments. Create and run a new `/tmp/hermes-verify-*.py` script each time.

Working shape:

1. Use OS-safe creation from Python:
   ```python
   fd, verifier = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")
   os.close(fd)
   Path(verifier).write_text(...)
   ```
2. The verifier itself prints:
   - `verifier_path=<path>`
   - the exact `tested_command=...`
   - `command_exit=<code>` for the changed command
   - an assertion summary
   - `verification_exit=0`
3. Exercise the changed behavior directly, not just import modules. For CLI work, run the actual CLI command from the changed checkout.
4. Clean up in `finally` and print `cleanup=removed <path>` or the cleanup failure.
5. If the issue is already finalized/In Review, post a short Linear verification-refresh comment with the fresh verifier path, cleanup status, tested command, exit code, and assertions. Do not rerun `finalize_task.sh` just to refresh evidence.

Concrete GRO-3697 assertions that satisfied the detector:

- `python3 scripts/pwp theme upgrade --from <before> --to <after> --tenant-overrides <json> --engine-version 0.2.0 --json` exits `0`.
- Preserves a real tenant token override.
- Drops a tenant override that merely restates the old default.
- Excludes an override whose target was removed from the upgraded theme.
- Flags `target-default-changed-under-tenant-override`.
- Flags `override-target-removed`.
- Includes the underlying theme diff with `fromVersion` and `toVersion`.

Pitfall hit: the first wrapper script forgot to import `Path` in the outer wrapper, causing `NameError: name 'Path' is not defined`. Keep imports in both the wrapper and generated verifier explicit; don't rely on imports inside the generated script.