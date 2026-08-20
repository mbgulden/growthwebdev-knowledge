# HDE stuck "Redirecting…" checkout — diagnosis + three-layer fix (2026-08-20)

Symptom: customer on `/deconditioning/` enters email + consent, button flips to
"Redirecting..." and never becomes clickable again. No Stripe session is ever
created (verify: Stripe `/v1/checkout/sessions?email=<user>` shows nothing at the
failure time). A later identical flow works — it's intermittent.

## Diagnosis recipe (do these BEFORE touching code)

1. Reproduce the exact public path the customer hit:
   `POST https://humandesignengine.com/api/checkout/create-session` (public domain,
   not localhost). Time it. If it hangs >20s with no response, that's the bug class.
2. Compare against the direct upstream:
   `POST http://127.0.0.1:8000/api/checkout/create-session`. If upstream answers in
   <1s but the public path hangs → the CF Pages Function proxy layer is the gap.
3. Confirm no session was created: query Stripe for the customer's email in a
   time window. Absence proves the request never completed end-to-end (client-side
   hang or dropped in transit), not a Stripe-side rejection.
4. Read the frontend submit handler. The bug pattern:
   ```js
   submitBtn.disabled = true;          // BEFORE try
   submitBtn.textContent = 'Redirecting...';
   try { const r = await fetch(...); } // NO timeout, NO re-enable on error
   ```
   Any hang (or any thrown error in the gap) leaves the button permanently disabled.

## Three-layer fix (all three are needed; any one alone is insufficient)

1. **Frontend (Astro inline script)**: wrap the fetch in a `Promise.race` with a
   `setTimeout` + `AbortController`; on timeout OR error, `re-enable the button` and
   set an error message ("Payment service unreachable — please try again"). Clear the
   timer in `finally`. This is the layer that stops the customer-facing stuck state.
   ```js
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 20000);
   try {
     const response = await fetch('/api/checkout/create-session', {
       method: 'POST', headers, body, signal: controller.signal,
     });
     ...
   } catch (err) {
     // re-enable + show retryable error
   } finally { clearTimeout(timeoutId); }
   ```
2. **CF Pages Function proxy** (`functions/api/checkout/create-session.js`): add a
   20s `AbortController` on the upstream `fetch`; on abort return a 504 JSON body
   instead of letting the request hang the client.
3. **Backend (FastAPI)**: the handler was `async def` but called
   `stripe.checkout.Session.create(...)` **synchronously** (blocking SDK). In a single
   uvicorn worker that blocks the ENTIRE event loop — any Stripe API stall freezes
   every concurrent request. Fix: make it `def` (FastAPI runs sync handlers in a
   threadpool) AND pass `timeout=20` to the Stripe call.
   ```python
   @router.post("/checkout/create-session")
   def create_stripe_session(body: CreateSessionRequest, ...) -> Dict[str, Any]:
       ...
       session = stripe.checkout.Session.create(timeout=20, **session_kwargs)
   ```

## Deploy + topology (where the time went)

- `humandesignengine.com` = CF Pages project **`hd-platform`** (custom domain,
  `production_branch: main`). NOT local nginx, NOT the `cloudflared-hde` tunnel —
  those are legacy. The live page is served from the Pages production deployment.
- **Deploy gotcha:** running `wrangler pages deploy dist --project-name=hd-platform`
  while in a git checkout on a non-`main` branch (e.g. `ned/...`) auto-deploys a
  **preview** (`<branch>.hd-platform.pages.dev`), NOT production. The live domain
  keeps serving the old production deployment. Fix: add `--branch=main`.
  Verify with the CF API:
  ```bash
  # token in terminal env; pass via python subprocess (inline $TOKEN gets scrubbed)
  python3 - <<'EOF'
  import os, urllib.request, json
  tok = os.environ['CLOUDFLARE_PAGES_API_TOKEN']; acct = os.environ['CLOUDFLARE_PAGES_ACCOUNT_ID']
  d = json.load(urllib.request.urlopen(urllib.request.Request(
      f"https://api.cloudflare.com/client/v4/accounts/{acct}/pages/projects/hd-platform/deployments?per_page=3",
      headers={'Authorization':'Bearer '+tok})))
  for dep in d['result']: print(dep['id'][:8], dep.get('environment'), dep['created_on'][:19])
  EOF
  ```
  Confirm the newest `production` env deployment is the one you just made.
- **Byte-compare to prove the live domain serves your build** (don't trust cache-bust
  params or "it should be live"):
  ```bash
  md5sum dist/deconditioning/index.html
  curl -sS https://humandesignengine.com/deconditioning/ | md5sum
  ```
  If they differ, the domain is still on the old deployment (preview vs production).
- End-to-end proof after deploy: a valid public `POST /api/checkout/create-session`
  returns 200 in <1s and a `cs_live_` id; the live HTML contains the new markers
  (`AbortController`, env-aware `checkout_source`).

## Pitfalls

- The credential scrubber mangles inline `$TOKEN` in terminal commands (arrives as
  literal `***` or with ellipsis). Pass tokens via a Python `subprocess` env dict,
  never on the command line.
- `async def` FastAPI handler + synchronous `stripe.*` SDK = event-loop freeze.
  This is the *root cause* of intermittent production hangs even when the API
  "works fine" on a quick local curl. Check `def` vs `async def` on any handler that
  makes blocking SDK/IO calls.
- A `404` from a test uvicorn instance can be a **port collision** (another service
  already on 8001/8002/8003), not your code. Check `ss -tlnp | grep :800x` before
  trusting a 404.
- Do NOT claim the fix is "live" until the byte-hash of the served page matches your
  built `dist`. Preview deployments do not update the production custom domain.
