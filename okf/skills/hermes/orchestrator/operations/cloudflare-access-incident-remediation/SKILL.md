---
name: cloudflare-access-incident-remediation
description: Triage and remediate Cloudflare Access bypass alerts for tunnel-backed internal apps without breaking webhook ingress.
---

# Cloudflare Access Incident Remediation

## When to Use

Use this skill when:
- A protected hostname/path returns origin `200`/`404` instead of Cloudflare Access `302`/challenge.
- A tunnel-backed internal dashboard appears publicly reachable.
- A quota/admin/API path is reachable through Cloudflare but should be Access-protected.
- You need to fix Access policy while avoiding collateral damage to public webhook endpoints.

## Core Workflow

1. **Verify live behavior first**
   - Use a no-redirect HTTP client.
   - Record status, `Location`, Cloudflare headers, and a short body prefix.
   - Classify:
     - `302` to `*.cloudflareaccess.com/cdn-cgi/access/login` = protected.
     - origin `200` or app `404` = Access is not intercepting.
     - app `404` is lower data-exposure risk, but still a bypass of the intended Access layer.

2. **Resolve the correct Cloudflare zone/account before mutating**
   - Do not trust env var names blindly; list zones and confirm the hostname’s zone.
   - For GrowthWeb-style setups, `CLOUDFLARE_*` env var names may not match the actual zone being modified.
   - Summarize IDs only; never print API keys/tokens.

3. **Read existing Access apps and policies**
   - Query Zero Trust Access apps for the affected hostnames and paths.
   - **Access apps are account-scoped, not zone-scoped.** The working read path is `GET /accounts/{account_id}/access/apps` (each app carries its `domain` and full `policies` array with `decision`, `include`, precedence, and timestamps). There is NO `/zones/{id}/access/apps` route. Enumerate the account id first via `GET /accounts`.
   - **WAF rulesets are zone-scoped.** The working read path is `GET /zones/{id}/rulesets` (custom `kind=zone` + managed `kind=managed`), then `GET /zones/{id}/rulesets/{ruleset_id}` for rule expressions. **Do NOT call `/zones/{id}/waf`, `/zones/{id}/httpsecurityanalysis`, or `/zones/{id}/firewall` — all three return `404 No route for that URI`** (the dashboard UI has those tabs; the API does not).
   - For each Access app, inspect policies for:
     - `decision: bypass` + `include: everyone`.
     - broad IP bypasses.
     - path-specific vs hostname-wide matching.
     - webhook-specific bypasses that may be required.
   - Classify before mutating:
     - Hostname-wide internal apps should still challenge/redirect.
     - Explicit public checkout/report/webhook apps may intentionally use `Bypass Everyone`; do not lock those by reflex.
     - Narrow `/32` verifier-IP bypass policies can make a protected app return origin content from your client only; verify the policy scope before calling it public.
   - If the monitor is wrong, patch the watchdog classification contract and prove `unexpected_unlocked_count=0` rather than changing Cloudflare policies unnecessarily. See `references/access-watchdog-public-bypass-classification.md`.

4. **Apply the least-destructive fix**

     - Narrow verifier/home-IP bypasses can make an app return origin `200` from Fred's machine while still locked for the world. Record the verifier IP and classify it separately from public exposure.

4. **Apply the least-destructive fix**
   - For quota/admin paths that must be reachable by a specific human AND by an agent's server, replace `Allow Everyone`/`Bypass Everyone` with a small precedence-ordered policy set: (1) `decision: bypass` + `include: {ip: {ip: "<server>/32"}}` for the verifier/agent server, (2) `decision: allow` + `include: {email: {email: "<user>"}}` (PIN) for the human. PUT the whole app with `PUT /accounts/{account_id}/access/apps/{app_id}` sending the full app object with the new `policies` array — strip server-managed fields (`app_launcher`, `public_key_certificate`, `service_token_key_id`) or the PUT 400s. Record the server's egress IP first (`curl https://api.ipify.org`) and note that it's a snapshot — if the host's public IP changes, the bypass policy must be re-issued.
   - For internal dashboards, remove broad public/home-IP bypasses unless explicitly required.
   - For webhook hostnames, avoid protecting the whole hostname unless webhook providers can pass Access. Prefer path-specific protection/deny for sensitive paths while preserving actual webhook routes.

5. **Verify after change (all three, or the lock-down is not proven)**
   - Re-run no-redirect checks against every alerted URL.
   - Expected: `302` and `Location` host is the Cloudflare Access domain.
   - Confirm body is not origin content (`{"detail":"Not Found"}`, dashboard HTML, JSON data, etc.).
   - **Dual-identity proof for a locked-down app:** (a) an anonymous request from a non-listed IP must now get the Access `302`/login wall (not the origin 200 it got before); (b) a request from the verifier/agent server IP still gets the origin `200` via the IP bypass; (c) `GET /.well-known/cloudflare-access-protected-resource/` on the hostname returns `"protected": true`. You cannot easily spoof a foreign source IP, so for (a) confirm via the account-level re-read that no `include: {everyone}` policy remains in the app — that's the authoritative "anonymous is locked" check.
   - Re-read the app at `GET /accounts/{account_id}/access/apps/{app_id}` and confirm the `policies` array exactly matches what you intended (decisions, includes, precedence) — the API is the source of truth, not your PUT payload.
   - Run a targeted safety check for legitimate webhook paths to ensure they were not accidentally put behind Access.

6. **When Michael asks you to verify the protected public URL, solve access instead of hand-waving**
   - First record your verifier egress IP (`curl -sS https://ifconfig.me`) and the current no-redirect public behavior.
   - If Access blocks your browser/session and Michael explicitly wants you to verify the public route, use Cloudflare API credentials to add a narrow Access policy for your verifier IP on the specific app/hostname/path.
   - Keep the bypass scoped to a single `/32`, name it clearly (for example `Bypass Fred Hermes verifier IP`), and verify both headers and rendered body from the public URL.
   - Do not broaden to `everyone`, whole accounts, or webhook hostnames. Do not expose Cloudflare tokens/API keys.
   - After adding access, use the browser against the public HTTPS URL, not just `localhost`, and capture live UI proof (`HEALTHY`, expected title/body, no origin `404`).

6. **Separate adjacent auth findings**
   - If webhook endpoints accept unsigned requests, capture it as a separate app-auth hardening issue.
   - Do not combine Cloudflare Access routing fixes with webhook signature enforcement unless asked; changing both at once can break production ingress and obscure rollback.

7. **Promote incident evidence into OKF**
   - Hermes profile `output/` files are temporary delivery/session artifacts, not canonical evidence.
   - Durable Cloudflare Access incident/remediation records should live in the OKF under `okf/audits/incidents/YYYY-MM-DD-slug.md`.
   - The OKF record should include: trigger, verified root cause, changes applied, verification scope, live no-redirect results, webhook safety check, adjacent follow-ups, and retention rule.
   - After writing or updating the OKF artifact, run a focused `/tmp/hermes-verify-*.py` artifact verifier and label it as ad hoc targeted verification, not suite-green.
   - If the OKF repo already has unrelated dirty changes, do not commit them opportunistically; report the exact new OKF path and git state instead.

## Public route proof through Access

When a production/public route is healthy locally but public proof is blocked by Cloudflare Access, do not stop at “Access blocked me” if a narrow verifier-IP bypass is safe and available. Add a temporary `/32` verifier bypass for the exact Access app, prove the public hostname route/API/assets/path-safety/browser console, fix any nginx asset proxy or stale Cloudflare cached 404s, and clearly separate localhost proof from public proof. See `references/public-route-proof-verifier-ip-bypass.md`.

## Pitfalls

- **Do not call origin `404` safe just because no data leaked.** If Access was expected, origin `404` means the request bypassed the Access layer.
- **Do not put an entire webhook hostname behind Access by reflex.** Linear/GitHub/Stripe-style webhooks usually cannot complete Access login; protect only sensitive paths unless a service-token design exists.
- **Do not trust current-client results without checking source IP.** A home/static IP bypass can make protected apps look public from your machine while still protected elsewhere — or can be broader than intended.
- **Do not print Cloudflare secrets.** Show env var presence, zone/account IDs, app/policy IDs, decisions, and redacted redirect hosts only.
- **Do not assume one credential set sees every zone.** Env often carries multiple `CLOUDFLARE_*` API-key pairs plus a bearer `CLOUDFLARE_*_API_TOKEN`, each bound to a different account. A zone (and its rulesets/Access apps) is only visible under its owning account's credential. To enumerate everything, list zones under every credential set, then read `access/apps` at the account level for each. The same account id can be reachable via both an API key and a bearer token — that is normal, not a conflict.
- **To measure what a public Access policy actually exposes, probe the tunnel origin directly.** `curl 127.0.0.1:<tunnel_port>` (or the origin backend) bypasses Access entirely and shows the raw surface an unauthenticated visitor would reach through an `Allow Everyone`/`Bypass Everyone` app. Compare that against the intended exposure before deciding lock-down vs. public.
- **Do not leave the incident at “policy updated.”** Final Done requires live verification of the exact public URL/path.
- **Do not say you cannot verify public behavior just because Access redirects.** If Michael asks you to verify the protected public app, add or reuse a narrow verifier-IP Access policy, then test the public HTTPS URL through Cloudflare.
- **Do not treat Hermes delivery artifacts as the long-term record.** If the user asks “where does this live?” or the work is incident/audit evidence, promote the durable copy into OKF and verify the written artifact.
- **Do not let verifier brittleness trigger unnecessary doc edits.** If an artifact verifier fails only because it ignored Markdown formatting, fix the verifier and rerun; do not churn the evidence file just to satisfy a brittle check.

## Support Files

- `references/cf-api-enumeration-working-routes.md` — which Cloudflare API routes actually work (account-level `access/apps`, zone-level `rulesets`) vs. the ones that 404 (`/waf`, `/httpsecurityanalysis`, `/firewall`), the multi-credential account topology, and the origin-probe pattern for sizing a public Access policy's real exposure. Load this before any cross-zone Access/WAF audit.
- `references/growthwebdev-access-bypass-2026-07-08.md` — worked example: quota-path `Bypass Everyone` policies, home-IP bypass on Prismatic dashboard, post-fix 302 verification, and webhook safety check.
- `references/prismatic-verifier-ip-bypass-2026-07-09.md` — worked example: adding a narrow Fred verifier-IP bypass so public Cloudflare-protected dashboard routes can be verified end-to-end instead of stopping at Access redirect.
- `references/prismatic-workspace-tree-access-proof-2026-07-16.md` — worked example: use a narrow verifier-IP Access bypass, then repair nginx/Cloudflare cached asset misses and prove `/workspace-tree` via public browser, API, JS, traversal, and screenshot checks.
- `references/cf-access-expected-public-bypass-classification.md` — pattern for classifying intentional public checkout/report/webhook Access bypass apps, narrow verifier-IP bypasses, and true unexpected unlocks while keeping all-clear cron stdout silent.
- `references/okf-incident-evidence-placement.md` — where durable incident evidence belongs in OKF, required sections, and the artifact-verification pattern after promotion from Hermes output.
