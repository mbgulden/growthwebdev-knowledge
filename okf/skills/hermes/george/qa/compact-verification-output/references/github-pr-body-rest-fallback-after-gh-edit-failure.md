# GitHub PR body update fallback after `gh pr edit` GraphQL failure

## When this applies

During Prismatic proof-packet or PR-body closeout, `gh pr edit --body-file ...` can fail before mutating the PR body because GitHub's CLI GraphQL path requests deprecated Projects-classic fields, e.g.:

```text
GraphQL: Projects (classic) is being deprecated ... (repository.pullRequest.projectCards)
```

This is a CLI/API-shape failure, not proof that the PR body is unchanged or updated. Do not assume either state from the failed command.

## Safe fallback

Use the REST pull-request endpoint with JSON generated from the already-written Markdown body file:

```bash
python3 -c 'import json; from pathlib import Path; Path("/tmp/pr-body-patch.json").write_text(json.dumps({"body":Path("/tmp/pr-body.md").read_text()}))'
gh api -X PATCH repos/OWNER/REPO/pulls/PR_NUMBER --input /tmp/pr-body-patch.json >/tmp/pr-body-patch-response.json
gh api repos/OWNER/REPO/pulls/PR_NUMBER > /tmp/pr-body-readback.json
python3 - <<'PY'
import json
p=json.load(open('/tmp/pr-body-readback.json'))
body=p.get('body') or ''
assert p['state']=='open'
assert not p['merged']
assert p['head']['sha']=='EXPECTED_HEAD'
for marker in ('EXPECTED_TREE', 'EXPECTED_REVIEW_ID', 'EXPECTED_TEST_SUMMARY'):
    assert marker in body
print('PR_BODY_REST_PATCH_READBACK_OK')
PY
```

## Reporting boundary

Report this as PR-body/readback verification only. It does not imply review acceptance, merge, deployment, or production proof.

## Pitfalls

- Do not retry `gh pr edit` in a loop after the Projects-classic GraphQL error; switch endpoint shape.
- Do not inline Markdown containing backticks, `$VARS`, or angle brackets into shell arguments. Keep the body in a file and JSON-encode from that file.
- Always re-read the PR after the PATCH and assert head SHA plus marker text survived.
