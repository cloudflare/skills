#!/usr/bin/env python3
"""Validate portable packaging and shared native adapter contracts, offline."""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator
from markdown_it import MarkdownIt
from skills_ref import validate

ROOT = Path(__file__).resolve().parents[1]


def check(root):
    errors = []

    def error(path, message):
        errors.append(f"{path.relative_to(root)}: {message}")

    def target(owner, value, base, prefix=False):
        if prefix and not value.startswith('./'):
            error(owner, f"package path must start with './': {value}")
        resolved = (base / value).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
            error(owner, f"missing or escaping package path: {value}")

    portable = {}
    for name in ('plugin', 'mcp'):
        path = root / f'{name}.json'
        data = json.loads(path.read_text())
        schema = json.loads((root / 'schemas/agent-plugins-1.0.0' / f'{name}.schema.json').read_text())
        for problem in Draft202012Validator(schema).iter_errors(data):
            error(path, problem.message)
        portable[name] = data

    for filename in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.cursor-plugin/plugin.json'):
        path = root / filename
        data = json.loads(path.read_text())
        for key in ('name', 'version', 'description'):
            if data.get(key) != portable['plugin'].get(key):
                error(path, f'{key} differs from portable manifest')
        for key in ('skills', 'mcpServers'):
            if key in data:
                target(path, data[key], root, prefix=True)
        interface = data.get('interface', {})
        for value in [interface.get('logo'), interface.get('composerIcon'), *interface.get('screenshots', [])]:
            if value:
                target(path, value, root, prefix=True)
        if 'logo' in data:  # Cursor's native logo field does not require './'.
            target(path, data['logo'], root)

    native = json.loads((root / '.mcp.json').read_text())['mcpServers']
    normalized = {name: {**server, 'type': 'streamable-http' if server['type'] == 'http' else server['type']}
                  for name, server in native.items()}
    if normalized != portable['mcp']['mcpServers']:
        error(root / '.mcp.json', 'native and portable MCP definitions differ')

    skills = {p.parent.name: p.parent for p in (root / 'skills').glob('*/SKILL.md')}
    for path in skills.values():
        for problem in validate(path):
            error(path / 'SKILL.md', problem)
    readme = (root / 'README.md').read_text().split('## Skills\n', 1)[1].split('## MCP Servers', 1)[0]
    listed = set(re.findall(r'^\| ([a-z][a-z0-9-]+) \|', readme, re.M))
    if listed != set(skills):
        error(root / 'README.md', f'skill inventory: missing {sorted(set(skills)-listed)}, stale {sorted(listed-set(skills))}')

    # Git's inventory excludes environments, installed packages, and local scratch files.
    tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'], text=True).split('\0')
    parser = MarkdownIt()
    for filename in filter(None, tracked):
        path = root / filename
        if path.is_symlink():
            target(path, path.name, path.parent)
        if path.suffix == '.md':
            for token in parser.parse(path.read_text()):
                for child in token.children or []:
                    attr = 'href' if child.type == 'link_open' else 'src' if child.type == 'image' else None
                    value = child.attrGet(attr) if attr else None
                    if value:
                        parsed = urlsplit(value)
                        if not parsed.scheme and not parsed.netloc and parsed.path:
                            target(path, unquote(parsed.path), path.parent)
            if filename.startswith('commands/'):
                for value in re.findall(r'`\$\{CLAUDE_PLUGIN_ROOT\}/([^`]+)`', path.read_text()):
                    target(path, value, root)
        if filename.startswith('skills/') and '/scripts/' in filename and path.suffix == '.sh':
            if not path.stat().st_mode & 0o111:
                error(path, 'packaged shell helper is not executable')
            result = subprocess.run(['bash', '-n', str(path)], capture_output=True, text=True)
            if result.returncode:
                error(path, result.stderr.strip())
    return errors


if __name__ == '__main__':
    problems = check(ROOT)
    print('\n'.join(problems) if problems else 'Package validation passed')
    sys.exit(bool(problems))
