---
type: Standard
title: Linear API Rate-Limit Codification
description: Codification of the 2500 req/hour Linear API budget. Every GraphQL call goes through LinearBudget.check_and_consume() before hitting the API.
resource: okf/standards/linear-rate-limit.md
tags: [linear, rate-limit, linearbudget, agent:agy, codification]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2008,GRO-2010,GRO-2020,GRO-2034
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/linear-rate-limit.md
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Linear API Rate-Limit Codification

**Status:** ENFORCED in both `agent_dispatcher.py` (orchestrator) and
`prismatic/linear_budget.py` (engine) as of Jun 18 2026.
**Linear budget:** 2500 req/hour (default).

This doc is also referenced from the prismatic-engine spoke bundle:
[`prismatic-engine/okf/linear-rate-limit.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/linear-rate-limit.md).

## What this standard guarantees

Every Linear GraphQL call — whether from a cron, a webhook handler, or a
manual operator — gates through `LinearBudget.check_and_consume(bucket)` before
the request is sent. When the bucket is exhausted, the call is refused with
a clear error rather than silently exhausting the API quota.

## Why this standard exists

In June 2026, the dispatcher hit Linear's 2500 req/hour ceiling during a
burst run. Until then, every `gql()` call went straight to the API with no
budget gate. This codification closes that gap.

## Where enforcement lives

| Path | Role | GRO |
|---|---|---|
| `prismatic/linear/budget.py` | Canonical engine module. Defines `LinearBudget.check_and_consume()`. | GRO-2008/2020 |
| `prismatic/linear_budget.py` | **NOT YET PRESENT** — referenced in earlier docs as canonical. The GRO-2020 module-move landed in branch `feature/linear-budget-engine-module` (commit `13de03d`) but never merged into `main` or `feature/rate-limit-runbook`. Until merge, `prismatic/linear/budget.py` is the only path. | (pending merge) |
| `~/.hermes/profiles/orchestrator/scripts/agent_dispatcher.py::_linear_gql()` | Wraps direct GraphQL with `LinearBudget.check_and_consume()`. | GRO-2034 |
| `agent_dispatcher.py::gql()` | Top-level dispatch helper. Calls `linear_call` (canonical) or `_linear_gql` (fallback). Both gated. | GRO-2034 |
| `scripts/check_linear_cron_rate.sh` | Lint script: fails CI if total expected cron usage > 2000 req/hour. | GRO-2008 |

## API

```python
from prismatic.linear.budget import LinearBudget

budget = LinearBudget(limit_per_hour=2500)
if budget.check_and_consume("cron.agent_dispatcher"):
    response = linear_call(...)
else:
    raise Exception("Rate limit exceeded for cron.agent_dispatcher")
```

Persistence: `prismatic_state/linear_budget.db` (SQLite).

## Buckets used today

| Bucket | Consumer | Approx rate |
|---|---|---|
| `cron.agent_dispatcher` | Orchestrator profile dispatcher | ~336/hour (every 5 min × 28 calls/tick) |
| `dispatcher.agent_*` | Engine dispatcher (per-agent) | varies |
| `webhook.linear` | Linear webhook handler | spike-prone |

## Webhook loophole (GRO-2034)

Webhook delivery itself is independent of Linear API budget (server-to-server
push). But the webhook handler scripts trigger `agent_dispatcher.py --one-shot`,
which now goes through `LinearBudget.check_and_consume()`. The dispatcher is
the single chokepoint for both cron and webhook paths.

Worst-case burst impact before GRO-2034: 100 webhook events × ~3 GraphQL calls
= 300 stealth-budget-burns/hour. After GRO-2034: same 300 calls, each gated;
budget exhaustion halts dispatch cleanly.

## How to add a new budget-aware caller

1. Import `LinearBudget` from `prismatic.linear.budget`.
2. Wrap your call site:
   ```python
   budget = LinearBudget()
   if not budget.check_and_consume("<your_bucket_name>"):
       raise Exception("Linear budget exhausted")
   response = linear_call(...)
   ```
3. Document your bucket in the "Buckets used today" table above.
4. Run `scripts/check_linear_cron_rate.sh` and update it if your caller adds
   > 200 req/hour.

## When the budget is exhausted

The dispatcher prints:

```text
Linear API rate limit exceeded (budget exhausted for cron.agent_dispatcher)
```

This is a hard fail, not a soft warning. The dispatch cycle aborts. The next
cron tick (5 min later) gets a fresh refill and proceeds.

## Related standards

- [review-loop-canonical.md](./review-loop-canonical.md) — companion standard

## Linear history

- GRO-2008 — LinearBudget codification (initial spec + token bucket)
- GRO-2010 — Recovery runbook
- GRO-2020 — Engine module move (`prismatic/linear_budget.py` canonical, shim at `prismatic/linear/budget.py`)
- GRO-2034 — Dispatcher fallback path wired through LinearBudget (closed loophole)
- GRO-2037 — Lint script must include webhook handlers (follow-up)
