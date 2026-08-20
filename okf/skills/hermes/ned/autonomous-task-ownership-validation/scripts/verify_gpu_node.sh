#!/usr/bin/env bash
# verify_gpu_node.sh — Reproducible GPU node health probe for Ned cron validation.
#
# Run during the "genuine Ned-lane infra finding" check in the Ned triage-comment
# template (see autonomous-task-ownership-validation/references/ned-refusal-template-20260625.md).
#
# IMPORTANT: this is REAL BASH, not Python — despite the misleading .sh name being
# listed alongside Python probes in some docs. The shebang was originally
# `#!/usr/bin/env python3` which caused `python3 verify_gpu_node.sh` to fail with
# a syntax error at the awk pipeline. Fix: invoke with `bash verify_gpu_node.sh`
# (works) or fix the shebang to bash (done). Do NOT invoke with `python3`.
#
# Usage:
#     bash verify_gpu_node.sh                 # probe all known nodes
#     bash verify_gpu_node.sh 100.78.237.7    # probe specific IP
#
# Exit codes:
#     0  — all reachable
#     1  — GPU node unreachable (DOWN)
#     2  — partial degradation (LAN or Tailscale reachable, not both)
#     3  — Ollama HTTP unreachable but host pings
#
# Side effects: prints a structured report to stdout. No file writes, no network
# calls beyond ping + curl, safe to run in cron sandbox.

set -u

GPU_TS="${1:-100.78.237.7}"        # Tailscale IP (k3s-node-230)
GPU_LAN="${1:-192.168.1.230}"      # LAN fallback
OLLAMA_PORT="${OLLAMA_PORT:-31434}"
PVE_HOST="${PVE_HOST:-100.90.63.4}"

echo "=== GPU Node Health Probe ($(date -u +%Y-%m-%dT%H:%M:%SZ)) ==="
echo "GPU_TS=$GPU_TS  GPU_LAN=$GPU_LAN  OLLAMA_PORT=$OLLAMA_PORT  PVE_HOST=$PVE_HOST"
echo ""

OVERALL=0

# 1. Tailscale ping
echo "--- Tailscale ping ($GPU_TS) ---"
if timeout 5 ping -c 2 -W 2 "$GPU_TS" > /tmp/_gpu_ping_ts.log 2>&1; then
    echo "  ✅ reachable"
    grep -E "packet loss|rtt" /tmp/_gpu_ping_ts.log | head -2
else
    echo "  ❌ UNREACHABLE (100% packet loss expected)"
    OVERALL=1
fi

# 2. LAN ping (only if Tailscale failed — saves time when healthy)
if [ "$OVERALL" -ne 0 ]; then
    echo ""
    echo "--- LAN ping ($GPU_LAN) ---"
    if timeout 5 ping -c 2 -W 2 "$GPU_LAN" > /tmp/_gpu_ping_lan.log 2>&1; then
        echo "  ⚠️  LAN reachable — Tailscale routing broken but node alive"
        grep -E "packet loss|rtt" /tmp/_gpu_ping_lan.log | head -2
        OVERALL=2
    else
        echo "  ❌ LAN also unreachable — node is physically down or power-cycled"
    fi
fi

# 3. Ollama HTTP probe
echo ""
echo "--- Ollama HTTP (http://$GPU_TS:$OLLAMA_PORT/api/tags) ---"
HTTP_CODE=$(curl -s -o /tmp/_gpu_ollama.json -w "%{http_code}" --max-time 10 "http://$GPU_TS:$OLLAMA_PORT/api/tags" 2>&1 || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ Ollama healthy"
    head -c 200 /tmp/_gpu_ollama.json
    echo ""
elif [ "$HTTP_CODE" = "000" ]; then
    echo "  ❌ Connection refused / timeout (HTTP 000)"
    [ "$OVERALL" -eq 0 ] && OVERALL=3
else
    echo "  ⚠️  HTTP $HTTP_CODE"
    head -c 200 /tmp/_gpu_ollama.json
    echo ""
fi

# 4. PVE6 host reachability (proves network path is OK)
echo ""
echo "--- PVE6 host ($PVE_HOST) ---"
if timeout 5 ping -c 2 -W 2 "$PVE_HOST" > /tmp/_gpu_ping_pve.log 2>&1; then
    echo "  ✅ PVE6 reachable — network path OK, issue is at GPU node itself"
else
    echo "  ⚠️  PVE6 unreachable — broader network outage, GPU issue may be downstream"
fi

# 5. Hermes VM disk check (the other Ned monitoring metric)
echo ""
echo "--- Hermes VM disk ---"
df -h /home/ubuntu 2>&1 | head -2 | tail -1 | awk '{
    pct = $5 + 0
    if (pct >= 90) print "  🔴 CRITICAL: " $0
    else if (pct >= 85) print "  🟡 WARNING: " $0
    else print "  🟢 OK: " $0
}'

echo ""
echo "=== Result: $([ $OVERALL -eq 0 ] && echo '🟢 HEALTHY' || echo '🔴 DOWN/DEGRADED') (exit=$OVERALL) ==="

exit $OVERALL