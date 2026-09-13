# 2026-09-03 — Coach-portal "premium client" promotion + stripe 15.x timeout fix

Session: Michael asked to promote his + Alicia's accounts to "premium clients" on the
promoted coach portal, after the demo/checkout work.

## "Premium client" = 5-condition dashboard predicate (not just a flag)

`GET /api/coach/clients` (staging orchestrator `:8011`, behind the promoted
`api.humandesignengine.com/coach/*` portal) lists a user only if ALL hold:

```
is_premium=True
AND subscription_status='active'
AND coach_review_consent=True
AND coach_review_consent_revoked_at IS NULL
AND (coaching_container_end IS NULL OR coaching_container_end >= now())
```

Michael (user id 2, mbgulden@gmail.com) was already `is_premium=True` + `active` +
bot `active`, but invisible because `coach_review_consent=False` AND
`coaching_container_end` had expired 2026-08-22. Lesson: a user can be "premium"
yet off the dashboard — all five conditions matter.

## Promotion (direct Postgres, prod `127.0.0.1:5432/hde`, role `hde_app`, asyncpg)

```sql
UPDATE users SET
  is_premium = True,
  coach_review_consent = True,
  coach_review_consent_at = <now>,
  coach_review_consent_source = 'admin_promotion',
  coach_review_consent_revoked_at = NULL,
  coaching_container_end = <now + 6 weeks>   -- matches checkout is_premium_tier window
WHERE id = <uid>;
```

The 6-week window mirrors `api/routes/stripe_webhook.py`:
`coaching_container_end = now + timedelta(weeks=6) if is_premium_tier else None`,
where `is_premium_tier = (tier in {premium, sovereign}) or product=='sovereign'`.

**Verify through the endpoint, not the DB row:**
`GET :8011/api/coach/clients` (with the coach's CF-Access email header or token) →
the user appears with `container_status` + a future `coaching_container_end`.

## "Alicia" was not in the system — sweep ALL tables before asking

Michael named a client "Alicia" who did not exist. Before creating/assuming a row:
- Query `information_schema.columns` (all tables, all columns) and test
  `LOWER(CAST(col AS TEXT)) LIKE '%alicia%'` across every column of every table.
- Zero hits across all 11 tables (and no alicia in `guide_name`, which only had
  Ed/George/Charlie/Ember) → the account genuinely doesn't exist here.
- **Ask for the account's email** (or where her bot/container lives) instead of
  guessing. Never fabricate a row for a name you can't resolve.

## Same-session continuation: never-expire + deactivating synthetic test accounts

Michael then asked to make the 5 real clients **never expire** and to "activate the other accounts too."

- **Never-expire = `coaching_container_end = NULL`.** The dashboard predicate treats
  NULL as unexpired (`IS NULL OR end >= now()`), so NULL is the permanent form of the
  same field — no new column/flag needed. Verify live: `/api/coach/clients` shows
  `coaching_container_end: null` for the user.
- **The `users` table mixes real clients with ~37 synthetic test rows**
  (`example.com`/`.invalid`/`.test`, `fred+*`, `guest+*`, `deleted+demo+*`,
  `michael+staging-*`, `ned-*`). "All the other accounts" does NOT mean all 42 —
  list the table first, classify real vs synthetic, and confirm scope before a bulk
  UPDATE (Michael chose **deactivate** the 37, not activate).
- **Deactivate (dormant, not deleted):** `subscription_status='inactive'`,
  `is_premium=FALSE`, clear `trial_expires_at` + `deletion_scheduled_at`, set
  `deactivated_at=COALESCE(deactivated_at, now())`. This stops every lifecycle cron
  from resurrecting them into the client list. Leave `bot_instances` alone
  (separate table; its statuses are independent).
- **Trial-lifecycle trap:** demo users can be auto-suspended with a pending
  `deletion_scheduled_at` (Jenni's was ~4h out). Any promotion must clear
  `deletion_scheduled_at`/`deactivated_at`/`trial_expires_at`, or the purge cron
  deletes the account you just activated. A `suspended` bot container **auto-wakes on
  the next Telegram message** (tenant router handles it) — do not force-flip
  `bot_instances.status`.

## Direct Postgres via asyncpg (operational gotchas, hit this session)

- **Read the DSN from `hd-platform-staging/.env`** (`DATABASE_URL`), don't transcribe
  the password by hand (a mis-typed secret → `InvalidPasswordError`). Strip the
  `postgresql+asyncpg://` prefix before `asyncpg.connect()` (raw asyncpg wants
  `postgresql://`).
- **No `con.commit()`** — asyncpg auto-commits each statement. A script that
  "crashed" on `commit()` had already applied the UPDATE; re-run would double-apply.
- **Placeholders are `$1,$2,…`**, not `%s` (`%s` → PostgresSyntaxError at prepare).
- **asyncpg validates params at PREPARE time** (before execution) — an UPDATE that
  binds unused params fails cleanly with no partial write. That's why the crash-on-first
  attempt left no half-applied state.
- `bot_instances` has **no email column** — join via `user_id` to `users.id`.

## Related fix found this session: stripe-python 15.x `timeout=` kwarg

While re-verifying the paid checkout, the prod checkout route 502'd. Root cause:
`stripe.checkout.Session.create(..., timeout=20)` — stripe-python **15.3.1 rejects a
top-level `timeout=` kwarg** (unknown API parameter → 400 → 502). Fix: drop the kwarg
(enforce the wait at the CF-proxy / frontend layer). The older "add `timeout=20`"
3-layer fix (see `stripe-payment-live-operations/references/2026-08-hde-stuck-redirecting-checkout.md`)
is not safe on 15.x. Recorded in `stripe-payment-live-operations` SKILL.md.

## Deploy/lane context (this session)

- Wrangler 6111 still blocks the CLI (see `cloudflare-pages-workers-build-checks`
  2026-09 correction) — prod ships via the `main` git build pipeline (merge a `ned/`
  branch + PR), not ad-hoc `wrangler pages deploy`.
- `functions/` and `landing/` are NOT in ned's lanes in hd-platform — pushes that
  carry them use the documented `--no-verify` bypass (flagged to Michael; a
  one-line `PRISMATIC_ENGINE.yaml` lane add is the clean follow-up).
- OKF hub repo (`growthwebdev-knowledge`) rejects direct-to-main pushes
  ("manual deployments only") — record doc updates via a `ned/...` branch + `gh pr create`.
