import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root/'installed bundle'
        shutil.copytree(BUNDLE,self.bundle,ignore=shutil.ignore_patterns('__pycache__'))
        (self.bundle/'revision.txt').write_text('installed-revision')
        self.project=self.root/'project'; self.project.mkdir()

    def run_copy(self,target):
        return subprocess.run(['/bin/bash',str(self.bundle/'scripts/persist-skill.sh'),'--path',str(target)],cwd=self.project,capture_output=True,text=True)

    def test_copies_executing_version_to_client_selected_path(self):
        dest=self.project/'.agents/skills/turnstile-spin'
        result=self.run_copy(dest/'SKILL.md')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'ok')
        for p in self.bundle.rglob('*'):
            if p.is_file(): self.assertEqual(p.read_bytes(),(dest/p.relative_to(self.bundle)).read_bytes())
        self.assertTrue(os.access(dest/'scripts/persist-skill.sh',os.X_OK))

    def test_refuses_nonempty_destination_without_modifying_it(self):
        dest=self.project/'existing'; dest.mkdir(); (dest/'keep').write_text('keep')
        result=self.run_copy(dest/'SKILL.md')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(list(dest.iterdir()),[dest/'keep'])

    def test_refuses_project_escape(self):
        result=self.run_copy(self.root/'outside/SKILL.md')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.root/'outside').exists())

    def test_refuses_source_recursion(self):
        self.bundle=self.project/'bundle'
        shutil.copytree(BUNDLE,self.bundle,ignore=shutil.ignore_patterns('__pycache__'))
        result=self.run_copy(self.bundle/'nested/SKILL.md')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.bundle/'nested').exists())

    def test_refuses_symlinked_bundle_content(self):
        (self.bundle/'external').symlink_to(self.root)
        result=self.run_copy(self.project/'copy/SKILL.md')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.project/'copy').exists())


if __name__ == '__main__': unittest.main()
