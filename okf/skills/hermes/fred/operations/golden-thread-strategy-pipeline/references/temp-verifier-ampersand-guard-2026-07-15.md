# Temp Verifier Ampersand Guard — 2026-07-15

## Context

A post-turn verification nudge required a focused `/tmp/hermes-verify-*` script for changed Markdown artifacts. The correct pattern was to create the verifier with Python `tempfile`, run it, remove it in the same terminal command, and label the result as ad-hoc targeted verification.

During the first retry, the terminal wrapper rejected the foreground command with:

```text
Foreground command uses '&' backgrounding. Use terminal(background=true) for long-lived processes...
```

The command was not actually trying to background a process; the inline verifier contained a literal ampersand in a string (`Operational & Assumption Validation Tracker`). The wrapper's shell-background guard can trip on ampersands inside heredoc/script text.

## Durable Pattern

When writing inline temporary verifier scripts inside a `terminal()` heredoc:

1. Use `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp", text=True)`.
2. Run and remove the verifier in the same terminal call.
3. Avoid literal `&` characters anywhere in the command body, including Python string literals, comments, Markdown headings, and expected substrings.
4. If you need to verify text containing `&`, either:
   - check adjacent substrings separately (`"Operational" in text and "Assumption Validation Tracker" in text`), or
   - build the expected string inside Python via concatenation (`"Operational " + chr(38) + " Assumption"`) so the shell guard does not see `&` in the command body.
5. If the guard fires, do not switch to prose. Retry once with the same verifier logic but remove/escape the ampersand from the inline command body.

## Report Wording

Always summarize this as:

> Ad-hoc targeted verification complete — not suite green. Verifier `/tmp/hermes-verify-*.py` ran against the named changed paths, exited 0, and was removed.

Do not imply canonical build/lint/test coverage unless a canonical command actually ran.
