# HDE Live Launch Gap Pattern — 2026-07-15

## Context

After the HDE guide/deconditioning runtime is green server-side, the next useful question is not another prompt tweak. It is: what proof is missing before public traffic?

This session established a reusable launch-gap audit for Human Design Engine Sanctuary / deconditioning bot work.

## Launch gap sequence

When Michael asks "what's the next step?" for HDE go-live, audit in this order:

1. **Server-side guide runtime**
   - `guest-hermes-23` Docker health.
   - `hde_guest_canary.py --guest-id 23 --pretty` passes.
   - Recent runtime/template match if guest server was edited.
   - HDE build passes if web/docs/runtime package changed.

2. **Router and queue health**
   - `hde_router.service`, `hde_api_staging.service`, `hde-reports.service`, `hde_orchestrator_staging.service` active.
   - `hde_router_metrics.py --pretty` status ok.
   - Redis enabled and queue pending counts zero or understood.
   - Guest containers healthy/running count makes sense.

3. **Telegram identity**
   - Safe `getMe` check: print only `ok`, `id`, `username`, `first_name`.
   - Confirm `HDE_ONBOARDING_BOT_USERNAME` matches `getMe.username`.
   - Never print the token.

4. **Public conversion path**
   - Main HDE pages load: home, buy-report, success/onboarding page.
   - Stripe/payment/onboarding smoke tests pass if changed.
   - Environment has expected keys for Stripe, DB, Redis, coach bot token, onboarding username.

5. **Live Telegram proof — usually the remaining gap**
   - Server-side canary is not live proof.
   - Start `scripts/hde_telegram_media_watch.py --since now --expect-documents 2 --watch-seconds 1200 --interval 10 --guest-id 23 --pretty`.
   - Ask Michael/a tester to message the actual Telegram bot, preferably `Compare me and Becca` because it exercises stored profiles, chart comparison, plural PDFs, router media upload, and queue drain.
   - Poll/wait for watcher result before claiming live transport green.

6. **Launch hygiene**
   - Dirty staging tree is a go-live risk. Checkpoint/commit or explicitly note what remains uncommitted.
   - Old launch reports are stale after many fixes; produce/refresh the launch report after live Telegram proof.
   - Coach review endpoints are a separate privacy gate: token-only `/api/coach/review` is not blocking basic public bot launch if coach dashboard is not exposed, but it is blocking coach-dashboard launch.

## Human-facing answer shape

Use a gap report, not a long archaeology dump:

```md
## Current read
🟢 Server-side guide runtime is ready / 🟡 not ready because ...

## Actual gap to live
1. 🔴 Live Telegram proof: <what tester must send>
2. 🟡 Workspace checkpoint: <dirty files / branch risk>
3. 🟡 Privacy/payment/report caveats: <only if relevant>

## Next step
Send `<exact canary message>` to `<bot username>`. I have the watcher running / I will start it now.
```

## Pitfalls

- Do not keep patching prompt/runtime after server-side canary is green unless the audit finds a specific broken behavior.
- Do not call the bot live from server-side API checks alone. Live Telegram media transport requires a real Telegram user message.
- Do not let stale RED launch reports override fresh evidence; explain which old blockers are now resolved and which still need verification.
- Do not bury the user in internal status. Michael wants the gap and the next action tied to go-live.
