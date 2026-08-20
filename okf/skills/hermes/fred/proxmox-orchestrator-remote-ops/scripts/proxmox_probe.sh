#!/usr/bin/env bash
# proxmox_probe.sh — runs the 4-step Proxmox reachability probe.
# Use before any Proxmox work from a non-Proxmox host to confirm
# the password path, the cookie name, and read permissions.
#
# Usage:
#   PVE_USER=root@pam PVE_PASS=proxmox123 ./proxmox_probe.sh 192.168.1.201
#   PVE_PASS=$(grep -oE 'PVE_PASS="[^"]+"' /mnt/.../.env.clean | sed -E 's/.*"([^"]+)".*/\1/') \
#     ./proxmox_probe.sh 192.168.1.201
#
# Output sections:
#   - TCP reachability on 8006
#   - SSH reachability on 22
#   - Auth ticket acquisition
#   - Read-only API verification (nodes, VMs, GPU passthrough)
#   - Final summary: GREEN/YELLOW/RED

set -u

PVE_HOST="${1:-}"
PVE_USER="${PVE_USER:-root@pam}"
PVE_PASS="${PVE_PASS:-proxmox123}"
PVE_URL="${PVE_URL:-https://${PVE_HOST}:8006}"

if [[ -z "$PVE_HOST" ]]; then
  echo "usage: $0 <pve-host> [PVE_USER=...] [PVE_PASS=...]" >&2
  exit 2
fi

HEAD=/tmp/.proxmox-probe-head
COOKIE_HEADER=/tmp/.proxmox-probe-cookie
TICKET_FILE=/tmp/.proxmox-probe-ticket

green() { printf '  \033[32m%s\033[0m\n' "$1"; }
yellow() { printf '  \033[33m%s\033[0m\n' "$1"; }
red() { printf '  \033[31m%s\033[0m\n' "$1"; }
section() { printf '\n=== %s ===\n' "$1"; }

# --- 1. TCP reachability ---
section "1. TCP reachability on $PVE_HOST:8006"
if timeout 3 bash -c "echo > /dev/tcp/$PVE_HOST/8006" 2>/dev/null; then
  green "  8006 OPEN"
  PROBE_OK=1
else
  red "  8006 closed or unreachable"
  PROBE_OK=0
fi

if [[ $PROBE_OK -eq 0 ]]; then
  exit 1
fi

# --- 2. SSH ---
section "2. SSH reachability on $PVE_HOST:22"
if timeout 3 bash -c "echo > /dev/tcp/$PVE_HOST/22" 2>/dev/null; then
  green "  22 OPEN"
  SSH_OK=1
else
  yellow "  22 closed (API may still work)"
  SSH_OK=0
fi

# --- 3. Auth ticket ---
section "3. Auth ticket acquisition"
RESP=$(curl -sk --max-time 8 -d "username=$PVE_USER&password=$PVE_PASS" "$PVE_URL/api2/json/access/ticket")
TICKET=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('ticket',''))" 2>/dev/null)
CLUSTER=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('clustername',''))" 2>/dev/null)
if [[ -n "$TICKET" ]]; then
  green "  ticket acquired (length=${#TICKET})"
  green "  cluster: $CLUSTER"
  echo "$TICKET" > "$TICKET_FILE"
  chmod 600 "$TICKET_FILE"
  TICKET_OK=1
else
  red "  auth failed — review $PVE_USER / $PVE_PASS or check PVE firewall"
  red "  raw response (first 200 chars):"
  echo "$RESP" | head -c 200 | sed 's/^/    /'
  echo
  exit 1
fi

# --- 4. Read-only API verification ---
section "4. Read-only API verification"

# nodes
NODES_JSON=$(curl -sk --max-time 8 -H "Cookie: PVEAuthCookie=$TICKET" "$PVE_URL/api2/json/nodes")
if echo "$NODES_JSON" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert "data" in d' 2>/dev/null; then
  ONLINE=$(echo "$NODES_JSON" | python3 -c "import sys,json; print(sum(1 for n in json.load(sys.stdin)['data'] if n.get('status')=='online'))")
  TOTAL=$(echo "$NODES_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']))")
  green "  nodes: $ONLINE online / $TOTAL total"
else
  red "  /api2/json/nodes failed"
  echo "$NODES_JSON" | head -c 200 | sed 's/^/    /'
  exit 1
fi

# VMs across online nodes
echo
VM_TOTAL=0
VM_GPU=0
for node in $(echo "$NODES_JSON" | python3 -c "import sys,json; [print(n['node']) for n in json.load(sys.stdin)['data'] if n.get('status')=='online']"); do
  qdata=$(curl -sk --max-time 8 -H "Cookie: PVEAuthCookie=$TICKET" "$PVE_URL/api2/json/nodes/$node/qemu")
  if echo "$qdata" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert "data" in d' 2>/dev/null; then
    for vmid in $(echo "$qdata" | python3 -c "import sys,json; [print(v['vmid']) for v in json.load(sys.stdin)['data']]"); do
      VM_TOTAL=$((VM_TOTAL+1))
      cfg=$(curl -sk --max-time 5 -H "Cookie: PVEAuthCookie=$TICKET" "$PVE_URL/api2/json/nodes/$node/qemu/$vmid/config")
      hostpci=$(echo "$cfg" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('hostpci',''))" 2>/dev/null)
      if [[ -n "$hostpci" ]]; then
        VM_GPU=$((VM_GPU+1))
        name=$(echo "$cfg" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('name',''))" 2>/dev/null)
        yellow "  GPU-pt  $node  vmid=$vmid  name=$name"
      fi
    done
  fi
done
green "  vms: $VM_TOTAL total, $VM_GPU with GPU passthrough"

# --- 5. Final ---
section "5. Summary"
green "  $PVE_HOST is reachable via API + SSH"
green "  $ONLINE/$TOTAL nodes online, $VM_TOTAL VMs, $VM_GPU GPU-passthrough"
green "  ticket stored at $TICKET_FILE (chmod 600)"
echo
echo "  next: drive VMs via SSH + qm on this host, or qm guest exec for VM-internal work"
echo "  reference: SKILL proxmox-orchestrator-remote-ops"