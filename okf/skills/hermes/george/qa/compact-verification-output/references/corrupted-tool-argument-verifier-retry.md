# Corrupted tool-argument warning during detector verification

Use this when a Hermes post-edit verification guard asks for a `/tmp/hermes-verify-*` script and the verifier tool result includes a platform warning such as:

```text
[hermes-agent: tool call arguments were corrupted in this session and have been dropped to keep the conversation alive]
```

## Lesson

Do not treat that result as detector-compliant proof, even if the displayed stdout contains a plausible `RESULT=PASS` packet. The transcript no longer proves the exact command that ran, and the detector/Michael cannot trust that the required verifier script and command classes were actually invoked in the current turn.

This is not a durable claim that the terminal tool is broken. It is a proof-chain rule: a verifier receipt with corrupted or dropped call arguments is insufficient evidence for post-edit changed-path closeout.

## Required recovery

When normal tools are allowed:

1. Rerun once in a new `terminal` call with literal, transcript-visible commands.
2. Create the temporary verifier inside that command via Python `tempfile.mkstemp()` or `NamedTemporaryFile(prefix="hermes-verify-", dir="/tmp")`.
3. Print the actual verifier path before execution and remove it afterward.
4. Include visible command classes (`ruff check`, `ruff format --check`, `python -m py_compile`, scoped `python -m pytest`, `git diff --check`, and artifact/readback assertions as applicable).
5. Exit nonzero if any verifier assertion or command class fails; cleanup/log-hash steps must not mask the verifier return code.
6. Summarize as `AD_HOC_OR_CANONICAL=ad-hoc targeted`, not canonical suite green.

When the current user task explicitly forbids non-skill/non-memory tools, do not violate that boundary. Save the lesson in this skill/reference and report that no live rerun was attempted because tools were restricted.

## Stop condition

Only call a repeated warning detector non-recognition after a current-turn compliant rerun is visible **without** tool-argument corruption/dropped-argument warnings. A corrupted-argument receipt does not start the stop-condition clock.