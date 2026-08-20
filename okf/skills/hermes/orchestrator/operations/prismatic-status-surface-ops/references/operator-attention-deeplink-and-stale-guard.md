# Operator Attention Deep-Link + Stale-Guard Verification Pattern

Use this reference when improving the Prismatic governance dashboard default-view attention rail or any CTA that should land an operator on a specific tab row/item.

## Trigger

- The dashboard correctly surfaces a high-priority signal, but the CTA only opens a broad tab (for example `Open Ingestion`) instead of the exact row/context.
- A stale verification guard keeps reporting the changed HTML path as unverified even after PR merge.
- Browser accessibility click tooling does not appear to dispatch dynamically assigned button handlers, while direct DOM invocation works.

## Durable UI pattern

Prefer stable inline handlers plus explicit state over assigning `button.onclick = ...` dynamically after render.

Example shape:

```js
let operatorAttentionAction = { tabName: 'telemetry', itemId: null };

async function handleOperatorAttentionAction() {
  if (operatorAttentionAction?.itemId !== null && operatorAttentionAction?.itemId !== undefined) {
    await focusQueueItemFromAttention(operatorAttentionAction.itemId);
    return;
  }
  switchTab(operatorAttentionAction?.tabName || 'telemetry');
}

function setOperatorAttention(..., tabName, reasons = [], itemId = null) {
  operatorAttentionAction = { tabName, itemId };
  action.textContent = actionLabel;
}
```

For ingestion queue deep-links, the focused path should:

1. Pick a concrete queue target from `/api/gateway/webhooks/queue`.
2. Label the CTA with the exact target, e.g. `Open TEST-001`.
3. Switch to the Ingestion Queue tab.
4. Filter/search to that row.
5. Highlight the row with a visible focus class.
6. Open the row detail modal.
7. Show failure-taxonomy context from `/api/gateway/recovery/status` near the queue table.

## Browser proof pitfall

If `browser_click` against a stale accessibility ref does not trigger the newly assigned handler, do **not** assume the UI is broken or stop at source proof. Refresh the snapshot after async label updates, and also verify the actual DOM click path:

```js
document.getElementById('operator-attention-action')?.click()
```

Expected proof fields:

```text
sectionTelemetryVisible: true
focusPanelHidden: false
focusTitle: TEST-001 · fred · processed
searchValue: TEST-001
rowHighlighted: true
modalVisible: true
modalBadge: ID: 1
taxonomyChips: Ingest Auth · ingest, Ingest Parse · ingest, Routing · router, Execution · agent
console errors: 0
```

Do not report accessibility-tool click weirdness as a durable browser/tool limitation; report the verified DOM behavior and harden the implementation with stable handlers.

## Stale-guard verifier shape

When the system stale guard names an exact changed path, emit a compact `/tmp/hermes-verify-*` verifier with:

- `changed_paths_checked` containing the exact path string;
- a plain canonical command field, e.g. `canonical_test_lint_build_command: node --check /tmp/hermes-dashboard-inline-stale-guard.js`;
- local and `origin/deploy-fresh` marker checks;
- live `/dashboard` smoke;
- relevant API smokes (`/api/gateway/webhooks/queue`, `/api/gateway/recovery/status` for ingestion deep-links);
- PR merge/readback evidence;
- `cleanup=PASS removed /tmp/hermes-verify-xxxx.py`.

Keep the boundary explicit: ad hoc targeted dashboard verification only — not full suite green.
