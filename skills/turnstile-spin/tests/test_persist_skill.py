"""Offline regression tests for persist-skill.sh (no Cloudflare credentials)."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "persist-skill.sh"
BASH = shutil.which("bash")


@unittest.skipUnless(BASH, "bash is required")
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
''', newline="\n")
        git.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}

    def run_script(self, target):
        # Git Bash's launcher prepends its own Git to PATH. Restore the fake
        # inside the shell, after translating its Windows path if necessary.
        result = subprocess.run(
            [BASH, "-c", '''
test_bin="$1"
if command -v cygpath >/dev/null 2>&1; then
  test_bin="$(cygpath -u "$test_bin")"
fi
export PATH="$test_bin:$PATH"
exec "$BASH" "$2" --path "$3"
''', "persist-skill-test", str(self.bin), str(SCRIPT), str(target / "SKILL.md")],
            cwd=self.project,
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
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

    def test_target_outside_project_is_rejected(self):
        for name, target in (
            ("sibling", self.root / "outside" / "turnstile-spin"),
            ("prefix", self.root / "project-evil" / "turnstile-spin"),
            ("dotdot", self.project / ".." / "escaped" / "turnstile-spin"),
        ):
            with self.subTest(name=name):
                result, output = self.run_script(target)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(output, {"status": "error", "reason": "target_outside_project"})
                self.assertFalse(target.exists())

    def test_relative_target_in_project_with_spaces(self):
        renamed = self.root / "project with spaces"
        self.project.rename(renamed)
        self.project = renamed
        result, output = self.run_script(Path(".claude") / "skills" / "turnstile-spin")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output["status"], "ok")
        self.assertEqual(
            (self.project / ".claude" / "skills" / "turnstile-spin" / "SKILL.md").read_text(),
            "fixture skill\n",
        )

    @unittest.skipUnless(os.name == "nt", "Windows path case and drives")
    def test_windows_case_and_drive_boundaries(self):
        target = self.project / "mixed-case" / "turnstile-spin"
        result, output = self.run_script(Path(str(target).upper()))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output["status"], "ok")
        self.assertEqual((target / "SKILL.md").read_text(), "fixture skill\n")
        other_drive = "D:" if self.project.drive.upper() != "D:" else "C:"
        outside = Path(other_drive + "/") / self.root.name / "turnstile-spin"
        result, output = self.run_script(outside)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(output, {"status": "error", "reason": "target_outside_project"})
        self.assertFalse(outside.exists())

    def test_symlink_outside_project_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.project / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"directory symlinks unavailable: {error}")
        target = link / "turnstile-spin"
        result, output = self.run_script(target)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(output, {"status": "error", "reason": "target_outside_project"})
        self.assertFalse((outside / "turnstile-spin").exists())

    def test_python_resolution_failure_is_rejected(self):
        python = self.bin / "python3"
        python.write_text("#!/usr/bin/env bash\nexit 1\n", newline="\n")
        python.chmod(0o755)
        target = self.project / "turnstile-spin"
        result, output = self.run_script(target)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(output, {"status": "error", "reason": "target_outside_project"})
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
