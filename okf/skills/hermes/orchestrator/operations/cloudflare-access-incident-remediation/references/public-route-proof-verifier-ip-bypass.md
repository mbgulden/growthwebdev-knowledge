# Cloudflare Access public-route proof with narrow verifier bypass

Use this when a Prismatic public route must be proven through the real public hostname but Cloudflare Access blocks unauthenticated browser/curl proof.

## Safe proof path

1. First prove the local production service route directly (`127.0.0.1:<port>`) so Access is not masking an app regression.
2. Discover the current verifier egress IP with a neutral IP echo endpoint.
3. Locate the exact Cloudflare Access application for the public hostname.
4. Add a narrow Access bypass policy for the verifier IP as `/32`; do not add broad everyone/public bypasses.
5. Re-test the public HTTPS route, API route, asset route, and traversal/path-safety route.
6. If the HTML route is `200` but a JS/CSS asset is `404`, inspect nginx/site config for exact-location proxy gaps before blaming the app.
7. If curl sees fixed asset `200` but browser still sees `404`, check Cloudflare cache headers. Purge the single stale asset URL, then consider cache-busting the script URL in the app page.
8. Capture browser DOM/console proof from the public hostname, not only localhost.
9. Remove or document the temporary bypass according to the incident/proof policy if it is not meant to persist.

## Evidence packet

Include:

```text
verifier_ip=<ip>/32
access_policy=<policy name/id, no secrets>
public_route=<url> status=200
public_asset=<url> status=200
safe_preview=<url> status=200
traversal=<url> status=403
browser_title=<title>
console_errors=0
NOT_CLAIMING=public proof until public hostname and browser proof pass
```

## Pitfalls

- Do not stop at “Cloudflare Access blocked me” if a narrow verifier-IP bypass is available and safe.
- Do not claim public route success from localhost proof.
- Cloudflare can cache a prior asset 404 after nginx/app config is fixed; purge only the affected URL before broad cache operations.
- Browser proof may require a cache-busted page or asset URL after a stale 404.
