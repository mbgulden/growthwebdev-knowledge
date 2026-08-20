# Worked example — sentinelitad.com email enablement

**Date:** 2026-07-27
**Trigger:** Michael said "I need to have my website actually be legit so I can share it with some IT professionals that do IT installs" while visiting family in CA. Audit had discovered that `sentinelitad.com` had **no MX records** and `team@sentinelitad.com` (the contact email on the site) could not receive mail, even though the FormSubmit contact form routed there.
**Grant:** Michael explicitly said "Fix the dns level stuff, you have Cloudflare access and my permission to setup email forwarding to michael@growthwebdev.com."
**Authoritative source document:** the `prismatic-engine-fred-governance` audit at `/home/ubuntu/work/sentinelitad.com/audit-2026-07-27/README.md`.

## Context

`/home/ubuntu/work/sentinelitad.com` is a static Astro site deployed to Cloudflare Pages at `sentinelitad.com`. Built and served as of 2026-07; visual + structural review confirmed six pages, structured data, sitemap, and clean design. The site is not the problem — the **delivery chain for the contact email** was broken at the DNS layer.

The FormSubmit.co form action (`https://formsubmit.co/team@sentinelitad.com`) was found unactivated by audit probe — both POSTs returned the FormSubmit marketing homepage instead of an activation/thank-you response. Even after activation, the destination mailbox would have bounced because the domain had no MX records.

## What was done (and what was blocked)

### 1. Resolved zone via API list, not env vars

Env `CLOUDFLARE_GROWTHWEB_ZONE_PRISMATICENGINE` is for prismaticengine.com. Listing zones via the Global API key (`X-Auth-Email` + `X-Auth-Key` headers, account `196c1798da487413b0281ccc570f05a1`) returned 11 zones. `sentinelitad.com` zone ID: `6bcb245621b2a0090c65cd71f7fd2eab`.

### 2. Confirmed destination address was already verified

`GET /accounts/{id}/email/routing/addresses` returned `michael@growthwebdev.com` (id `c9a207edfd8345d88de7e76cdd9be98a`), verified 2026-06-06. No re-verification needed.

### 3. Initial attempt: PATCH `/zones/:id/email/routing` to enable Email Routing

```bash
curl -X PATCH .../zones/$ZONE/email/routing --data '{"enabled": true}'
```

Returned `success: true` but `enabled` stayed `false` after re-fetch. **The zone-level Email Routing PATCH endpoint is unreliable for this use case.** This is the critical pitfall — do not waste time retrying PATCH.

### 4. Correct path: create MX + SPF manually via DNS records endpoint + create rule

```bash
# MX records (priorities 10/20/30)
POST /zones/$ZONE/dns_records type=MX content=route{1,2,3}.mx.cloudflare.net priority={10,20,30}

# SPF TXT
POST /zones/$ZONE/dns_records type=TXT content="v=spf1 include:_spf.mx.cloudflare.net ~all"

# Routing rule
POST /zones/$ZONE/email/routing/rules \
  matchers=[{to: team@sentinelitad.com}] \
  actions=[{forward: michael@growthwebdev.com}]
```

All three succeeded. Rule enabled immediately.

### 5. External verification

```text
$ dig @1.1.1.1 sentinelitad.com MX +short
10 route1.mx.cloudflare.net.
20 route2.mx.cloudflare.net.
30 route3.mx.cloudflare.net.

$ dig @1.1.1.1 sentinelitad.com TXT +short
"v=spf1 include:_spf.mx.cloudflare.net ~all"
```

Re-listing routing rules confirmed:
```json
{
  "id": "0268ed9ff260432f8f89bfe36746a814",
  "enabled": true,
  "name": "Forward team@ to Michael@growthwebdev.com",
  "matchers": [{"type":"literal","field":"to","value":"team@sentinelitad.com"}],
  "actions": [{"type":"forward","value":["michael@growthwebdev.com"]}]
}
```

### 6. Build check (no live-site breakage)

```text
$ npm run build
[build] 3 page(s) built in 1.55s
$ python3 scripts/verify-theme.py
PASS: Sentinel theme/Astro/EmDash scaffolding invariants hold
$ git status --porcelain
?? audit-2026-07-27/
```

No DNS mutation, no repo mutation, no Cloudflare Pages redeploy.

### 7. End-to-end SMTP smoke — BLOCKED

Tried `python3 smtplib.SMTP('route1.mx.cloudflare.net', 25)` from this VM:
```text
OSError: [Errno 101] Network is unreachable
```

Outbound port 25 is blocked by VM network policy. **This is normal and expected** — the only end-to-end proof is Michael sending an email from another account to `team@sentinelitad.com` and checking `michael@growthwebdev.com`.

## What was *not* done (deferred by Michael's intent)

- **FormSubmit activation** was not done — the activation link (if any) is in `team@sentinelitad.com`'s inbound history and not accessible from this VM. Until activation, the contact form remains broken at layer 1 even though DNS layer 2 is now fixed.
- **No site files modified** — the FormSubmit action in `public/index.html` still points to `https://formsubmit.co/team@sentinelitad.com`. When Michael wants to swap it out, the durable replacement (`audit-2026-07-27/cloudflare-worker-form.js`) is staged locally.
- **No Pages redeploy** — the only build artifacts that changed would be the homepage form action and the new Founder Note (both deferred). Neither was committed.

## Reusable patterns from this session

1. **Always resolve zone by listing**, never by env-var name. Mismatched zone IDs are a silent failure mode.
2. **Always verify DNS externally** with `dig @1.1.1.1`. API readback can race propagation; resolver readback is canonical.
3. **Email Routing has two halves**: MX records AND routing rules. Either alone doesn't deliver mail. PATCH on `/zones/:id/email/routing` is unreliable — use `/zones/:id/dns_records` for MX/SPF and `/zones/:id/email/routing/rules` for routing.
4. **Destination addresses must already be verified** before creating rules — Cloudflare sends a confirmation email, and the rule creation silently fails otherwise.
5. **End-to-end SMTP smoke from this VM is blocked by network policy** — accept that and hand off the final "did the email land" check to the operator.
6. **Always re-run `npm run build` + the repo's canonical verifier** after any non-CF mutation. For CF-only mutations, `npm run build` is still cheap insurance and catches accidental file changes.
7. **Document before deeming done** — keep the audit doc updated so the next session sees the new state, not the broken state.
