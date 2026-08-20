# Dashboard refresh state preservation

Session-derived pattern for Prismatic dashboard surfaces that auto-refresh or hydrate on a timer/WebSocket event.

## Failure class

A dashboard tab can look correct immediately after rendering but still be unusable if global polling re-renders the whole tab every few seconds. For workspace/file-tree navigation this resets expanded folders, selected files, scroll position, and previews, sending the user back to a fresh page while navigating.

## Durable fix pattern

1. Locate the global refresh path (`fetchData`, WebSocket event handlers, periodic hydrate timers) and identify whether it re-renders the active tab unconditionally.
2. Add an idempotence/state guard for interactive tabs: first render initializes the tree; subsequent data polls should update backing data without replacing the live DOM while the user is navigating.
3. Preserve user-facing state explicitly: expanded folder nodes, selected file/preview, scroll position if relevant, and deep-link parameters.
4. Add a source-contract regression that prevents future unconditional `renderWorkspacesView()` calls from `fetchData`/global polling without an `initialized`/`rendering` gate.
5. Rebuild generated dashboard assets from source; do not patch generated bundles only.
6. Verify with rendered behavior, not static source inspection only: open the real dashboard, expand nested folders, select a file, wait longer than two refresh intervals, and assert the same DOM nodes are still connected, folders remain expanded, and preview content is unchanged.
7. For production, keep the existing canonical dashboard and workspace registry. Deploy as a new immutable release/drop-in with rollback, not by mutating the live checkout or creating a fallback mini-dashboard.

## Proof packet shape

```text
REFRESH_INTERVAL=<seconds>
WAIT_SECONDS=<>=two refresh intervals
SAME_ROOT_DOM_NODE=true
SAME_NESTED_FOLDER_DOM_NODE=true
ROOT_STILL_EXPANDED=true
NESTED_FOLDER_STILL_EXPANDED=true
SELECTED_FILE_PREVIEW_PRESERVED=true
DASHBOARD_BUILD=PASS
FOCUSED_TESTS=PASS
PUBLIC_OR_LOCAL_RENDERED_PROOF=PASS
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<non-claims>
```

## Pitfalls

- Do not claim a polling-reset fix from static JS/CSS checks alone. The regression is behavioral and must be observed through a rendered dashboard across actual timer intervals.
- Do not weaken production containment or replace the canonical dashboard just to make the proof easy. If public browser paths are contained, prove the route locally through the production proxy headers or use the existing approved edge route pattern.
- Avoid session-specific opaque IDs in the skill body. Record those in deployment receipts/handoffs only.
