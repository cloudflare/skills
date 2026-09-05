import json
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import MANIFESTS, ROOT, validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in (*MANIFESTS, ".mcp.json", "logo.svg"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.skill = self.root / "skills/example/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('---\nname: example\ndescription: >-\n  Example skill\n---\n')

    def test_valid_bundle_and_folded_yaml(self):
        self.assertEqual(validate(self.root), [])

    def test_invalid_skill_metadata(self):
        for text, expected in (
            ("# Skill", "missing YAML"),
            ("---\nname: wrong\ndescription: fine\n---", "name must match"),
            ("---\nname: example\ndescription: []\n---", "description must"),
            ("---\nname: [\n---", "SKILL.md:"),
        ):
            with self.subTest(text=text):
                self.skill.write_text(text)
                self.assertTrue(any(expected in error for error in validate(self.root)))

    def test_missing_skill_entrypoint(self):
        self.skill.unlink()
        self.assertTrue(any("SKILL.md:" in error for error in validate(self.root)))

    def test_manifest_drift_and_missing_assets(self):
        path = self.root / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text())
        data.update(version="99.0.0", skills="./missing", mcpServers="../outside")
        path.write_text(json.dumps(data))
        errors = "\n".join(validate(self.root))
        for expected in ("version differs", "path './missing'", "path '../outside'"):
            self.assertIn(expected, errors)

    def test_invalid_manifest_json(self):
        (self.root / "plugin.json").write_text("{")
        self.assertTrue(any("plugin.json:" in error for error in validate(self.root)))
