# Rendered refresh-persistence proof

Use this when a UI/dashboard edit claims to fix state loss caused by polling, hydration, or WebSocket-driven refresh.

## Trigger

A tab/tree/file viewer resets every few seconds while the user is navigating, usually because a global refresh path re-renders the active view unconditionally.

## Required proof

1. Find the actual refresh cadence or event path.
2. Reproduce the interaction on a rendered page, not just source inspection.
3. Expand at least one root and one nested folder or equivalent interactive state.
4. Select a file/item/preview or equivalent selected state.
5. Wait longer than two refresh intervals.
6. Assert both DOM continuity and user-visible state:
   - same key DOM node(s) remain connected when applicable,
   - folders/controls remain expanded,
   - selected item/preview remains unchanged,
   - no unwanted navigation reset occurred.
7. Keep the proof ad-hoc unless the canonical suite also ran.

## Minimal proof markers

```text
REFRESH_INTERVAL=<seconds>
WAIT_SECONDS=<seconds>
POLL_INTERVALS_SURVIVED=2
SAME_ROOT_DOM_NODE=true
SAME_NESTED_DOM_NODE=true
EXPANDED_STATE_PRESERVED=true
SELECTED_PREVIEW_PRESERVED=true
RENDERED_PROOF=PASS
AD_HOC_OR_CANONICAL=ad-hoc targeted
```

## Pitfalls

- A static regression that checks for an `initialized` guard is useful but insufficient alone; it must be paired with rendered persistence proof.
- If the verifier script has an expectation typo while product behavior passes, fix the verifier and rerun the whole rendered wait from the beginning.
- Do not mutate production containment to make a browser proof easier unless deployment scope explicitly includes that edge route.
