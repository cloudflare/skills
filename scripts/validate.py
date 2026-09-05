"""Check local bundle structure (not remote links or agent behavior).

Run: python -m pip install -r scripts/requirements.txt
     python scripts/validate.py
     python -m unittest discover -s scripts -p 'test_*.py'
"""

import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json",
             ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json")


def validate(root):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def local_path(value, source):
        check(isinstance(value, str) and bool(value), f"{source}: expected a local path")
        if isinstance(value, str) and value:
            path = (root / value).resolve()
            check(path.is_relative_to(root.resolve()) and path.exists(),
                  f"{source}: missing or outside-bundle path {value!r}")

    metadata = []
    for name in MANIFESTS:
        try:
            data = json.loads((root / name).read_text())
            if not isinstance(data, dict):
                raise ValueError("expected an object")
            metadata.append(data)
            for key in ("name", "version", "description"):
                check(isinstance(data.get(key), str) and bool(data[key].strip()),
                      f"{name}: {key} must be a nonempty string")
                if metadata:
                    check(data.get(key) == metadata[0].get(key),
                          f"{name}: {key} differs from plugin.json")
            for key in ("skills", "mcpServers", "logo"):
                if key in data:
                    local_path(data[key], f"{name}.{key}")
            interface = data.get("interface", {})
            if not isinstance(interface, dict):
                raise ValueError("interface must be an object")
            for key in ("composerIcon", "logo"):
                if key in interface:
                    local_path(interface[key], f"{name}.interface.{key}")
        except (OSError, ValueError) as error:
            errors.append(f"{name}: {error}")

    skills = sorted((root / "skills").iterdir()) if (root / "skills").is_dir() else []
    check(bool(skills), "skills/: no skills found")
    for directory in skills:
        if not directory.is_dir():
            continue
        name = f"skills/{directory.name}/SKILL.md"
        try:
            lines = (root / name).read_text().splitlines()
            if not lines or lines[0] != "---" or "---" not in lines[1:]:
                raise ValueError("missing YAML frontmatter delimiters")
            data = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
            if not isinstance(data, dict):
                raise ValueError("frontmatter must be a mapping")
            check(data.get("name") == directory.name and
                  re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", directory.name),
                  f"{name}: name must match its lowercase hyphenated directory")
            description = data.get("description")
            check(isinstance(description, str) and bool(description.strip()),
                  f"{name}: description must be a nonempty string")
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(f"{name}: {error}")
    return errors


if __name__ == "__main__":
    failures = validate(ROOT)
    print("\n".join(failures) if failures else "Bundle structure is valid.")
    raise SystemExit(bool(failures))
