# Fresh verification repeat after dependency install

## Trigger

A post-response verifier repeats an older failure such as:

```text
npm run build
sh: 1: astro: not found
```

even though the session already installed dependencies and later produced a passing build.

## Rule

Do not argue from the prior transcript. Treat the repeated verifier prompt as a new evidence contract and rerun the exact requested verification command in the exact changed worktree.

## Recommended transcript shape

```bash
cd /tmp/<task-worktree>
printf 'cwd=%s\n' "$PWD"
printf 'node=%s npm=%s\n' "$(node --version)" "$(npm --version)"
printf 'astro_bin='; test -x node_modules/.bin/astro && echo present || echo missing
git status --short --branch
test -s <changed-doc-or-file>
test -s /tmp/issue-batches/<ISSUE>_RESULT.md
npm run build
```

If the local project binary is missing, install dependencies first using the project’s canonical install command, then immediately rerun the verifier:

```bash
npm ci
npm run build
```

## Durable lesson

The durable lesson is not “Astro is missing” or “npm is broken.” That was transient setup state. The reusable workflow is:

1. Re-enter the changed worktree explicitly.
2. Show local dependency/binary state.
3. Confirm changed files and local result file exist.
4. Run the canonical verification command fresh.
5. Summarize only the fresh command output.

This avoids stale-verifier loops after finalize/PR work where a first build failed before `npm ci`, then a later build passed but the detector still keys on the older failure.