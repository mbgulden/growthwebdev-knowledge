# Agent Context Discovery Layer

Session learning: skill/workflow distribution is stronger when every agent runtime can discover compact capability context from Prismatic Engine itself, rather than from hand-maintained per-profile notes.

## Durable pattern

Use a packaged manifest → CLI/API → generated markdown block flow:

```text
prismatic/agent_context/manifest.yaml
→ prismatic.agent_context module
→ prismatic-agent-context CLI
→ /api/agent-context and /api/agent-context/line
→ generated AGENTS.md / soul.md managed block
```

This lets Hermes, AGY CLI, OpenClaw, and future agents consume the same source of truth.

## Why this beats hand-written soul.md notes

- Hand-written `soul.md` / `AGENTS.md` snippets drift.
- Hermes profile skill copies are local convenience, not production distribution.
- A packaged PE manifest can be wheel-tested and used on another computer after install.
- Managed markdown blocks can preserve human notes while replacing only generated context.

## Minimum verifier contract

For this class of change, a `/tmp/hermes-verify-*.py` ad-hoc verifier should cover:

1. Changed paths exist.
2. `py_compile` for `prismatic/agent_context.py`, gateway server, and tests.
3. Focused tests for agent-context behavior.
4. Manifest renders cards for `hermes`, `agy`, and `openclaw`.
5. `install_context_doc()` preserves human content and replaces only the managed block.
6. Gateway endpoints pass: `GET /api/agent-context`, `GET /api/agent-context/line`.
7. Wheel portability: build wheel, install into fresh venv, run `prismatic-agent-context line`, and `prismatic-agent-context install-doc`.

Report as **ad-hoc targeted verification**, not suite green.
