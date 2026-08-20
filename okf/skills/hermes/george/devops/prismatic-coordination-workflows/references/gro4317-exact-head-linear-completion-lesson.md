# GRO-4317 exact-head acceptance and Linear completion lesson

Session lesson for foundational Prismatic critical-path work.

## What mattered

Michael redirected the lane back to the live Linear critical path and explicitly said:

- pull the live Linear graph first;
- use the latest valid checkpoint and standing authorization;
- work GRO-4317 to independently accepted implementation;
- do not create more precontracts, blocker documents, or adjacent reviews unless a newly observed fact requires them.

The accepted implementation eventually produced exact head `d1319e55178354adb241dad0b4b5db5db10b7a99` with independent `CLEAN/PASS`. The final Linear action was bookkeeping: move GRO-4317 to canonical `Done`.

## Durable workflow lesson

When the critical-path issue has exact-head acceptance and the remaining Linear write is a one-field completion transition, avoid launching a new precontract/writer-review loop. Use the bounded state-transition pattern instead:

1. live baseline read of the exact issue and available completed states;
2. exact-head/clean-status guard bound to the accepted commit;
3. prior `updatedAt`, state, and `completedAt` drift guard;
4. durable JSONL intent before mutation;
5. one `issueUpdate` for `stateId` only;
6. immediate read-only readback;
7. receipt hash and strict non-claims;
8. advance the critical-path pointer without starting the downstream issue.

See `../linear-read-verify/references/single-issue-state-transition-after-acceptance.md` for the reusable procedure.

## Do not generalize too far

This does **not** authorize broad Linear mutation outside a single accepted issue state transition. For description/label/relation/topology/comment mutations, continue using reviewed fail-closed writer packets.
