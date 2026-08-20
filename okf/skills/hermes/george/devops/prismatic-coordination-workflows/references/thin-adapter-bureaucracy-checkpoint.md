# Thin-adapter bureaucracy checkpoint

Use when Michael challenges whether a Prismatic source slice is creating too much durable machinery or process overhead.

## Trigger language

Examples: "too many rules", "tripping over yourself", "is this actually helpful?", "too much bureaucracy", "too many durable systems".

## Response pattern

1. Pause the merge/deploy path immediately. Do not defend the candidate reflexively.
2. Restate the real problem the slice should solve in one or two bullets.
3. Separate useful minimum from overbuilt machinery:
   - keep concrete task binding/admission handoff if it closes a real gate;
   - remove custom process management, duplicate status polling, duplicate ledgers, and duplicate security readers when an existing harness/consumer already owns them;
   - trust authenticated admission/consumer revalidation for the control-plane invariants it already enforces.
4. Measure the candidate before and after simplification: changed paths, insertion count, adapter line count, and focused/canonical proof.
5. Continue only if the smaller candidate still closes the real workflow gap and preserves fail-closed review findings.
6. If an independent review finds valid defects, repair them by reusing existing primitives first; do not re-grow the abandoned durable subsystem.

## Proof shape

```text
PROBLEM=<actual gap>
KEPT=<minimal value>
REMOVED=<duplicate/overbuilt machinery>
CHANGE_SIZE_BEFORE=<insertions/lines>
CHANGE_SIZE_AFTER=<insertions/lines>
REUSED_EXISTING=<harness/consumer/security primitive>
PROOF=<focused + canonical logs>
BOUNDARY=<not claiming deploy/admission/review unless proven>
```

## Pitfalls

- Do not let a security/review repair become an excuse to rebuild the larger system that was just rejected.
- Do not count line reduction alone as correctness; rerun focused and canonical proof after simplification.
- Do not ignore the style signal: Michael is asking for usefulness and operational simplicity, not just green tests.
