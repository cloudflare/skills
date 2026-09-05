"""Run recovery against synthetic Wrangler/curl processes, never cloud APIs."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/recover-worker-secret.sh'


@unittest.skipUnless(shutil.which('jq'), 'jq required')
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.project=self.root/'project'; self.project.mkdir()
        self.bin=self.root/'bin'; self.bin.mkdir()
        for name,source in [('python3',sys.executable),('jq',shutil.which('jq'))]:
            (self.bin/name).symlink_to(source)
        wrangler=self.bin/'wrangler'
        wrangler.write_text('#!'+sys.executable+'''
import os,sys,json
from pathlib import Path
args=sys.argv[1:]
assert 'synthetic-secret' not in ' '.join(args)
assert 'synthetic-secret' not in os.environ.values()
assert os.environ['WRANGLER_WRITE_LOGS']=='false'
assert os.environ['WRANGLER_LOG_SANITIZE']=='true'
if args==['--version']: print('4.109.0')
elif args[:3]==['turnstile','widget','get']:
    print(json.dumps({'sitekey':'key','domains':['example.com'],'clearance_level':'no_clearance','secret':'synthetic-secret'}))
elif args[:2]==['secret','list']:
    assert args[2:]==['--name','existing-worker','--env','staging']
    if os.environ.get('NO_WORKER'): sys.exit(1)
    print('[{"name":"TURNSTILE_SECRET"}]')
elif args[:2]==['secret','put']:
    assert args[2:]==['TURNSTILE_SECRET','--name','existing-worker','--env','staging']
    assert sys.stdin.read()=='synthetic-secret'
    Path(os.environ['WRITE_MARKER']).write_text('written')
else: sys.exit(99)
''');wrangler.chmod(0o755)
        curl=self.bin/'curl';curl.write_text('#!'+sys.executable+'''
import os,sys,json
from urllib.parse import parse_qs
assert 'synthetic-secret' not in ' '.join(sys.argv)
assert 'synthetic-secret' not in os.environ.values()
assert parse_qs(sys.stdin.read())['secret']==['synthetic-secret']
print(json.dumps({'success':False,'error-codes':['invalid-input-secret' if os.environ.get('BAD_SECRET') else 'invalid-input-response']}))
''');curl.chmod(0o755)
        self.marker=self.root/'written'
        self.env={'PATH':str(self.bin),'PROJECT_ROOT':str(self.project),'WRANGLER_BIN':str(wrangler),'WRANGLER_VERSION':'4.109.0','ACCOUNT_ID':'account','SITEKEY':'key','EXPECTED_DOMAINS_JSON':'["example.com"]','SECRET_NAME':'TURNSTILE_SECRET','WORKER_NAME':'existing-worker','WRANGLER_ENV':'staging','WRITE_MARKER':str(self.marker)}

    def run_recovery(self):
        r=subprocess.run(['/bin/bash',str(SCRIPT)],cwd=self.project,env=self.env,capture_output=True,text=True)
        self.assertNotIn('synthetic-secret',r.stdout+r.stderr)
        return r

    def test_validates_then_writes_exact_target(self):
        r=self.run_recovery();self.assertEqual(r.returncode,0,r.stderr);self.assertTrue(self.marker.exists())

    def test_rejects_invalid_secret_before_write(self):
        self.env['BAD_SECRET']='1';self.assertNotEqual(self.run_recovery().returncode,0);self.assertFalse(self.marker.exists())

    def test_rejects_domain_mismatch_before_write(self):
        self.env['EXPECTED_DOMAINS_JSON']='["wrong.example"]';self.assertNotEqual(self.run_recovery().returncode,0);self.assertFalse(self.marker.exists())

    def test_requires_existing_worker(self):
        self.env['NO_WORKER']='1';self.assertNotEqual(self.run_recovery().returncode,0);self.assertFalse(self.marker.exists())

    def test_rejects_version_mismatch(self):
        self.env['WRANGLER_VERSION']='4.110.0';self.assertNotEqual(self.run_recovery().returncode,0);self.assertFalse(self.marker.exists())

    def test_rejects_project_local_executable(self):
        p=self.project/'wrangler';shutil.copy2(self.bin/'wrangler',p);self.env['WRANGLER_BIN']=str(p)
        self.assertNotEqual(self.run_recovery().returncode,0);self.assertFalse(self.marker.exists())


if __name__ == '__main__': unittest.main()
