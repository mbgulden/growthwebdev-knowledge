# Live verification receipt — 2026-08-19 (George, pre-distribution)

## Standalone smoke test
COMMAND=`/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python /home/ubuntu/work/okf-mcp-server/smoke_test.py`
RESULT=PASS — `ALL SMOKE TESTS PASS`
Coverage: INIT (server name `okf`, mcp sdk 1.27.1), TOOLS (all 7 expected: categories, list, read, recent, search, status, update), STATUS, SEARCH (3 hits, top=standards/linear-rate-limit.md, scored), READ (4859 chars, frontmatter+body), CONTAINMENT (`../README.md` rejected: `{"error": "not an okf doc: ../README.md"}`), UPDATE-GATE (disabled without `OKF_ALLOW_UPDATE=1`).

## Live in-session tool calls (profile: george)
| Call | Result |
|---|---|
| `mcp_okf_status` | head `f8f37d0` (2026-08-19, "[George] Register george in PRISMATIC_ENGINE.yaml + OKF commit authorization"), dirty_files=0, doc_count=266, 13 categories (plugins=90, operations=47, standards=42, projects=27, reports=19, audits=13, integrations=11, decisions=5, research=5, incidents=2, sessions=2, playbooks=2, (root)=1) |
| `mcp_okf_categories` | total 266 docs; index.md present for audits/decisions/incidents/integrations/playbooks/plugins/projects/research/sessions/standards; **no index for operations** |
| `mcp_okf_search("linear rate limit", limit=3)` | 3 hits: standards/linear-rate-limit.md (top), standards/webhook-security.md, standards/dispatch-production-grade.md |
| `mcp_okf_recent(limit=3)` | decisions/okf-agent-commit-authorization.md (2026-08-19), index.md, integrations/llama-cpp-george-local-server.md |
| `mcp_okf_read("../README.md")` | rejected: `not an okf doc` (containment works) |
| `mcp_okf_update` | rejected: `update disabled (OKF_ALLOW_UPDATE != 1)` (gate works) |
| `mcp_okf_list(category="decisions", limit=3)` | 3 docs: event-driven-dispatch.md, index.md, okf-adoption.md |
| `mcp_okf_list_resources` / `mcp_okf_list_prompts` | both return empty `[]` (server serves none) |

## Profile wiring audit (2026-08-19, `mcp_servers.okf` in config.yaml)
Wired (8): (default) `~/.hermes/config.yaml`, autobot, fred, george, kai, ned, next-step, orchestrator.
Not wired: active-oahu, ai-consulting, google-ai-toolkit, hdengine (gdrive-only), jules (no config.yaml).
Note: `mcp_discovery_timeout: 10` must be set per profile or cold stdio handshake (~1.4–1.7s) races the 1.5s default and tools silently disappear. Verify via `hermes --profile <p> mcp test okf` + registration probe; see hermes-mcp-stdio-server-wiring.
