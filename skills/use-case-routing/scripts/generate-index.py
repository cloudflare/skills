#!/usr/bin/env python3
"""
Generate references/index.md from the YAML frontmatter of every
references/use-cases/*.md file.

Usage:
    python3 scripts/generate-index.py

This is a starting point. For production use, swap the regex frontmatter
parser for PyYAML (`pip install pyyaml`) and add validation gates such as:

- All required frontmatter fields present
- `category` matches the controlled vocabulary
- `id` is unique across the corpus
- `related` IDs all exist as files
- `default_path` matches a path heading defined in the body
"""

import re
from pathlib import Path

# Run from the skill root: python3 scripts/generate-index.py
SKILL_ROOT = Path(__file__).resolve().parent.parent
USE_CASES_DIR = SKILL_ROOT / "references" / "use-cases"
OUTPUT_PATH = SKILL_ROOT / "references" / "index.md"

# Display name for each category slug. Files with categories not in this map
# get listed in an "Uncategorized" section so missing entries are visible.
CATEGORY_DISPLAY = {
    "ai-security": "AI Security",
    "multi-vendor-architecture": "Architecture",
    "application-performance-delivery": "Application Performance & Delivery",
    "compliance-data-governance": "Compliance & Data Governance",
    "developer-platform-build": "Developer Platform — Build",
    "developer-platform-operate": "Developer Platform — Operate",
    "getting-started": "Getting Started",
    "industry-verticals": "Industry Verticals",
    "network-application-security": "Network & Application Security",
    "network-connectivity-wan": "Network Connectivity & WAN",
    "observability-analytics": "Observability & Analytics",
    "zero-trust-secure-access": "Zero Trust & Secure Access",
}

# Output order for category sections.
CATEGORY_ORDER = list(CATEGORY_DISPLAY.keys())

# Maximum number of aliases to show in the table. Aliases beyond this stay
# in the file's frontmatter and contribute to fuzzy matching.
ALIAS_PREVIEW_COUNT = 3


def parse_field(fm: str, field: str) -> str:
    """Extract a single-line scalar field from frontmatter."""
    m = re.search(rf"^{re.escape(field)}:\s*(.+?)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_list(fm: str, field: str) -> list[str]:
    """Extract a multi-line list field (each item on its own indented line)."""
    pattern = rf"^{re.escape(field)}:\s*\n((?:  - .+\n?)*)"
    m = re.search(pattern, fm, re.MULTILINE)
    if not m:
        return []
    items = []
    for line in m.group(1).split("\n"):
        line = line.rstrip()
        if line.startswith("  - "):
            v = line[4:].strip().strip('"').strip("'")
            items.append(v)
    return items


def main():
    entries = []
    for f in sorted(USE_CASES_DIR.glob("*.md")):
        text = f.read_text()
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            print(f"WARN: no frontmatter in {f.name}")
            continue
        fm = fm_match.group(1)
        entries.append({
            "id": parse_field(fm, "id"),
            "name": parse_field(fm, "name"),
            "category": parse_field(fm, "category"),
            "description": parse_field(fm, "description"),
            "aliases": parse_list(fm, "aliases"),
            "filename": f.name,
        })

    by_cat = {}
    for e in entries:
        by_cat.setdefault(e["category"], []).append(e)

    out = []
    out.append("# Use case index")
    out.append("")
    out.append(
        "Match the user's question to the closest entry by name, description, "
        "aliases, and keywords. The ID column links to the use case file — "
        "follow the link rather than guessing the path."
    )
    out.append("")
    out.append(
        "This index is auto-generated from the frontmatter of each use case "
        "file. **Do not edit by hand** — see `_template.md` for the source "
        "format and `scripts/generate-index.py` for the generator."
    )
    out.append("")

    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        out.append(f"## {CATEGORY_DISPLAY[cat]}")
        out.append("")
        out.append("| ID | Name | Description | Aliases |")
        out.append("|----|------|-------------|---------|")
        for e in sorted(by_cat[cat], key=lambda x: x["id"]):
            aliases = (
                ", ".join(e["aliases"][:ALIAS_PREVIEW_COUNT])
                if e["aliases"]
                else "—"
            )
            out.append(
                f"| [{e['id']}](use-cases/{e['filename']}) | {e['name']} | "
                f"{e['description']} | {aliases} |"
            )
        out.append("")

    unknown = sorted(set(by_cat.keys()) - set(CATEGORY_ORDER))
    if unknown:
        out.append("## Uncategorized (categories not in display map)")
        out.append("")
        out.append("Add these categories to `CATEGORY_DISPLAY` in this script:")
        out.append("")
        for cat in unknown:
            out.append(f"### {cat}")
            out.append("")
            out.append("| ID | Name | Description | Aliases |")
            out.append("|----|------|-------------|---------|")
            for e in sorted(by_cat[cat], key=lambda x: x["id"]):
                aliases = (
                    ", ".join(e["aliases"][:ALIAS_PREVIEW_COUNT])
                    if e["aliases"]
                    else "—"
                )
                out.append(
                    f"| [{e['id']}](use-cases/{e['filename']}) | {e['name']} | "
                    f"{e['description']} | {aliases} |"
                )
            out.append("")

    OUTPUT_PATH.write_text("\n".join(out))
    print(f"Wrote {len(entries)} entries to {OUTPUT_PATH}")
    print(f"Categories: {sorted(by_cat.keys())}")


if __name__ == "__main__":
    main()
