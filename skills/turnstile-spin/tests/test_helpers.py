"""Offline helper contracts. No real account, credentials, or network access."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'; self.bin.mkdir()
        for name, source in [('python3', sys.executable), ('jq', shutil.which('jq')), ('basename', shutil.which('basename'))]:
            if source:
                (self.bin / name).symlink_to(source)
        curl = self.bin / 'curl'
        curl.write_text('#!' + sys.executable + '''
import os,sys
sys.stdin.read()
assert 'CLOUDFLARE_API_TOKEN' not in os.environ
assert 'fake-token' not in ' '.join(sys.argv)
if os.environ.get('FAIL_CURL') == '1': sys.exit(7)
print(os.environ['FAKE_RESPONSE'])
if '--write-out' in sys.argv: print('403')
''')
        curl.chmod(0o755)
        self.env = {'PATH': str(self.bin), 'CLOUDFLARE_API_TOKEN': 'fake-token',
                    'CLOUDFLARE_ACCOUNT_ID': 'fake-account', 'FAKE_RESPONSE': '{}'}

    def run_helper(self, name, args=(), data=''):
        return subprocess.run(['/bin/bash', str(SCRIPTS / name), *args], cwd=self.root,
                              env=self.env, input=data, text=True, capture_output=True)

    def test_missing_auth(self):
        del self.env['CLOUDFLARE_API_TOKEN']
        r = self.run_helper('auth-probe.sh')
        self.assertEqual(json.loads(r.stdout)['status'], 'missing_token')

    def test_missing_argument(self):
        r = self.run_helper('widget-create.sh', ['--name'])
        self.assertEqual(r.returncode, 2)

    def test_missing_dependency(self):
        (self.bin / 'python3').unlink()
        r = self.run_helper('widget-create.sh', ['--account-id','x','--name','test','--domains','example.com'])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('python3 is required', r.stderr)

    def test_api_errors_do_not_echo_remote_message(self):
        for response in ['not json', json.dumps({'success':False,'errors':[{'code':10000,'message':'UNTRUSTED_REMOTE_TEXT'}]})]:
            with self.subTest(response=response):
                self.env['FAKE_RESPONSE'] = response
                r = self.run_helper('widget-create.sh', ['--account-id','x','--name','test','--domains','example.com'])
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(json.loads(r.stdout)['status'], 'error')
                self.assertNotIn('UNTRUSTED_REMOTE_TEXT', r.stdout+r.stderr)
                self.assertNotIn('fake-token', r.stdout+r.stderr)

    def test_network_failure(self):
        self.env['FAIL_CURL'] = '1'
        r = self.run_helper('widget-create.sh', ['--account-id','x','--name','test','--domains','example.com'])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)['code'], 0)

    @unittest.skipUnless(shutil.which('jq'), 'jq required for validator tests')
    def test_wrong_widget_secret_rejected(self):
        self.env['FAKE_RESPONSE'] = json.dumps({'success':True,'result':{'sitekey':'key','secret':'different-secret','domains':['example.com'],'clearance_level':'no_clearance'}})
        r = self.run_helper('validate.sh', ['--sitekey','key','--account-id','x','--expected-domains','["example.com"]'], 'fake-secret')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('does not belong', r.stderr)
        self.assertNotIn('different-secret', r.stdout+r.stderr)

    def test_persistence_rejects_file_target(self):
        r = self.run_helper('persist-skill.sh', ['--path', 'rules.md'])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)['reason'], 'file_target_not_supported')


if __name__ == '__main__':
    unittest.main()
