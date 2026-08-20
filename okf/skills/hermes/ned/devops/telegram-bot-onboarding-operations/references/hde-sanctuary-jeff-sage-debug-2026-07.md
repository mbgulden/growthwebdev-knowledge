# HDE Sanctuary Jeff/Sage Bot Debug — 2026-07

## Reusable lesson

When a user clicks a Telegram onboarding link and sees an application error after `/start`, separate **Telegram identity** from **application backend**.

In this session, the user clicked a link to:

- display name: `Jeff`
- username: `@TheNextNextStepBot`

The first message was:

```text
❌ Error: Database connection issue. Please try again.
```

That error was not caused by the user doing the wrong thing. It came from the Human Design Engine tenant router's `/start <token>` path while validating the invitation and associating the Telegram chat ID.

## Evidence pattern used

1. Checked session history and local files for bot names and service ownership.
2. Compared running processes/services:
   - `hde_router.service` was active and polling the `TheNextNextStepBot` token.
   - `next-step-bot.service` was inactive.
   - `jeff.service` was a Hermes gateway with separate platform state; active service alone was not proof of Telegram connectivity.
   - `becca-sage.service` existed and used a different Sage-like bot identity.
3. Used Telegram `getMe` against configured token sources, printing only safe fields:
   - HDE router token mapped to `@TheNextNextStepBot` / `Jeff`.
   - Becca Sage token mapped to a separate existing bot.
4. Grepped the exact user-facing error string and read surrounding code:
   - `Database connection issue` was sent in the router's DB transaction exception branch.
5. Smoke-tested backend dependencies with the router environment:
   - no explicit `DATABASE_URL` was set in the HDE staging env,
   - code fell back to default local Postgres,
   - Postgres was inactive / port `5432` not listening,
   - DB connection failed before invitation validation could complete.
6. Correct fix was not to stand up a new empty Postgres shadow DB. The staging API already used `sqlite+aiosqlite:////home/ubuntu/work/hd-platform-staging/staging_database.db`, with real users/invitations. Add that same `DATABASE_URL` to the router environment and restart `hde_router.service`, then verify invitation lookup against the shared staging DB.

## Human-facing conclusion shape

Use this concise framing:

> The link reached the bot currently wired to the HDE onboarding router. The failure is not you clicking the wrong thing. The router received `/start`, then failed while connecting to the database to validate/link the invitation. Creating a new BotFather bot would improve customer-facing identity, but it will not fix this database failure.

## BotFather guidance

For HDE Sanctuary, a dedicated bot is still the right product move, but after the backend is healthy:

1. Fix/verify DB connectivity and invitation lookup.
2. Create or select the customer-facing bot identity.
3. Wire `HDE_COACH_BOT_TOKEN` and `HDE_ONBOARDING_BOT_USERNAME` to that identity.
4. Restart the router.
5. Generate a fresh onboarding link and test `/start <token>` end-to-end.

Recommended naming pattern from the session:

- display name: `Sage Sanctuary`
- username: `@SageSanctuaryBot` if available
- fallback: `@HumanDesignSageBot`

Avoid reusing an existing personal/private Sage bot identity for a customer-facing product.

## Commands/patterns to reuse safely

Redact tokens in logs:

```bash
sed -E 's/[0-9]+:[A-Za-z0-9_-]+/[REDACTED_TOKEN]/g; s/(token|api[_-]?key|password|secret)[=: ]+[^ ]*/\1=[REDACTED]/Ig'
```

Token identity probe shape:

```python
# Load token from env file, call https://api.telegram.org/bot<TOKEN>/getMe,
# print only: source, ok, id, username, first_name.
# Never print token.
```

DB smoke-test rule:

- Use the same env and `PYTHONPATH` as the systemd unit.
- Report whether `DATABASE_URL` is explicit or defaulted.
- Report only URL scheme/host class, not credentials.

## Pitfall captured

`systemctl is-active <bot-service>` can be misleading. A service may be alive while Telegram platform state is retrying, token is invalid, or the app handler is crashing after receiving updates. Always tie identity + process + handler path + backend dependency together before recommending BotFather or token changes.
