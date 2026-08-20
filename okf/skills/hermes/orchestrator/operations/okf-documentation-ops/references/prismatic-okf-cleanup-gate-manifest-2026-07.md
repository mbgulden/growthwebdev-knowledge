# Prismatic OKF cleanup-gate manifest pattern — 2026-07

Use after canonical/current docs, archive/quarantine docs, standards/decisions, and repo-local breadcrumbs have landed and been post-merge verified.

## Trigger

The user asks to move from OKF treasure-hunt/archive work toward cleanup, but has not explicitly approved deletion of branches, refs, worktrees, local dirs, duplicate docs, or unsafe/private material.

## Core rule

Create a cleanup **gate manifest only**. Do not execute cleanup. The manifest is an approval surface, not permission to delete.

## Manifest path

```text
/tmp/prismatic-okf-treasure-hunt/manifests/final-cleanup-candidates.json
```

## Required top-level fields

```json
{
  "scope": "cleanup-gate-manifest-only",
  "cleanup_executed": false,
  "approval_required_before_any_cleanup": true,
  "source_manifests": [],
  "durable_evidence": [],
  "summary": {},
  "candidates": []
}
```

## Candidate requirements

Each candidate should include:

- `candidate_type`: `branch`, `ref`, `worktree`, `local-dir`, `duplicate-doc`, `manifest`, or `unsafe-private`
- `path_or_ref`
- `source_repo`, `source_branch`, `source_head`
- `concept_family`, `classification`, `content_sha256`
- `safe_after` evidence paths
- `risk`
- `recommended_action`
- `requires_manual_approval: true`
- `approval_reason`
- `notes`

## Classification defaults

| Candidate | Risk | Recommended action | Rule |
|---|---|---|---|
| Branch/ref | high | ask-human | Never mark branch/ref deletion safe automatically. |
| Worktree/local dir | medium/high | ask-human or delete-local-only | Local deletion still requires explicit approval and provenance check. |
| Exact duplicate docs | medium | archive-only | Duplicate family recorded does not itself authorize deletion. |
| Hidden useful docs | high | ask-human/keep | Confirm promoted or archived before cleanup. |
| Historical docs | medium | archive-only | Preserve archive/provenance unless approved. |
| Unsafe/private | high | manual-review-only | Redacted metadata only; no raw paths/content. |

## Unsafe/private handling

For unsafe/private candidates:

- include exactly redacted markers like `[REDACTED_PATH_001]`;
- keep only safe hash prefixes if needed;
- do not include raw path, raw title, raw content, secrets, private text, or sensitive identifiers;
- set `recommended_action: manual-review-only`;
- set `requires_manual_approval: true`.

## Verification

Use a fresh tempfile verifier:

```python
tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)
```

Verify:

1. manifest exists and parses;
2. `cleanup_executed is False`;
3. `approval_required_before_any_cleanup is True`;
4. every candidate has required fields;
5. every candidate requires manual approval;
6. branch/ref candidates are high-risk and ask-human;
7. unsafe/private candidates are high-risk/manual-review-only/redacted;
8. no secret/private-key assignment patterns appear;
9. durable evidence exists on remote branches, not dirty local checkouts;
10. retained source manifests still exist;
11. no deletion occurred;
12. verifier script is removed.

Expected language:

```text
AD_HOC_VERIFICATION: PASS
scope: OKF cleanup-gate manifest only — no cleanup executed, not full docs-suite green
cleanup=PASS removed /tmp/hermes-verify-xxxx.py
```

## Reporting

Report counts by candidate type and recommended action. State clearly that cleanup safety remains yellow/blocked and every candidate still requires manual approval.
