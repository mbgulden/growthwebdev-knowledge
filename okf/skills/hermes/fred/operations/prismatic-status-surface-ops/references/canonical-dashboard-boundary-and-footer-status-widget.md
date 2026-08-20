# Canonical Dashboard Boundary + Footer Status Widget

Session learning: when repairing Prismatic dashboard/status surfaces, never let a temporary health/status view replace the canonical operator dashboard.

## User correction that matters

Michael explicitly corrected the workflow after `/dashboard` was aliased to a full-page status surface:

> The “status” should just be a popover for a footer “system status” bar in the bottom right corner.

This is a first-class product boundary for Prismatic status work.

## Correct contract

- `/dashboard` is the canonical **Prismatic Operator Dashboard**.
- It should serve `prismatic/gateway/templates/dashboard.html` via the canonical `DASHBOARD_HTML` template path / `serve_dashboard()` pattern.
- System status belongs as an additive footer/bottom-right widget or popover inside the operator dashboard.
- A standalone status page must use a separate explicit route only if the user asks for it.
- Do not alias `/dashboard` to `/` just because `/dashboard` 404s; first inspect the route table and canonical dashboard template contract.

## Good implementation pattern

Gateway:

```python
_template_path = Path(__file__).parent / "templates" / "dashboard.html"
DASHBOARD_HTML = _template_path.read_text(encoding="utf-8") if _template_path.exists() else "<h1>Dashboard Template Not Found</h1>"

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML, status_code=200)

@app.get("/api/gateway/system-status")
async def system_status() -> dict[str, Any]:
    return _collect_system_status_summary()
```

Dashboard template:

- Add `#system-status-widget` fixed bottom-right.
- Add `#system-status-popover` hidden by default.
- Fetch `/api/gateway/system-status` on load and periodically.
- Keep the rest of the operator dashboard intact.

## Verification expectations

A targeted verifier should prove:

```text
dashboard_route=serves_canonical_DASHBOARD_HTML
full_page_status_takeover=absent
footer_status_popover=present
system_status_endpoint=responding_with_services
local_dashboard=200_operator_dashboard
public_dashboard=200_operator_dashboard
dashboard_not_found=false
```

Also use live browser proof on the public URL when authorized; Michael prefers live UI evidence over source/API-only claims.
