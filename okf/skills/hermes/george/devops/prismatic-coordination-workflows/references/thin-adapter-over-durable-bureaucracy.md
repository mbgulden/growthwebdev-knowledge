# Thin adapter over durable bureaucracy

## Trigger

Use this note when coordinating Prismatic event-gate, launcher, bus, dashboard durability, or deployment/configuration-before-admission work and the proposed slice starts adding a second ledger, duplicate supervisor, duplicate status polling, conflating deployment with task admission, or extra proof bureaucracy around an existing canonical subsystem.

## Session signal

Michael challenged a generic event-launcher bootstrap as possibly overbound by rules and bureaucracy. The useful correction was not to abandon the real blocker; it was to simplify the solution until it became a thin adapter over existing durable machinery.

## Durable lesson

Before building new runtime infrastructure, identify which existing component already owns the durable contract. For AGY event admission, the authenticated consumer can own request selection/claim binding, and `AGYCLIHarness` can own cap/replay/runtime/tmux containment. A launcher adapter should avoid becoming a second control plane.

## Good pattern

1. State the real blocker in one sentence.
2. Ask whether the proposed machinery is necessary for that blocker.
3. Map responsibilities to existing canonical components.
4. Keep the new code responsible only for the missing seam.
5. Verify reduced scope before PR/review/merge.
6. When Michael challenges bureaucracy/overbinding, pause the merge path, measure the added surface area, and simplify before continuing. Treat the challenge as a first-class workflow correction, not a side comment.
7. After review repairs, re-run the simplicity check: did the fix reintroduce duplicated machinery that an existing primitive already owns?
8. Prefer importing/reusing an existing tested primitive (secure descriptor read, harness receipt replay, cap enforcement, etc.) over rewriting equivalent safety code in the adapter.
9. Invite/accept user challenge as a governance input, not as a derailment.
10. Keep deployment/configuration slices separate from admission/producer-launch slices when Michael explicitly authorizes only the first boundary; prove `ADMITTED=false` and `PRODUCER_LAUNCHED=false` instead of treating a healthy deployment as task progress.
11. For the detailed deployment/configuration stop-boundary checklist, see `references/immutable-release-config-before-admission.md`.

## Review-repair pattern from generic launcher work

When an exact-head review finds real defects in a thin adapter, keep the repair defect-bound instead of expanding into a new durable system:

- Deterministic replay/recovery should use an event-level stable run ID rather than per-claim randomness when claim identity can change across recovery.
- If a launcher delegates to an existing harness, read back the canonical harness receipt and fail closed on incomplete launch state; do not invent a parallel receipt format.
- Terminal-at-cap behavior should preserve the real error class (for example, `launch_failed`) rather than relabeling third-attempt failures as validation errors.
- For descriptor-bound file/receipt reads, search for and reuse the repository's tested primitive before adding local `O_NOFOLLOW`/`fstat` security code.

## Anti-patterns

- Adding a new ledger when the canonical harness already has durable replay/active slots.
- Adding custom process supervision when the canonical harness owns tmux/process containment.
- Revalidating every upstream invariant in the adapter when an authenticated consumer already fails closed before invocation.
- Reimplementing security or receipt-read machinery locally when the repository already has a tested descriptor-bound primitive.
- Letting review repairs balloon the adapter back into a second subsystem; after each blocker fix, measure changed lines and deleted duplication before proceeding.
- Treating more proof layers as automatically safer; excess bureaucracy can create new stale-state and detector-loop failure modes.

## Suggested proof language

```text
DESIGN_BOUNDARY=thin adapter; not a second durable runtime
EXISTING_OWNER=<component that owns replay/cap/process/ledger>
NEW_CODE_OWNS=<minimal seam only>
REMOVED_DUPLICATION=<ledger|polling|Popen|wall-clock|worktree revalidation>
NOT_CLAIMING=deployment/runtime policy change until explicitly authorized
```
