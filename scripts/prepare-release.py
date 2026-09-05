#!/usr/bin/env python3
"""Prepare synchronized plugin versions, or verify a tag before distribution."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.cursor-plugin/plugin.json')


def version(value):
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('Use a stable MAJOR.MINOR.PATCH version without a v prefix')
    return tuple(map(int, value.split('.')))


def release(root, value, notes=None):
    target = version(value)
    paths = [root / p for p in MANIFESTS]
    manifests = [json.loads(p.read_text()) for p in paths]
    current = {m['version'] for m in manifests}
    if len(current) != 1:
        raise ValueError('Manifest versions disagree; resolve the drift first')
    changelog = root / 'CHANGELOG.md'
    text = changelog.read_text()
    heading = f'## {value}\n'
    if notes is None:
        if current != {value} or heading not in text:
            raise ValueError('Tag version must match all manifests and a changelog entry')
        entry = text.split(heading, 1)[1].split('\n## ', 1)[0].strip()
        if not entry:
            raise ValueError('Release notes must not be empty')
        return
    if target <= version(next(iter(current))):
        raise ValueError('New release version must be greater than the current version')
    if not notes.strip() or re.search(r'^##? ', notes, re.M):
        raise ValueError('Provide nonempty release notes without top-level headings')
    if heading in text:
        raise ValueError('Release version already exists in the changelog')
    if '## Unreleased\n' not in text:
        raise ValueError('Changelog requires an Unreleased heading')
    # Validate every input before writing any file.
    for path, data in zip(paths, manifests):
        data['version'] = value
        path.write_text(json.dumps(data, indent=2) + '\n')
    changelog.write_text(text.replace('## Unreleased\n', f'## Unreleased\n\n## {value}\n\n{notes.strip()}\n', 1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', help='MAJOR.MINOR.PATCH, without v')
    parser.add_argument('--notes-file', type=Path, help='Prepare files using these notes; otherwise check only')
    args = parser.parse_args()
    try:
        release(ROOT, args.version, args.notes_file.read_text() if args.notes_file else None)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print('Release files prepared' if args.notes_file else 'Release version verified')
