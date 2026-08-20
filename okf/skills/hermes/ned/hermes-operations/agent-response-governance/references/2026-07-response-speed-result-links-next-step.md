# 2026-07 conversation: response speed, result links, and golden-path next steps

## Trigger signals
Michael raised first-class workflow/style corrections:

- Responses were too slow for simple asks because agents over-used tools and verification.
- Verification output often failed to make the actual result clear, causing an extra ask and another long wait.
- Final product links were missing or buried under procedural jargon.
- Completed work should always include a **Next Step** aligned with the specific project/task/goal's golden thread/golden path.
- In YOLO mode, agents should keep executing along the safe next-step path rather than stopping complacently after one increment.

## Durable lessons

### Fast path vs deep path
Use a fast/simple path for conceptual, editorial, or advisory requests: answer first and avoid tool fan-out unless live state is required.

Use a deep/verified path for build/fix/deploy/live-system tasks: actually inspect, execute, and verify before claiming completion.

### Final report shape
Lead with status and result links. Then concise changes and scoped verification evidence. End with a golden-path Next Step.

### Cross-profile rollout pattern
For durable behavior preferences across Hermes profiles:

1. Write a concise declarative preference to each profile's `memories/USER.md`.
2. Back up existing memory files before editing.
3. Verify every detected profile contains the new entry.
4. Explain session-refresh semantics: new sessions pick up changes; existing warm sessions may need `/new` or gateway restart.

### Safe gateway refresh pattern
When asked to proceed with the next step after bulk preference rollout:

1. Discover active Hermes gateway services.
2. Restart only affected active profile gateways, avoiding unnecessary broad restarts.
3. If the current gateway cannot be restarted from inside itself, use an outside process such as a systemd transient unit/timer.
4. Verify services are active and report process start times or equivalent concrete evidence.
5. Schedule a follow-up verification if the current profile restart will interrupt the active session.

## Anti-patterns to avoid

- Long procedural summaries with no final link.
- Saying “updated” without pointing to the thing Michael can inspect.
- Running heavyweight verification for simple conceptual/editorial work.
- Treating “Next Step” as generic boilerplate instead of aligning it to the goal's golden path.
- Stopping after one increment when YOLO mode explicitly authorizes safe continued execution.
