# Access watchdog public-bypass classification

Use when a Cloudflare Access health check reports public/unlocked paths but live policy inspection shows the routes may be intentional public exceptions or narrow verifier bypasses.

## Pattern

1. **No-redirect live probe first.**
   - Probe the exact app domain/path without following redirects.
   - Record status and whether the redirect target contains `cloudflareaccess`.
   - App-origin `200`/`400`/`404` means Access did not challenge, but this may still be expected for public ingress routes.

2. **Inspect Access app names and policies before mutating.**
   - Query Access apps and per-app policies.
   - Separate:
     - hostname-wide protected apps, expected to challenge;
     - explicit public apps such as checkout/report/webhook routes, often named with a public prefix and `Bypass Everyone`;
     - narrow verifier/client IP bypass policies, usually `/32`, that only affect your egress IP;
     - true unexpected public exposure.

3. **Patch the monitor contract when classification is the bug.**
   - Maintain an allowlist for expected public app domains/prefixes.
   - Treat `Bypass Everyone` as acceptable only when both the domain/path and app name match the public contract.
   - Treat narrow IP-only bypass as protected-from-general-public, but label it explicitly in verbose output.
   - Keep true unexpected unlocked apps as alerts.

4. **Keep all-clear quiet for no-agent cron.**
   - Verbose/manual mode may print full classifications.
   - Normal scheduled all-clear should produce empty stdout so Hermes does not deliver routine health dumps.
   - Alert mode should still print and/or Telegram exactly once with the unexpected paths.

5. **Verification shape.**
   - Use `/tmp/hermes-verify-*.py` via `tempfile.mkstemp`, then delete it.
   - Assert `py_compile` passes, verbose mode has `unexpected_unlocked_count=0`, expected public count matches the current explicit public apps, hostname-wide sensitive apps are locked, narrow verifier-IP bypass is classified, and quiet all-clear stdout is empty.
   - Run the cron through the scheduler and inspect latest output for `Status: silent (empty output)`.

## Pitfall

Do not "fix" this class by locking webhook/checkout paths blindly. Webhook providers and checkout flows often cannot pass an Access login; protect them with path-specific design and app-level signature/parameter validation instead.
