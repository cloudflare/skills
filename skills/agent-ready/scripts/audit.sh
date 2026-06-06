#!/usr/bin/env bash
# audit.sh <host> — measure which agent-discovery signals a site already serves.
# Read-only: only GETs / HEADs public URLs and queries public DNS. No credentials.
# Usage: scripts/audit.sh www.example.com
set -euo pipefail
HOST="${1:?usage: audit.sh <host>   e.g. www.example.com}"
BASE="https://$HOST"

ok()   { printf "  \033[32mPASS\033[0m %s\n" "$1"; }
bad()  { printf "  \033[31mFAIL\033[0m %s\n" "$1"; }

# check <path> <expect-substring-in-content-type>
check() {
  local path="$1" want="$2"
  local out code ct
  out=$(curl -s -o /dev/null -w "%{http_code} %{content_type}" "$BASE$path" || echo "000 -")
  code="${out%% *}"; ct="${out#* }"
  if [ "$code" = "200" ] && printf '%s' "$ct" | grep -qi "$want"; then
    ok "$path ($code, $ct)"
  else
    bad "$path ($code, ${ct:-no-ct}; want 200 + $want)"
  fi
}

echo "== Agent-readiness audit: $HOST =="

echo "-- well-known JSON/markdown documents --"
check "/.well-known/api-catalog"               "linkset+json"
check "/.well-known/agent-card.json"           "json"
check "/.well-known/mcp/server-card.json"      "json"
check "/.well-known/agent-skills/index.json"   "json"
check "/.well-known/oauth-authorization-server" "json"
check "/.well-known/oauth-protected-resource"  "json"
check "/.well-known/security.txt"              "text/plain"
check "/auth.md"                               "markdown"
check "/llms.txt"                              "text"

echo "-- homepage headers / negotiation --"
if curl -sI "$BASE/" | grep -qi '^link:'; then ok "Link header on /"; else bad "Link header on / (missing)"; fi
md=$(curl -s -o /dev/null -w "%{content_type}" -H "Accept: text/markdown" "$BASE/")
printf '%s' "$md" | grep -qi markdown && ok "Markdown for Agents ($md)" || bad "Markdown for Agents (got $md)"
curl -s "$BASE/robots.txt" | grep -qi 'content-signal' && ok "Content-Signal in robots.txt" || bad "Content-Signal in robots.txt (missing)"

echo "-- DNS-AID (SVCB under _agents) --"
for label in _index _mcp _a2a; do
  ans=$(dig +short "$label._agents.${HOST#www.}" TYPE64 2>/dev/null | head -1)
  [ -n "$ans" ] && ok "$label._agents SVCB present" || bad "$label._agents SVCB (none)"
done
dnssec=$(dig +dnssec +short "${HOST#www.}" SOA 2>/dev/null | grep -c RRSIG || true)
[ "${dnssec:-0}" -gt 0 ] && ok "DNSSEC RRSIG present" || bad "DNSSEC not validated (publish DS at registrar)"

echo "== done =="
