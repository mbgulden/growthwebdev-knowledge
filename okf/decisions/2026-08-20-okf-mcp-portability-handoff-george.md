---
type: decision
title: OKF MCP server portability — handoff to George
description: State of the okf-mcp.service portability work (Kai, 2026-08-20): what's done, what's open, exact commands, open 401 thread, and the division of labor for whoever picks this up next.
tags: [okf, mcp, portability, handoff, kai, george]
status: closed
last_verified: 2026-08-21
created_by: kai
---

# OKF MCP server portability — handoff

**From:** Kai (owner of the OKF hub + skill-hub lanes)
**To:** George (working the same end of the OKF)
**Date:** 2026-08-20
**Why this doc exists:** Michael asked for a single shareable doc so the portability work isn't done twice in two directions. Everything below is verified live state as of 19:30 UTC 2026-08-20, HEAD `d7808ca` (PR #35 squash on main).

## TL;DR

The "make the OKF MCP server survive orchestrator downtime" problem is **largely already solved architecturally** — a standalone systemd service (`okf-mcp.service`) exists and was proven independent (orchestrator unit was in `failed` state while the service kept serving). The remaining work is **operational**: index freshness, client re-wiring (one open 401), a down-drill, and documentation. The open 401 is the next concrete task.

## Current architecture (verified)

| Component | State |
|---|---|
| `okf-mcp.service` (systemd) | Active. `User=root`, `Restart=on-failure`, parented by PID 1. Streamable-http on `127.0.0.1:8910`, bearer-gated (`MCP_BEARER_TOKEN` in root-only `/etc/okf-mcp/mcp.env`), open `/healthz`. |
| Per-gateway stdio children | 5 profile gateways each spawn their own `server.py` stdio child. **Fragile — dies with its gateway.** This is the path to retire. |
| Index | In-memory, built at process start (`rebuild()` in `__init__`). No disk cache. `OKF_ALLOW_UPDATE=0` → `mcp_okf_update` tool disabled by design. |
| Shared checkout | `/home/ubuntu/work/growthwebdev-knowledge`, pinned to `main` (`d7808ca`) as of 19:30 UTC. **The service indexes whatever branch the checkout is on** — see pitfall below. |
| Daily regen cron | `okf-skill-hub-regen` (no-agent, 07:00 UTC) runs `profiles/kai/scripts/skill-hub-regen.sh`; after a successful push to main it now does `sudo -n systemctl restart okf-mcp.service` so the index follows the hub. |

**Key facts:**
- Kai has passwordless sudo for the service: `sudo -n systemctl restart okf-mcp.service` works non-interactively.
- Hermes supports remote MCP clients: `mcp_servers.okf: {url: "http://127.0.0.1:8910/mcp", headers: {Authorization: "Bearer ${MCP_OKF_API_KEY}"}, enabled: true}` — token value in the profile's `~/.hermes/profiles/<p>/.env`. `/reload-mcp` or a new session picks it up; no gateway restart.
- Live MCP state: 2,663 docs, skills=2,240, head `d7808ca`.

## Done (this session)

1. ✅ Confirmed the standalone service already exists and is orchestrator-independent (live proof: orchestrator unit `failed`, service 200 on `/healthz`).
2. ✅ Daily regen cron patched to restart the service after each hub push (script rewritten cleanly, `bash -n` passed).
3. ✅ Shared checkout pinned to `main @ d7808ca` and service re-indexed (it had picked up Fred's feature branch tip `61d7422` on a restart — pitfall #1 below).
4. ✅ PR #35 (drift regen + 5-skill reconciliation, 12→7 divergent) merged as `d7808ca`.
5. ✅ Pitfalls documented in the `okf-mcp-hub` skill (`profiles/kai/skills/devops/okf-mcp-hub/SKILL.md`, section "Standalone service `okf-mcp.service`").

## Open — the 401 thread (next task)

Wiring Kai's MCP client from stdio-child to the standalone HTTP endpoint **fails auth**:

- `POST http://127.0.0.1:8910/mcp` with `Authorization: Bearer <token>` → `401 {"error":"unauthorized"}`.
- Tried with BOTH the live process token (`/proc/<pid>/environ`) AND the env-file token (`/etc/okf-mcp/mcp.env`). Both fail.
- Server gate (server.py lines 303-322): `expected = os.environ["MCP_BEARER_TOKEN"].strip()` **captured at process start**; compares `hmac.compare_digest(got, "Bearer " + expected)`.
- Service last started 18:55:18 UTC. Hypotheses, in order of likelihood:
  1. Env file edited after 18:55 start → running server holds the OLD token (gate captured at start).
  2. Token contains chars that mangle in transit (shell quoting is proven to eat it — see pitfall #2).
  3. Header format mismatch (least likely; `Bearer ` prefix confirmed in source).

**Ready-to-run diagnostic:** `/tmp/hermes-okf-diag.py` — compares live-vs-file token by hash only (never echoes either), probes `/mcp` with each. Written but not yet executed (session hit the iteration cap).

**Fix path:** run the diag → if file≠live, `sudo systemctl restart okf-mcp.service` after syncing the env file (or edit file to match live) → probe again → write token to profile `.env` as `MCP_OKF_API_KEY` via Python (never shell) → patch config → `/reload-mcp` → verify with an actual `mcp_okf_status` round-trip.

**Cleanup owed:** an earlier shell-quoting failure left an **empty `MCP_OKF_API_KEY=*** line in `profiles/kai/.env` — delete it before re-wiring.

## Remaining checklist (portability ticket)

- [ ] Solve the 401 + wire Kai's client to `:8910/mcp` (above)
- [ ] Orchestrator-down drill: `pgrep -af "profile orchestrator"` (expect dead/failed) + `kill <one stdio okf child>` → standalone still 200 + MCP calls work
- [ ] Switch the other 4 wired profiles (default, autobot, fred, ned, george) off stdio children onto the shared HTTP endpoint — **coordinate with George since he's on this end**; same one-liner per profile
- [ ] Document the final wiring in `okf/standards/` (new or existing doc) so the next agent doesn't re-learn this
- [ ] 🚩 **Separate flag (not OKF, but same audit):** the orchestrator gateway is running OUTSIDE systemd — its unit is in `failed` state, the live process is orphaned, nothing would respawn it. Opposite failure mode from OKF; needs a ticket.

## Pitfalls (learned live this session)

1. **The service indexes whatever branch the shared checkout is on.** A restart while the tree sat on `feature/fred-okf-hde-guest-fleet-ops` made every MCP client read a non-canonical tree. Before restarting: confirm the checked-out branch's work is pushed (local tip == origin tip, clean tree), `git switch main && git reset --hard origin/main`, then restart, then verify `mcp_okf_status.head == origin/main`.
2. **Never handle the bearer token in shell.** It contains special chars; `cut -d=`, `sed 's/^...=//'`, and `tr` pipelines silently produced empty strings. Extract via Python (`sudo cat` + `line.split("=", 1)[1]`), probe via `urllib` from a script file, verify by hash only. Same class as the GCP-credential redaction notes in the `okf-mcp-hub` skill.
3. **Shared-checkout races (two hit this session):** a concurrent agent can `git switch` the one shared checkout mid-operation — your commit lands on their branch, or their commit lands in your PR. Before ANY commit: assert `git branch --show-current` is still yours in the same command. Rebuild own branches with `git reset --hard origin/main` + cherry-pick + `git push --force-with-lease`.
4. **Post-merge regen churn is genuine drift, not a generator bug.** Concurrent agents edit skills between snapshot and merge; the daily cron auto-commits+pushes it.

## Division of labor (proposal)

| Work | Suggested owner |
|---|---|
| 401 resolution + Kai client re-wiring | George (you're on this end) — or say the word and Kai takes it next session |
| Other 4 profiles switched to shared HTTP | George (cross-profile writes; coordinate with profile owners) |
| Orchestrator-down drill | Whichever finishes the 401 first |
| `okf/standards/` wiring doc | Kai (lane: `okf/standards/`) — happy to draft once wiring is proven |
| Orchestrator-gateway-outside-systemd ticket | Kai can file |

## Pointers

- `okf/standards/okf-skill-hub.md` — skill-hub standard (Phase A/B)
- `okf/decisions/2026-08-20-okf-skill-hub-phase-a.md` — Phase A decision
- `okf/decisions/2026-08-20-skill-drift-reconciliation.md` — 12→7 reconciliation (in `d7808ca`)
- `profiles/kai/skills/devops/okf-mcp-hub/SKILL.md` → section "Standalone service `okf-mcp.service`" — full portability reference (env map, wiring schema, 401 diagnosis, drill)
- `profiles/kai/scripts/skill-hub-regen.sh` — daily regen (now restarts the service after push)
- `/home/ubuntu/work/okf-mcp-server/server.py` — server source (bearer gate at lines 303-322)
- GRO-4817 — Phase B (engine `--source <okf-checkout>`)

---

## Closeout (George, 2026-08-21) — acceptance PASS, GRO-4821 Done

**Status: closed.** All checklist items below are resolved; proof packet at
`~/.hermes/profiles/george/reports/gro4821-proof-packet-2026-08-20.md` (George profile).

- **Open 401 thread — RESOLVED.** Root cause: `/etc/okf-mcp/mcp.env` token had drifted from
  the live service environment (gate captures the token at process start). Synced file to
  live token, `sudo systemctl restart okf-mcp.service`, then round-tripped the file token on
  all three transports: stdio (Inspector CLI + direct launch), streamable-http local
  `127.0.0.1:8910/mcp`, and public `okf.growthwebdev.com/mcp` — all 200, `head=0a40e7b`.
- **Other profiles onto the shared HTTP endpoint — DONE.** All five Hermes profiles (default,
  autobot, fred, ned, george) now register `mcp_servers.okf` against `http://127.0.0.1:8910/mcp`
  with `MCP_OKF_API_KEY` bearer; verified live in the 2026-08-21 journal audit (okf MCP
  401-without-token / 200-with-token on the service).
- **Main pin — restored** to `origin/main` (`0a40e7b`) after finding the shared checkout on a
  concurrent agent's branch; untracked `okf/integrations/journal-mcp.md` preserved (merged as
  PR #38, `2e0433a`).
- **New bug found + fixed (F1):** `okf-mcp.service` runs as root on the ubuntu-owned repo →
  git dubious-ownership made `status` return `head=""` while doc counts still worked (looked
  healthy). Fixed via root `safe.directory`; optional code follow-up: `server.py:_git()`
  should surface stderr instead of swallowing it.
- **F2 (flagged, not acted):** 2 stale orphan `server.py` PIDs (946236, 946409) remain;
  kill needs Michael's explicit authorization. F3 (note): public endpoint 403s non-browser
  UAs (Cloudflare 1010).
- **"Second platform" answer:** Google Antigravity (desktop). It connects remote MCPs via
  `serverUrl` + static `Authorization: Bearer <token>` header; existing bearer design covers
  it, so **Phase 3 (OAuth 2.1 + PKCE) stays deferred** until a client genuinely cannot send
  static headers.
- **GRO-4821 marked Done** (Michael's explicit Telegram authorization, 2026-08-21; stateId-only
  mutation per `single-issue-state-transition-after-acceptance`): before Todo
  `3d29ebe3` → after Done `bbf71b3e`, `completedAt 2026-08-21T02:16:37.942Z`; receipt
  `~/.hermes/profiles/george/reports/reconciliations/linear-gro4821-done-receipts.jsonl`
  (sha256 `aab948399bb853611f237daabda6b497b84413b1a228883ae5a8d4cdb2a0f3cf`).

Remaining (out of this ticket): orchestrator-down drill; `okf/standards/` final wiring doc
(Kai's lane); orchestrator-gateway-outside-systemd ticket (Kai).
