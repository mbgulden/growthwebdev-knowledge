# Live dashboard file-serving architecture — 2026-07-31

Worked session: when Michael asked for a clickable link to the Review/Merge
Factory V1 OKF on the live Prismatic dashboard, the file discovery took
several iterations because the obvious path was wrong. This reference
captures the final recipe and the four pitfalls hit along the way.

## The setup

- **Target URL:** `https://prismatic.growthwebdev.com` (canonical live
  Prismatic Engine governance/control-plane dashboard).
- **Goal:** Make `state/okf-review-factory-v1.md` (43.8KB, 772 lines)
  browseable as a clickable link in the dashboard.
- **Constraint:** Don't restart the George gateway without authorization
  (interrupts an active agent session).

## The wrong-path trap (don't fabricate URLs)

First failure mode: when Michael asked for a clickable link, the
agent defaulted to "there is no public clickable URL for that local file"
and offered five alternatives (code-server, public IP, paste inline, push
to GitHub, terminal `cat`). Michael redirected: *"You can link it to my
workspace tree prismatic engine dashboard remember? ... That Hermes plugin
is defunct."*

The lesson: **when Michael names a specific system, probe it first.**
Don't declare a thing unavailable based on memory of what existed two
turns ago. `curl https://prismatic.growthwebdev.com/api/workspaces`
takes 0.4 seconds and confirms whether the system is live, what its
workspace_id is, and what its serving paths are.

## The four candidate roots

After probing, the workspace-tree API exposes a file browser. The
gateway plugin auto-discovers workspaces from `/home/ubuntu/work/`, but
the live API serves from a pinned release directory. The four
candidate paths and their actual contents:

| Path | File count | Served? |
|---|---|---|
| `/home/ubuntu/.prismatic/releases/b5f474e6.../docs/` | 81 | **YES — exact match** |
| `/home/ubuntu/.prismatic/repos/prismatic-engine-control/docs/` | 81+1 (after copy) | No (one-file diff) |
| `/home/ubuntu/.prismatic/versions/v0.1.0-ac48b21/docs/` | 26+1 | No (25 diff) |
| `/home/ubuntu/work/prismatic-engine/docs/` | 9+1 | No (3 diff) |

The release dir at `b5f474e6` (pre-PR-382 SHA) matches the API output
exactly: 81 files, identical filenames, identical sizes (verified via
`stat -c '%s'` against the API's reported size for `okf-evidence-map.md`
— both 13751 bytes).

## The size-fingerprint recipe

When you suspect the served path is one of several candidates, fingerprint
a known file:

```bash
# 1. Pick a file you know is in the API
KNOWN=docs/okf-evidence-map.md

# 2. Get the API's reported size
API_SIZE=$(curl -s "https://prismatic.growthwebdev.com/api/workspace-tree/preview?workspace_id=<id>&path=$KNOWN" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['size'])")

# 3. Stat each candidate root until sizes match
for p in \
    /home/ubuntu/.prismatic/releases/*/docs/ \
    /home/ubuntu/.prismatic/repos/prismatic-engine-control/docs/ \
    /home/ubuntu/.prismatic/versions/*/docs/ \
    /home/ubuntu/work/prismatic-engine/docs/; do
    if [ -f "$p$KNOWN" ]; then
        local_size=$(stat -c '%s' "$p$KNOWN")
        [ "$local_size" = "$API_SIZE" ] && echo "MATCH: $p"
    fi
done
```

The release dirs use short-SHA names; the glob finds the right one.

## The read-only + cache problem

The served release dir has `dr-xr-xr-x` perms. After `sudo cp` of the
OKF, the file is on disk but:

1. The gateway has an **in-process tree cache** loaded at startup. New
   files don't appear in `/api/workspace-tree/node` until the gateway
   restarts.
2. The gateway runs as `User=ubuntu`. Files copied via `sudo` are
   owned by `root:root`. There may be an ownership filter that excludes
   them even after cache refresh — `chown ubuntu:ubuntu` is the safer
   move.
3. **Restarting the gateway interrupts George's active agent session.**
   This is the dashboard-readiness-vs-agent-disruption tradeoff.

## What the agent should do

1. **Confirm Michael's authorization for the gateway restart** before
   executing. Surface the tradeoff: "OKF is on disk at the served path,
   the gateway needs a restart to refresh its tree cache; restart
   interrupts George's session for ~2 minutes."
2. **Use the size-fingerprint recipe** to verify which path the live
   API actually serves from, not which path the plugin's code
   "should" serve from.
3. **If Michael wants a normal-path deployment** (not the break-glass
   `sudo + restart`), the correct workflow is: commit the file to
   `prismatic-engine-control`, open a PR, merge, deploy the new release,
   restart. That's ~30+ minutes of lead time vs. 2 minutes of gateway
   downtime.
4. **Do not silently bounce the gateway.** Even with `RestartSec=5` in
   the systemd unit, the in-flight agent session context is lost.

## Why this belongs in `multirepo-file-find`

The session was a multirepo-file-find case in three layers:
- Layer 1: the file was at the right path (orchestrator state).
- Layer 2: the file needed to be at the served path (release dir).
- Layer 3: the served path differs from the auto-discovered path.

The skill's existing "wrong path → find the right path" framing extends
naturally to "served path ≠ source path" — when a public surface serves
from a pinned snapshot rather than the latest source.

## Other observations worth keeping

- The `docs/okf-map.md` file (referenced from dashboard templates) is
  **also not served** by the live API at `/docs/okf-map.md` (404) —
  the dashboard template renders links to paths that aren't routed.
  Same root cause: template references `docs/<file>.md` but no route
  handler exists.
- The plugin's `WORKSPACE_ROOTS` static dict only seeds two workspaces
  ("HD Reports", "HD Birth Data"). Everything else comes from
  auto-discovery. So adding a new workspace is `mkdir` in
  `/home/ubuntu/work/` (which is what creates the symlinked "Prismatic
  Engine" workspace pointing at `/home/ubuntu/.prismatic/repos/prismatic-engine-control/`).
- The active version symlink `/home/ubuntu/.prismatic/active` is
  what `bin/prismatic_*` scripts resolve to. Switching the active
  version (e.g. by deploying a new release) affects CLI behavior but
  not the workspace-tree plugin's served path until the gateway
  restarts.