#!/usr/bin/env bash
# Probes Cloudflare API auth state for the Turnstile Spin agent.
#
# Reads:
#   $CLOUDFLARE_API_TOKEN  (required)
#   $CLOUDFLARE_ACCOUNT_ID (optional; if set, must be one of the token's accounts)
#
# Outputs JSON to stdout, always exits 0. The agent reads `status`:
#   "ok"                   ; selected account passed both Turnstile and Workers scope probes
#   "missing_token"        ; no token set, or wrangler whoami failed
#   "missing_scope"        ; token lacks Account.Turnstile:Edit on the selected account
#   "missing_workers_scope"; token has Turnstile scope but lacks Workers Scripts on the selected account
#   "multiple_accounts"    ; token covers >1 accounts and $CLOUDFLARE_ACCOUNT_ID is unset; agent must ask user to pick, set it, and re-run
#   "account_mismatch"     ; $CLOUDFLARE_ACCOUNT_ID is set but is not in the token's accounts list
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

# Extract the accounts array. Fall back to python3 if jq is missing.
accounts_json=$(echo "$whoami_json" | (jq -c '.accounts' 2>/dev/null || python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['accounts']))"))
account_count=$(echo "$accounts_json" | (jq 'length' 2>/dev/null || python3 -c "import sys,json; print(len(json.load(sys.stdin)))"))

if [ -z "$account_count" ] || [ "$account_count" = "0" ] || [ "$account_count" = "null" ]; then
  echo "auth-probe: wrangler whoami succeeded but no accounts found on the token." >&2
  emit '{"status":"missing_token","reason":"no_accounts"}'
fi

# Pick the account to probe:
#   - $CLOUDFLARE_ACCOUNT_ID set: must be in the token's accounts list, else account_mismatch
#   - unset, exactly 1 account: use it silently
#   - unset, >1 accounts: emit multiple_accounts; agent picks and re-runs
if [ -n "$declared_account" ]; then
  in_list=$(echo "$accounts_json" | (jq --arg id "$declared_account" 'map(.id) | index($id) != null' 2>/dev/null || python3 -c "import sys,json; print('true' if any(a['id']==sys.argv[1] for a in json.load(sys.stdin)) else 'false')" "$declared_account"))
  if [ "$in_list" != "true" ]; then
    echo "auth-probe: \$CLOUDFLARE_ACCOUNT_ID ($declared_account) is not one of the token's accounts." >&2
    echo "auth-probe: Either unset \$CLOUDFLARE_ACCOUNT_ID, or set it to an account included in the token's Account Resources." >&2
    emit "{\"status\":\"account_mismatch\",\"declared\":\"$declared_account\",\"accounts\":$accounts_json}"
  fi
  account_id="$declared_account"
elif [ "$account_count" = "1" ]; then
  account_id=$(echo "$accounts_json" | (jq -r '.[0].id' 2>/dev/null || python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])"))
else
  echo "auth-probe: token covers $account_count accounts; ask the user to pick one, then export \$CLOUDFLARE_ACCOUNT_ID and re-run." >&2
  emit "{\"status\":\"multiple_accounts\",\"accounts\":$accounts_json}"
fi

# Probe Turnstile scope on the selected account
tmp=$(mktemp)
http_code=$(curl -sS -w "%{http_code}" -o "$tmp" \
  "https://api.cloudflare.com/client/v4/accounts/$account_id/challenges/widgets" \
  -H "Authorization: Bearer $token" 2>/dev/null || echo "000")
body=$(cat "$tmp"); rm -f "$tmp"
success=$(echo "$body" | (jq -r '.success' 2>/dev/null || echo "false"))

if [ "$success" != "true" ]; then
  echo "auth-probe: token cannot read /challenges/widgets on account $account_id (HTTP $http_code). Missing Account.Turnstile:Edit." >&2
  emit "{\"status\":\"missing_scope\",\"account_id\":\"$account_id\",\"http_code\":$http_code}"
fi

# Probe Workers scope on the selected account. GET /workers/scripts requires
# Account.Workers Scripts:Read, which is a best-effort proxy for Edit. Tokens
# granted Edit-only (without Read) will fail this probe and emit a confusing
# missing_workers_scope; the agent should suggest adding Read alongside Edit.
tmp=$(mktemp)
workers_code=$(curl -sS -w "%{http_code}" -o "$tmp" \
  "https://api.cloudflare.com/client/v4/accounts/$account_id/workers/scripts" \
  -H "Authorization: Bearer $token" 2>/dev/null || echo "000")
workers_body=$(cat "$tmp"); rm -f "$tmp"
workers_success=$(echo "$workers_body" | (jq -r '.success' 2>/dev/null || echo "false"))

if [ "$workers_success" != "true" ]; then
  echo "auth-probe: token cannot read /workers/scripts on account $account_id (HTTP $workers_code). Missing Account.Workers Scripts:Edit." >&2
  emit "{\"status\":\"missing_workers_scope\",\"account_id\":\"$account_id\",\"http_code\":$workers_code}"
fi

emit "{\"status\":\"ok\",\"account_id\":\"$account_id\",\"accounts\":$accounts_json}"
