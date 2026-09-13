# Cloudflare Access: Email-Based Access Policies (prismatic.growthwebdev.com)

Session 2026-08-28: added `Becca.gulden@gmail.com` to the prismatic workspace Access app.

## Where the Access app lives (gotcha #1 — account, not zone)

- The Access app is in the **growthweb / pages account**, not the AOT account.
  - Account id: `$CLOUDFLARE_PAGES_ACCOUNT_ID`
  - Auth: **legacy headers** `X-Auth-Email` + `X-Auth-Key` with the growthweb CF API key (a Bearer token without Zero Trust:Edit scope won't do).
- AOT-account credentials (`CLOUDFLARE_AOT_*`) return **zero** Access apps. "NO MATCH found among access apps" usually means *wrong account*, not "app doesn't exist". Before concluding an Access app is missing, enumerate every CF account credential pair in env and query each account's `/access/apps`.
- App: `Hermes Service (prismatic.growthwebdev.com)` (id starts `40972e2b`). Per-person pattern: `Allow mbgulden@gmail.com (PIN)` (email-only include), plus `Admin Only` and others (5 policies total as of 2026-08-28).

## Endpoints (all under `/client/v4`)

| Op | Call |
|---|---|
| List apps | `GET /accounts/{acct}/access/apps` |
| List policies | `GET /accounts/{acct}/access/apps/{app_id}/policies` |
| Create policy | `POST /accounts/{acct}/access/apps/{app_id}/policies` → 201 |
| Update policy | `PUT .../access/apps/{app_id}/policies/{policy_id}` |

## Policy JSON shape (email allow + OTP/PIN)

```json
{
  "name": "Allow Becca.gulden@gmail.com (PIN)",
  "precedence": 5,
  "decision": "allow",
  "include": [{"email": {"include": ["Becca.gulden@gmail.com", "becca.gulden@gmail.com"]}}],
  "bypass": false,
  "require": []
}
```

Precedence: lower = evaluated first. New *allow* policies go at `max(existing) + 1` so they don't preempt existing deny/admin rules (Becca's landed at 5).

## Email case-safety trick

Cloudflare does not document the email selector's case behavior. Include **both case forms** in the include list — same mailbox, OR semantics, zero security impact (as above).

## Verified pattern for adding a person

1. Write a **standalone probe script to `/tmp`** and run via `terminal` — CF credentials live in the terminal session env, not the `execute_code` sandbox (if env vars read empty in `execute_code`, that's why).
2. `GET` the policy list → confirm exact app id, existing policy names, max precedence.
3. `POST` a **dedicated per-person allow policy** (independently revocable — never append an email into a shared policy).
4. **Read back**: re-`GET` the policy list and diff the matchers verbatim. `201 success:true` alone is not proof.
5. Smoke test: `curl -s -o /dev/null -w '%{http_code}'` the protected domain — expect the Access flow to still respond.

## Result & contingency

Becca's policy live (201 + re-read verified), domain still 200. She gets the same email-OTP flow as Michael — no IP grant, no bypass. Untested contingency if she still 403s after the OTP: her mailbox may not be covered by the Zero Trust email-IdP config — in that case fold her into the `Admin Only` policy (diagnosis unverified, do not treat as confirmed fix).
