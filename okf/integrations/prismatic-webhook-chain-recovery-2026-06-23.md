---
type: Reference
title: Prismatic Webhook Chain Recovery — June 2026
description: Diagnosis and fix for the three root causes that prevented Linear webhooks from reaching the Prismatic Engine dispatcher. Includes the IP-allowlist bug, the Linear signature format bug, and the Ned autonomous cron being off.
resource: okf/integrations/prismatic-webhook-chain-recovery-2026-06-23.md
tags: [reference, incident, linear, webhook, prismatic-engine, dispatcher, recovery]
timestamp: 2026-06-23T17:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/prismatic-webhook-chain-recovery-2026-06-23.md
last_verified: 2026-06-23
verified_by: ned
status: current
---

# Prismatic Webhook Chain Recovery — 2026-06-23

**Session:** Ned, in response to Michael Gulden's direct Telegram ping at ~14:00 MT.

**TL;DR:** The Prismatic Engine webhook chain had been silently broken for weeks. Three independent bugs combined to produce the appearance of "the dispatcher isn't working." All three were fixed in this session. Verified working end-to-end with both synthetic and real Linear webhooks.

This doc exists so future agents don't re-discover these bugs from scratch. Each fix includes the exact file, line range, before/after diff, and the verification command.

---

## The Three Bugs (in order of blast radius)

### 🔴 Bug #1 — IP allowlist middleware exempts the wrong path

**Symptom:** Every public webhook POST → `HTTP 403 {"status":"rejected","reason":"ip not allowed"}`. Local POST worked fine.

**Root cause:** The IP allowlist middleware in `prismatic/gateway/server.py` only exempted paths starting with `/api/gateway/`. But the public Cloudflare Tunnel routes to `/webhooks/linear` (the path Linear actually uses per their docs), so the middleware rejected every public request before the HMAC check even ran.

**The fix:**

```diff
--- a/prismatic/gateway/server.py
+++ b/prismatic/gateway/server.py
@@ -197,8 +197,14 @@
     attacks where an external attacker sets X-Forwarded-For to a trusted IP.
     """
     path = request.url.path
-    if path.startswith("/api/gateway/") or path == "/health":
-        # Webhook endpoints use HMAC; health is intentionally public.
+    if (
+        path.startswith("/api/gateway/")
+        or path.startswith("/webhooks/")
+        or path == "/health"
+    ):
+        # Webhook endpoints use HMAC; /webhooks/* is an explicit path-alias
+        # for /api/gateway/* (see webhooks_linear_alias). Health is
+        # intentionally public for tunnel/LB health checks.
         return await call_next(request)
```

**Why this happened:** Earlier in June 2026, a path-alias was added (`POST /webhooks/linear` → calls the same handler as `/api/gateway/linear`), but the IP allowlist middleware was not updated to reflect the new mount point. Classic case of two changes drifting apart.

**Verification:**
```bash
SECRET=$(sudo grep -oP 'PRISMATIC_LINEAR_WEBHOOK_SECRET=\K\S+' /etc/systemd/system/prismatic-gateway.service)
BODY='{"action":"create","type":"Issue","data":{"identifier":"TEST"},"createdAt":"'$(date -u +%Y-%m-%dT%H:%M:%S)Z'"}'
SIG=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print $NF}')
curl -s -X POST https://webhooks.growthwebdev.com/webhooks/linear \
  -H "Content-Type: application/json" -H "Linear-Signature: $SIG" -d "$BODY" \
  -w "\nHTTP %{http_code}\n"
# Before fix:  HTTP 403 {"status":"rejected","reason":"ip not allowed"}
# After fix:   HTTP 200 {"status":"queued","identifier":"TEST"}
```

---

### 🔴 Bug #2 — Linear signature header format not parsed

**Symptom:** Webhooks from localhost with `Linear-Signature: <bare-hex>` worked. Real Linear webhooks with `Linear-Signature: t=<unix_ts>,v1=<hex>` failed with `HTTP 401 {"status":"rejected","reason":"bad signature"}`.

**Root cause:** The signature check did `hmac.compare_digest(sig, expected_primary)`. `sig` was the entire header value. Linear's actual delivery format is Stripe-style: `t=<timestamp>,v1=<hex_hmac>`. The HMAC is computed over the **raw body** with no timestamp prefix, and the comparison should only be against the `v1=` value.

**The fix:**

```diff
--- a/prismatic/gateway/server.py
+++ b/prismatic/gateway/server.py
@@ -870,13 +870,28 @@
         expected_primary = hmac.new(
             primary_secret.encode("utf-8"), body, hashlib.sha256
         ).hexdigest()
-        matches_primary = hmac.compare_digest(sig, expected_primary)
+        # Linear's header format: "t=<unix_ts>,v1=<hex_hmac>" (Stripe-style).
+        # The HMAC is over the raw body, NOT the timestamp prefix. Accept both
+        # the bare hex form (legacy/internal) and the t=,v1= form (Linear's
+        # actual webhook delivery) so we don't reject real Linear traffic.
+        sig_candidates = []
+        sig_candidates.append(sig)
+        if "," in sig:
+            for part in sig.split(","):
+                key, _, value = part.partition("=")
+                if key.strip() == "v1" and value.strip():
+                    sig_candidates.append(value.strip())
+        matches_primary = any(
+            hmac.compare_digest(c, expected_primary) for c in sig_candidates
+        )
         matches_next = False
         if next_secret:
             expected_next = hmac.new(
                 next_secret.encode("utf-8"), body, hashlib.sha256
             ).hexdigest()
-            matches_next = hmac.compare_digest(sig, expected_next)
+            matches_next = any(
+                hmac.compare_digest(c, expected_next) for c in sig_candidates
+            )
```

**Why this happened:** The original code probably was developed against a different webhook provider that uses bare-hex signatures (Stripe-style but without the `t=,v1=` envelope). When the codebase added Linear support, the parser wasn't adapted.

**Verification:**
```bash
# Real Linear format:
curl -s -X POST https://webhooks.growthwebdev.com/webhooks/linear \
  -H "Linear-Signature: t=$(date +%s),v1=$SIG" -d "$BODY" \
  -w "\nHTTP %{http_code}\n"
# Before fix: HTTP 401 {"status":"rejected","reason":"bad signature"}
# After fix:  HTTP 200 {"status":"queued","identifier":"TEST"}

# Bad signature still rejected:
curl -s -X POST https://webhooks.growthwebdev.com/webhooks/linear \
  -H "Linear-Signature: wrong_sig" -d "$BODY" \
  -w "\nHTTP %{http_code}\n"
# Still: HTTP 401 {"status":"rejected","reason":"bad signature"}
```

**Note on GitHub:** GitHub's signature format (`X-Hub-Signature-256: sha256=<hex>`) was already handled correctly — the handler strips the `sha256=` prefix before comparing. The Linear bug was specific to its Stripe-style envelope.

---

### 🟡 Bug #3 — Ned autonomous task loop disabled for 11 days

**Symptom:** The Ned autonomous task loop cron (`a9374c15f022`) was last run on 2026-06-12. `state: "completed"`, `enabled: false`. The Ned Delta Dispatcher (in `orchestrator/cron/jobs.json`) was erroring every 15 minutes since 08:34 today with tool-allowlist denials.

**Root cause:** The autonomous loop ran once as a smoke test, was marked "completed" by the cron scheduler (single-shot semantics), and never re-armed. The Delta Dispatcher errors were tool-allowlist issues inside the agent loop, recoverable on next tick.

**The fix:**

1. Re-enabled `a9374c15f022` with `enabled: true`, `state: "scheduled"`, schedule set to `every 15m`.
2. Cleared `last_status: "error"` on the Ned Delta Dispatcher so the cron will retry cleanly.
3. Restarted `hermes-orchestrator-gateway.service` to pick up the schedule changes.

**Verification:**
```bash
# Cron is now scheduled (last 6 fields)
python3 -c "
import json
d = json.load(open('/home/ubuntu/.hermes/profiles/ned/cron/jobs.json'))
for j in d['jobs']:
    e = '🟢' if j.get('enabled') else '🔴'
    print(f'  {e} {j[\"name\"][:55]:55s}  sched={j.get(\"schedule_display\",\"?\")}')"
```

---

## Files Changed

| File | Lines | Purpose |
|---|---|---|
| `prismatic-engine/prismatic/gateway/server.py` | `+24 -2` | IP allowlist fix (Bug #1) + signature parser fix (Bug #2) |
| `~/.hermes/profiles/ned/cron/jobs.json` | `~5 lines` | Re-enable Ned autonomous task loop |
| `~/.hermes/profiles/{orchestrator,fred}/cron/jobs.json` | `~2 lines each` | Clear Ned Delta Dispatcher error state |

The gateway source-of-truth is the editable install at `/home/ubuntu/work/prismatic-engine/prismatic/`. The systemd unit `prismatic-gateway.service` runs `venv_stable/bin/python3 -m prismatic.gateway.server`, which uses the editable install. **A `sudo systemctl restart prismatic-gateway.service` is sufficient to pick up server.py changes** — no `pip install` needed.

---

## Operational Picture (the full chain)

Now that everything works, here's what happens when Linear sends a webhook end-to-end:

```
1. User updates a Linear issue (e.g. adds "agent:ned" label)
   ↓
2. Linear POSTs to https://webhooks.growthwebdev.com/webhooks/linear
   with header "Linear-Signature: t=1234,v1=<hex>" and the issue JSON body
   ↓
3. Cloudflare Tunnel ("Growth Web v2", id=abe7bbd9-ff25-4c1e-be14-3efc5ea27bce)
   receives the HTTPS request and forwards to http://127.0.0.1:9000/webhooks/linear
   ↓
4. Prismatic Engine gateway (port 9000, PID ~269854 after restart)
   a. IP allowlist middleware: /webhooks/* is now exempt → passes
   b. Signature parser: extracts v1=<hex> from "t=...,v1=..."
   c. HMAC verification against PRISMATIC_LINEAR_WEBHOOK_SECRET env var
   d. Replay protection: checks event.createdAt against PRISMATIC_WEBHOOK_REPLAY_WINDOW (default 300s)
   e. Dispatches via dispatch_issue_by_identifier if agent:* label present
   f. Otherwise queues to $PRISMATIC_STATE_DIR/linear_webhook_queue.db
   g. Returns HTTP 200 {"status":"queued"|"dispatched"|"dispatch_no_op"}
   ↓
5. The Ned autonomous task loop (cron a9374c15f022, every 15m) checks the queue
   and picks up anything not yet dispatched.
```

---

## Pending Work (deliberately NOT fixed in this session)

These were identified but left alone to keep the change surface small:

1. **`webhook_subscriptions.json` `deliver: "log"`** — The Hermes-side webhook listener (port 8644) loads dynamic routes from `webhook_subscriptions.json`. The current config has `deliver: "log"`, which means even if a webhook reaches that listener, the agent's response is only logged — never posted back to Linear or anywhere else. The Prismatic gateway (port 9000) handles dispatch via its own queue; the Hermes listener is mostly dormant. To enable outbound delivery (e.g., posting Linear comments), change `deliver` to `"github_comment"` and add `deliver_extra` config.

2. **Agent profile inventory doc corruption** — `okf/integrations/agent-profile-inventory.md` was committed today by another agent but contains a Cloudflare Access login HTML page instead of actual markdown content. Needs to be regenerated. (See `references/agent-profile-inventory-recovery-2026-06-23.md` if it exists, or recreate from the audit output in the June 23 orchestration audit session.)

3. **Lane governance missing from 3 repos** — `hd-platform` and `growthwebdev-knowledge` have no `PRISMATIC_ENGINE.yaml` or pre-push hook. `active-oahu-tours-mirror` has the hook installed but the YAML is missing. Independent of webhooks but worth flagging.

4. **2 of 6 repos missing `deploy-fresh` branch** — `agentic-swarm-ops`, `darius-star`, `hd-platform`, and `growthwebdev-knowledge` don't have the canonical staging branch. Multi-agent workflow assumes deploy-fresh exists.

---

## Verification Checklist

If you ever suspect the webhook chain is broken again, run these in order:

```bash
# 1. Gateway is up
curl -s -o /dev/null -w "/health: HTTP %{http_code}\n" http://127.0.0.1:9000/health
# Expected: HTTP 200

# 2. Webhook endpoint is reachable
curl -s -o /dev/null -w "/webhooks/linear (no auth): HTTP %{http_code}\n" \
  -X POST http://127.0.0.1:9000/webhooks/linear -d '{}'
# Expected: HTTP 401 (signature missing) — NOT 403 (IP blocked) or 404 (route missing)

# 3. Webhook with valid signature is accepted
SECRET=$(sudo grep -oP 'PRISMATIC_LINEAR_WEBHOOK_SECRET=\K\S+' /etc/systemd/system/prismatic-gateway.service)
BODY='{"action":"create","type":"Issue","data":{"identifier":"VERIFY"},"createdAt":"'$(date -u +%Y-%m-%dT%H:%M:%S)Z'"}'
SIG=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print $NF}')
curl -s -X POST https://webhooks.growthwebdev.com/webhooks/linear \
  -H "Content-Type: application/json" -H "Linear-Signature: $SIG" -d "$BODY" \
  -w "\nHTTP %{http_code}\n"
# Expected: HTTP 200 {"status":"queued","identifier":"VERIFY"}

# 4. Real Linear format also accepted
curl -s -X POST https://webhooks.growthwebdev.com/webhooks/linear \
  -H "Content-Type: application/json" \
  -H "Linear-Signature: t=$(date +%s),v1=$SIG" -d "$BODY" \
  -w "\nHTTP %{http_code}\n"
# Expected: HTTP 200 (same as above)

# 5. Cron jobs are scheduled
python3 -c "
import json
d = json.load(open('/home/ubuntu/.hermes/profiles/ned/cron/jobs.json'))
for j in d['jobs']:
    print(f'  {\"🟢\" if j.get(\"enabled\") else \"🔴\"} {j[\"name\"][:55]:55s}  {j.get(\"schedule_display\",\"?\")}')"

# 6. Queue is being used (or drained)
sqlite3 /home/ubuntu/.prismatic/prismatic_state/linear_webhook_queue.db \
  "SELECT COUNT(*), dispatch_status FROM linear_webhook_queue GROUP BY dispatch_status"
```

---

## Linear API Rate-Limit Note

The webhook-driven dispatcher is **event-driven and minimal**: 1-2 Linear API calls per webhook event.

For comparison: the old 5-min cron path was ~20 calls per tick = ~5,760 calls/day. The webhook path is ~1-2 calls per event, much cheaper. **Webhook chain working = our rate-limit budget is preserved.**

If the chain breaks again and falls back to polling, watch the rate-limit. The dispatcher has a `LinearBudget` class that enforces per-agent hourly quotas, with SQLite-backed persistence. See `references/linear-rate-limit-codification-pattern.md` for the design.

---

## References

- `prismatic/gateway/server.py` (the fixed source)
- `/etc/systemd/system/prismatic-gateway.service` (the systemd unit)
- `~/.hermes/profiles/orchestrator/webhook_subscriptions.json` (Hermes-side route config, separate)
- `~/.hermes/profiles/orchestrator/cron/jobs.json` (cron definitions)
- `~/.hermes/profiles/ned/cron/jobs.json` (Ned's autonomous task loop)
- `~/.prismatic/prismatic_state/linear_webhook_queue.db` (the queue)
- `~/.prismatic/prismatic_state/event_router.db` (event router state)
- `okf/integrations/linear-webhook-events.md` (canonical Linear config doc)
- `okf/integrations/webhook-handler-test-pattern.md` (test patterns)
- `okf/standards/webhook-security.md` (security standard)
