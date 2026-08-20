# Open Linear Task Audit → AGY Routing Triage

## When this applies

Use this pattern when Michael asks which open Linear tasks can be handed to AGY, which actually need his help, or why a factory digest shows a confusing queue count.

## Durable lessons

- Factory/fleet digests may report a **narrow queue lens** (for example dispatch-ready/open counts), not the full Linear team backlog. Query live Linear for non-completed issues before making routing claims.
- The local `linear_api_compat.linear_call()` shim returns the GraphQL response **data object directly** in this environment. Do not always parse as `response["data"]`; inspect/normalize both shapes:
  - `payload["issues"]["nodes"]`
  - `payload["data"]["issues"]["nodes"]`
- `agent:needs-human-review` is often queue sludge. Treat it as a triage signal, not proof Michael is required.
- Be strict about "actually needs Michael": only manual send/publish/recording, explicit approval/decision, credentials/billing/access, or named Becca/Ella/Michael feedback blockers should land there.
- Do **not** over-classify generic words like `post`, `publish`, or `review` from long descriptions as Michael blockers. Prefer title + explicit blocker phrases over broad description keyword scans.

## Recommended audit buckets

1. `AGY-ready now`
   - `agent:agy` + `dispatch:ready`.
   - Caveat: outbound send/publish or interview/recording titles still need Michael even if AGY-labeled.
2. `Candidate to hand to AGY`
   - Backlog/Todo items with audit, QA, verification, crawl, schema, alt text, media, SEO, regression, evidence, fixture, triage, or reconciliation work.
   - No conflicting owner like Jules/Codex/Kai/Ned.
3. `Actually needs Michael`
   - Title or explicit blocker says: send, publish externally, interview, record, audio/voice, approval, decision, confirm, credentials/login/billing, Stripe/FareHarbor access, Becca/Ella feedback, explicit user consent.
4. `Human-review label cleanup/triage`
   - Has `agent:needs-human-review` but no explicit Michael blocker.
   - Usually needs label cleanup, self-review evidence, peer-review routing, or ownership correction.
5. `Other-agent ready`
   - `dispatch:ready` plus Jules/Codex/Kai/Ned labels.
6. `Peer-review / self-review loop`
   - `agent:peer-review` without evidence/self-review may be stuck in review automation, not Michael.
7. `Fred-ready / orchestration`
   - `agent:fred` + `dispatch:ready`, especially governance/infra coordination.
8. `Paused / held`
   - `dispatch:paused` or known deferred project.
9. `Backlog / unclear`
   - Not enough evidence to route safely.

## Workflow

1. Query live Linear once with a budgeted call for all non-completed GRO issues.
2. Normalize response shape before counting rows.
3. Generate two artifacts:
   - Markdown summary for Michael.
   - CSV with one row per issue for follow-up mutation scripts.
4. Classify with strict blockers first, then AGY/other-agent readiness, then cleanup buckets.
5. Verify the artifacts with a temporary `/tmp/hermes-verify-*` script:
   - expected row count
   - required buckets present
   - no obvious token/secret prefixes in the Markdown artifact
6. Do not mutate labels in the audit pass unless Michael explicitly asks you to route/update.

## Reporting shape

Keep the Telegram response compact:

- State live count vs digest count and explain the lens difference.
- Table of bucket counts.
- Short AGY-ready list.
- Short `Candidate to hand to AGY` list.
- Short `Actually needs Michael` list, grouped by recording/outbound/access/feedback.
- Attach the full Markdown/CSV artifacts.
- Label verification as ad hoc audit verification, not full governance suite green.

## Pitfalls

- Do not present `agent:needs-human-review` as Michael work without inspecting title/description/comments.
- Do not hand outbound email/profile publishing to AGY. Agents can draft/package/check, but Michael sends/publishes unless explicitly confirmed otherwise.
- Do not hand interview/recording tasks to AGY as if the recording exists. AGY can prepare scripts/checklists, but Michael provides/approves source audio.
- Do not mutate 100+ issues from a first-pass classifier. Audit first; route in small batches.
