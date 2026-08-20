# Dashboard Modal Flow (Phase 4.2) — Reference

This reference captures the canonical shape for adding an interactive UI
fragment (modal, per-site CTA buttons, inline edit forms) to the static
PWP KPI dashboard without giving up the static-HTML deployment model.

Source: Phase 4.2 work on `prismatic-pwp-ubersuggest-auth`,
`prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/funnel_form.py`
plus modifications to `publish_kpi_tracker.py`. Verified by
`/tmp/hermes-verify-phase42-v2.py` (83/83 checks) and pytest 348/348.

## The shape

```
publish_kpi_tracker/
├── funnel_form.py                  <-- NEW: modal owner
│   ├── render_modal_html(...)
│   ├── render_modal_css() -> str
│   ├── render_button_wiring_js() -> str
│   ├── site_row_buttons(site) -> str
│   └── load_prior_submission(slug) -> dict | None
├── publish_kpi_tracker.py          <-- modified
│   └── render_index(agg, *, csrf_token: Optional[str] = None) -> str
└── templates/pwp-publish-kpi.css   <-- modal CSS appended
```

## Why one module per modal

A new module per UI fragment keeps `render_index` unchanged for callers
that only consume the data + card grid. To add a second modal
("Run registry validation now", "Mark site stale") drop in
`announcements.py` or `actions.py` alongside `funnel_form.py` and inject
the same way. The injection contract:

```python
def render_index(agg, *, csrf_token=None):
    modal_html = ""
    wiring_js = ""
    try:
        from .funnel_form import render_modal_html, render_button_wiring_js
        modal_html = render_modal_html(csrf_token=csrf_token)
        wiring_js = render_button_wiring_js()
    except Exception:
        modal_html = ""
        wiring_js = ""
    # ... use modal_html + wiring_js in the <body> tail ...
```

The cost: one import-time guard. The benefit: a partial install or a
pinned dashboard-only build keeps working without breaking on a missing
feature module.

## The CSRF / determinism interaction (durable pitfall)

`render_index` is contractually byte-identical for the same `agg` input.
The existing integration test relies on this for cache-key assertions
and snapshot diffing. Naively injecting a per-render random token via
`secrets.token_urlsafe()` into the modal HTML breaks the contract:

```
> assert html_a == html_b
E   AssertionError: render_index is not deterministic
E   - ata-csrf="H_Sj9K2FjZARBVEUNExPSw">
E   + ata-csrf="O3-esDEqaE2rjqiPyhymXA">
```

The fix — and the durable rule for any "self-rendering" builder that
adds non-deterministic data — is the keyword-only `csrf_token` argument:

- `render_index(agg, csrf_token=None)` — defaults to None, which means
  "generate fresh via secrets.token_urlsafe(16)"
- `render_modal_html(csrf_token=None)` — same shape, passed through
- Tests pass `csrf_token="test-csrf-stable"` to verify the rest of the
  HTML is byte-identical
- Live callers (build_dashboard, FastAPI gateway) pass `csrf_token=None`
  for fresh tokens per render

Same rule applies to: timestamps, request IDs, fresh hash salts,
correlation tokens, anything that "should be different per request but
stable per re-render of the same input."

## Pre-fill from prior submission log (subtle test pattern)

The refinement flow pre-fills form fields from the prior submission log:

```python
def site_row_buttons(site: Dict[str, Any]) -> str:
    slug = site.get("slug", "")
    has_prior = load_prior_submission(slug) is not None
    # ... switch button label and add refinement button when has_prior ...
```

`load_prior_submission` reads from `SUBMISSION_LOG_DIR/<slug>.json`. In
tests:

```python
def test_no_prior_shows_configure_label(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "plugins.pwp.capabilities.publish_kpi_tracker.funnel_form.SUBMISSION_LOG_DIR",
        tmp_path,
    )
    out = site_row_buttons({"slug": "ezshare", "domain": "ezshare.systems"})
    assert "Configure website KPIs" in out
```

DO NOT mock `load_prior_submission` itself — the test stops exercising
the production reading code. The data stays on disk under
`PWP_FUNNEL_CONFIG_DIR`; only the directory moves in tests.

## Two-layer safety escape (no-backend fallback)

The modal POSTs to `/pwp/api/funnel-config`. If the host has no backend,
the JS detects the 404 and falls back to downloading the JSON payload as
a file the user hands to the agent. Static-hosting-friendly by default;
backend is a progressive enhancement:

```js
fetch(endpoint, { ... }).then(function (resp) {
  if (resp.status === 404) {
    fallbackDownload(payload);  // Blob → download
    showFeedback('No backend at ' + endpoint + ' — JSON downloaded.', 'pwp-kpi-modal-feedback-warn');
    return null;
  }
  if (!resp.ok) { ... }
  return resp.json();
}).then(function (data) {
  if (!data) return;
  showFeedback('Dispatched to Linear · ' + data.linear_issue_identifier,
               'pwp-kpi-modal-feedback-ok');
});
```

The fallback path is the **always-works** path; the real backend is
just a nicer UX when a `pwp-api` service exists.

## Live verification (what to prove)

The fresh ad-hoc verifier for this flow covers:

1. funnel_form imports cleanly
2. render_modal_html shape (form fields, controller JS, fallback
   download, prefill, safety: no eval(), aria-live feedback, kind
   badge)
3. render_modal_css shape (panel backdrop, responsive max-width,
   CSS variables for theming)
4. CSRF token uniqueness across 20 renders
5. site_row_buttons correctly switches on prior submission log
6. load_prior_submission correctly reads / parses / returns None on
   missing/corrupt files
7. render_index integration (modal injected, CSRF present, all
   sites have buttons)
8. Live build_dashboard writes modal HTML + CSS to publish_root
9. CSRF escape safety (`&quot;`, `&lt;`, `&gt;`)
10. Lazy-import fallback: dashboard still works without funnel_form
11. Full pytest suite remains green (348/348)

The canonical output for "all checks pass, fresh verifier" is:

```
=== Summary ===
  83/83 checks passed

✅ ALL PHASE 4.2 CHECKS PASS
```

## Common pitfalls (Phase 4.2 specific)

- **Forgetting the csrf_token kwarg on render_index.** Adding the modal
  without an escape hatch breaks the byte-identical determinism test.
  Always thread the keyword arg through.
- **Hardcoding /home/ubuntu/... in funnel_form.py.** Path-portability
  commit gate aborts. Use `~/.hermes`, `~/work`, `__file__.resolve().parents[N]`,
  or `PRISMATIC_REPO_ROOT` env var.
- **Mocking load_prior_submission.** Tests must exercise the
  production reading path; only `SUBMISSION_LOG_DIR` moves.
- **Adding eval() / Function() / new Function() in the modal JS.** A
  future XSS protection audit will catch this. The data is JSON-
  deserialized and inserted via `textContent` / `value` setters, never
  via `.innerHTML`.
- **Escaping single quote `'` in modal HTML attributes.** `_esc` only
  escapes `&<>"`. Single quotes in CSRF tokens survive unescaped —
  but since `data-csrf` attributes use **double quotes**, `&quot;` is
  the right escape. Do not switch to single-quoted attributes without
  updating `_esc` first.

## Files touching this flow

- `funnel_form.py` (NEW, ~600 lines, owns the modal)
- `publish_kpi_tracker.py` (modified: `render_index` accepts `csrf_token`
  kwarg, lazy-imports `funnel_form` for the modal block + per-site
  buttons)
- `templates/pwp-publish-kpi.css` (modal CSS appended ~5KB)
- `tests/test_funnel_form.py` (NEW, 48 tests covering shape, switches,
  safety, escape, lazy-import fallback, render_index integration)
- `tests/test_publish_kpi.py` (modified: determinism test passes
  `csrf_token="test-csrf-stable"`)
