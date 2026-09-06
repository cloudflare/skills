#!/usr/bin/env bash
# Persists the canonical Spin skill bundle into the current project.

set +x
set -euo pipefail

unset CLOUDFLARE_API_TOKEN CF_API_TOKEN CLOUDFLARE_API_KEY CF_API_KEY
unset CLOUDFLARE_EMAIL CF_API_EMAIL WIDGET_SECRET TURNSTILE_SECRET
unset WRANGLER_BIN WRANGLER_VERSION
unset GITHUB_TOKEN GH_TOKEN GITLAB_TOKEN NPM_TOKEN

need_arg() {
  if [[ -z "${2-}" || "$2" == --* ]]; then
    echo "persist-skill: missing value for $1" >&2
    exit 2
  fi
}

PATH_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) need_arg "$1" "${2-}"; PATH_ARG="$2"; shift 2 ;;
    *) echo "persist-skill: unknown arg $1" >&2; exit 2 ;;
  esac
done

[[ -n "$PATH_ARG" ]] || { echo "persist-skill: --path required" >&2; exit 2; }
if [[ "$(basename "$PATH_ARG")" != "SKILL.md" ]]; then
  echo "persist-skill: --path must end in SKILL.md for a directory-based skill bundle" >&2
  echo '{"status":"error","reason":"file_target_not_supported"}'
  exit 2
fi

for command_name in python3; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "persist-skill: $command_name is required" >&2
    echo "{\"status\":\"error\",\"reason\":\"${command_name}_not_available\"}"
    exit 1
  }
done

PROJECT_ROOT="$(pwd -P)"
TARGET_DIR="$(python3 -I -c 'import os,sys; print(os.path.realpath(os.path.abspath(sys.argv[1])))' "$(dirname "$PATH_ARG")")"
if [[ "$TARGET_DIR" != "$PROJECT_ROOT" && "$TARGET_DIR" != "$PROJECT_ROOT/"* ]]; then
  echo "persist-skill: target must be inside the current project" >&2
  echo '{"status":"error","reason":"target_outside_project"}'
  exit 1
fi
if [[ -e "$TARGET_DIR" ]] && ! python3 -I -c 'import os,sys; raise SystemExit(0 if not os.listdir(sys.argv[1]) else 1)' "$TARGET_DIR"; then
  echo "persist-skill: target directory is not empty" >&2
  echo '{"status":"error","reason":"target_not_empty"}'
  exit 1
fi

# Copy the bundle containing this executing helper, including when invoked via a symlink.
SOURCE_DIR="$(python3 -I -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().parent.parent)' "${BASH_SOURCE[0]}")"
if [[ ! -f "$SOURCE_DIR/SKILL.md" ]]; then
  echo 'persist-skill: executing bundle is missing SKILL.md' >&2
  echo '{"status":"error","reason":"skill_missing"}'
  exit 1
fi

python3 -I - "$SOURCE_DIR" "$TARGET_DIR" <<'PY'
import pathlib
import shutil
import sys

source = pathlib.Path(sys.argv[1]).resolve()
target = pathlib.Path(sys.argv[2]).resolve()
# Never recurse into a destination inside the source, or copy links outside the bundle.
if target == source or source in target.parents:
    raise SystemExit("persist-skill: target must be outside the executing bundle")
for entry in source.rglob("*"):
    if entry.is_symlink():
        raise SystemExit("persist-skill: bundle contains a symlink; copy a regular-file bundle")
if target.exists():
    target.rmdir()
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, target, dirs_exist_ok=False, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
for script in (target / "scripts").glob("*.sh"):
    script.chmod(0o755)
PY

python3 -I - "$PATH_ARG" "$TARGET_DIR" <<'PY'
import json
import pathlib
import sys

path_arg, bundle_root = sys.argv[1], pathlib.Path(sys.argv[2])
scripts = sorted(path.name for path in (bundle_root / "scripts").glob("*.sh"))
print(json.dumps({
    "status": "ok",
    "path": path_arg,
    "bundle_root": str(bundle_root),
    "scripts": scripts,
}))
PY
