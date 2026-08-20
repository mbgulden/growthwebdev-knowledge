# Skills Tab Mock-to-Live API Wiring

Session-derived reference for Prismatic Core skill distribution work.

## Symptom

The governance dashboard had a Skills tab, but it rendered hardcoded `mockSkills` rather than the real Prismatic Core skill registry. Core already had `prismatic.skills` CLI/local install primitives, but there were no gateway endpoints for the dashboard.

## Real API slice

Add gateway endpoints backed by `prismatic.skills`:

```text
GET  /api/skills
GET  /api/skills/{name}
POST /api/skills/{name}/install
POST /api/skills/{name}/uninstall
```

`GET /api/skills` should return a normalized card payload with:

```json
{
  "source": "prismatic.skills",
  "bundled_count": 0,
  "installed_count": 0,
  "skills": [
    {
      "id": "skill-name",
      "name": "skill-name",
      "version": "1.0.0",
      "description": "...",
      "category": "...",
      "labels": [],
      "author": "...",
      "installed": false,
      "status": "Available",
      "path": "..."
    }
  ]
}
```

## Dashboard contract

Replace hardcoded skills with:

```js
let skillsCache = [];
await renderSkillsView();
const res = await fetch("/api/skills");
```

Install/uninstall action route:

```js
fetch(`/api/skills/${encodeURIComponent(skillId)}/${action}`, { method: 'POST' })
```

Required UI states:

- Loading live skill registry
- Empty registry
- API error message
- Active vs Available badges

## Verification pattern

Use a `/tmp/hermes-verify-*.py` verifier. In API tests, isolate the user store:

```python
with tempfile.TemporaryDirectory(prefix='hermes-verify-core-skills-home-') as home:
    os.environ['HOME'] = home
    client = TestClient(app)
```

Exercise:

- list returns `source == "prismatic.skills"`
- info returns manifest
- install creates `$HOME/.prismatic/skills/<name>`
- duplicate install returns 409
- uninstall removes the directory
- unknown skill paths return 404
- dashboard HTML no longer contains `mockSkills` and does contain `/api/skills` fetch/action routes

Report as ad-hoc targeted verification, not full suite-green.