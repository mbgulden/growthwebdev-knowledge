# HDE staging schema drift + success-page breathing fix (2026-07-16)

## Trigger
Michael reported the Human Design Companion bot felt broken after he used one existing Telegram conversation, then completed a fresh one-click onboarding walkthrough. He also asked for the success-page breathing animation to be real box breathing, smoother, and visually transparent.

## Bot failure pattern
Symptoms:
- `hde_router.service` remains active, but queued chat jobs repeatedly fail.
- Logs show `AttributeError: 'User' object has no attribute 'guide_name'` from `scripts/hde_tenant_router.py` wake/provision paths.
- Database columns may already exist (`users.guide_name`, `users.guide_name_source`), but `shared/database.py` ORM model may be missing mapped fields.
- The user's chat can get stuck in `bot_instances.status='waking'` when no corresponding `guest-hermes-<user_id>` container exists.

Root cause class:
- Schema drift between the live DB and SQLAlchemy model, not user error.
- A second checkout/onboarding can expose stale chat-to-user/bot-instance state, but the safe fix is to repair model/runtime state, not blame duplicate use.

## Fix sequence
1. Confirm router identity and logs without printing tokens.
2. Inspect DB columns and recent `users`, `invitations`, `bot_instances` rows using the same systemd env.
3. Add the missing ORM fields to `shared/database.py` if DB already has them:
   - `guide_name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)`
   - `guide_name_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)`
4. `py_compile` the model and router.
5. Restart `hde_router.service`.
6. Check the new MainPID logs specifically; journal output from the old PID can make the error look current after a restart.
7. If a real customer/tester chat is stuck in `waking` and no matching guest container exists, reset only that bot instance to `awaiting_guide_choice` so the user can choose the guide name again. Avoid broad DB rewrites.
8. Verify Redis split queues with Python/redis if `redis-cli` is not available; check `pending`, not retained stream `length`.

## Success-page breathing animation checklist
For HDE `/success/` breathing UI:
- Real box breathing is four phases: inhale 4s, hold 4s, exhale 4s, hold 4s.
- Do not combine labels like `Hold... Exhale...`; that is not box breathing.
- Use CSS classes for phases, not only inline transforms in JS.
- Use smooth cubic-bezier transitions for transform/opacity, e.g. `cubic-bezier(0.45, 0, 0.20, 1)`.
- Remove `mix-blend-mode: multiply` when the PNG is supposed to be transparent; use `mix-blend-mode: normal`.
- If the asset has a checkered or white background, convert edge-connected neutral light pixels to alpha 0, then verify alpha extrema and transparent corners with Pillow.
- Cache-bust the image URL after replacing the PNG, e.g. `/somatic_mandala.png?v=box-breathing-transparent-YYYYMMDD`, because Cloudflare may keep the old opaque PNG.
- If staging serves from a separate root, copy/sync the rebuilt frontend `dist/` into the staging `dist/` root and verify the live page references the new asset hash/query string.

## Focused verification recipe
Use a `/tmp/hermes-verify-*.py` verifier when Hermes asks for fresh proof or when changes span backend model + frontend animation:
- assert ORM fields exist in `shared/database.py`;
- `py_compile` `shared/database.py` and `scripts/hde_tenant_router.py`;
- assert `/success/` source contains `phase-inhale`, `phase-hold-full`, `phase-exhale`, `phase-hold-empty`, `setInterval(..., 4000)`, bezier easing, and `mix-blend-mode: normal`;
- assert old `Hold... Exhale...` copy is absent;
- assert PNG alpha extrema are `(0, 255)` and four corners have alpha 0;
- run `npm run build` for the frontend repo;
- remove the temp verifier and report this as focused ad-hoc verification, not full suite green.
