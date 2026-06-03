#!/usr/bin/env bash
# Validates a deployed Turnstile siteverify Worker end-to-end.
#
# Reads:
#   $CLOUDFLARE_API_TOKEN (required for hostname check)
#
# Args:
#   --worker-url <url>     Deployed Worker URL (from worker-deploy.sh)
#   --account-id <id>      Cloudflare account ID
#   --sitekey <key>        Widget sitekey (from widget-create.sh)
#   --expected-domains <a,b,c>  Comma-separated domains that must appear in the widget's domains array
#
# Outputs JSON. Exit 0 if all three checks pass, 1 otherwise.
#   ok:    {"status":"ok"}
#   fail:  {"status":"error","check":"health|dummy_siteverify|hostname","detail":"<msg>"}

set -uo pipefail

while [[ $# -gt 0 ]]; do
  case $1 in
    --worker-url)       WORKER_URL="$2"; shift 2 ;;
    --account-id)       ACCOUNT_ID="$2"; shift 2 ;;
    --sitekey)          SITEKEY="$2"; shift 2 ;;
    --expected-domains) EXPECTED_DOMAINS="$2"; shift 2 ;;
    *) echo "validate: unknown arg $1" >&2; exit 2 ;;
  esac
done

: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN must be set}"
: "${WORKER_URL:?--worker-url required}"
: "${ACCOUNT_ID:?--account-id required}"
: "${SITEKEY:?--sitekey required}"
: "${EXPECTED_DOMAINS:?--expected-domains required}"

# Check 1: health endpoint
health=$(curl -sSf "${WORKER_URL}/" 2>/dev/null || echo "")
if [ -z "$health" ] || ! echo "$health" | grep -q '"ok":true'; then
  echo "validate: health check failed; $WORKER_URL did not return {ok:true,version:...}" >&2
  echo "{\"status\":\"error\",\"check\":\"health\",\"detail\":\"worker /health did not respond ok:true\"}"
  exit 1
fi

# Check 2: dummy siteverify; should return success:false + error-codes array
dummy=$(curl -sS -X POST "${WORKER_URL}/" \
  -H "Content-Type: application/json" \
  -d '{"token":"XXXX.DUMMY.TOKEN.XXXX"}' 2>/dev/null || echo "")

success=$(echo "$dummy" | (jq -r '.success // "missing"' 2>/dev/null || echo "missing"))
errors=$(echo "$dummy" | (jq -r '.["error-codes"] | length // 0' 2>/dev/null || echo "0"))

if [ "$success" != "false" ] || [ "$errors" = "0" ]; then
  echo "validate: dummy siteverify check failed; expected success:false + error-codes; got: $dummy" >&2
  echo "{\"status\":\"error\",\"check\":\"dummy_siteverify\",\"detail\":\"unexpected response shape\"}"
  exit 1
fi

# Check 3: hostname / widget domains registered
widget=$(curl -sS \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/challenges/widgets/$SITEKEY" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" 2>/dev/null)
registered=$(echo "$widget" | (jq -r '.result.domains[]' 2>/dev/null || python3 -c "import sys,json; [print(d) for d in json.load(sys.stdin)['result']['domains']]"))

missing=""
IFS=',' read -ra DOMS <<< "$EXPECTED_DOMAINS"
for d in "${DOMS[@]}"; do
  if ! echo "$registered" | grep -qFx "$d"; then
    missing="${missing}${d} "
  fi
done

if [ -n "$missing" ]; then
  echo "validate: hostname check failed; domains not on widget: $missing" >&2
  echo "{\"status\":\"error\",\"check\":\"hostname\",\"detail\":\"missing domains: ${missing% }\"}"
  exit 1
fi

echo '{"status":"ok"}'
