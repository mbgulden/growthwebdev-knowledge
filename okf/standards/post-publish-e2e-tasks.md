# Post-Publish E2E — 100% Live Task List

**Epic:** GRO-2280
**Created:** 2026-06-23
**Owner:** Fred (orchestrator)
**Status:** All 14 children filed + assigned

## Goal

Take the event-driven post-publish system from **80% built / 60% wired / 0% proven live**
to **100% built / 100% wired / 100% proven live**.

## Children (14 total)

### P0 — Block real Linear event flow (3 issues)

| ID | Title | Agent |
|---|---|---|
| GRO-2281 | Bypass Cloudflare Access for `prismatic.growthwebdev.com/api/gateway/linear` | `agent:ned` |
| GRO-2282 | Verify real Linear webhook fires the bridge end-to-end | `agent:fred` |
| GRO-2283 | Investigate the 4-day Linear webhook outage (Jun 19 → today) | `agent:fred` |

### P1 — Verification and hardening (4 issues)

| ID | Title | Agent |
|---|---|---|
| GRO-2284 | Add post-condition verification: confirm OKF doc was actually written | `agent:ned` |
| GRO-2285 | Add Telegram notification when issues are stuck in `Done - Doc Pending` > 24h | `agent:fred` |
| GRO-2286 | Add a Linear-side heartbeat: bridge posts a comment every hour when alive | `agent:fred` |
| GRO-2287 | Document the post-publish state machine in OKF | `agent:fred` |

### P2 — Nice-to-haves (4 issues)

| ID | Title | Agent |
|---|---|---|
| GRO-2288 | Add retry logic to the bridge: transient failures shouldn't drop events | `agent:agy` |
| GRO-2289 | Add a stuck post-publish alert (any stage > 7 days) | `agent:fred` |
| GRO-2290 | Add per-repo velocity tracking to make audit thresholds smarter | `agent:agy` |
| GRO-2291 | Add a Linear dashboard for post-publish metrics | `agent:fred` |

### P3 — Tools and tests (3 issues)

| ID | Title | Agent |
|---|---|---|
| GRO-2292 | Add a self-test cron that exercises the full post-publish chain weekly | `agent:agy` |
| GRO-2293 | Add a pre-commit hook for the bridge + orchestrator scripts | `agent:ned` |
| GRO-2294 | Add a replay tool to re-run a webhook event from the bridge log | `agent:agy` |

## Agent Distribution

- **agent:fred** (orchestration/docs): 7 issues
- **agent:ned** (infra/network): 3 issues
- **agent:agy** (code): 4 issues
- **agent:jules** (PR review): 0 issues
- **agent:kai** (content): 0 issues
- **agent:human** (Michael): 0 issues

## Success Criteria

The epic is **done** when:
- [ ] GRO-2281 + GRO-2282 + GRO-2283: A real Linear label change triggers the bridge within 3 seconds
- [ ] GRO-2284: A test issue that completes WITHOUT writing the doc stays in `Done - Doc Pending`
- [ ] GRO-2285: A synthetic stuck issue triggers a Telegram alert
- [ ] GRO-2286: The bridge posts a heartbeat comment every hour
- [ ] GRO-2287: The state machine doc is published
- [ ] GRO-2288: A transient failure is retried 3x before failing
- [ ] GRO-2289: A 7-day-stuck issue triggers a Telegram alert
- [ ] GRO-2290: The audit thresholds use EMA, not raw 7-day
- [ ] GRO-2291: A weekly metrics report is generated
- [ ] GRO-2292: A weekly self-test exercises the full chain
- [ ] GRO-2293: A pre-commit hook catches syntax errors
- [ ] GRO-2294: A failed event can be replayed with one command

## Current State (filed)

- ✅ Epic GRO-2280 created with full description
- ✅ All 14 children filed
- ✅ All children parented under the epic
- ✅ All children assigned to agents via labels
- ✅ Agent distribution verified: fred (7), ned (3), agy (4)

## Recommended Execution Order

1. **First** (parallel): GRO-2281 + GRO-2283 (unblock real event flow)
2. **Then**: GRO-2282 (verify the unblocked flow works)
3. **Then** (parallel): GRO-2284, GRO-2285, GRO-2286 (hardening)
4. **Then**: GRO-2287 (document the new state)
5. **Then** (parallel): P2 issues
6. **Finally** (parallel): P3 issues

## Related

- `okf/standards/event-driven-post-publish.md` — the architecture
- `okf/standards/post-publish-review-architecture.md` — the chain
- GRO-2247: Original synthetic Jules test
- GRO-2268: Synthetic post-publish test (proved the bridge logic)
- GRO-2062: CF Access OKF publisher lockdown (the original cause of the outage)
