"""Check observable validator failures using disposable, tracked packages."""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', ROOT / 'scripts/validate-package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '.venv'))
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)

    def test_valid_package(self):
        self.assertEqual(validator.check(self.root), [])

    def test_version_drift(self):
        p = self.root / '.codex-plugin/plugin.json'
        data = json.loads(p.read_text()); data['version'] = '99.0.0'
        p.write_text(json.dumps(data))
        self.assertTrue(any('version differs' in e for e in validator.check(self.root)))

    def test_missing_reference_and_stale_inventory(self):
        p = self.root / 'README.md'
        p.write_text(p.read_text().replace('| agents-sdk |', '| nonexistent-skill |') + '\n[missing](missing.md)\n')
        errors = validator.check(self.root)
        self.assertTrue(any('skill inventory' in e for e in errors))
        self.assertTrue(any('missing.md' in e for e in errors))

    def test_escaping_asset(self):
        p = self.root / '.codex-plugin/plugin.json'
        data = json.loads(p.read_text()); data['interface']['logo'] = '../outside.svg'
        p.write_text(json.dumps(data))
        self.assertTrue(any('escaping package path' in e for e in validator.check(self.root)))


if __name__ == '__main__':
    unittest.main()
