#!/usr/bin/env bash
# HDE prod read-only health probe (no writes, no test rows).
# Usage: bash probe-hde-prod.sh
set -u
API="https://api.humandesignengine.com"
SITE="https://humandesignengine.com"

probe_get() { # url
  local out code size title
  out=$(mktemp)
  code=$(curl -s -o "$out" -w "%{http_code}" --max-time 15 "$1")
  size=$(wc -c < "$out")
  title=$(grep -oiE "<title>[^<]*" "$out" | head -1 | cut -c8-60)
  echo "GET $1 -> $code ($size b) ${title:-n/a}"
  rm -f "$out"
}

probe_post() { # url json
  local out code body
  out=$(mktemp)
  code=$(curl -s -o "$out" -w "%{http_code}" --max-time 15 -X POST \
    -H "Content-Type: application/json" -d "$2" "$1")
  body=$(head -c 160 "$out")
  echo "POST $1 -> $code | $body"
  rm -f "$out"
}

echo "=== frontend (content check — status 200 alone means NOTHING on Pages) ==="
probe_get "$SITE/"
probe_get "$SITE/deconditioning/"
probe_get "$SITE/sanctuary-demo/"
probe_get "$SITE/definitely-not-a-page-xyz123/"
echo "(sanctuary-demo healthy iff its size/title DIFFER from the nonsense URL above)"
echo
echo "=== backend (api subdomain — the real API) ==="
probe_post "$API/api/demo/start" '{"email":""}'          # expect 400 (route alive, bad email) — never 404
probe_post "$API/api/checkout/create-session" '{}'      # expect 422 (route alive)
echo
echo "=== OPTIONS preflight (browser cross-origin POST readiness) ==="
curl -s -i --max-time 15 -X OPTIONS -H "Origin: https://humandesignengine.com" \
  -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type" \
  "$API/api/demo/start" 2>&1 | grep -iE "^HTTP|access-control-allow" | head -6
