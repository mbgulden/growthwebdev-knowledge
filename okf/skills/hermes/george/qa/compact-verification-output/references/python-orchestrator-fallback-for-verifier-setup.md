# Python orchestrator fallback for brittle verifier shell wrappers

## Signal

Use this when a long closeout verifier fails because the wrapper guessed source identifiers, nested heredocs broke, or shell quoting made the transcript unreliable, while the underlying product/test commands need a clean full rerun.

## Pattern

1. Label the first failure as **verifier setup** only after reading enough context to prove it is not a product failure.
2. Inspect the actual source/schema identifiers instead of guessing names for semantic assertions.
3. Replace fragile nested shell heredocs with a disposable Python orchestrator when needed.
4. The orchestrator should:
   - create and remove a disposable immutable archive/work area;
   - run the same literal subprocess commands from the beginning;
   - capture stdout/stderr and exit codes into a log;
   - snapshot any mutable system state before and after;
   - print a compact proof packet with log SHA and non-claims.
5. Do not resume at the failed assertion; rerun the full exact-head sequence after verifier setup changes.
6. Preserve failed verifier attempts as context, but do not report them as product blockers when they were caused by guessed names or malformed wrapper syntax.

## Boundary language

```text
VERIFIER_SETUP_FAILURE=<guessed identifier | malformed wrapper | schema-key mismatch>
RERUN_SCOPE=full exact-head sequence from start
RESULT=<PASS|FAIL|BLOCKED>
AD_HOC_OR_CANONICAL=<accurate proof class>
NOT_CLAIMING=<non-claims>
```
