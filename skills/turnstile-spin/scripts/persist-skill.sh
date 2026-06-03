#!/usr/bin/env bash
# Persists the canonical Spin skill to the user's repo so the agent stays
# useful for follow-up tasks.
#
# Args:
#   --path <path>   Destination, e.g. .claude/skills/turnstile-spin/SKILL.md
#
# Outputs JSON. Exit 0 if the skill was written, 1 if the upstream URL
# returned non-200 or unexpected content.
#   ok:    {"status":"ok","path":"<path>"}
#   fail:  {"status":"error","reason":"<reason>","http_code":<code>}

set -uo pipefail

PATH_ARG=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --path) PATH_ARG="$2"; shift 2 ;;
    *) echo "persist-skill: unknown arg $1" >&2; exit 2 ;;
  esac
done

: "${PATH_ARG:?--path required}"

URL="https://developers.cloudflare.com/turnstile/spin/index.md"

mkdir -p "$(dirname "$PATH_ARG")"
tmp=$(mktemp)
http_code=$(curl -sSL -w "%{http_code}" -o "$tmp" "$URL" 2>/dev/null || echo "000")

# Validate: HTTP 200 AND first line is YAML frontmatter (matches the SKILL.md shape).
# Without this check, a 404 would happily write Astro's HTML 404 page to the user's skill path.
if [ "$http_code" = "200" ] && head -1 "$tmp" | grep -q "^---$"; then
  mv "$tmp" "$PATH_ARG"
  echo "persist-skill: wrote $PATH_ARG" >&2
  echo "{\"status\":\"ok\",\"path\":\"$PATH_ARG\"}"
  exit 0
fi

rm -f "$tmp"
echo "persist-skill: refused to write; upstream returned HTTP $http_code or non-frontmatter content" >&2
echo "{\"status\":\"error\",\"reason\":\"upstream_invalid\",\"http_code\":$http_code}"
exit 1
