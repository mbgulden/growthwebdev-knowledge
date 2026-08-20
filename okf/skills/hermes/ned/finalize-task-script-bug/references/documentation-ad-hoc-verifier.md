# Documentation-only ad-hoc verification

## Trigger

Use when a task changes only Markdown/documentation and the external verifier reports `unverified` because no canonical test, lint, or build command was detected.

## Fresh-proof recipe

1. Create a temporary script with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`; close the descriptor before writing the script.
2. In the script, read the changed document and assert its durable acceptance tokens/sections.
3. Where the document inventories source behavior, independently query the immutable source with commands such as `git show <freeze-sha>:<path>` and assert the recorded dependency remains present.
4. Normalize Markdown whitespace before phrase matching:
   ```python
   flat = re.sub(r"\s+", " ", text)
   ```
   This prevents false failures caused only by Markdown line wrapping. Prefer structural terms/tokens over invented exact prose.
5. Run `git diff --check <base>...HEAD` inside the verifier or immediately beside it.
6. Print `VERIFIER=`, `COMMAND=`, `EXIT_CODE=`, and a concise assertion summary. Remove the script in a `finally` block and print `CLEANUP=... removed=True`.
7. If the verification prompt repeats, create and run a new temporary verifier; prior successful output is not fresh evidence.

## Reporting

Call it **ad-hoc documentation verification**. Do not call it suite green or imply that an unrelated test suite ran.

## Finalizer lock follow-up

`finalize_task.sh` can report an unlock under a generic owner while the lock remains held by the actual agent. Always run `swarm.js status <locked-path>` after finalization and explicitly unlock the real owner when needed before reporting completion.