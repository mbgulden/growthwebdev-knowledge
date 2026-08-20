# Repeated system verifier prompt after finalize

## Trigger

After a task is finalized and reported, the system/user may immediately send a corrective prompt like:

```text
Verification status: unverified
Changed paths:
- /tmp/.../docs/...
- /tmp/.../scripts/...
Run the relevant verification command now (`npm run build`)
```

This can happen even when a build or targeted verifier passed earlier in the session.

## Rule

Treat the prompt as a fresh evidence contract for the current turn. Do not argue from:

- prior `RESULT.md` contents;
- a previous build transcript;
- PR check state;
- a prior finalize comment.

Run the exact requested verifier again from the changed worktree, read the output, repair only if it fails, and summarize the fresh pass.

## Node/Astro variant

If ignored build artifacts were cleaned after finalization, reinstall before rerunning the verifier:

```bash
cd /tmp/<task-worktree>
if [ ! -d node_modules ]; then npm ci; fi
npm run build
```

If the verifier prompt repeats again, rerun `npm run build` again in that turn. The important artifact is fresh tool output attached to the response, not the fact that the same command passed minutes ago.

## Why this matters

The post-turn verifier is keyed on fresh detected evidence. A correct earlier run can still be invisible to the detector after finalization, cleanup, or a new user/system correction. Re-running the requested command is cheaper and safer than explaining that it already passed.
