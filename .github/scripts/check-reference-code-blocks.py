#!/usr/bin/env python3
"""Warn about fenced code blocks in skills/cloudflare/references/.

The product references in the `cloudflare` skill should route agents to
developers.cloudflare.com, not copy it (see CONTRIBUTING.md). A fenced code
block in a reference is the most reliable sign of copied docs content, so this
check annotates each one as a GitHub Actions warning.

It is advisory: it always exits 0 unless --strict is passed.

Usage: check-reference-code-blocks.py [--strict] [root]
"""

import pathlib
import re
import sys

REFERENCES = pathlib.Path("skills/cloudflare/references")

# Directories that still copy docs and are being edited by open pull requests.
# Remove an entry once its directory is converted to a docs link table.
ALLOWLIST: set[str] = set()

FENCE = re.compile(r"^\s*(```|~~~)")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--strict"]
    strict = "--strict" in sys.argv[1:]
    root = pathlib.Path(args[0]) if args else pathlib.Path(".")
    base = root / REFERENCES
    if not base.is_dir():
        print(f"::error::{REFERENCES} not found under {root.resolve()}")
        return 1

    blocks = 0
    files = 0
    for path in sorted(base.rglob("*.md")):
        product = path.relative_to(base).parts[0]
        if product in ALLOWLIST:
            continue
        opening = None
        found = 0
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not FENCE.match(line):
                continue
            if opening is None:
                opening = number
                rel = path.relative_to(root).as_posix()
                print(
                    f"::warning file={rel},line={number},title=Code block in reference::"
                    "References should link to developers.cloudflare.com instead of "
                    "copying its content. See CONTRIBUTING.md."
                )
                found += 1
            else:
                opening = None
        if found:
            files += 1
            blocks += found

    print(f"{blocks} code block(s) in {files} reference file(s); allowlisted: {', '.join(sorted(ALLOWLIST)) or 'none'}")
    return 1 if strict and blocks else 0


if __name__ == "__main__":
    sys.exit(main())
