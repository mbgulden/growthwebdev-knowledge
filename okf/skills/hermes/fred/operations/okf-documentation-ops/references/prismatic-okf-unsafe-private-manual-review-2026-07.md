# Prismatic OKF unsafe/private manual-review package pattern — 2026-07

## When to use

Use after OKF treasure-hunt/archive work identifies `unsafe/private` candidates that must not be published, promoted, or cleaned up without human review.

## Pattern

1. Keep unsafe/private records out of public/current OKF docs.
2. Create a local-only JSON package, usually:

```text
/tmp/prismatic-okf-treasure-hunt/manifests/unsafe-private-manual-review-package.json
```

3. Optional local-only Markdown companion:

```text
/tmp/prismatic-okf-treasure-hunt/reports/unsafe-private-manual-review-package.md
```

4. Required JSON flags:

```json
{
  "scope": "unsafe-private-manual-review-package-only",
  "publish_or_promote_authorized": false,
  "cleanup_authorized": false,
  "manual_review_required": true
}
```

5. Each record should include only safe metadata:

- `review_id`
- `source_repo`
- `source_branch`
- short `source_head`
- `redacted_path` such as `[REDACTED_PATH_001]`
- broad `path_hint` with no slash/path-like content
- `content_sha256_prefix`
- `classification: unsafe/private`
- `recommendation: manual-review-only`
- `risk: high`
- allowed/disallowed next actions

## Markdown companion table

If making a Markdown companion, keep the table to exactly these seven columns:

```markdown
| Review ID | Source repo | Source branch | Source head prefix | Redacted path | Hash prefix | Recommended action |
|---|---|---|---|---|---|---|
```

Do not include raw paths or broad extra columns.

## Verification

Use a fresh `/tmp/hermes-verify-*` script and verify:

- package exists and parses;
- exactly expected unsafe/private records are present;
- publish/promotion/cleanup flags are all false;
- every record is `unsafe/private`, `manual-review-only`, `risk: high`;
- no raw content fields (`content`, `raw_content`, `body`, `text`, `markdown`, etc.);
- no raw path fields (`path`, `raw_path`, `full_path`, `source_path`);
- `redacted_path` matches `[REDACTED_PATH_###]`;
- `path_hint` contains no `/` or `\\`;
- no secret/private-key assignment patterns;
- durable quarantine record exists on the remote hub branch;
- no cleanup/deletion occurred;
- verifier script is removed.

Required wording:

```text
AD_HOC_VERIFICATION: PASS
scope: unsafe/private manual-review package only — no publish, no promotion, no cleanup, not full docs-suite green
cleanup=PASS removed /tmp/hermes-verify-xxxx.py
```

## Linear parking

After package verification, create a paused Linear task for manual review instead of continuing to work the sensitive set inline. Use labels like `agent:needs-human-review` and `dispatch:paused`; include local artifact paths, durable quarantine doc path, non-negotiable boundaries, and exit criteria. Do not mark it dispatch-ready.