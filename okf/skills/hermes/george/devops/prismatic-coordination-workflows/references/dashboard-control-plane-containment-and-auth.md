# Dashboard control-plane containment and durable auth hardening

Use when a Prismatic readiness/security audit finds the dashboard/gateway has real mutation or command-execution endpoints reachable before a source-owned auth/RBAC layer is merged and deployed.

## Trigger signals

- Gateway binds to `0.0.0.0:<port>` while Nginx/Cloudflare/Tailscale/LAN can reach it.
- Dashboard/API routes expose real `POST`/`PUT`/`PATCH`/`DELETE` effects, queue mutations, plugin/policy changes, quota edits, native-cron run/delete, or subprocess-backed commands.
- Auth middleware exists but only covers selected observability paths, not the canonical dashboard/control routes.
- Dashboard looks like a control plane but mixes real controls with no-op/dry-run/readiness surfaces.

## Emergency operational containment sequence

1. **Classify ingress before editing.** Read service/unit/proxy/tunnel configuration and prove whether Nginx/Cloudflare routes use `localhost`/loopback upstreams. If they do, loopback binding can preserve proxied reads while removing direct LAN/Tailscale/container access.
2. **Contain latent autonomous merge/deploy authority first when present.** If a legacy merge/deploy daemon is active or enabled, stop/disable it without recreating its missing worktree or state paths. Preserve source/unit/state into a restricted deployment bundle and hash every artifact before further source work.
3. **Bind the gateway to loopback.** Update the systemd/env configuration so the gateway listens on `127.0.0.1:<port>`, then reload/restart only the relevant service after validating staged units/configs.
4. **Fail closed at the public proxy for mutations.** Add a central Nginx/server-level guard that blocks public non-read methods while preserving explicitly required ingress such as `/webhooks/`. Prefer one `map`/server guard over duplicated fragile per-location rules.
5. **Verify direct and proxied paths separately.** Prove local health, Nginx/proxied read health, direct LAN/Tailscale/container-interface refusal, public non-read `403`, and webhook exception configuration. Do not replay real webhooks or dashboard mutations unless explicitly authorized.
6. **Preserve rollback packet.** Store pre/post gateway unit, Nginx config, site config, receipt, hashes, and rollback instructions in a restricted deployment bundle.
7. **Update durable handoff/control state.** Record containment as temporary operational mitigation, not source repair or production-safe control-plane completion.

## Durable source-hardening slice

After emergency containment, admit one cap-1 source producer for central control auth/RBAC. Keep it source-only until independent review and release/deploy authorization.

Recommended bounded contract:

- central fail-closed auth module;
- external hash-only credential file, no plaintext secrets in repo/logs;
- Bearer-header auth only;
- roles such as `operator`, `approver`, `executor`;
- native-cron command execution restricted to executor role;
- webhook signature boundary preserved and not converted to dashboard auth;
- request actor/role metadata available to mutation handlers;
- secret-safe `401`/`403` responses;
- CSRF-safe mutation authorization or equivalent non-cookie bearer-only posture;
- docs explaining operational setup and nonclaims.

Suggested <=4 path scope:

```text
prismatic/gateway/control_auth.py
prismatic/gateway/server.py
tests/test_dashboard_control_auth.py
docs/dashboard-control-auth.md
```

If existing gateway `TestClient(server.app)` suites are expected to remain green after fail-closed auth, allow a narrowly justified test-harness expansion such as `tests/conftest.py` to inject explicit non-production test credentials/authorization. Record that expansion in the task contract and invalidate the old task digest/review evidence. Do **not** add a production bypass.

Role-classification review targets:

- ordinary dashboard/API mutations → `operator`;
- PR approval/update approval surfaces such as `/pr-approval`, `/pr-create-approved`, and operator-action approval routes → `approver`;
- command execution/native-cron run/delete/real executor paths → `executor`;
- public webhooks stay outside dashboard bearer auth and keep their own signature boundary.

After every repair commit, preserve the lineage and require a fresh exact-head review; earlier review/CI belongs to the old head. Add adversarial route-policy probes over actual mutation decorators, not only synthetic test routes, and watch for overmatching route fragments that can misclassify dry-run/read-only persisted previews as approval endpoints.

## Verification packet

```text
COMMAND=<grouped systemctl/ss/curl/config/hash/state verifier>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=gateway containment + proxy mutation guard + active source-auth task state
AD_HOC_OR_CANONICAL=ad-hoc operational
NOT_CLAIMING=source auth merged; source deployed; dashboard fully production-safe; webhook replay; live cursor repair
MARKER=PRISMATIC_CONTAINMENT_AND_PLAN_START_AD_HOC_OK
```

## Pitfalls

- Loopback binding removes direct network exposure but does not secure a public Cloudflare/Nginx proxy by itself; public non-read methods need their own guard until source auth is live.
- A rendered dashboard with real data adapters is not automatically a safe control plane if public mutation routes bypass central auth.
- Do not treat an enabled but currently wedged merge daemon as harmless. If its code has autonomous candidate application, fast-forward merge, deployment, or rollback authority, it is latent authority and should be explicitly disabled before recreating any missing paths.
- Some public probes may return `403` to Python’s default user agent at the CDN edge. If the purpose is verifying application/proxy behavior, retry with a browser-like User-Agent and report that as a verifier detail, not a product claim.
- Preserve public webhook ingress structurally but do not live-replay webhooks unless separately authorized.
