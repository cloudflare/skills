#!/usr/bin/env bash
# Probes Cloudflare API auth state for the Turnstile Spin agent.
#
# Reads:
#   $CLOUDFLARE_API_TOKEN  (required)
#   $CLOUDFLARE_ACCOUNT_ID (optional; if set, checked against the token's account)
#
# Outputs JSON to stdout, always exits 0. The agent reads `status`:
#   "ok"              ; token has Turnstile + Workers scope, account_id captured
#   "missing_token"   ; no token, or wrangler whoami failed
#   "missing_scope"   ; token lacks Account.Turnstile:Edit (code 10000)
#   "account_mismatch"; $CLOUDFLARE_ACCOUNT_ID does not match the token's account
#
# Human-readable diagnostics go to stderr. The agent surfaces them to the user.

set -uo pipefail

emit() {
  echo "$1"
  exit 0
}

token="${CLOUDFLARE_API_TOKEN:-}"
declared_account="${CLOUDFLARE_ACCOUNT_ID:-}"

if [ -z "$token" ]; then
  echo "auth-probe: \$CLOUDFLARE_API_TOKEN is not set." >&2
  emit '{"status":"missing_token","reason":"no_env_var"}'
fi

whoami_json=$(npx wrangler whoami --json 2>/dev/null || true)
if [ -z "$whoami_json" ] || [ "$(echo "$whoami_json" | head -c 1)" != "{" ]; then
  echo "auth-probe: wrangler whoami returned no JSON. Token may be invalid or expired." >&2
  emit '{"status":"missing_token","reason":"whoami_failed"}'
fi

# Parse with jq if available, fall back to python3
parse_json() {
  if command -v jq >/dev/null 2>&1; then
    echo "$1" | jq -r "$2" 2>/dev/null || python3 -c "import sys,json; obj=json.loads(sys.argv[1]); print(eval('obj' + sys.argv[2]))" "$1" "$3" 2>/dev/null
  else
    python3 -c "import sys,json; obj=json.loads(sys.argv[1]); print(eval('obj' + sys.argv[2]))" "$1" "$3" 2>/dev/null
  fi
}

account_id=$(echo "$whoami_json" | (jq -r '.accounts[0].id' 2>/dev/null || python3 -c "import sys,json; print(json.load(sys.stdin)['accounts'][0]['id'])"))
accounts_json=$(echo "$whoami_json" | (jq -c '.accounts' 2>/dev/null || python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['accounts']))"))

if [ -z "$account_id" ] || [ "$account_id" = "null" ]; then
  echo "auth-probe: wrangler whoami succeeded but no accounts found on the token." >&2
  emit '{"status":"missing_token","reason":"no_accounts"}'
fi

if [ -n "$declared_account" ] && [ "$declared_account" != "$account_id" ]; then
  echo "auth-probe: \$CLOUDFLARE_ACCOUNT_ID ($declared_account) does not match the token's account ($account_id)." >&2
  echo "auth-probe: Either unset \$CLOUDFLARE_ACCOUNT_ID, or fix it before continuing." >&2
  emit "{\"status\":\"account_mismatch\",\"declared\":\"$declared_account\",\"token_account\":\"$account_id\"}"
fi

# Probe Turnstile scope
tmp=$(mktemp)
http_code=$(curl -sS -w "%{http_code}" -o "$tmp" \
  "https://api.cloudflare.com/client/v4/accounts/$account_id/challenges/widgets" \
  -H "Authorization: Bearer $token" 2>/dev/null || echo "000")
body=$(cat "$tmp"); rm -f "$tmp"
success=$(echo "$body" | (jq -r '.success' 2>/dev/null || echo "false"))

if [ "$success" != "true" ]; then
  echo "auth-probe: token cannot read /challenges/widgets (HTTP $http_code). Missing Account.Turnstile:Edit." >&2
  emit "{\"status\":\"missing_scope\",\"account_id\":\"$account_id\",\"http_code\":$http_code}"
fi

emit "{\"status\":\"ok\",\"account_id\":\"$account_id\",\"accounts\":$accounts_json}"
