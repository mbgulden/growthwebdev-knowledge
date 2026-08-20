# Ned test-file lane refinement

## Trigger

A Ned task in `prismatic-engine` asks for tests or smoke tests, but the current Prismatic lane gate only permits Ned to push paths under `scripts/`, `prismatic/`, and `plugins/`.

## Symptom

A push from a Ned branch fails with a pre-push message like:

```text
Lane violation by ned:
   - tests/test_<name>.py
Owned directories: ['scripts/', 'prismatic/', 'plugins/']
```

The work may be technically correct, but the file is in the wrong lane.

## Correct recovery

1. Do not bypass the hook just to publish repo-root `tests/` changes.
2. Move the test into an allowed path, usually `prismatic/tests/test_<name>.py`.
3. Update any report/doc path references and verification commands.
4. Rerun the targeted test by explicit path:

   ```bash
   python3 -m pytest prismatic/tests/test_<name>.py -q
   ```

5. Amend or create the commit after the lane-corrected move.
6. Push normally and let the pre-push hook validate the lane.

## Notes

- This applies when acceptance says a test/smoke test must exist, not when a project convention explicitly requires root `tests/` and a human has widened Ned's lane.
- Keep evidence or operator notes under `scripts/reports/`, which is also in Ned's lane.
- Label the verification as a targeted smoke test, not a full-suite pass unless the full suite actually ran.
