#!/usr/bin/env bash
# Check local dependencies without credentials, installs, or network requests.
set -eu
commands=(bash curl python3 jq)
for arg in "$@"; do
  case "$arg" in
    --env-file) commands+=(git) ;;
    *) printf 'preflight: unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done
missing=()
for name in "${commands[@]}"; do
  command -v "$name" >/dev/null 2>&1 || missing+=("$name")
done
if (( ${#missing[@]} )); then
  printf '{"status":"missing_dependencies","missing":['
  sep=''
  for name in "${missing[@]}"; do
    printf '%s"%s"' "$sep" "$name"
    sep=','
  done
  printf ']}\n'
  exit 1
fi
printf '{"status":"ok"}\n'
