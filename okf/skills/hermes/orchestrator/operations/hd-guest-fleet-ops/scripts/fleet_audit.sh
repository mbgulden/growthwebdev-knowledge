#!/bin/bash
# HD guest fleet audit: host matrix, live matrix, in-container truth, drift vs template.
# Read-only. Safe to run any time. Usage: bash fleet_audit.sh
set -u
TPL="${TPL:-/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py}"
WS_ROOT="${WS_ROOT:-/home/ubuntu/users}"
BOT_ROOT="${BOT_ROOT:-/home/ubuntu}"

echo "=== TEMPLATE ==="
md5sum "$TPL"
wc -l "$TPL"

echo
echo "=== HOST MATRIX (all guest_* workspaces) ==="
for f in "$WS_ROOT"/guest_*/guest_agent_server.py; do
  g=$(basename "$(dirname "$f")")
  printf "%-12s lines=%-6s md5=%s mtime=%s\n" "$g" "$(wc -l < "$f")" "$(md5sum "$f" | cut -d' ' -f1)" "$(stat -c '%y' "$f" | cut -d. -f1)"
done

echo
echo "=== LIVE MATRIX (containers) ==="
timeout 20 docker ps --format '{{.Names}}\t{{.Status}}' | grep '^guest-hermes-' || echo "(no live guest containers)"

echo
echo "=== WORKSPACE -> BOT DIR -> CONTAINER mapping ==="
for d in "$BOT_ROOT"/guest_hermes_bot*; do
  [ -f "$d/.env" ] || continue
  cid=$(grep '^GUEST_CONTAINER_NAME=' "$d/.env" | cut -d= -f2)
  wspath=$(grep '^GUEST_WORKSPACE_PATH=' "$d/.env" | cut -d= -f2)
  live=$(timeout 10 docker ps --format '{{.Names}}' 2>/dev/null | grep -cxF "$cid")
  live=${live:-0}
  printf "%-24s workspace=%-28s container=%s\n" "$(basename "$d")" "$wspath" "$cid (live=$live)"
done

echo
echo "=== IN-CONTAINER TRUTH (served file = /workspace, NOT /app) ==="
for c in $(timeout 20 docker ps --format '{{.Names}}' | grep '^guest-hermes-'); do
  lines=$(timeout 15 docker exec "$c" sh -c 'wc -l < /workspace/guest_agent_server.py 2>/dev/null' 2>/dev/null || echo "?")
  health=$(timeout 15 docker exec "$c" python3 -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/docs')" >/dev/null 2>&1 && echo OK || echo DOWN)
  printf "%-16s lines=%-6s health=%s\n" "$c" "$lines" "$health"
done

echo
echo "=== DEV-NAME SWEEP (expect: only 'Becca Gulden' matches) ==="
grep -rn "Michael Gulden" "$WS_ROOT"/guest_*/guest_agent_server.py 2>/dev/null || echo "clean"
