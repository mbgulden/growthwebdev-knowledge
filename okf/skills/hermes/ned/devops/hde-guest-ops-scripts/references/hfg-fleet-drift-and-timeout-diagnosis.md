# HFG fleet drift + guest-bot timeout/routing diagnosis

Session: 2026-08-20. Independent review of the HFG (guest-fleet build-drift) fix
(GRO-4797, VERDICT=CLEAN) + root-causing Michael's live "Sanctuary container took
too long" / someone-else's-chart symptoms. Root causes CONFIRMED this session;
ticketed as GRO-4822 (umbrella) / GRO-4823 (routing+rebind) / GRO-4824 (timeout
chain), prio 1, label `agent:ned-infra`.

**STATUS 2026-08-21 (final): both failure modes repaired AND shipped. Router timeout fix + full router subsystem on main (PR #56, a13723b); GRO-4823 rebind guard = PR #57 (7817c81); PROD rebind `8190664947`→user 2 + user-43 suspension EXECUTED against the prod Postgres DB; vLLM prefix caching enabled + verified. Read the "2026-08-21 resolution" section at the end BEFORE re-diagnosing or re-fixing — several earlier findings in this doc were overturned (see the "CORRECTION" note under Failure mode B).**

## Scope boundary (answer "will HFG fix X?" with this)

The HFG fix is **code-version unification only**: 12 guest containers each run
their own copy of `guest_agent_server.py`; HFG makes all live copies hash-identical
(`fleet_audit.py` / `fleet_sync.py` / `.build` markers / dev-name guard).
It does **NOT** touch:
- the LLM backend (guests run `hermes -z <prompt>` one-shots against a local model),
- the tenant router (`scripts/hde_tenant_router.py` — chat → container mapping),
- per-guest data (people/charts under `/home/ubuntu/users/guest_N/`).

So HFG cannot fix (a) model latency/availability timeouts or (b) a chat being
routed to the wrong guest container. Check Linear scope before attributing a fix.

## Prod DB access (needed for failure mode B)

- Real DB: **Postgres `127.0.0.1:5432/hde`**, user `hde_app`. Credentials come
  from `DATABASE_URL` in `/home/ubuntu/work/hd-platform-staging/.env` — never
  print the password. Use Python (sqlalchemy async or asyncpg); the `sqlite3`
  CLI is not installed on this host.
- **Trap:** `/home/ubuntu/work/hd-platform/production_database.db` is a 0-byte
  decoy file — the real store is Postgres.
- Schema facts: `users` has **no `username` column** (query `email` instead);
  useful columns `email`, `access_status` (`paid`/`demo`/`expired_demo`/…),
  `guide_name`. `bot_instances`: `id, user_id, telegram_user_id, container_name,
  workspace_path, api_key_limits, status, host_node_ip`. **CORRECTION (verified
  live 2026-08-21):** `bot_instances.telegram_user_id` IS unique — the index
  `ix_bot_instances_telegram_user_id` is `UNIQUE` in both the model (main) and the
  prod DB (Postgres treats NULLs as distinct, so unbound rows never collide). The
  earlier "no unique constraint" note was wrong: the silent-steal bug was NOT a
  missing constraint — it was the app claim path *intentionally* NULLing the prior
  binding then rebinding, a sequence the constraint can't catch. The fix is the
  application-level guard (`scripts/hde_rebind_guard.py`, PR #57), not DDL.

## Failure mode A: "⚠️ Connection timeout: Sanctuary container took too long to process"

CONFIRMED timeout chain (2026-08-20):

| Layer | Limit | Location |
|---|---|---|
| Router per-POST to guest | **35s** | `hde_tenant_router.py:682/716` |
| Router per-chat budget | 45s (`HDE_ROUTER_CHAT_TIMEOUT_SECONDS`) | line 40 |
| Guest `hermes -z` subprocess | **120s** | `guest_agent_server.py` `run_llm_with_context` (~line 1941) |

The router abandons exactly the slow turns that would have finished inside the
guest's 120s cap; the guest keeps burning GPU on the abandoned request.

Model path (confirmed, not inferred):
- Guest containers' hermes config lives at `/home/pn/.hermes/config.yaml` **inside
  the container**: provider `qwen27b-fred-local` → `http://192.168.1.230:8000/v1`
  (vLLM), model `local-qwen-27b-q8-fred`.
- `192.168.1.230:8002` (llama.cpp Qwen3.8-27B Q4) is a **zombie**: `/health` → 200
  but completions hang >15-20s (HTTP 000). Nothing in the guest configs references
  it, but it's a diagnostic trap — `/health` is not proof of service.
- **Prompt bloat is the multiplier**: `build_llm_prompt` sends ~**14k tokens**
  per turn (full system prompt + entire conversation history + guide constitution +
  tool policy — a single `hermes -z` argv in the logs is ≈56k chars). Benchmarks
  on `:8000` (2026-08-20): 3-token completion 11.25s (cold first probe),
  4,941-token prompt → 4.5s. At ~14k tokens with CLI overhead + 10 concurrent
  guests contending for one vLLM, the 35s router wall is routine.

Diagnosis recipe (all live probes, no inference):
1. `docker ps | grep guest-hermes` — "healthy" ≠ model healthy.
2. Read the **container's** hermes config (`docker exec <c> sh -c 'grep -A6
   providers ~/.hermes/config.yaml'`) to find the endpoint actually called —
   don't assume from host env.
3. Probe every candidate endpoint with a **real completion + curl timing**
   (`-w "%{http_code} %{time_total}s"`), not `/health`.
4. Compare measured latency at **realistic prompt size** (~14k tokens) against
   the 35s router POST cap.
5. Verdict shape: "timeout chain mismatch + prompt bloat (+ zombie sibling
   server), not a down server, not a code-version problem."

Fix directions (GRO-4824): align the timeout chain (or stream/heartbeat);
prompt diet (cap history, cache the static constitution/policy block, target
<5k tokens); quarantine `:8002`; per-guest semaphore/queue on the vLLM call.

## Failure mode B: chat shows someone else's chart (CONFIRMED root cause)

**Root cause (2026-08-20, prod DB):** chat→container resolution is by
`bot_instances.telegram_user_id`. Michael's phone (chat `8190664947`) was bound
to **user 43** — `ned-probe@growthwebdev.com`, a **demo** probe account created
2026-08-19 **from the same phone** — → `guest-hermes-43` → workspace
`/home/ubuntu/users/guest_43` whose `people/index.json` default person is the
seeded **`sanctuary_guest`** chart (1955-03-22 16:45 San Diego,
Generator/Sacral 4/6). Michael's real account (user 2, `mbgulden@gmail.com`,
→ `guest-hermes-2`, default person `michael_gulden`) had
`telegram_user_id = NULL` — his phone could not reach his own container at all.

**How it happened (code):** `hde_tenant_router.py:433-463` claim/rebind path —
when a chat already bound to one bot instance signs in as a **new** user (the
08-19 demo signup), the code sets the prior binding
`existing_chat_bot.telegram_user_id = None` (line 447) and rebinds to the new
user (lines 454/463). **No guard** for the prior owner being a real/paid
account (the unique index does NOT save you here — the code NULLs the prior
row *before* rebinding, so the constraint never fires). Any future test
signup from a real owner's phone silently steals the chat. **Fixed (PR #57):**
`scripts/hde_rebind_guard.py` `evaluate_rebind()` refuses to move a chat whose
prior owner is protected (`access_status=paid` or `is_premium`), allows
reclaiming demo/expired/inactive bindings with a `REBIND ALERT` log, and fails
closed on unreadable access_status.

**Collateral damage to watch:** the LLM on the misrouted container, fed the
foreign chart in a 14k-token context, will *confidently rationalize* it — in the
guest_43 logs the guide hallucinated a person named "Rosa" to explain whose
birthday was stored. Never trust the bot's self-diagnosis of "whose chart is
this"; go to the DB.

Fast diagnosis recipe:
1. `SELECT id, user_id, telegram_user_id, container_name, status FROM bot_instances
   WHERE telegram_user_id = '<chat_id>';` → which user/container owns the chat.
2. `SELECT id, email, access_status FROM users WHERE id = <user_id>;` → real or
   demo account?
3. `cat /home/ubuntu/users/guest_<user_id>/people/index.json` → `default_person`;
   that profile is what the chat sees.
4. If mismatched: repair = 2-row UPDATE (null the demo row, set the real row),
   **gated on owner approval — prod DB write**. Then verify with the SELECT.
5. Code fix (GRO-4823): refuse/require-confirmation in the claim path when the
   existing binding is a real (non-demo) account; add partial unique index
   `CREATE UNIQUE INDEX … ON bot_instances(telegram_user_id) WHERE
   telegram_user_id IS NOT NULL`; alert-log on any rebind.

## Verification facts from the HFG independent re-run (2026-08-20)

- `.build` markers are **dotfiles at the guest-dir root**
  (`/home/ubuntu/users/guest_N/.build`), NOT `guest_agent_server.py.build` —
  probing `<file>.build` gives false MISMATCH on every guest.
- The packet's evidence JSON sweep is a *subset* of a full walk: a full walk also
  hits `people/<name>/profile.json` + `latest_chart_data.json` (pre-incident
  mtimes). Same guest set (2 & 23) — don't call it a discrepancy.
- Boot log is the durable record of drift tests: grep `BUILD-IDENTITY` in
  `docker logs guest-hermes-N` (md5/lines/marker per boot).
- Template identity: `md5sum` + `wc -l` of
  `scripts/guest_hermes_template/guest_agent_server.py` (was `baf3887b…`/2725).
- Guard: `grep -c is_blocked_person_name` inside the container (expect 3) and a
  live import test (blocks `Michael Gulden`/`becca`, passes `Jordan Smith`).

## Linear tickets (session detail)

- GRO-4822 umbrella (symptoms + both root causes + evidence).
- GRO-4823 routing/rebind: gated data repair (2-row UPDATE, SQL in ticket) +
  claim-path guard + partial unique index.
- GRO-4824 timeout chain: timeout-chain alignment, `:8002` quarantine (gated),
  prompt diet, concurrency.
- HFG close-out still open separately: GRO-4814/4815 (skill + readback),
  commit/PR of the 5 uncommitted HFG paths (owner's gate).

## 2026-08-21 resolution (both failure modes fixed on staging)

### Failure mode B (wrong chart) — rebind DONE, verified
- Michael approved the rebind (his explicit "do the rebind"). Applied to staging
  DB: chat `8190664947` → **user 2** → `guest-hermes-2` (workspace
  `/home/ubuntu/users/guest_2`, default person `michael_gulden`).
- The demo row (user 43) was left **orphaned** (`telegram_user_id=NULL`), not
  deleted → rollback path preserved. Row state verified: `bot_instances.id=7,
  user_id=2, status=active, guide_name=Ember, is_premium=True`.
- Router resolves `telegram_user_id` **per message, no cache** (49 references in
  `hde_tenant_router.py`) → the DB change took effect **immediately, no router
  restart required for the binding itself**.
- Verify the served identity live: `docker exec` is unnecessary — POST
  `http://<guest-hermes-2-ip>:8000/api/message` and the response self-reports the
  profile ("serving Michael Gulden — Projector/Splenic 3/5"). Get the IP with
  `docker inspect guest-hermes-2 --format
  '{{range $n,$c := .NetworkSettings.Networks}}{{if $n}}{{printf "%s " $c.IPAddress}}{{end}}{{end}}'`
  (the `.Network.Networks` template key is WRONG for this setup — use
  `.NetworkSettings.Networks`).

### Failure mode A (timeout chain) — root cause was DEEPER than the 35s cap
The 35s router wall was real, but it was the **symptom**, not the whole story.
Measured live (2026-08-21) on the re-bound, healthy container:
- Trivial 43-token prompt took **50s** direct to vLLM; real guest turns **59–119s**.
- vLLM log during the test: `Running: 2 reqs` + generation throughput collapsing
  to **1–40 tok/s**. **Something else was sharing the GPU** — this is the
  multiplier the 2026-08-20 session only hypothesized.
- All 4× RTX 3090 at **87–100%** util, VRAM near full. `nvidia-smi
  --query-compute-apps` showed the contention: `VLLM::Worker_TP0/TP1` (vllm-fred,
  GPUs 0-1) **plus two `llama-server-new` processes** (vllm-george GPU2, vllm-ned
  GPU3). vLLM-fred is a 2-GPU tensor-parallel instance (27B INT8 + MTP
  spec-decoding), so it is NOT isolated to 2 GPUs by construction — it shares the
  box with the two llama.cpp services.
- **`192.168.1.59` (`webtop-hermes`) is ALSO a vLLM `:8000` client** (its own
  Hermes running the same `local-qwen-27b-q8-fred`). So the local model is a
  shared multi-tenant endpoint: webtop-hermes + the guest containers all hit one
  vLLM engine. This is why "Fred's profile works" — **Fred's path has no timeout
  wall and no bloated prompt**, so it just waits out the shared model; the guest
  path has the 35s wall + the ~14k-token prompt. Multi-tenancy is NOT the bug;
  the per-path timeout budget + prompt bloat are.

**Fix applied (staging, UNCOMMITTED — dirty tree, no branch yet):**
1. Router per-POST timeout: hardcoded `35.0` at `hde_tenant_router.py:682/716`
   → new constant `GUEST_TURN_TIMEOUT_SECONDS` (env
   `HDE_GUEST_TURN_TIMEOUT_SECONDS`, default **180s**), defined right after
   `ROUTER_CHAT_TIMEOUT_SECONDS` (~line 40).
2. Router per-chat budget `.env`: `HDE_ROUTER_CHAT_TIMEOUT_SECONDS` 45 → **240**.
3. Guest inner `hermes -z` subprocess timeout `guest_agent_server.py`
   (`run_llm_with_context`, ~line 1935): `120` → **240** so the inner cap can't
   500-out under the router's new 180s budget.
4. History de-bloat: `/home/ubuntu/users/guest_2/conversation_history.json` had
   **16 entries, 13 of them a July "Yes pdf report" loop** re-prefilling ~20k
   tokens every turn (vLLM `Prefix cache hit rate: 0.0%`). Trimmed to the 3 real
   2026-08-21 turns. Backup: `.bak-20260821T032759Z`.
5. Router restarted (`sudo -n systemctl restart hde_router.service` — plain
   `systemctl restart` fails with "Interactive authentication required" for the
   ubuntu user; `sudo -n` works). Confirmed the **live process** env via
   `tr '\0' '\n' < /proc/<pid>/environ`.

**Post-fix measured result:** final warm turn **18.7s** (was 59–119s) — well
inside the 180s budget.

**Residual risk (NOT fixed):** when webtop-hermes AND a guest container run
simultaneously, throughput drops and a turn can still stretch toward the 3-min
budget. Durable options (need owner OK, they touch a SHARED service): enable
vLLM prefix caching (`--enable-prefix-caching`) so the stable ~5k-token prompt
prefix isn't re-prefilled every turn; per-guest semaphore/queue on the vLLM
call; move vllm-fred onto its own GPUs. Do NOT restart `vllm-fred.service`
without explicit approval — it serves webtop-hermes (Fred) too.

**Re-verify recipe (fast, no inference):**
```bash
IP=$(docker inspect guest-hermes-2 --format '{{range $n,$c := .NetworkSettings.Networks}}{{if $n}}{{printf "%s " $c.IPAddress}}{{end}}{{end}}')
time curl -s -m 300 -X POST http://$IP:8000/api/message \
  -H 'Content-Type: application/json' \
  -d '{"text":"Confirm in one short sentence which person you are serving."}'
# healthy: response self-reports michael_gulden, real time < ~60s (not 3-min)
```
