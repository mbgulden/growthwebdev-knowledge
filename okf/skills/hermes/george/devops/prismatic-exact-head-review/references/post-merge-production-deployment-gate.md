# Post-merge production deployment gate

After an exact-head accepted Prismatic candidate is merged, deployment is a separate authorization and proof gate. This reference points to the fuller class runbook in `prismatic-coordination-workflows/references/immutable-production-deployment-gate.md` and summarizes the acceptance-critical checks.

## Required separation

- `merged` does not mean `deployed`.
- Deployment requires Michael authorization or an explicit prompt granting that policy.
- Do not delete branches, mutate Linear, enable consumers/watchdogs, or claim canonical full-suite green unless separately authorized and proven.

## Minimum production proof

```text
MERGE_COMMIT=<sha>
MERGE_TREE=<sha>
RELEASE=<standalone immutable checkout>
RELEASE_FSCK=PASS
RELEASE_NO_ALTERNATES=true
VENV=<commit-specific venv>
INSTALLED_MODULE_PATH=<venv site-packages path>
INSTALLED_HASH_MATCH=true
SYSTEMD_WORKING_DIRECTORY=<release path>
ROLLBACK=<receipt-owned rollback script>
DB_COUNTS_PRESERVED=true
LOCAL_HEALTH=PASS
EDGE_ROUTES=PASS|not applicable
PUBLIC_API=PASS|not applicable
BROWSER_PROOF=PASS|not applicable
MOBILE_PROOF=PASS|not applicable
RECEIPT=<deployment receipt path>
NOT_CLAIMING=<explicit non-claims>
```

## Durable lessons from GRO-4368

- Use a standalone release checkout and commit-specific venv; never deploy from a mutable dev/control checkout.
- If a new feature needs production config, create a strict-permission registry/manifest and validate it with the installed package before activation.
- Back up the exact active Nginx enabled-site file before edge changes; rollback must restore both gateway and edge containment.
- Patch only exact read-only proxy routes needed for public proof; do not weaken mutation containment.
- Do not persist full process environments in receipts; allowlist non-secret provenance only.
- Separate local service proof, Nginx/edge proof, public API proof, rendered browser proof, and mobile viewport geometry. If a verifier transport fails but curl/browser pass, fix the verifier transport and rerun the final proof rather than weakening the deployment claim.
- Store a deployment receipt with hashes for release/drop-in/Nginx/registry/rollback/logs/screenshots and append only a compact marker block to the handoff.
