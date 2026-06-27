---
type: Architecture Decision Record
title: Approval, versioning, and rollback for PWP site changes
project: prismatic-web-plugin
resource: okf/projects/prismatic-web-plugin/decisions/2026-06-26-pwp-approval-versioning-rollback.md
tags: [adr, pwp, approval, versioning, rollback, deploy-history, evidence, astro, emdash, cloudflare]
timestamp: 2026-06-26T23:55:00Z
linear_issue: GRO-2505
git_repo: mbgulden/prismatic-web-plugin
branch: ned/GRO-2505
status: accepted
verified_by: ned
extends:
  - okf/projects/prismatic-web-plugin/decisions/2026-06-26-astro-emdash-pwp-standard.md
---

# ADR: Approval, versioning, and rollback for PWP site changes

## Decision

The Prismatic Web Plugin owns a **durable approval/versioning/rollback kernel** that every generated site must use, not an ad-hoc "deploy and pray" path. The kernel exposes a small library + CLI:

```text
prismatic_web_plugin.approval
  propose_change    → ApprovalRequest (pending)         [persisted]
  approve_request   → ApprovalRequest (approved)
  reject_request    → ApprovalRequest (rejected)
  block_production_deploy(request, policy) → ProductionBlock(blocked, reason)
  DeployRecord.publish(workspace, request, target, url, actor, evidence_path)
  write_evidence(workspace, request, deploy_target, deploy_url, linear_issue_id, okf_paths)
  rollback_to(workspace, style_guide_version, content_model_version)
```

The kernel's defaults:

- **Production deploy is blocked unless the current `ApprovalRequest` is `APPROVED`.**
- **Staging deploys do not require approval** by default (configurable via `ApprovalPolicy`).
- **Rejected requests are always blocked** at staging and production.
- **Every deploy (staging, production, rollback) is appended to `history/deploy_history.json`.**
- **Every deploy writes evidence to `evidence/<linear-issue>-<target>.md`** linking to Linear + OKF.
- **Rollback restores the snapshot's `style_guide.json` and `content_model.json` from the paired state file** and records a `rollback` entry in deploy history.

## Why now

GRO-2491 shipped the Astro + EmDash site kernel (the "what"), but its deploy path was implicit: build, then `wrangler deploy`, then hope. That left three gaps called out explicitly in GRO-2505:

1. No way to block a production deploy until a human (client or account owner) signs off.
2. No way to roll back a bad change to a known-good previous version of the site, style guide, or content model.
3. No automatic evidence trail linking a deploy back to the Linear issue and the OKF decision that authorized it.

Without those, a "client-approved direction" can be silently overwritten by the next agent run. The ADR for the Astro+EmDash standard (2026-06-26-astro-emdash-pwp-standard.md) explicitly listed this slice as the next deliverable:

> `ingest → synthesize → distill → scaffold Astro+EmDash site → staging deploy → approval → production deploy`

GRO-2505 builds the `staging deploy → approval → production deploy` part. GRO-2500 (existing-site importer) feeds into this pipeline; PWP-I13 ensures that what 2500 ingests can also be safely evolved.

## What ships in `ned/GRO-2505`

### Library

```python
from prismatic_web_plugin.approval import (
    ApprovalRequest, ApprovalState, ApprovalPolicy,
    DeployRecord, DeployTarget, VersionSnapshot,
    ProductionBlock, RollbackResult, EvidenceRecord,
    propose_change, approve_request, reject_request,
    block_production_deploy, rollback_to, write_evidence,
    list_deploy_history,
    compute_style_guide_version, compute_content_model_version,
    persist_snapshot_with_state,
)
```

### CLI

```bash
PYTHONPATH=src python3 -m prismatic_web_plugin.approval \
  propose ./workspace \
    --client-slug valkyrie-arms-training \
    --summary "Update hero headline + accent color" \
    --staging-url https://staging-valkyrie.pwp.dev/ \
    --file src/data/site.json \
    --file src/pages/index.astro \
    --requested-by michael@gulden.io

PYTHONPATH=src python3 -m prismatic_web_plugin.approval approve \
    ./workspace --approver client@valkyrie.com --notes "Approved"

PYTHONPATH=src python3 -m prismatic_web_plugin.approval rollback \
    ./workspace \
    --style-guide-version 7d3c... \
    --content-model-version a91f...

PYTHONPATH=src python3 -m prismatic_web_plugin.approval history ./workspace
```

### Generated-site wiring

Every site produced by `scaffold_astro_emdash_site` now carries:

- `pwp-approval.json` at the project root: client slug, style guide version, content model version, approval state, staging preview URL placeholder, rollback command, OKF evidence paths.
- `pwpApproval` block inside `src/data/site.json` so the running Astro site can read its own deploy state.
- The seed `rollback_command` is a runnable `python3 -m prismatic_web_plugin.approval rollback` invocation against the current versions.

## Acceptance criteria (from GRO-2505)

| Criterion | Where it lives | Verified by |
|---|---|---|
| Production deploy is blocked without approval | `block_production_deploy` + `ApprovalPolicy.default` | `test_pending_request_blocks_production_deploy_by_default`, `test_approved_request_unblocks_production_deploy`, `test_reject_request_blocks_production_deploy` |
| Rollback can restore previous site/style guide/content model version | `VersionSnapshot.persist(..., style_guide=..., content_model=...)` + `rollback_to` | `test_rollback_restores_previous_style_guide_and_content_model` |
| Evidence is written automatically | `write_evidence` (called from `DeployRecord.publish`) | `test_write_evidence_persists_okf_and_linear_metadata`, `test_deploy_history_records_staging_and_production_with_evidence` |

| "Must include" requirement | Where it lives |
|---|---|
| staging preview URL | `ApprovalRequest.staging_preview_url`, `pwp-approval.json.staging_preview_url` |
| approval metadata | `ApprovalRequest.approved_by / approved_at / notes`, `pwpApproval.approvalState` |
| style guide/content model version snapshot | `VersionSnapshot` + `compute_style_guide_version` / `compute_content_model_version` |
| deploy history | `history/deploy_history.json` (append-only `DeployRecord` list) |
| rollback command/path | `pwp-approval.json.rollback_command` + `rollback_to` + the `rollback` CLI subcommand |
| OKF/Linear evidence on publish | `evidence/<linear-issue>-<target>.md` produced by `write_evidence` |

## Test coverage

```
PYTHONPATH=src python3 -m pytest -q
→ 139 passed in 2.69s   (was 122 before GRO-2505; +17 new tests)
```

New test files:

- `tests/test_approval.py` — 15 tests covering the kernel
- `tests/test_astro_emdash.py` — 2 new tests covering the scaffold wiring

## Integration with existing PWP work

- Builds on the Astro+EmDash site kernel from GRO-2491 (commit `87072c8`).
- Pairs with GRO-2500 (existing-site importer/classifier): importer output seeds a workspace; approval kernel governs every change to that workspace.
- Honest scope boundary: this kernel **does not** call the Cloudflare API or the Linear API itself. Those calls are made by the builder/orchestrator at the deploy boundary, which is the right place to put API-key-bearing code. The kernel is the data shape and gate logic; the builder is the network boundary.

## Consequences

### Positive

- Every generated client site is *deployable but not deployable to production* without an explicit approval decision.
- Every deploy is auditable: history shows what happened, evidence files show why.
- Rollback is a one-liner: `python3 -m prismatic_web_plugin.approval rollback ./workspace --style-guide-version X --content-model-version Y`.
- The same kernel works for any PWP client (Valkyrie, Meridian, ActiveOahu, future sites) — no per-site custom deploy logic.

### Tradeoffs

- The kernel is local-first by design; the builder must wire its CF API client and Linear client to call into it.
- Workspace layout is conventional (`history/`, `evidence/`, `current_request.json`, `style_guide.json`, `content_model.json`) — other agents touching the workspace must respect those paths.
- Version hashing is content-only (sha256 of canonical JSON). Two different style guides that happen to render the same effective look will collide. That's acceptable for human-edited content; if PWP later needs perceptual hashing, this is the layer to extend.

## Next slice

- Wire the builder (`prismatic_web_plugin.builder`) to call `block_production_deploy` before any CF Pages publish, and `write_evidence` after.
- Add a CF Pages deploy record fixture (deploy URL + commit SHA → `history/deploy_history.json`) so `rollback_to` can also point Cloudflare at the previous deployment.
- Optional: add a small HTTP server that exposes `history/`, `evidence/`, and `pwp-approval.json` for the client to read.