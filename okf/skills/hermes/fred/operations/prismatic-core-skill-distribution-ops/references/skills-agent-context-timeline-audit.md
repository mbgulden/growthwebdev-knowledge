# Skills + Agent Context Timeline Audit Pattern

Use this when wiring Prismatic Core skill distribution, the governance dashboard Skills tab, or agent-context install-doc behavior.

## Durable lesson

Skill system changes must be **audit-first** and **timeline-visible**. Do not patch dashboard buttons on top of stale assumptions. First audit the existing Core skill primitives and recent agent-owned work, then wire the smallest live API/dashboard layer around what already exists.

## Pre-change audit

Run these before changing skill distribution code:

```bash
git branch -a --list '*kai*' '*skill*' '*agent-context*'
git log --all --oneline --author='Kai' --since='90 days ago' -- prismatic/skills.py prismatic/gateway/server.py prismatic/gateway/templates/dashboard.html prismatic/agent_context.py tests
git log --all --oneline --grep='kai.*skill\|skill.*kai\|agent-context\|agent context\|skills tab' --regexp-ignore-case --since='90 days ago'
```

Interpretation:

- If relevant Kai/agent changes are present, inspect and integrate those first.
- If no relevant changes are present, preserve the existing `prismatic.skills` implementation and add gateway/dashboard/timeline wiring around it.

## Required audit events

Skill capability changes are not complete until `/api/timeline` shows them:

```text
POST /api/skills/{name}/install      -> SkillRegistry / Skill installed
POST /api/skills/{name}/uninstall    -> SkillRegistry / Skill uninstalled
POST /api/agent-context/install-doc  -> AgentContext / Agent context doc installed
```

The API response should include the `timeline_item` when possible, and the verifier should also fetch:

```text
GET /api/timeline?source=SkillRegistry
GET /api/timeline?source=AgentContext
```

## Dashboard contract

The Skills tab must not render hardcoded capability data:

```text
mockSkills absent
fetch("/api/skills") present
/api/skills/${encodeURIComponent(skillId)}/${action} present
toggleSkillInstall present
skills-grid present
```

Use loading/empty/error states rather than fake fallback cards.

## Isolated verification contract

Use a focused `/tmp/hermes-verify-*.py` script and report **ad-hoc targeted verification, not suite-green**.

Verifier checklist:

```text
changed paths exist
py_compile prismatic/agent_context.py, gateway server, tests
node --check extracted dashboard <script>
python -m pytest tests/test_gateway_skills_audit_api.py -q -o addopts=
set HOME to tempfile.TemporaryDirectory(prefix='hermes-verify-skills-home-')
set PRISMATIC_STATE_DIR to tempfile.TemporaryDirectory(prefix='hermes-verify-skills-state-')
GET /dashboard confirms no mockSkills and /api/skills present
GET /api/skills returns source=prismatic.skills and bundled_count >= 1
GET /api/skills/{name} works; unknown skill 404
POST install works and creates $HOME/.prismatic/skills/{name}
duplicate install returns 409
SkillRegistry timeline contains Skill installed
POST uninstall works and removes isolated skill dir
missing uninstall returns 404
SkillRegistry timeline contains Skill uninstalled
GET /api/agent-context and /api/agent-context/line work
POST /api/agent-context/install-doc preserves human content and adds managed block
missing install-doc path returns 400
AgentContext timeline contains Agent context doc installed
python -m prismatic.agent_context line/install-doc works
fresh venv + pip install --no-deps . + prismatic-agent-context line works
cleanup removes verifier and temp HOME/state/venv
```

## Live smoke pitfall

If live uvicorn is started with an isolated `HOME`, user-site packages may disappear from import resolution. Do **not** record that as a durable tool failure. Either use TestClient for the required verifier or, for live smoke only, preserve import resolution explicitly, e.g.:

```bash
HOME=/tmp/... PRISMATIC_STATE_DIR=/tmp/... PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages:/home/ubuntu/work/prismatic-engine \
  python3 -m uvicorn prismatic.gateway.server:app --host 127.0.0.1 --port 9126
```

The durable lesson is: isolate state mutation (`HOME`, `PRISMATIC_STATE_DIR`) while preserving Python dependency resolution for live smoke.
