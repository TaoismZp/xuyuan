"""Actual temporary Git objects protect release/runtime identity, not book quality."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from activation import ACTIVE_ENGINE, ACTIVE_RUNNER, resolve


def h(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def encoded(obj):
    return (json.dumps(obj, indent=2) + '\n').encode()


class TestReleaseIdentity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.g('init', '-q', '--initial-branch=main')
        self.g('config', 'user.name', 'Local engineering fixture')
        self.g('config', 'user.email', 'fixture@example.invalid')
        self.write('deepwrite/versions/v0.1.md', 'Original writing workbench policy.\n')
        self.write('wish-delivery/versions/v7.6.md', 'Original parent policy.\n')
        self.write('wish-delivery/CURRENT.json', encoded({'active_version':'v7.6',
                                                       'active_spec':'wish-delivery/versions/v7.6.md'}))
        self.write('deepwrite/release/runtime.py', 'from helper import VALUE\nprint(VALUE)\n')
        self.write('deepwrite/release/helper.py', 'VALUE="original"\n')
        self.current = {'schema':'deepwrite/current/v1','active_workbench_version':'v0.1',
                        'active_workbench_spec':'deepwrite/versions/v0.1.md',
                        'capability_status':{'automatic_full_book_generation':'NOT_IMPLEMENTED'}}
        self.write('deepwrite/CURRENT.json', encoded(self.current))
        self.impl = self.commit('Pinned implementation; not a release')
        self.record = {'schema':'deepwrite/release-record/v1','status':'ACTIVE_RELEASE',
            'version':'e24.1','workbench_version':'v0.1','implementation_commit':self.impl,
            'runtime_files':[self.item(p) for p in ('deepwrite/release/runtime.py','deepwrite/release/helper.py')],
            'spec':self.item('deepwrite/versions/v0.1.md'),
            'parent':{'version':'v7.6','current_sha256':h(self.read('wish-delivery/CURRENT.json')),
                      'spec':self.item('wish-delivery/versions/v7.6.md')},
            'module_identities':[]}
        self.engine = {'version':'e24.1','implementation_commit':self.impl,
                       'path':'deepwrite/release/runtime.py',
                       'sha256':h(self.read('deepwrite/release/runtime.py')),
                       'release_channel':'STABLE','release_record':'deepwrite/releases/e24.1.json'}
        self.publish()

    def tearDown(self):
        self.temp.cleanup()

    def g(self, *args):
        result = subprocess.run(['git','--no-replace-objects','-C',str(self.root),*args],
                                capture_output=True,check=True)
        return result.stdout.decode().strip()

    def write(self, path, data):
        p=self.root/path; p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data if isinstance(data,bytes) else data.encode())

    def read(self, path):
        return (self.root/path).read_bytes()

    def item(self, path):
        return {'path':path,'sha256':h(self.read(path))}

    def commit(self, message):
        self.g('add','.');self.g('commit','-qm',message)
        return self.g('rev-parse','HEAD')

    def publish(self):
        record=encoded(self.record)
        self.write(self.engine['release_record'],record)
        self.engine['release_record_sha256']=h(record)
        self.current['active_engine']=copy.deepcopy(self.engine)
        self.write('deepwrite/CURRENT.json',encoded(self.current))
        self.activation=self.commit('Fixture activation; no real release or approval claim')

    def test_real_git_release_resolves_engine_without_claiming_book_quality(self):
        actual=resolve(self.root)
        self.assertEqual(actual['status'],ACTIVE_ENGINE)
        self.assertEqual(actual['active_version'],'v0.1')
        self.assertEqual(actual['engine_version'],'e24.1')
        self.assertEqual(actual['implementation_commit'],self.impl)
        self.assertFalse(actual['book_quality_verified_by_resolver'])
        self.assertEqual(actual['project_lock']['activation_commit'],self.activation)

    def test_invalid_implementation_string_rejected(self):
        self.engine['implementation_commit']='not-a-git-commit'
        self.record['implementation_commit']='not-a-git-commit'
        self.publish()
        with self.assertRaisesRegex(ValueError,'IMPLEMENTATION_COMMIT'):
            resolve(self.root)

    def test_nonexistent_real_looking_commit_rejected(self):
        self.engine['implementation_commit']='f'*40;self.record['implementation_commit']='f'*40
        self.publish()
        with self.assertRaisesRegex(ValueError,'GIT_IDENTITY_UNAVAILABLE'):
            resolve(self.root)

    def test_nonancestor_git_object_rejected(self):
        orphan=self.g('commit-tree',self.g('rev-parse','HEAD^{tree}'),'-m','Not in release history')
        self.engine['implementation_commit']=orphan;self.record['implementation_commit']=orphan
        self.publish()
        with self.assertRaisesRegex(ValueError,'GIT_IDENTITY_UNAVAILABLE'):
            resolve(self.root)

    def test_uncommitted_current_cannot_claim_activation(self):
        self.current['uncommitted_claim']='new';self.write('deepwrite/CURRENT.json',encoded(self.current))
        with self.assertRaisesRegex(ValueError,'GIT_FILE_BYTES_MISMATCH'):
            resolve(self.root)

    def test_release_record_bytes_are_frozen_by_current(self):
        self.write(self.engine['release_record'],encoded({**self.record,'status':'REVOKED'}))
        with self.assertRaisesRegex(ValueError,'RECORD_MISMATCH'):
            resolve(self.root)

    def test_uncommitted_record_and_rehashed_pointer_cannot_activate(self):
        record=encoded({**self.record,'note':'Forged local mutation'})
        self.write(self.engine['release_record'],record)
        self.current['active_engine']['release_record_sha256']=h(record)
        self.write('deepwrite/CURRENT.json',encoded(self.current))
        with self.assertRaisesRegex(ValueError,'GIT_FILE_BYTES_MISMATCH'):
            resolve(self.root)

    def test_imported_dependency_tamper_rejected(self):
        self.write('deepwrite/release/helper.py','VALUE="changed"\n')
        with self.assertRaisesRegex(ValueError,'RUNTIME_FILE_BYTES_MISMATCH'):
            resolve(self.root)

    def test_rehashed_dependency_cannot_lie_about_implementation_commit(self):
        self.write('deepwrite/release/helper.py','VALUE="changed"\n')
        self.record['runtime_files'][1]=self.item('deepwrite/release/helper.py')
        self.publish()
        with self.assertRaisesRegex(ValueError,'GIT_FILE_BYTES_MISMATCH'):
            resolve(self.root)

    def test_spec_change_without_release_rejected(self):
        self.write('deepwrite/versions/v0.1.md','Changed writing policy\n')
        with self.assertRaisesRegex(ValueError,'ACTIVE_SPEC_BYTES_MISMATCH'):
            resolve(self.root)

    def test_parent_pointer_change_rejected(self):
        self.write('wish-delivery/CURRENT.json',encoded({'active_version':'v7.7','active_spec':'wish-delivery/versions/v7.6.md'}))
        with self.assertRaisesRegex(ValueError,'PARENT_RELEASE_BINDING_MISMATCH'):
            resolve(self.root)

    def test_parent_spec_change_rejected(self):
        self.write('wish-delivery/versions/v7.6.md','Changed parent policy\n')
        with self.assertRaisesRegex(ValueError,'PARENT_SPEC_BYTES_MISMATCH'):
            resolve(self.root)

    def test_empty_or_duplicate_runtime_inventory_rejected(self):
        for rows,message in (([], 'INVENTORY_REQUIRED'),
                (self.record['runtime_files']+[self.record['runtime_files'][0]],'DUPLICATE_RUNTIME_FILE')):
            self.record['runtime_files']=rows;self.publish()
            with self.assertRaisesRegex(ValueError,message):resolve(self.root)

    def test_entrypoint_must_belong_to_declared_inventory(self):
        self.record['runtime_files']=self.record['runtime_files'][1:];self.publish()
        with self.assertRaisesRegex(ValueError,'ENTRYPOINT_NOT_IN_RUNTIME_INVENTORY'):
            resolve(self.root)

    def test_canonical_paths_required(self):
        self.engine['path']='deepwrite/release/../release/runtime.py';self.publish()
        with self.assertRaisesRegex(ValueError,'UNSAFE_RELATIVE_PATH'):
            resolve(self.root)

    def test_internal_symlink_rejected_even_if_bytes_match(self):
        p=self.root/'deepwrite/release/helper.py';p.unlink()
        p.symlink_to('runtime.py')
        with self.assertRaisesRegex(ValueError,'SYMLINK_RELEASE_FILE'):
            resolve(self.root)

    def test_missing_complete_project_lock_cannot_silently_upgrade(self):
        self.write('PROJECT_LOCK.json',encoded({'resolved_deepwrite_version':'v0.1'}))
        with self.assertRaisesRegex(ValueError,'COMPLETE_ENGINE_LOCK'):
            resolve(self.root,self.root/'PROJECT_LOCK.json')

    def test_same_version_different_engine_project_is_not_match(self):
        lock=resolve(self.root)['project_lock'];lock['implementation_commit']='0'*40
        self.write('PROJECT_LOCK.json',encoded(lock))
        with self.assertRaisesRegex(ValueError,'PROJECT_ACTIVATION_POINTER_MISMATCH'):
            resolve(self.root,self.root/'PROJECT_LOCK.json')

    def test_project_parent_module_and_record_differences_not_match(self):
        for field,value in (('parent',{'version':'v7.5'}),('module_identities',[{'id':'other','commit':'a'*40}]),
                            ('engine_version','older-engine')):
            lock=resolve(self.root)['project_lock'];lock[field]=value
            self.write('PROJECT_LOCK.json',encoded(lock))
            actual=resolve(self.root,self.root/'PROJECT_LOCK.json')
            self.assertEqual(actual['project_alignment'],'PINNED_DIFFERENT_ENGINE_REQUIRES_MIGRATION')
            self.assertIn(field,actual['project_identity_mismatches'])

    def test_complete_project_lock_survives_later_documentation_commit(self):
        lock=resolve(self.root)['project_lock'];self.write('PROJECT_LOCK.json',encoded(lock))
        self.write('README.md','Unrelated later documentation.\n');self.commit('Documentation only')
        actual=resolve(self.root,self.root/'PROJECT_LOCK.json')
        self.assertEqual(actual['project_alignment'],'MATCH')
        self.assertNotEqual(actual['project_lock']['activation_commit'],lock['activation_commit'])

    def test_invalid_project_activation_commit_rejected(self):
        lock=resolve(self.root)['project_lock'];lock['activation_commit']=self.impl
        self.write('PROJECT_LOCK.json',encoded(lock))
        with self.assertRaisesRegex(ValueError,'GIT_IDENTITY_UNAVAILABLE'):
            resolve(self.root,self.root/'PROJECT_LOCK.json')

    def test_legacy_active_runner_requires_same_full_identity(self):
        self.current['active_runner']=self.current.pop('active_engine')
        self.write('deepwrite/CURRENT.json',encoded(self.current));self.commit('Legacy metadata spelling')
        actual=resolve(self.root)
        self.assertEqual(actual['status'],ACTIVE_RUNNER)
        self.assertEqual(actual['engine_version'],'e24.1')


if __name__=='__main__':unittest.main()
