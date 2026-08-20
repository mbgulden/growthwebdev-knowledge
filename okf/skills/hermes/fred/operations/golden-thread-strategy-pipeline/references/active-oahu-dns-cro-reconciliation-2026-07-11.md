# Active Oahu DNS → CRO Reconciliation Pattern (2026-07-11)

Use this when a Golden Thread run selects Active Oahu / static mirror / SEO work and the registry says DNS cutover or live 404s are urgent.

## What happened

The registry still claimed Active Oahu needed urgent DNS cutover to the Cloudflare Pages mirror because key live pages were 404ing. AGY research repeated that stale premise and also mixed in an unrelated HD Engine Stripe task that happened to be filed under the Active Oahu project.

Fresh verification showed:

- `activeoahutours.com` and `active-oahu-tours-mirror.pages.dev` both returned `200` with Cloudflare headers.
- Local audit evidence already recorded apex `CNAME` → `active-oahu-tours-mirror.pages.dev`.
- 10 high-intent/support paths returned `200` on both apex and mirror.
- The registry `next_action` needed to be corrected away from DNS and toward CRO.

## Durable pattern

1. **Do not trust stale registry DNS/404 claims.** Reconcile against fresh HTTP checks and local DNS/Page audit artifacts before creating cutover work.
2. **Treat AGY project-issue evidence as contaminated until checked.** A project can contain misfiled issues; verify whether a cited issue actually belongs to the selected project/domain before making it an assumption challenge.
3. **If DNS/cutover is already complete, pivot to CRO enablement:**
   - style high-priority inline booking CTAs,
   - build/verify conversion signal tracking,
   - bucket broken references by revenue risk instead of fixing scanner totals blindly.
4. **Update the registry when the premise is stale.** Otherwise future Golden Thread runs keep re-opening completed infrastructure work.
5. **Close only the executed reconciliation task if evidence satisfies the exit criterion.** Leave downstream CRO implementation tasks open.

## Verification commands / artifacts from the session

- Verifier: `/home/ubuntu/work/research/dns_reconciliation_verifier.py`
- Evidence JSON: `/home/ubuntu/work/research/dns_reconciliation_evidence.json`
- Evidence Markdown: `/home/ubuntu/work/research/dns_reconciliation_evidence.md`
- Durable site report copy: `/home/ubuntu/work/active-oahu-tours-mirror-1251/reports/golden-thread/dns_reconciliation_evidence.md`

Expected fresh rerun summary:

```text
rows 20 errors 0
apex_200 10
mirror_200 10
```

## Linear task pattern

Create tasks with rubrics and exit criteria, for example:

- Reconcile DNS cutover status and stale 404 registry claims — top task, Todo, execute immediately.
- Convert 8 high-priority inline booking CTAs into styled buttons.
- Triage 1,139 broken internal references into revenue-risk buckets.
- Build AOT conversion signal tracker for CRO vs content decisions.

## Linear GraphQL pitfall from this run

When writing idempotent Linear scripts, GraphQL variables used for IDs must be `ID!`, not `String!`, when the schema expects an ID. The failed query used `$teamId:String!` in a team id filter and returned:

```text
Variable "$teamId" of type "String!" used in position expecting type "ID".
```

Fix by declaring `$teamId:ID!`.
