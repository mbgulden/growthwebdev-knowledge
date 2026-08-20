# Dashboard polling state preservation

## Trigger

Use this when a Prismatic dashboard tab is backed by periodic global refresh (`fetchData`/WebSocket refresh) and the user reports that navigation resets every few seconds.

## Durable lesson

Do not solve this by slowing or disabling the global poll. Preserve the live refresh path, but make the tab renderer idempotent after its first successful initialization.

Recommended pattern:

- Keep tab-local state, e.g. `workspaceTreeState.initialized` and `workspaceTreeState.rendering`.
- At the start of the expensive tree renderer, return early when either flag is true: already initialized or currently rendering.
- Set `rendering=true` before async fetch/render work.
- Set `initialized=true` only after successful render/hydration.
- Reset `rendering=false` in `finally` so failed first renders remain retryable.
- Do not clear expanded folders, selected file, preview DOM, or scroll position on unrelated global polls.
- Keep generated dashboard output fresh if dashboard HTML is built from source fragments.

## Verification recipe

Run both source-contract and rendered behavior proof:

1. Source/literal regression: assert the initialized/rendering guard exists in the source fragment and generated dashboard, and that the success path sets `initialized=true` while `finally` resets `rendering=false`.
2. Focused project tests covering dashboard source split/build freshness.
3. `scripts/build_dashboard.py --check`, lint/format, `node --check` for the dashboard script, and `git diff --check`.
4. Rendered proof with a real browser/CDP viewport: expand at least one folder, select a file preview, wait longer than two poll intervals, and assert:
   - same root DOM node identity,
   - same expanded child folder DOM node identity,
   - folders remain expanded,
   - selected preview remains visible,
   - no absolute workspace root leaks.

Label this proof `ad-hoc targeted` unless the canonical full suite also ran.

## Pitfalls

- A static source check alone is insufficient; this failure is temporal and only appears after at least one poll interval.
- Re-rendering the whole tab on every global `fetchData()` destroys DOM identity even if the API data is unchanged.
- If the first fetch fails, `initialized` must stay false so the next poll can retry.
- Do not introduce a fallback mini-dashboard; preserve the existing canonical dashboard shell and adapters.
