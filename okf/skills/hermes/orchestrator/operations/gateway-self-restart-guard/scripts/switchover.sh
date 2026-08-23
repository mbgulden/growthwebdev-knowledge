#!/usr/bin/env bash
# ── Orchestrator gateway switchover: manual stopgap → systemd unit ──
# Purpose: cut over the manually‑launched orchestrator gateway to the new 
#          systemd unit. Run ONLY from a terminal OUTSIDE the gateway session.
# Built from the 2026-08-22 Fred/Kai session where the permanent unit was 
#          staged at /tmp but never sudo‑installed.
set -u

UNIT=hermes-orchestrator-gateway
UNIT_FILE_TMP=/tmp/hermes-orchestrator-gateway.service
PROFILE_LOG=/home/ubuntu/.hermes/profiles/orchestrator/logs/gateway.log
OLD_PID=2118074   # the manual stopgap PID found during diagnosis

echo "[1/4] Killing old manual stopgap (PID ${OLD_PID})"
if kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID"
    sleep 2
else
    echo "  Old PID ${OLD_PID} already gone."
fi

echo "[2/4] Installing permanent unit & reloading systemd"
sudo cp "$UNIT_FILE_TMP" /etc/systemd/system/
sudo systemctl daemon-reload

echo "[3/4] Restarting ${UNIT} under systemd"
sudo systemctl restart "$UNIT"

echo "[4/4] Waiting for active state (max 90s)..."
active=no
for _ in $(seq 1 45); do
    if [ "$(systemctl is-active "$UNIT" 2>/dev/null)" = "active" ]; then
        active=yes
        break
    fi
    sleep 2
done

if [ "$active" = "yes" ]; then
    echo "OK — ${UNIT} is active under systemd."
    echo "  Verify: exactly one gateway process (PPID=1), old PID gone."
    echo "  New PID: $(systemctl show -p MainPID --value $UNIT)"
else
    echo "!!! UNIT NOT ACTIVE — dumping last 30 lines of journal:"
    sudo journalctl -u "$UNIT" --no-pager -n 30
    echo ""
    echo "Emergency fallback: relaunching manual stopgap..."
    setsid /home/ubuntu/.local/bin/hermes --profile orchestrator gateway run \
        </dev/null >/dev/null 2>&1 &
    echo "Manual stopgap relaunched. Check $PROFILE_LOG and journal."
    exit 1
fi
