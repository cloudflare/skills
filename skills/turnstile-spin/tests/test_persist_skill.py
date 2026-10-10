"""Offline regression tests for persist-skill.sh (no Cloudflare credentials)."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "persist-skill.sh"


class PersistSkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        # Supply a minimal cloned bundle without contacting GitHub.
        git = self.bin / "git"
        git.write_text('''#!/usr/bin/env bash
set -eu
if [[ "$*" == *sparse-checkout* ]]; then
  exit 0
fi
for destination; do :; done
mkdir -p "$destination/skills/turnstile-spin/scripts"
printf 'fixture skill\\n' > "$destination/skills/turnstile-spin/SKILL.md"
printf '#!/usr/bin/env bash\\n' > "$destination/skills/turnstile-spin/scripts/helper.sh"
''')
        git.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}

    def run_script(self, target):
        result = subprocess.run(
            ["bash", str(SCRIPT), "--path", str(target / "SKILL.md")],
            cwd=self.project,
            env=self.env,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_copy_failure_is_reported(self):
        # A file where the parent directory should be prevents installation.
        parent = self.project / ".claude"
        parent.write_text("keep this file\n")
        result, output = self.run_script(parent / "skills" / "turnstile-spin")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output, {"status": "error", "reason": "copy_failed"})
        self.assertEqual(parent.read_text(), "keep this file\n")

    def test_copy_to_new_or_empty_directory(self):
        for existing in (False, True):
            with self.subTest(existing=existing):
                target = self.project / str(existing) / "turnstile-spin"
                if existing:
                    target.mkdir(parents=True)
                result, output = self.run_script(target)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(output["status"], "ok")
                self.assertEqual((target / "SKILL.md").read_text(), "fixture skill\n")
                self.assertTrue(os.access(target / "scripts" / "helper.sh", os.X_OK))

    def test_nonempty_destination_is_preserved(self):
        target = self.project / "turnstile-spin"
        target.mkdir()
        existing = target / "SKILL.md"
        existing.write_text("existing skill\n")
        result, output = self.run_script(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output["reason"], "target_not_empty")
        self.assertEqual(existing.read_text(), "existing skill\n")


if __name__ == "__main__":
    unittest.main()
