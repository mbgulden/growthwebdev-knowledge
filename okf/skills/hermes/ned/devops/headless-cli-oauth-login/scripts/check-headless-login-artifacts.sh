#!/usr/bin/env bash
# check-headless-login-artifacts.sh
# Verify that a headless CLI OAuth login actually left credentials on disk.
# Exit 0 if at least one credential artifact is present, non-empty, and recent.
# Exit 1 otherwise. Prints a human-readable status block.
#
# Usage: ./check-headless-login-artifacts.sh [--name <profile>] [--max-age-min <N>] [--cli <name>]
#
# Defaults: looks for zapier-sdk credentials under ~ and ~/.config/.

set -uo pipefail

PROFILE=""
MAX_AGE_MIN=5
CLI="zapier-sdk"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) PROFILE="$2"; shift 2 ;;
    --max-age-min) MAX_AGE_MIN="$2"; shift 2 ;;
    --cli) CLI="$2"; shift 2 ;;
    -h|--help)
      sed -n '1,14p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

HUMAN_HOME="$HOME"
[[ -z "$HUMAN_HOME" ]] && HUMAN_HOME="/home/ubuntu"

# Candidate paths to probe, by CLI. Add more here as the skill extends.
case "$CLI" in
  zapier-sdk|zapier)
    CANDIDATES=(
      "$HUMAN_HOME/.zapier/credentials.json"
      "$HUMAN_HOME/.config/zapier/credentials.json"
      "$HUMAN_HOME/.cache/zapier/credentials.json"
    )
    ;;
  gcloud)
    CANDIDATES=(
      "$HUMAN_HOME/.config/gcloud/application_default_credentials.json"
      "$HUMAN_HOME/.config/gcloud/credentials"
    )
    ;;
  gh)
    CANDIDATES=(
      "$HUMAN_HOME/.config/gh/hosts.yml"
    )
    ;;
  aws)
    CANDIDATES=(
      "$HUMAN_HOME/.aws/credentials"
      "$HUMAN_HOME/.aws/sso/cache"
    )
    ;;
  *)
    echo "no candidate paths registered for --cli=$CLI" >&2
    exit 2
    ;;
esac

# If a profile name is given, only consider files whose contents mention the profile.
echo "=== headless login artifact check ==="
echo "cli       : $CLI"
echo "profile   : ${PROFILE:-<any>}"
echo "max-age   : ${MAX_AGE_MIN}m"
echo "home      : $HUMAN_HOME"
echo

FOUND=0
for path in "${CANDIDATES[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "missing  : $path"
    continue
  fi
  size=$(stat -c%s "$path" 2>/dev/null || stat -f%z "$path" 2>/dev/null || echo 0)
  mtime_epoch=$(stat -c%Y "$path" 2>/dev/null || stat -f%m "$path" 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  age_min=$(( (now_epoch - mtime_epoch) / 60 ))
  if [[ "$size" -eq 0 ]]; then
    echo "empty    : $path (0 bytes)"
    continue
  fi
  if [[ "$age_min" -gt "$MAX_AGE_MIN" ]]; then
    echo "stale    : $path (${age_min}m old, > ${MAX_AGE_MIN}m)"
    continue
  fi
  if [[ -n "$PROFILE" ]] && ! grep -q -- "$PROFILE" "$path" 2>/dev/null; then
    echo "wrong-pf : $path (does not contain '$PROFILE')"
    continue
  fi
  echo "OK       : $path (${size}B, ${age_min}m old)"
  FOUND=1
done

echo
if [[ "$FOUND" -eq 1 ]]; then
  echo "VERDICT: ✅ credentials present"
  exit 0
else
  echo "VERDICT: 🔴 no recent credential file found"
  exit 1
fi
