# Exact-head clean-env acceptance proof pattern — 2026-07-25

Use when a candidate is ready for PR/review and must be accepted against an exact commit/tree, especially for Prismatic Engine/AGY work.

## Pattern

1. Record candidate `COMMIT` and `TREE` before launching independent review.
2. Run focused gates and canonical gates as separate proof classes.
3. For clean-room/canonical proof, use a fresh environment seeded with the same project extras and development tools needed by the canonical suite.
4. If the fresh verifier environment is missing setup pieces, label that run as `BLOCKED verifier setup`, repair the environment, and rerun exact-head. Do not silently convert verifier setup failures into product failures, and do not discard the failed setup log.
5. For AGY/auth-dependent follow-on work, run a tiny auth/model/protocol preflight from the intended runtime `HOME`. Record only status, log path, digest, and marker; never quote tokens or credential contents.
6. Preserve proof-class boundaries in the final packet. A focused regression pass does not imply canonical suite green; canonical local green does not imply hosted CI, production, or browser proof.

## Compact packet fields

```text
COMMIT=<candidate commit>
TREE=<candidate tree>
COMMAND=<exact command or grouped summary>
RESULT=<PASS|FAIL|BLOCKED>
RC=<exit code if applicable>
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=<scope>
AD_HOC_OR_CANONICAL=<focused|canonical suite|clean-room wheel|release smoke|auth preflight>
NOT_CLAIMING=<explicit non-claims>
MARKER=<marker>
```

## Pitfall

When a long sequence hits an iteration ceiling, the durable receipt files written before the ceiling become the source for the final no-tool summary. Write exact-head checkpoint files before starting optional downstream probes.
