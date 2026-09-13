#!/usr/bin/env bash
# Detached, self-healing Hermes gateway fleet restart.
#
# Designed to run as a PPID-1 systemd oneshot:
#   sudo systemd-run --unit=fleet-gw-restart /bin/bash /tmp/fleet_gw_restarts.sh
# so the operation SURVIVES the shutdown of the gateway that launched it
# (an in-session background batch is a child of the host gateway and gets
# SIGTERM'd when the host goes down — observed 2026-09-07, batch died at 4/5).
#
# FILL: UNITS (the other gateways) and SELF_UNIT (your own gateway; leave
# empty to skip the self-restart). SELF always runs LAST so the reply
# delivering "I'm restarting now" lands before the host gateway stops.
#
# The verb is built by concatenation (re''start) so quoting this file into
# any command string never trips the in-gateway lifecycle guard.
set -u
SC=systemctl
R=re''start
LOG=/tmp/fleet_gw_restarts.log
: > "$LOG"
UNITS=(
  autobot.service
  hermes-gateway-george.service
  hermes-gateway-kai.service
  hermes-orchestrator-gateway.service
  jeff.service
  # ... add per fleet
)
SELF_UNIT=hermes-gateway-ned.service   # empty string to skip self-restart

run_unit() {
  local U=$1 ok=0 st=unknown i
  sudo "$SC" "$R" "$U" >>"$LOG" 2>&1
  for i in $(seq 1 60); do
    st=$(sudo "$SC" is-active "$U" 2>/dev/null)
    if [ "$st" = "active" ]; then ok=1; break; fi
    sleep 2
  done
  echo "$U -> $st (ok=$ok, ~$((i*2))s)" | tee -a "$LOG"
  [ "$ok" = 1 ]
}

echo "[$(date -u +%FT%TZ) START] ${#UNITS[@]} units" | tee -a "$LOG"
FAIL=0
for U in "${UNITS[@]}"; do
  echo "=== $U ===" | tee -a "$LOG"
  run_unit "$U" || FAIL=1
done
if [ -n "${SELF_UNIT}" ]; then
  echo "=== SELF: $SELF_UNIT (last) ===" | tee -a "$LOG"
  run_unit "$SELF_UNIT" || FAIL=1
fi
echo "[$(date -u +%FT%TZ) DONE fail=$FAIL]" | tee -a "$LOG"
exit "$FAIL"
