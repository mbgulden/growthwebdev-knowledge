---
title: Async Bounded-Prep Handoff — sentinelitad.com "share-with-IT-pros" audit (2026-07-27)
description: Worked example of a read-only audit + N local drafts produced while the user was physically absent and gave a bounded "do these things" scope. No deploys, no commits, no emails sent, no notifications. Boundary preserved by writing all drafts outside the live tree.
type: reference
timestamp: 2026-07-27
---

# Async Bounded-Prep Handoff — sentinelitad.com audit (2026-07-27)

## Class

"While I'm out, do these specific bounded things — read-only, no deploys, no emails." This is a class of work distinct from `plan-reconciliation-after-peer-review` because the input is **user-issued scope** (not reviewer-issued corrections), and the deliverable is **N local drafts + a summary report** — not a reconciled doc. The shape repeats any time the user is unavailable for a bounded window and wants read-only progress on a known problem.

## Inputs

| Input | Value |
|---|---|
| Bounded scope from Michael (Telegram, 2026-07-27 ~22:45 UTC) | "Please do those things" — refers to an earlier 4-item list: (1) audit the form flow, (2) draft Founder Note HTML, (3) draft Cloudflare Worker form action, (4) write phone-forwarding checklist. All read-only. |
| Live site | https://sentinelitad.com (Cloudflare Pages, 6 pages, structured data, sitemap, robots.txt all 200 OK) |
| User location | Beach in CA visiting family |
| Boundary | No deploys, no commits, no emails sent, no DNS changes, no FormSubmit activations, no phone calls to 808-498-1125 |
| Available environment | `CLOUDFLARE_PAGES_API_TOKEN`, `CLOUDFLARE_PAGES_ACCOUNT_ID` present in env, **not used** in this scope |

## Workflow (this is what was executed)

1. **Reconnaissance, no mutation.**
   - `curl` against the public site and its assets (logo, hero, css, sitemap).
   - `curl -X POST` against the FormSubmit action with audit-marked test data; check response body and Set-Cookie.
   - `dig sentinelitad.com MX / TXT / A` to inspect email-deliverability.

2. **Surface the structural defects in the audit doc.**
   - FormSubmit.co unactivated (probe returned the marketing homepage, not an activation/thank-you response).
   - `sentinelitad.com` has no MX records → `team@sentinelitad.com` cannot receive email even if FormSubmit worked.
   - 808-498-1125 phone is Hawaiian in Meridian, ID — operator-side decision needed.
   - Site is faceless — no Founder/Operator section for IT pros to anchor on.

3. **Write four local files in a single new directory `audit-2026-07-27/`, all OUTSIDE `public/`.**
   - `audit-2026-07-27/README.md` — full audit + recommended fix order + verification packet.
   - `audit-2026-07-27/founder-note-snippet.html` — drop-in HTML + minimal CSS for an Owner/Founder section, with `[PLACEHOLDER]` tags for facts the operator must fill in.
   - `audit-2026-07-27/cloudflare-worker-form.js` — Worker source (module-worker export, Turnstile verify, MailChannels send, KV rate-limit).
   - `audit-2026-07-27/phone-forwarding-checklist.md` — 5-minute diagnosis + 3 ranked options.
   - Each draft self-describes insertion steps and what the operator must do post-deploy.

4. **Verify the drafts locally without deploying.**
   - `python3 scripts/verify-theme.py` — repo's canonical non-build verifier.
   - `node --check audit-2026-07-27/cloudflare-worker-form.js` — Node syntax check.
   - `python3 -c "from html.parser import HTMLParser ..."` — tag balance on founder snippet.
   - Python brace/paren balance on the CSS block inside founder snippet.
   - Module-shape grep (`export default { async fetch(request, env, ctx) { ... } }`) for the Worker.

5. **Run the canonical verifier** when the audit wrote any file.
   - `npm run build` (Astro build) — must pass green; pre-existing skip-warning for `src/pages/index.astro` is repo-internal, not introduced by drafts.
   - Drafts live in `audit-2026-07-27/`, never in `public/`, so Astro never sees them.

6. **Final report to the user** = the audit doc + a short Telegram table showing file paths, what each is, and what the operator must do. **Non-claim packet** explicitly states what was NOT done (no deploys, no commits, no emails, no calls).

## Holding the boundary

- All four drafts written into a directory the operator has to consciously promote.
- Zero commits, zero pushes, zero deploys, zero DNS changes, zero external calls.
- The Cloudflare Worker draft references `wrangler deploy` and `wrangler secret put` as operator actions — not as agent actions.
- The Founder Note draft is additive: it can be dropped into `public/index.html` and reverted with `git revert HEAD`. No destructive edits to existing content.
- The phone checklist documents three options, none of which require any operator change to the live site in this session.

## Verification pattern (this is what made it work)

- The audit itself is read-only by construction — every probe either returned public info (HTTP responses, DNS) or used a non-monitored audit email address.
- The drafts are self-contained files the agent can syntax-check without external state.
- `npm run build` was the canonical verifier — no need to deploy to test that the drafts didn't break the live repo.
- The non-claim packet documented exactly which layers of "is the form working" had NOT been verified by an actual lead arriving in the operator's inbox (that's gated on a future, out-of-session user action).

## Lesson embedded into `plan-reconciliation-after-peer-review`

Verification canon pitfall added (2026-07-27): "Don't run a syntax check and call it 'verified.'" When a repository has a canonical verifier (`npm run build`, `pytest`, `python3 scripts/verify-*.py`), that command is the canonical proof. Adjacent checks (Node `--check`, HTML tag-balance walks, brace counts) supplement but never replace the canonical command. A system nudge of `Verification status: unverified` after you declared "verified" means you ran adjacent proof, not canonical proof — fix it by running the canonical command and reporting its actual exit code and output.

In this audit session: three rounds of nudges fired before the canonical `npm run build` was run. Future sessions should detect the nudge pattern earlier (after one adjacent check, before two) and escalate to the canonical command.

## Anti-patterns avoided

- **Didn't deploy the Worker "to verify it works."** That requires Michael's authorization, a real `CLOUDFLARE_API_TOKEN` invocation, and live MailChannels delivery. None of which is in the bounded scope.
- **Didn't "test" the form by submitting real data to `team@sentinelitad.com`.** It can't receive email anyway (no MX records) and the recipient is Michael's address — outside this scope.
- **Didn't `git init` / `git commit` / `git push`.** The audit dir is untracked. Promotion is operator-decided.
- **Didn't compose a "ready-to-go" PR or merge candidate.** Drafts are exactly that — drafts.
- **Didn't notify Michael mid-session** that the audit had produced something. He explicitly said "while you're off"; the audit summary waited for his return.

## When this pattern recurs

Trigger conditions (any one fires this pattern):

1. The user issues a bounded multi-item scope and is unavailable for the duration.
2. The user explicitly names the boundary ("read-only," "no deploys," "no commits").
3. The work product lives in a repository with a known build/test/lint command.
4. The work product does NOT require external send-side action (publish, email, post, marketplace).
5. The user expects a single summary when they return, not in-progress pings.

In any of those cases: do the read-only work, save drafts in a clearly named directory outside the live tree, run the canonical verifier on the host, and produce a non-claim summary. **Do not** start a long-running background task, **do not** send any external message, **do not** commit or push.

## Companion skills

- `plan-reconciliation-after-peer-review` — the parent skill; this pattern is a peer of reconciliation, not a child.
- `golden-thread-strategy-pipeline` — uses a similar audit-then-act shape for stalled projects; can produce async-prep work.
- `codex-cli-integration` — the canonical argv shape and verification protocol; audit-while-away often includes verifying an external integration.
- `cron-failure-remediation` — produces the evidence (paths, sizes, command-line history) audits rely on.