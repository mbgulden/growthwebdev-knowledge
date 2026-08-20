# GrowthWebDev Cloudflare Access bypass — 2026-07-08

## Incident shape

Alerted host/path checks returned origin responses instead of Cloudflare Access challenges:

- `webhooks.growthwebdev.com/api/quota` → origin `404 {"detail":"Not Found"}`
- `webhooks.growthwebdev.com/quota` → origin `404`
- `quota.growthwebdev.com/api/quota` → origin `404`
- `quota.growthwebdev.com/quota` → origin `404`
- `prismatic.growthwebdev.com/api/quota` → origin `404`
- `prismatic.growthwebdev.com/quota` → origin `404`
- `prismatic.growthwebdev.com` → origin `200` dashboard HTML

Expected protected behavior was unauthenticated `302` to:

```text
growthwebdev.cloudflareaccess.com/cdn-cgi/access/login
```

## Diagnosis pattern that worked

1. Used no-redirect HTTP checks so `302` challenges were visible.
2. Confirmed the origin behind `prismatic.growthwebdev.com` matched local Prismatic gateway behavior on `127.0.0.1:9000`.
3. Listed Cloudflare zones; the relevant zone was `growthwebdev.com`, not the misleading env var name pointing at `prismaticengine.com`.
4. Listed Zero Trust Access apps for GrowthWeb hostnames.
5. Read each app’s policies.

## Root cause

Six quota-path Access apps existed, but each had a policy equivalent to:

```json
{
  "name": "Bypass Everyone",
  "decision": "bypass",
  "include": [{"everyone": {}}],
  "precedence": 1
}
```

`prismatic.growthwebdev.com` also had a broad home-IP bypass:

```text
65.129.148.239/32
```

The verifier machine’s public IP was exactly `65.129.148.239`, so the dashboard returned `200` from that origin.

## Remediation applied

- Converted the six quota-path policies from `bypass everyone` to authenticated `allow` for `mbgulden@gmail.com`:
  - `webhooks.growthwebdev.com/api/quota`
  - `webhooks.growthwebdev.com/quota`
  - `quota.growthwebdev.com/api/quota`
  - `quota.growthwebdev.com/quota`
  - `prismatic.growthwebdev.com/api/quota`
  - `prismatic.growthwebdev.com/quota`
- Deleted the broad home-IP bypass for `prismatic.growthwebdev.com`.
- Did **not** protect all of `webhooks.growthwebdev.com`; legitimate webhook ingress needed to stay reachable.

## Final verification shape

No-redirect unauthenticated verifier should produce:

```json
{
  "verdict": "PASS",
  "rows": [
    {"url": "https://webhooks.growthwebdev.com/api/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://webhooks.growthwebdev.com/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://quota.growthwebdev.com/api/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://quota.growthwebdev.com/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://prismatic.growthwebdev.com/api/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://prismatic.growthwebdev.com/quota", "status": 302, "access_redirect": true, "origin_leak": false},
    {"url": "https://prismatic.growthwebdev.com", "status": 302, "access_redirect": true, "origin_leak": false}
  ]
}
```

## Safety check

After policy changes, verify real webhook paths were not accidentally Access-protected. In this session:

```json
[
  {"url": "https://webhooks.growthwebdev.com/webhooks/linear", "status": 200, "access_redirect": false},
  {"url": "https://webhooks.growthwebdev.com/webhooks/github", "status": 404, "access_redirect": false}
]
```

## Adjacent issue discovered

`POST /webhooks/linear` accepted an unsigned `{}` with `200`. Source search suggested Linear HMAC verification only ran if the signature header was present. Treat this as a separate app-auth hardening task; do not silently combine it with Access policy remediation.
