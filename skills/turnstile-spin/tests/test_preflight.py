import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/preflight.sh'


class PreflightTests(unittest.TestCase):
    def test_reports_missing_tools_without_python(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(['/bin/bash',str(SCRIPT)],env={'PATH':d},capture_output=True,text=True)
        self.assertEqual(r.returncode,1)
        self.assertEqual(json.loads(r.stdout)['missing'],['bash','curl','python3','jq'])

    def test_checks_only_selected_requirements_without_running_them(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ['bash','curl','python3','jq']:
                p=Path(d)/name; p.write_text('#!/bin/sh\nexit 99\n'); p.chmod(0o755)
            r=subprocess.run(['/bin/bash',str(SCRIPT)],env={'PATH':d},capture_output=True,text=True)
            self.assertEqual(json.loads(r.stdout),{'status':'ok'})
            r=subprocess.run(['/bin/bash',str(SCRIPT),'--env-file'],env={'PATH':d},capture_output=True,text=True)
            self.assertEqual(json.loads(r.stdout)['missing'],['git'])

    def test_unknown_option(self):
        r=subprocess.run(['/bin/bash',str(SCRIPT),'--install'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)


if __name__ == '__main__': unittest.main()
