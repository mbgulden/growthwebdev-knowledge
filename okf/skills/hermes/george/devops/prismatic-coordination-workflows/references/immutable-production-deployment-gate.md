# Immutable production deployment gate

Use this reference after a Prismatic candidate has been independently accepted and merged, and Michael explicitly authorizes deployment/next steps. It captures the production-safe pattern from GRO-4368 without making that PR a standalone skill.

## Goal

Deploy the exact merged artifact without mutable checkout dependence, preserve rollback, avoid secret leakage, and prove public/browser/runtime behavior without overclaiming canonical suite green.

## Sequence

1. **Bind merge artifact first.** Record PR, merge commit, merge tree, parent order, changed paths, and immutable archive/reproduction proof before touching runtime.
2. **Prepare a standalone release checkout.** Create `/home/ubuntu/.prismatic/releases/<merge-commit>` from the exact object; ensure no `.git/objects/info/alternates`, `git fsck` passes, and `git status --porcelain` is empty.
3. **Create a commit-specific venv.** Use a new `/home/ubuntu/.prismatic/venvs/gateway-<short-commit>`; install non-editably from the release checkout; run `pip check`; bind installed module path/hash to the release source bytes.
4. **Preserve current runtime and state.** Capture current systemd drop-ins, active Nginx site bytes, rollback source, health status, and pre-activation SQLite/table counts. Do not activate until rollback artifacts exist and pass syntax checks.
5. **Create production config explicitly.** If the feature requires a registry/manifest, write it as a deployment artifact with strict permissions (for example `0600`) and validate it with the new installed package before systemd activation.
6. **Stage systemd before restart.** Install a higher-order drop-in that points WorkingDirectory/ExecStart/venv/env to the immutable release. Run `systemctl daemon-reload` and assert the effective unit binds to the release/venv before restart.
7. **Restart with automatic rollback.** On health/provenance/state-count/API failure, run the receipt-owned rollback. Prove rollback script syntax before activation.
8. **Sanitize provenance.** Never persist the full process environment; use a strict allowlist of non-secret keys and hash/version fields.
9. **Handle edge containment narrowly.** If Nginx/edge blocks new read-only routes, patch only exact read-only proxy locations needed by the deployed feature. Do not weaken mutation containment. Back up the active enabled site file and include restoration in rollback.
10. **Verify from multiple paths.** Prove local service health, local/edge route behavior, public API bytes, rendered dashboard/deep link, and mobile viewport geometry when UI is affected. If one verifier transport fails (for example urllib 403 while curl/browser pass), classify it as verifier transport and rerun with the successful transport rather than weakening the claim.
11. **Write a durable receipt.** Store a deployment receipt under `/home/ubuntu/.prismatic/deployments/<id>/DEPLOYMENT_RECEIPT.md` with hashes for release/drop-in/Nginx/registry/rollback/logs/screenshots, explicit non-claims, rollback path, and marker.
12. **Append handoff.** Add only a compact marker block to `PRISMATIC_CURRENT_HANDOFF.md` with receipt path/hash and production state. Do not rewrite prior handoff history.
13. **Final binding proof.** Run a disposable `/tmp/hermes-verify-*` script/test that asserts receipt hashes, active systemd WorkingDirectory, public API response, handoff marker, DB count preservation, Nginx syntax, rollback syntax, focused release tests, dashboard build check, compile/diff checks, and live service active. Keep the final log durable; clean only the disposable script.

## Proof packet shape

```text
RESULT=PASS|PARTIAL|BLOCKED
PR=<url>
MERGE_COMMIT=<sha>
MERGE_TREE=<sha>
RELEASE=<immutable checkout>
VENV=<commit-specific venv>
DROPIN=<systemd drop-in>
REGISTRY=<if any>
EDGE_CHANGE=<none|exact read-only routes>
PUBLIC_API=<PASS|BLOCKED + why>
BROWSER_PROOF=<PASS|BLOCKED + why>
MOBILE_PROOF=<PASS|not applicable|BLOCKED + why>
DB_COUNTS_PRESERVED=<true|false>
ROLLBACK=<path>
RECEIPT=<path>
AD_HOC_OR_CANONICAL=ad-hoc targeted deployment proof
NOT_CLAIMING=canonical full-suite green, GitHub CI execution, branch deletion, Linear mutation, consumer/watchdog enablement unless separately proven
MARKER=<deployment marker>
```

## Pitfalls

- Do not deploy from the mutable development/control checkout.
- Installed-package TestClient staging must run from a neutral directory with `PYTHONPATH` removed and module paths asserted under the commit-specific venv. If production already owns a WebSocket port, set the staging broadcaster port to `0` (OS-assigned ephemeral) instead of colliding with live runtime.
- For runtime registries/configs installed as `0600`, preserve the service user/group ownership (for example `ubuntu:ubuntu`). `0600 root:root` is unreadable to a non-root gateway and can turn otherwise valid Workspace APIs into `503`.
- A live authenticated dashboard is not proven by health/readiness alone. Verify a configured least-privilege principal exists, authenticated read APIs succeed locally/publicly, unsafe/admin operations remain denied, and no credential value enters logs, scripts, screenshots, or chat.
- Do not persist raw full process environments in receipts; they may contain secrets.
- Do not treat Browserbase/public verifier 403s as permission to weaken allowlists. First reproduce through local gateway/Nginx and identify whether the block is edge containment, IP allowlist, or verifier transport.
- Do not rely on screenshots alone for mobile proof; use CDP/DOM geometry assertions for overflow, visibility, and absence of path leaks.
- Do not claim public proof from local host-only checks. Separate local proof, edge proof, public API proof, and rendered browser proof.
