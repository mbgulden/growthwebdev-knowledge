# HDE Phase 3/4 paid onboarding proof pattern — 2026-07-15

Use this reference when proving Human Design Engine's paid web checkout → Telegram onboarding path and post-payment bot quality.

## Core lesson

Do not mark Phase 3/4 green from server-side checks alone. The paid checkout can create a user and invitation, and the bot runtime can pass canaries, but the final Telegram handoff requires a real human tester to tap the deep link and send `/start`. Bots cannot initiate that user-side `/start` through the Bot API.

## Phase 3 proof shape

1. Use Stripe **test mode** unless Michael explicitly approves live mode.
2. Complete checkout through the staging website flow, rooted at:
   `https://staging.humandesignengine.com/deconditioning/`
3. Confirm Stripe session status safely:
   - `status=complete`
   - `payment_status=paid`
   - customer/subscription present
   - redact session/customer IDs in user-facing output.
4. Verify webhook handling:
   - inspect redacted `hde_api_staging.service` logs for `checkout.session.completed`, user registration, durable invitation/onboarding messages;
   - if a webhook failed due to code/schema mismatch, fix the actual mismatch and use a signed replay against local staging API to re-exercise the exact handler path.
5. Verify DB state without dumping private fields:
   - user exists;
   - `subscription_status=active`;
   - Stripe customer ID is present;
   - invitation exists with token present;
   - invitation is unused before Telegram `/start`;
   - coach consent remains false unless explicitly granted.
6. Verify success/session resolution returns exactly one clear Telegram deep link and redact `?start=` tokens:
   `https://t.me/<bot_username>?start=[REDACTED]`
7. Run router metrics after the flow and require pending queues to stay zero.
8. Write a report. Status should be:
   - GREEN only after real human Telegram `/start` proof;
   - YELLOW if checkout/webhook/invitation/session link work but human Telegram handoff is pending;
   - RED if checkout completion or webhook/user/invitation creation fails.

## Phase 4 proof shape

After Phase 3 proves the pipe, verify actual bot quality and consent boundaries:

1. Use the actual paid user BotInstance after human `/start` when available.
2. If the paid user has not entered Telegram yet, run canonical guest canary against the live known guest and label the result server-side quality proof only.
3. Run canonical canary:
   `python3 scripts/hde_guest_canary.py --guest-id <id> --pretty`
4. Evidence should cover:
   - paid context recognition (requires real paid user `/start`);
   - one clear next question, not a rigid intake wall;
   - strict real first+last name capture;
   - low-friction chart/profile edits;
   - Sanctuary tone and no fake-companion loop;
   - PDF/report generation or delivery;
   - continuity lookup;
   - consent boundaries.
5. Coach consent proof must show active premium consented users are allowed and non-premium/inactive/missing-consent/revoked/expired users are denied. Payment/subscription alone must never infer coach consent.
6. Capture PDF proof honestly:
   - `pdfinfo` for pages/metadata;
   - `pdftoppm` first-page render;
   - OCR or semantic visual review if available;
   - label mechanical/OCR proof as controlled-staging proof, not final semantic design approval.
7. Run router metrics before and after; alert on `pending`, not retained stream `length`.
8. Report status:
   - GREEN only if paid Telegram onboarding, bot response quality, PDF delivery, and consent boundaries are all evidenced;
   - YELLOW if server-side bot path works but paid human Telegram start, consent, or PDF proof is incomplete;
   - RED if paid user cannot enter the correct bot flow.

## Report integrity verifier

For Hermes verification nudges or before committing reports, create a temporary `/tmp/hermes-verify-*` script that checks the report artifacts themselves:

- JSON parses and status semantics are honest (YELLOW while human Telegram proof is pending).
- Markdown and JSON both record the same recommendation.
- No shaped secrets appear: Stripe keys, webhook secrets, Telegram bot tokens, DB URLs, Redis URLs, or unredacted `?start=` tokens.
- Router metrics are currently clean.
- Relevant services are active.
- The temporary verifier deletes itself afterward.

Call this **focused ad-hoc verification**, not suite green.

## Common pitfall

A Stripe webhook can fail after checkout because the staging ORM model lacks fields referenced by checkout code. If logs show an ORM constructor error (for example a consent field not accepted by `User`), fix the model/migration and replay the signed Stripe event against the staging API. Do not call checkout green until DB user + invitation state exists.