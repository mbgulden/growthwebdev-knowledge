# Prismatic public dashboard verifier-IP bypass — 2026-07-09

## Trigger

Michael asked Fred to stop treating Cloudflare Access as a blocker and verify `https://prismatic.growthwebdev.com/dashboard` publicly after the local gateway was fixed.

## Pattern

1. Capture verifier egress IP:

```bash
curl -sS --max-time 10 https://ifconfig.me
```

In this session the verifier IP was `65.129.148.239`.

2. Confirm public behavior without following redirects and without trusting localhost:

```bash
curl -sS -I --max-time 15 https://prismatic.growthwebdev.com/dashboard
```

3. Resolve the Cloudflare zone/account from the actual hostname (`growthwebdev.com`) using the GrowthWeb Cloudflare credentials. Do not print tokens or API keys.

4. Locate the Access app for `prismatic.growthwebdev.com` and add a narrow bypass policy:

```text
name: Bypass Fred Hermes verifier IP
decision: bypass
include: ip 65.129.148.239/32
precedence: 1
```

5. Verify the public URLs through Cloudflare, not just origin:

```bash
curl -sS -D headers -o body https://prismatic.growthwebdev.com/
curl -sS -D headers -o body https://prismatic.growthwebdev.com/dashboard
```

Expected for the verifier IP:

```text
HTTP 200
content-type: text/html
body contains: Prismatic Engine Status
body contains: HEALTHY
body contains: First-failing layer: none
body does not contain: {"detail":"Not Found"}
```

6. Use the browser on the public HTTPS URL for live UI proof when the user complained about browser-visible behavior.

## Pitfall captured

Do not stop at “Cloudflare Access redirects me.” If Michael asks for verification from Fred's side, solve the access path with a scoped verifier-IP bypass and then verify the exact public route.
