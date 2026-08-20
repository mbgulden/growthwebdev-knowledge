# Telegram lane dispatch bridge — 2026-07-19

Use this reference when Prismatic durable assigned-agent dispatch is not ready yet, but Michael wants George to coordinate Kai/Fred through Telegram groups without creating branch/worktree mess.

## Pattern

Temporary bridge:

```text
George watcher / live state check
→ George writes bounded Kai/Fred prompt artifacts
→ George sends prompt to lane-specific Telegram group
→ Kai/Fred reply with compact proof packet
→ George verifies PR/runtime/API/dashboard claims
→ George recommends next slice or merge-readiness
```

Future replacement:

```text
Prismatic event
→ durable assigned-agent queue
→ resolver/preflight
→ context pack
→ exact agent wake
→ completed-work packet
→ George review/writeback
```

## Group layout

Prefer separate lane groups, not one all-agent room:

| Lane | Purpose |
|---|---|
| Prismatic Kai | Golden-path implementation spine, valid completed-work/operator loop. |
| Prismatic Fred | Adjacent hardening, invalid packet repair, dashboard/operator support. |
| George/Michael DM or control room | Merge recommendations, blockers, cross-lane status. |

Current session group targets:

```text
Kai lane:  telegram:-5338154051  (Prismatic Kai)
Fred lane: telegram:-5167970174  (Prismatic Fred)
```

## Hermes Telegram inbound setup

Sending with `hermes send --to telegram:<chat_id>` proves only outbound/write access. Inbound replies require:

1. Telegram BotFather group privacy off for each bot that must read group messages.
2. Group chat IDs listed in the corresponding profile's `telegram.allowed_chats`.
3. Gateway restart/reload after config change.
4. If privacy was changed after adding the bot, remove/re-add the bot to the group if messages still do not arrive.

Commands used in this session:

```bash
hermes --profile george config set telegram.allowed_chats '8190664947,8424997958,-5106332713,-5338154051,-5167970174'
hermes --profile kai config set telegram.allowed_chats '8190664947,8424997958,-5106332713,-5338154051'
hermes --profile fred config set telegram.allowed_chats '8190664947,-5106332713,-5167970174'
```

## Gateway process/service notes

Hermes may refuse `gateway restart` from inside a running gateway session to prevent killing the active command. Workarounds:

- restart from an external shell when possible;
- for temporary foreground replacement: `hermes --profile <profile> gateway run --replace`;
- for durability: install systemd services and verify `active` + `enabled`.

Kai/Fred service pattern:

```bash
sudo /home/ubuntu/.local/bin/hermes --profile kai gateway install --system --run-as-user ubuntu --force
# If installer resolves the wrong profile for another bot, inspect `systemctl cat` and write/fix the systemd unit explicitly.
systemctl is-active hermes-gateway-kai.service hermes-gateway-fred.service
systemctl is-enabled hermes-gateway-kai.service hermes-gateway-fred.service
```

Pitfall from this session: installing Fred under sudo unexpectedly produced `hermes-gateway-orchestrator.service`; remove mistaken units and create/enable `hermes-gateway-fred.service` explicitly if needed. Also kill old manual `gateway run --replace` processes before expecting the service to start cleanly, because the service exits when it sees an existing gateway PID.

## Prompt dispatch discipline

Before dispatching prompts:

1. Live-check PR/main/runtime/service/API state.
2. Create `.md` prompt artifacts with exact marker, scope, forbidden side effects, OKF table, and return-packet shape.
3. Verify prompt artifacts with a temporary `/tmp/hermes-verify-*` script and no-secret scan.
4. Send to the lane group with a subject and `MEDIA:/absolute/path.md`.
5. Do not claim work is done until the target agent returns proof and George independently verifies.

Example targets:

```bash
hermes send --to telegram:-5338154051 --subject 'KAI DISPATCH — ONE_AGENT_OPERATOR_VERIFICATION_LOOP_OK' 'Kai, please take this Prismatic lane task. Full prompt attached. Return the required compact proof packet in this group. MEDIA:/path/to/kai-prompt.md'
hermes send --to telegram:-5167970174 --subject 'FRED DISPATCH — INVALID_PACKET_REPAIR_QUEUE_OK' 'Fred, please take this Prismatic lane task. Full prompt attached. Return the required compact proof packet in this group. MEDIA:/path/to/fred-prompt.md'
```

## Authority boundary

George may proactively:

- read repo/runtime/PR/API state;
- write and send Kai/Fred prompts;
- run prompt/report verification;
- flag stale PRs and side-effect risk;
- recommend merge order.

George must wait for Michael before:

- merging PRs;
- production deploys/restarts beyond an authorized closeout;
- real Linear/GitHub side effects;
- bulk/autopilot dispatch;
- closing/deleting PRs.
