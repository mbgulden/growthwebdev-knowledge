# HDE coach portal Cloudflare Access exposure — 2026-07-16

## When this matters

Use this when Michael wants the Human Design Engine coaching customer portal exposed publicly but protected by the existing Cloudflare Access policy.

## Pattern

1. Keep the coach dashboard/API on the staging orchestrator (`hde_orchestrator_staging.service`, usually `127.0.0.1:8011`).
2. Add public staging Nginx routes only for:
   - `/coach/dashboard`
   - `/api/coach/`
3. Gate those origin routes on Cloudflare Access headers before proxying:
   - require `Cf-Access-Jwt-Assertion` / `$http_cf_access_jwt_assertion`
   - forward `Cf-Access-Authenticated-User-Email`
   - return `403` at origin when the Access header is missing
4. In the orchestrator, allow either:
   - legacy `COACH_ACCESS_TOKEN` for local/internal work, or
   - Cloudflare Access email auth when `cf-access-jwt-assertion` is present and `cf-access-authenticated-user-email` is in the allowed email list.
5. Default allowed HDE coach emails used in this session:
   - `mbgulden@gmail.com`
   - `becca.gulden@gmail.com`
6. Add `/api/coach/session` so the dashboard can detect Cloudflare Access auth and skip the legacy token prompt.
7. Update the dashboard JavaScript to call `/api/coach/session` on load; if authenticated, call coach APIs without a token. Keep the token prompt as local fallback.
8. Preserve all existing client consent checks before reading or writing customer workspace files. Access email/token auth is only portal auth; it is not customer data consent.

## Nginx shape

```nginx
location = /coach/dashboard {
    if ($http_cf_access_jwt_assertion = "") { return 403; }
    proxy_pass http://127.0.0.1:8011/coach/dashboard;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cf-Access-Jwt-Assertion $http_cf_access_jwt_assertion;
    proxy_set_header Cf-Access-Authenticated-User-Email $http_cf_access_authenticated_user_email;
}

location /api/coach/ {
    if ($http_cf_access_jwt_assertion = "") { return 403; }
    proxy_pass http://127.0.0.1:8011/api/coach/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cf-Access-Jwt-Assertion $http_cf_access_jwt_assertion;
    proxy_set_header Cf-Access-Authenticated-User-Email $http_cf_access_authenticated_user_email;
}
```

## Focused verification recipe

Use a fresh `/tmp/hermes-verify-*.py` verifier or equivalent commands that prove:

- `python3 -m py_compile scripts/vm_orchestrator.py` passes.
- `nginx -t` passes.
- Origin without CF header returns `403`:
  - `curl -H 'Host: staging.humandesignengine.com' http://127.0.0.1/coach/dashboard`
- Simulated allowed CF headers return dashboard HTML `200`:
  - include `Cf-Access-Jwt-Assertion: verify-jwt`
  - include `Cf-Access-Authenticated-User-Email: mbgulden@gmail.com`
- `/api/coach/session` with `Becca.gulden@gmail.com` returns JSON with `method=cloudflare_access` and normalized lower-case email.
- `/api/coach/session` with a stranger email returns `401`.
- `/api/coach/clients` with allowed CF headers returns a JSON list.
- Public unauthenticated route is not raw portal HTML (`403`, `401`, or a Cloudflare Access redirect are acceptable depending on Cloudflare policy state).
- Scan changed artifacts for token-shaped strings; allow env var names, reject actual values.

## Pitfalls

- Do not paste `COACH_ACCESS_TOKEN` into chat or docs. Report only that it is configured.
- Do not rely only on Cloudflare-side policy. Add an origin-side Access-header gate so a tunnel/policy mismatch cannot expose the raw portal.
- Do not treat portal auth as client consent. The coach APIs must still require active premium status, coach review consent, no revoked consent, and a non-expired coaching window before reading or mutating workspaces.
- If the public URL returns plain `403`, the origin is protected but the Cloudflare Access app/policy probably does not match the path. Add/verify Access rules for `staging.humandesignengine.com/coach/*` and `staging.humandesignengine.com/api/coach/*`.
- Keep the dashboard's legacy token prompt as fallback for local/internal troubleshooting; Cloudflare Access should be the first path for browser use.
