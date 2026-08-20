# 2026-07 response contract and golden next step notes

## Source signal

Michael corrected the agent's interaction style after asking why responses take so long. The key complaint was not simply latency; it was the combination of:

- heavy verification/tool use for simple asks,
- unclear final results after long verification runs,
- lack of immediately clickable final product links,
- procedural/technical jargon instead of user-facing outcomes,
- agents stopping after a single increment instead of following the larger goal path when autonomous/YOLO mode is expected.

## Durable learning

The class-level behavior to preserve is a response contract:

1. Simple conceptual/editorial/advisory asks should get a fast direct answer without unnecessary tools.
2. Live/build/fix/deploy/system tasks still require tool-backed verification.
3. Final reports should be result-first and link-first.
4. Verification evidence must be scoped and legible.
5. Completed work should include a `Next Step` section aligned to the project's golden thread/golden path.
6. In YOLO mode, the agent should continue executing along that next-step path until a real boundary appears.

## Suggested final answer skeleton

```md
✅ Done: <result>

**Open it:** [<artifact/result>](https://...)

**Changed**
- ...

**Verified**
- Focused/full verification: ...

**Next Step**
- Golden path: ...
```

## Boundary note

Do not turn this into a blanket ban on tools or verification. The point is proportionality: simple asks get speed; operational work gets evidence; all completed work gets clear links/results and a golden-thread next step.
