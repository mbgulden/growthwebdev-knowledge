# Dashboard main-tab live adapter restoration

Use this reference when the Prismatic governance dashboard routes/tabs return 200, but the default **Dashboard** tab still shows simulated or hardcoded operational data.

## Symptom

The backend tab surfaces can be restored while the default Dashboard tab still contains hardcoded JavaScript arrays and fake labels, for example:

```text
const mockAgents
const mockWorkspaces
const mockSignals
Completed UI mockup draft and layout updates
Creating rebase branches for GRO-671
Watcher daily backup completed successfully
Simulate Webhook Event
mockSignals.map
mockWorkspaces.map
```

This is a separate failure from missing route 404s or backend fallback payloads. Treat it as a live-UI truth issue: the page itself is still rendering simulated telemetry.

## Proven recovery pattern

1. Scan the dashboard template for hardcoded/mock main-tab data:

```bash
rg "mockAgents|mockWorkspaces|mockSignals|Completed UI mockup|Creating rebase|Watcher daily backup|Simulate Webhook Event|mockSignals\.map|mockWorkspaces\.map" prismatic/gateway/templates/dashboard.html
```

2. Compare against Kai/design branches before inventing a new contract:

```bash
git grep -n -E "agent_status|/api/gateway/agents/status|timeline|mockAgents|mockSignals" $(git for-each-ref --format='%(refname:short)' refs/remotes refs/heads | tr '\n' ' ') -- prismatic/gateway/templates/dashboard.html prismatic/gateway/server.py prismatic 2>/dev/null
```

3. Restore or wire the normalized live adapters:

```text
/api/gateway/agents/status      -> prismatic.agent_status.build_agent_status
/api/gateway/agents/{agent_id}  -> prismatic.agent_status.build_agent_detail
/api/gateway/timeline           -> prismatic.timeline.list_timeline
/events/recent                  -> fallback only when timeline has no items
/locks                          -> workspace summary, never static workspace mocks
```

The expected agent source is:

```text
run_records+agent_registry+queue_state+timeline+health_context
```

The expected timeline source is:

```text
prismatic.timeline
```

4. Rename test-only controls so they are visibly not production telemetry. In the worked case, `Simulate Webhook Event` became `Test Webhook Harness`.

5. Prefer honest empty states over fake fallbacks:

```text
No live operational timeline events recorded. No mock fallback rendered.
No active file locks. No mock workspace fallback rendered.
```

## Verification checklist

Use a temporary `/tmp/hermes-verify-*` script and clean it up in the same shell operation. Verify:

- current branch and HEAD match `origin/deploy-fresh`;
- worktree clean and gateway active;
- stale verifier/PR body files absent;
- changed paths exist and Python files compile;
- served dashboard HTML contains live fetches and test-harness label;
- served dashboard HTML/source do **not** contain the mock arrays or fake text;
- live routes return 200:

```text
/api/gateway/agents/status
/api/gateway/agents/<agent>
/api/gateway/timeline?limit=12
/events/recent?limit=12
/locks
/dashboard
```

- route payload sources are real:

```text
/api/gateway/agents/status -> run_records+agent_registry+queue_state+timeline+health_context
/api/gateway/timeline      -> prismatic.timeline
```

- browser DOM after async settle shows live EventBus/timeline activity and no old fake strings.

## Pitfalls

- Do not stop after backend tab routes are green. The default Dashboard tab may still be hardcoded.
- Do not treat `200` as proof of truth. Inspect the rendered DOM and source strings.
- Do not leave test tooling labeled as simulated production status.
- If browser console reports blank harness exceptions with no stack but DOM/API proof passes, report that caveat plainly rather than claiming console-perfect. Still investigate real message/stack if available.
