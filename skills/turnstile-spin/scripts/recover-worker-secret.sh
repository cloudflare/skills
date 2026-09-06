#!/usr/bin/env bash
# Run only after approval of the exact existing-Worker secret destination.
# Credential-bearing operations use the approved absolute Wrangler executable.
(
  set +x
  set -euo pipefail
  export WRANGLER_WRITE_LOGS=false
  export WRANGLER_LOG=log
  export WRANGLER_LOG_SANITIZE=true

  : "${PROJECT_ROOT:?PROJECT_ROOT is required}"
  : "${WRANGLER_BIN:?WRANGLER_BIN is required}"
  : "${WRANGLER_VERSION:?WRANGLER_VERSION is required}"
  : "${ACCOUNT_ID:?ACCOUNT_ID is required}"
  : "${SITEKEY:?SITEKEY is required}"
  : "${EXPECTED_DOMAINS_JSON:?EXPECTED_DOMAINS_JSON is required}"
  : "${SECRET_NAME:?SECRET_NAME is required}"
  : "${WORKER_NAME:?WORKER_NAME is required}"

  project_root="$(python3 -I -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$PROJECT_ROOT")"
  wrangler_bin="$(python3 -I -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$WRANGLER_BIN")"
  [[ "$wrangler_bin" = /* && -x "$wrangler_bin" ]] || exit 1
  if [[ "$wrangler_bin" == "$project_root" || "$wrangler_bin" == "$project_root/"* ]]; then
    exit 1
  fi

  actual_version="$(
    "$wrangler_bin" --version |
      python3 -I -c 'import re,sys; m=re.search(r"\b(\d+\.\d+\.\d+)\b", sys.stdin.read()); print(m.group(1) if m else "")'
  )"
  [[ "$actual_version" == "$WRANGLER_VERSION" ]] || exit 1
  python3 -I -c 'import sys; v=tuple(map(int,sys.argv[1].split("."))); raise SystemExit(0 if v >= (4,109,0) else 1)' "$actual_version"

  export CLOUDFLARE_ACCOUNT_ID="$ACCOUNT_ID"
  target_args=(--name "$WORKER_NAME")
  if [[ -n "${WRANGLER_CONFIG:-}" ]]; then
    WRANGLER_CONFIG="$(python3 -I -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$WRANGLER_CONFIG")"
    target_args+=(--config "$WRANGLER_CONFIG")
  fi
  if [[ -n "${WRANGLER_ENV:-}" ]]; then
    target_args+=(--env "$WRANGLER_ENV")
  fi

  "$wrangler_bin" secret list "${target_args[@]}" >/dev/null

  secret="$(
    "$wrangler_bin" turnstile widget get "$SITEKEY" --json |
      jq -er --arg sitekey "$SITEKEY" --argjson expected "$EXPECTED_DOMAINS_JSON" '
        . as $widget
        | select(
            ($widget.sitekey == $sitekey) and
            (($widget.clearance_level | type) == "string") and
            (["no_clearance", "interactive", "managed", "jschallenge"] | index($widget.clearance_level) != null) and
            (($widget.domains | type) == "array") and
            (($widget.secret | type) == "string") and
            ($widget.secret | test("^\\S+$")) and
            (all($expected[]; . as $domain | $widget.domains | index($domain) != null))
          )
        | $widget.secret
      '
  )"

  if ! printf '%s' "$secret" |
    python3 -I -c 'import sys,urllib.parse; print(urllib.parse.urlencode({"secret":sys.stdin.read(),"response":"XXXX.DUMMY.TOKEN.XXXX"}),end="")' |
    curl --disable -sS "https://challenges.cloudflare.com/turnstile/v0/siteverify" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-binary @- |
    python3 -I -c 'import json,sys; d=json.load(sys.stdin); c=d.get("error-codes") or []; raise SystemExit(0 if d.get("success") is False and "invalid-input-response" in c and "invalid-input-secret" not in c else 1)'
  then
    unset secret
    exit 1
  fi

  "$wrangler_bin" secret list "${target_args[@]}" >/dev/null

  if ! printf '%s' "$secret" |
    "$wrangler_bin" secret put "$SECRET_NAME" "${target_args[@]}"
  then
    unset secret
    exit 1
  fi

  "$wrangler_bin" secret list "${target_args[@]}" |
    jq -e --arg name "$SECRET_NAME" 'any(.[]; .name == $name)' >/dev/null
  unset secret
)
