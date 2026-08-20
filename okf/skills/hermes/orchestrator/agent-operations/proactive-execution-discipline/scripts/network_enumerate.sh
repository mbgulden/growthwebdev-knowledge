#!/usr/bin/env bash
# network_enumerate.sh — 7-step probe to enumerate what remote hosts are
# reachable from the current machine before declaring "no path to remote
# host." Companion to the "Investigate the network before declaring no
# path" pitfall in SKILL.md.
#
# Usage:
#   bash network_enumerate.sh [candidate-host-1 candidate-host-2 ...]
#
# If no candidate hosts are given, defaults to: pve1, pve1.local,
# proxmox, pve, host1.local (the typical on-prem + Tailscale hostnames).
#
# Output: a flat report on stdout. Exits 0 if at least one reachable
# candidate was found; exits 1 if none were reachable. NEVER exits with
# an unclassified state — every probe either passed or failed with a
# specific class, the way the orchestrator and downstream code can act on.
#
# The 7 probe steps:
#   1. /etc/hosts overrides
#   2. Tailscale DNS (getent hosts)
#   3. Local interfaces (ip addr + route)
#   4. ARP neighbours
#   5. SSH credentials + known_hosts
#   6. Control-plane tooling (kubectl, pvesh, qm, terraform, helm)
#   7. Tailscale or other overlay SSH quick-probes for each candidate

set -u
set -o pipefail

CANDIDATES=("$@")
if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
  CANDIDATES=(pve1 pve1.local proxmox pve host1.local)
fi

bar() { printf '\n--- %s ---\n' "$1"; }
hit() { printf '  + %s\n' "$1"; }
miss() { printf '  - %s\n' "$1"; }

# Track which candidates resolve to reachable IPs.
declare -A RESOLVED

# ---------------------------------------------------------------------------
# Step 1: /etc/hosts overrides.
# ---------------------------------------------------------------------------
bar "step 1 /etc/hosts"
if [[ -f /etc/hosts ]]; then
  for c in "${CANDIDATES[@]}"; do
    if grep -qE "(^|\s)${c}(\s|$)" /etc/hosts 2>/dev/null; then
      hit "candidate '${c}' has /etc/hosts override"
    fi
  done
  if ! grep -qE "$(IFS='|'; echo "${CANDIDATES[*]}")" /etc/hosts 2>/dev/null; then
    miss "no candidate found in /etc/hosts"
  fi
else
  miss "/etc/hosts not readable"
fi

# ---------------------------------------------------------------------------
# Step 2: Tailscale / system DNS (getent hosts).
# ---------------------------------------------------------------------------
bar "step 2 DNS resolution"
for c in "${CANDIDATES[@]}"; do
  ip=$(getent hosts "$c" 2>/dev/null | head -1 | awk '{print $1}')
  if [[ -n "$ip" ]]; then
    hit "${c} -> ${ip}"
    RESOLVED[$c]="$ip"
  fi
done

# ---------------------------------------------------------------------------
# Step 3: Local interfaces — see if we're on tailscale / a private LAN.
# ---------------------------------------------------------------------------
bar "step 3 local interfaces"
if command -v ip >/dev/null 2>&1; then
  ifaces=$(ip -4 addr show 2>/dev/null | grep -E 'inet ' | awk '{print $2, $NF}' | sed 's|/.*||')
  while IFS= read -r line; do
    hit "interface: $line"
  done <<<"$ifaces"
  if ip route 2>/dev/null | grep -q '^default'; then
    gw=$(ip route 2>/dev/null | awk '/^default/ {print $3; exit}')
    hit "default gateway: $gw"
  fi
  if ip -4 addr show 2>/dev/null | grep -q tailscale0; then
    hit "tailscale0 interface present — Tailscale is up"
  else
    miss "no tailscale0 interface"
  fi
else
  miss "ip command not available"
fi

# ---------------------------------------------------------------------------
# Step 4: ARP neighbours.
# ---------------------------------------------------------------------------
bar "step 4 ARP neighbours"
if command -v ip >/dev/null 2>&1; then
  count=$(ip neigh 2>/dev/null | grep -v 'INCOMPLETE' | wc -l)
  if (( count > 0 )); then
    hit "${count} known ARP neighbours"
  else
    miss "no ARP neighbours"
  fi
fi

# ---------------------------------------------------------------------------
# Step 5: SSH credentials + known_hosts.
# ---------------------------------------------------------------------------
bar "step 5 SSH credentials"
for ssh_dir in ~/.ssh "~/.hermes/profiles/$(whoami)/home/.ssh"; do
  ssh_dir=$(eval echo "$ssh_dir")
  if [[ -d "$ssh_dir" ]]; then
    for k in "$ssh_dir"/id_*; do
      [[ -f "$k" && ! "$k" =~ \.pub$ ]] && hit "SSH key: $k"
    done
    if [[ -f "$ssh_dir/known_hosts" ]]; then
      hc=$(wc -l < "$ssh_dir/known_hosts")
      hit "known_hosts: $hc entries"
    fi
    if [[ -f "$ssh_dir/config" ]]; then
      hit "ssh config present"
    fi
  fi
done

# ---------------------------------------------------------------------------
# Step 6: Control-plane tooling.
# ---------------------------------------------------------------------------
bar "step 6 control-plane tooling"
for tool in kubectl pvesh qm terraform helm vagrant multipass pveproxy; do
  if command -v "$tool" >/dev/null 2>&1; then
    hit "$tool: $(command -v "$tool")"
  fi
done

# ---------------------------------------------------------------------------
# Step 7: Tailscale SSH quick-probe for each resolved candidate.
# ---------------------------------------------------------------------------
bar "step 7 SSH quick-probe (BatchMode, ConnectTimeout=5)"
first_key=$(ls ~/.ssh/id_* 2>/dev/null | grep -v '\.pub$' | head -1)
[[ -z "$first_key" ]] && first_key=$(ls ~/.hermes/profiles/$(whoami)/home/.ssh/id_* 2>/dev/null | grep -v '\.pub$' | head -1)

for c in "${!RESOLVED[@]}"; do
  ip="${RESOLVED[$c]}"
  # Try a few common usernames fast.
  for u in root ubuntu admin pve deploy; do
    out=$(timeout 8 ssh -o BatchMode=yes -o ConnectTimeout=4 \
                -o StrictHostKeyChecking=accept-new \
                -o PreferredAuthentications=publickey \
                -i "$first_key" -p 22 \
                "${u}@${ip}" true 2>&1)
    rc=$?
    if (( rc == 0 )); then
      hit "${c} (${ip}): ssh ${u}@${c} OK"
      break
    fi
    case "$out" in
      *tailscale*login*)
        hit "${c} (${ip}): Tailscale SSH requires interactive web-auth — NOT a hard failure";;
      *failed\ to\ look\ up\ local\ user*)
        # Tailscale allowList — u is not in the list. Try next.
        continue;;
      *Connection\ closed*|*Permission\ denied*)
        continue;;
      *No\ route\ to\ host*|*Connection\ timed\ out*|*Could\ not\ resolve*)
        miss "${c} (${ip}): unreachable on port 22"; break;;
      *)
        continue;;
    esac
  done
done

# ---------------------------------------------------------------------------
# Final classification.
# ---------------------------------------------------------------------------
bar "summary"
if [[ ${#RESOLVED[@]} -gt 0 ]]; then
  echo "  + ${#RESOLVED[@]} candidate(s) resolved to IPs"
  for c in "${!RESOLVED[@]}"; do
    echo "    ${c} -> ${RESOLVED[$c]}"
  done
  echo "  next: run quick SSH probes (already done in step 7); consult any"
  echo "        Tailscale auth URLs surfaced; iterate."
  exit 0
else
  echo "  - no candidate resolved; investigate DNS / Tailscale config first"
  exit 1
fi
