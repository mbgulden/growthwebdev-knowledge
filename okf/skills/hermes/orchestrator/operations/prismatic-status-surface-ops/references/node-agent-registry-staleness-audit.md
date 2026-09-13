# Node/Agent Registry Staleness Audit Pattern

Use when auditing the Prismatic gateway's agent/node registry for stale or offline registrations, or when Michael asks "are all nodes healthy?" / "what's on the dashboard?"

## Core pattern

1. **Fetch the agent list:**

```bash
curl -s http://localhost:9000/api/agents | python3 -c "
import sys, json
from datetime import datetime, timezone
d = json.load(sys.stdin)
agents = d.get('agents', {})
now = datetime.now(timezone.utc)
for name, a in sorted(agents.items()):
    ls = a.get('last_seen', '')
    status = a.get('status', '?')
    source = a.get('source', '?')
    model = a.get('active_model', '?')[:25]
    if ls:
        last = datetime.fromisoformat(ls.replace('Z', '+00:00'))
        age_min = (now - last).total_seconds() / 60
        flag = ' STALE' if age_min > 10 else ''
        print(f'{a.get(\"name\",\"?\"):30s} {status:10s} {age_min:6.0f}m  {source}{flag}')
    else:
        print(f'{a.get(\"name\",\"?\"):30s} {status:10s}   N/A   {source}')
print(f'Total: {len(agents)}')
"
```

2. **Classify by source type:**
   - `Profile (...)` — live Hermes profile agents. These should have fresh `last_seen` (seconds ago). If stale, the profile gateway is down.
   - `Dynamic Registration (Discovered Node)` — external worker nodes that self-registered. These are expected to go stale when the node machine goes offline. **Do not treat stale dynamic registrations as a current incident** unless the node was recently online (check `last_seen` date vs today).
   - `Dynamic Registration (prismatic-engine)` / `Dynamic Registration (Lightbringer ...)` — specific external tool nodes. Same rule: staleness is expected when the host machine is off.

3. **Check `last_seen` freshness threshold:**
   - Profile agents: > 5 min stale = gateway for that profile is likely down. Investigate.
   - Dynamic registrations: staleness is normal for nodes that were historically registered but are no longer active. These accumulate over time and are a **cleanup candidate**, not a health alert.

4. **Cross-check with `tailscale status`** for external nodes (Lightbringer, k3s nodes, etc.) to confirm whether the underlying machine is actually offline vs. just not heartbeating to the gateway:

```bash
tailscale status 2>/dev/null | grep -iE 'offline|idle'
```

5. **Check active work claims:**

```bash
cat /home/ubuntu/.antigravity/active_work.json
```

If `claims` is empty, no work is in flight — a fully idle fleet is not an incident.

## Reporting shape

Report in three tiers, not a flat list of 58 agents:

```text
Healthy (N profile agents, last_seen < 1 min): [names or count]
Stale-dynamic (N registrations, expected offline): [count, oldest last_seen]
Active work: [claims count / "none"]
```

Flag only genuinely new staleness (profile agents that were fresh yesterday but stale today, or a dynamic node that was online in the last 24h and is now silent). Historical stale registrations (Aug/early-Sep last_seen on a Sep-12 audit) are cleanup candidates, not incidents.

## Pitfalls

- **Do not alarm on stale dynamic registrations without checking recency.** A `Discovered Node` agent with `last_seen` from 3 weeks ago that was already offline before the audit is not a new drop. Report it as "stale, pre-existing" and suggest a registry sweep only if Michael wants cleanup.
- **The gateway port is 9000, not 8787.** Earlier documentation or assumptions may reference the wrong port. Confirm with `ss -tlnp | grep prismatic` or the running process cmdline.
- **`/api/agents` is the canonical registry endpoint.** `/api/nodes`, `/api/node-registry`, `/api/registry` all 404. `/api/workspaces` returns the workspace list (4 workspaces: System Root, User Home, Work Repositories, Prismatic Engine).
- **The `services` entry** (status `Unknown`, no `last_seen`) is a placeholder, not a real agent. Ignore it in counts.
- **Tailscale offline ≠ gateway stale.** A Tailscale node can be offline for weeks (core-brain: 171d, k3s-node-233: 137d, k3s-node-234: 93d) without affecting the gateway registry. Only flag as new if the Tailscale status changed recently.
