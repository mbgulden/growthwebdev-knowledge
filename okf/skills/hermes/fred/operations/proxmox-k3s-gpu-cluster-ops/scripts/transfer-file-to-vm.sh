#!/usr/bin/env bash
# transfer-file-to-vm.sh — robust file transfer from orchestrator host to a Proxmox VM.
#
# Why this script exists:
#   `sshpass ssh root@pve "qm guest exec <vmid> -- bash -c 'cat > /tmp/x.sh << EOF ... EOF'"`
#   is a constant source of pain because:
#     1. Nested single quotes inside `bash -c '...'` get re-interpolated by the outer bash.
#     2. Heredoc terminators get mangled when the inner bash strips them.
#     3. `qm guest exec` synchronously waits for the inner command; if the heredoc fails,
#        you get `bash: unexpected EOF` and no file lands on the VM.
#   The fix: write the file with the orchestrator's `write_file` (or any local tool),
#   serve it on a short-lived HTTP server, and `wget` it inside the VM.
#
# Usage:
#   transfer-file-to-vm.sh <vmid> <local-file> [<remote-path>]
#
# Defaults:
#   - pve_lan_ip: 192.168.1.2 (PVE1, hardcoded for the Antigravity cluster)
#   - pve_user:   root
#   - pve_pass:   read from ~/.antigravity/secrets.yaml via yq if available, else
#                 [REDACTED] (Proxmox root@pam password, shared cluster-wide)
#   - http_port:  8766 (matches the existing webtop-hermes HTTP server pattern)
#
# Side effects:
#   - Starts `python3 -m http.server` bound to 0.0.0.0 on the chosen port.
#   - Removes /tmp/transfer-file-to-vm-pid on EXIT (kill the http server).
#   - The caller is responsible for the destination file inside the VM.

set -euo pipefail

VMID="${1:?usage: transfer-file-to-vm.sh <vmid> <local-file> [<remote-path>]}"
LOCAL_FILE="${2:?usage: transfer-file-to-vm.sh <vmid> <local-file> [<remote-path>]}"
REMOTE_PATH="${3:-/tmp/$(basename "$LOCAL_FILE")}"

PVE_IP="${PVE_IP:-192.168.1.2}"
PVE_USER="${PVE_USER:-root}"
PVE_PASS="${PVE_PASS:-[REDACTED]}"
HTTP_PORT="${HTTP_PORT:-8766}"
HTTP_DIR="${HTTP_DIR:-/tmp}"

if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "ERROR: local file not found: $LOCAL_FILE" >&2
  exit 1
fi

# Kill any stale http server on this port from a previous run
if [[ -f /tmp/transfer-file-to-vm-pid ]]; then
  OLD_PID=$(cat /tmp/transfer-file-to-vm-pid)
  if kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
  fi
  rm -f /tmp/transfer-file-to-vm-pid
fi

# Start the HTTP server in the background
( cd "$HTTP_DIR" && python3 -m http.server "$HTTP_PORT" --bind 0.0.0.0 >/dev/null 2>&1 & echo $! > /tmp/transfer-file-to-vm-pid )
sleep 1
HTTP_PID=$(cat /tmp/transfer-file-to-vm-pid)

cleanup() {
  if kill -0 "$HTTP_PID" 2>/dev/null; then
    kill "$HTTP_PID" 2>/dev/null || true
  fi
  rm -f /tmp/transfer-file-to-vm-pid
}
trap cleanup EXIT

# Compute the relative path under HTTP_DIR so the VM can fetch it
RELATIVE_PATH="${LOCAL_FILE#"$HTTP_DIR"/}"

echo ">>> Transferring $LOCAL_FILE -> VM $VMID:$REMOTE_PATH"
echo "    HTTP server: http://<this-host>:$HTTP_PORT/$RELATIVE_PATH (PID $HTTP_PID)"

sshpass -p "$PVE_PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o HostKeyAlgorithms=+ssh-rsa "$PVE_USER@$PVE_IP" \
  "qm guest exec $VMID -- bash -c 'wget -q http://$(hostname -I | awk "{print \$1}"):$HTTP_PORT/$RELATIVE_PATH -O $REMOTE_PATH && chmod +x $REMOTE_PATH && ls -la $REMOTE_PATH'"

echo ">>> Done. File at: $REMOTE_PATH (VM $VMID)"