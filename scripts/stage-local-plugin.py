#!/usr/bin/env python3
"""Stage this checkout in a new local marketplace without installing anything."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stage(root, output):
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError('Marketplace output must be outside the source checkout')
    if output.exists():
        raise ValueError('Use a new output directory; existing marketplaces are never overwritten')
    names = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], text=True)
    sources = []
    for name in sorted(set(filter(None, names.split('\0')))):
        source = root / name
        if not source.exists():  # Tracked deletion in the working tree.
            continue
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            raise ValueError(f'Cannot stage symlink or escaping source: {name}')
        if source.is_file():
            sources.append((source, name))
    plugin = output / 'plugins/cloudflare'
    output.mkdir(parents=True)
    for source, name in sources:
        target = plugin / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    catalog = output / '.agents/plugins/marketplace.json'
    catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps({
        'name': 'cloudflare-dev', 'interface': {'displayName': 'Cloudflare local development'},
        'plugins': [{'name':'cloudflare', 'source':{'source':'local','path':'./plugins/cloudflare'},
                     'policy':{'installation':'AVAILABLE','authentication':'ON_USE'}, 'category':'Developer Tools'}]
    }, indent=2) + '\n')
    return catalog


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        print(stage(ROOT, args.output))
    except (ValueError, OSError) as error:
        parser.error(str(error))
