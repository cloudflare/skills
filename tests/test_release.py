import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


release=load('prepare-release');staging=load('stage-local-plugin')


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'repo';self.root.mkdir()
        for name in (*release.MANIFESTS,'CHANGELOG.md'):
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)

    def test_updates_all_manifests_and_notes(self):
        current=json.loads((self.root/'plugin.json').read_text())['version']
        major,minor,patch=map(int,current.split('.'));new=f'{major}.{minor}.{patch+1}'
        release.release(self.root,new,'- Test release notes.')
        release.release(self.root,new)
        self.assertTrue(all(json.loads((self.root/name).read_text())['version']==new for name in release.MANIFESTS))
        self.assertIn('- Test release notes.',(self.root/'CHANGELOG.md').read_text())

    def test_rejects_drift_without_partial_writes(self):
        path=self.root/'.codex-plugin/plugin.json';data=json.loads(path.read_text());data['version']='99.0.0';path.write_text(json.dumps(data))
        before={name:(self.root/name).read_bytes() for name in release.MANIFESTS}
        with self.assertRaises(ValueError):release.release(self.root,'100.0.0','- Notes')
        self.assertEqual(before,{name:(self.root/name).read_bytes() for name in release.MANIFESTS})

    def test_rejects_invalid_version_and_empty_notes(self):
        for value,notes in [('v1.2.3','- Notes'),('01.2.3','- Notes'),('100.0.0','')]:
            with self.subTest(value=value,notes=notes), self.assertRaises(ValueError):release.release(self.root,value,notes)

    def test_staging_copies_local_edits_and_excludes_ignored_files(self):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        (self.root/'.gitignore').write_text('secret.env\n')
        (self.root/'secret.env').write_text('ignored synthetic value')
        (self.root/'local-edit.txt').write_text('uncommitted local edit')
        out=self.root.parent/'marketplace'
        catalog=staging.stage(self.root,out)
        entry=json.loads(catalog.read_text())['plugins'][0]
        self.assertEqual(entry['source'],{'source':'local','path':'./plugins/cloudflare'})
        self.assertEqual((out/'plugins/cloudflare/local-edit.txt').read_text(),'uncommitted local edit')
        self.assertFalse((out/'plugins/cloudflare/secret.env').exists())
        self.assertFalse((out/'plugins/cloudflare/.git').exists())
        with self.assertRaises(ValueError):staging.stage(self.root,out)
        with self.assertRaises(ValueError):staging.stage(self.root,self.root/'nested')


if __name__=='__main__':unittest.main()
