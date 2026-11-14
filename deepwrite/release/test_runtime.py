"""Actual CLI + temporary Git integration; never a real GitHub release or model run.

All manuscripts here are public synthetic engineering text. No existing private
project is read. --export-dir retains one reproducible fixture, commands and SHA.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import test_identity

SOURCE = Path(__file__).resolve().parents[2]
BUNDLE = (
    'deepwrite/release/runtime.py', 'deepwrite/release/activation.py',
    'deepwrite/qa/checkpoint.py', 'deepwrite/qa/resume_check.py',
    'deepwrite/tools/book_packager_v0.1.py',
    'deepwrite/candidates/e15-review-closure/review_closure_guard.py',
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()


def json_stream(text):
    decoder = json.JSONDecoder(); values=[]; text=text.strip()
    while text:
        value, end=decoder.raw_decode(text)
        values.append(value); text=text[end:].lstrip()
    return values


class TestRuntimeIntegration(unittest.TestCase):
    def setUp(self):
        self.fixture = test_identity.TestReleaseIdentity()
        self.fixture.setUp()
        self.repo = self.fixture.root
        for name in BUNDLE:
            self.fixture.write(name,(SOURCE/name).read_bytes())
        self.fixture.impl = self.fixture.commit('Actual engineering runtime bundle fixture')
        self.fixture.record.update(implementation_commit=self.fixture.impl,
                                  runtime_files=[self.fixture.item(name) for name in BUNDLE])
        self.fixture.engine.update(implementation_commit=self.fixture.impl,
                                  sha256=digest((self.repo/'deepwrite/release/runtime.py').read_bytes()))
        self.fixture.publish()
        self.temp=tempfile.TemporaryDirectory(prefix='deepwrite-public-integration-')
        self.work=Path(self.temp.name)
        self.project=self.work/'project'
        self.seed=b'# Public original material\n\nConcrete facts require stated assumptions.\n'
        (self.work/'original.md').write_bytes(self.seed)
        self.config={'project_id':'PUBLIC_ENGINEERING_FIXTURE','wish':'Preserve a concrete public engineering example.',
                     'channel':'STABLE','modules':{},
                     'sources':[{'path':'original.md','sha256':digest(self.seed)}]}
        self.config_path=self.work/'config.json'
        self.config_path.write_bytes(encoded(self.config))
        self.commands=[]

    def tearDown(self):
        self.temp.cleanup();self.fixture.tearDown()

    def cli(self,*args,repo=None,expected=0):
        repo=repo or self.repo
        cmd=[sys.executable,'-B',str(repo/'deepwrite/release/activation.py'),
             '--root',str(repo),'--run','--',*map(str,args)]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        self.commands.append({'command':cmd,'returncode':result.returncode,
                              'stdout':result.stdout,'stderr':result.stderr})
        self.assertEqual(result.returncode,expected,self.commands[-1])
        values=json_stream(result.stdout)
        if not values:return {'status':'BLOCKED','reason':result.stderr.strip()}
        results=[v for v in values if v.get('schema')!='deepwrite/activated-resolution/v1']
        return results[-1] if results else values[-1]

    def init(self,repo=None,destination=None):
        return self.cli('init',self.config_path,destination or self.project,repo=repo)

    def state_sha(self):
        return digest((self.project/'STATE.json').read_bytes())

    def save_json(self,name,obj):
        path=self.project/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(encoded(obj));return digest(path.read_bytes())

    def prepare_keep(self):
        texts={'front.md':'# Public preface\n\nConcrete assumptions make examples checkable.\n',
               'chapters/01.md':'# Public arithmetic example\n\nConcrete arithmetic: two plus two equals four.\n',
               'tail.md':'# Public closing\n\nConcrete evidence does not certify writing quality.\n'}
        for name,text in texts.items():
            p=self.project/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
        def entry(name):
            raw=(self.project/name).read_bytes()
            return {'relative_path':name,'sha256':digest(raw),'bytes':len(raw)}
        manifest={'working_title':'Public engineering fixture only','expected_chapters':1,
                  'front':entry('front.md'),'tail':entry('tail.md'),
                  'chapters':[{'number':1,'title':'Checkable example',**entry('chapters/01.md')}]}
        artifacts=[];findings=[]
        for i,(name,text) in enumerate(texts.items()):
            aid='artifact_'+str(i);raw=text.encode();paragraph=text.split('\n\n')[1]
            location={'paragraph':2,'sha256':digest(paragraph.encode())}
            version={'path':name,'sha256':digest(raw)}
            artifacts.append({'artifact_id':aid,'baseline':version.copy(),'candidate':version.copy()})
            findings.append({'id':'keep_'+str(i),'artifact_id':aid,'kind':'computable',
                'severity':'NOTE','status':'KEEP','issue':'Preserve the verified concrete statement',
                'reason':'The located statement is correct in this public synthetic example.',
                'evidence':'The exact supplied paragraph contains the retained literal.',
                'location':{'baseline':location.copy(),'candidate':location.copy()},
                'assertion':{'op':'contains','value':'Concrete'}})
        record={'schema':'deepwrite/review-closeout/v1','artifacts':artifacts,
                'coverage':[a['artifact_id'] for a in artifacts],'findings':findings}
        self.save_json('manifest.json',manifest)
        self.save_json('review.json',record)
        frozen_sha=self.save_json('frozen.json',copy.deepcopy(findings))
        return texts,manifest,record,frozen_sha

    def assemble(self,frozen_sha,review='review.json',expected=0):
        return self.cli('assemble',self.project,'--state-sha256',self.state_sha(),
                        '--manifest','manifest.json','--review',review,
                        '--frozen-findings','frozen.json','--frozen-sha256',frozen_sha,expected=expected)

    def test_activation_cli_initializes_actual_lock_and_phase(self):
        result=self.init()
        lock=json.loads((self.project/'PROJECT_LOCK.json').read_text())
        state=json.loads((self.project/'STATE.json').read_text())
        self.assertEqual(result['status'],'PROJECT_INITIALIZED_WITH_RELEASED_ENGINE')
        self.assertEqual(state['phase'],'INITIALIZED')
        self.assertEqual(state['automatic_book_generation'],'EXPERIMENTAL_NOT_ACTIVATED')
        self.assertEqual(state['mandatory_gates'],['e15_actual_file_closeout'])
        self.assertEqual(lock['implementation_commit'],self.fixture.impl)
        self.assertEqual(lock['activation_commit'],self.fixture.activation)
        self.assertEqual((self.project/'sources/0001.md').read_bytes(),self.seed)
        self.assertEqual(digest((self.project/'PROJECT_LOCK.json').read_bytes()),state['files']['PROJECT_LOCK.json'])

    def test_unknown_candidate_cannot_enter_stable_project(self):
        self.config['modules']={'UNACCEPTED_FRAME':True}
        self.config_path.write_bytes(encoded(self.config))
        result=self.cli('init',self.config_path,self.project,expected=2)
        self.assertIn('UNACCEPTED_MODULES_REQUIRE',result['reason'])
        self.assertFalse(self.project.exists())

    def test_guard_off_has_no_cli_entry(self):
        result=self.cli('init',self.config_path,self.project,'--guard','off',expected=2)
        self.assertEqual(result['status'],'ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED')
        self.assertFalse(self.project.exists())

    def test_guard_off_config_is_rejected_instead_of_silently_ignored(self):
        self.config['guard']='off';self.config_path.write_bytes(encoded(self.config))
        result=self.cli('init',self.config_path,self.project,expected=2)
        self.assertIn('MANDATORY_CLOSEOUT_CANNOT_BE_DISABLED',result['reason'])
        self.assertFalse(self.project.exists())

    def test_initialization_never_overwrites_existing_project(self):
        self.init();before=(self.project/'sources/0001.md').read_bytes()
        result=self.cli('init',self.config_path,self.project,expected=2)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual((self.project/'sources/0001.md').read_bytes(),before)

    def test_actual_guard_rejects_fake_close_then_evidenced_keep_assembles(self):
        self.init();texts,_,record,frozen_sha=self.prepare_keep()
        fake=copy.deepcopy(record);fake['findings'][1]['status']='CLOSED'
        fake['findings'][1]['severity']='MAJOR'
        self.save_json('review-fake.json',fake)
        held=self.assemble(frozen_sha,review='review-fake.json',expected=2)
        self.assertEqual(held['status'],'HOLD')
        self.assertIn('non-whitespace',str(held['gate']['errors']))
        self.assertFalse((self.project/'derived/book-0001.md').exists())
        result=self.assemble(frozen_sha)
        self.assertEqual(result['status'],'ASSEMBLED_PENDING_HUMAN')
        self.assertEqual(result['gate']['status'],'PASS_STRUCTURAL_ONLY')
        self.assertEqual(result['literary_quality'],'NOT_CERTIFIED')
        for name,text in texts.items():self.assertEqual((self.project/name).read_text(),text)
        self.assertEqual((self.work/'original.md').read_bytes(),self.seed)
        self.assertEqual(digest(Path(result['artifact']).read_bytes()),result['artifact_sha256'])

    def test_verified_source_is_used_instead_of_untracked_bytecode_cache(self):
        import importlib.util
        import importlib._bootstrap_external as bootstrap
        target=self.repo/'deepwrite/release/activation.py'
        actual_sha=digest(target.read_bytes())
        code=compile('raise RuntimeError("UNTRACKED_CACHE_EXECUTED")\n',str(target),'exec')
        cache=Path(importlib.util.cache_from_source(str(target)))
        cache.parent.mkdir(parents=True,exist_ok=True)
        cache.write_bytes(bootstrap._code_to_timestamp_pyc(code,int(target.stat().st_mtime),target.stat().st_size))
        result=self.cli('identity')
        self.assertEqual(result['status'],'ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED')
        self.assertEqual(digest(target.read_bytes()),actual_sha)
        self.assertNotIn('UNTRACKED_CACHE_EXECUTED',self.commands[-1]['stderr'])

    def test_external_state_sha_is_required_and_checked(self):
        self.init()
        result=self.cli('resume',self.project,'--state-sha256','0'*64,expected=2)
        self.assertIn('EXTERNAL_PROJECT_STATE_SHA_MISMATCH',result['reason'])

    def test_external_frozen_findings_sha_is_checked_before_assembly(self):
        self.init();self.prepare_keep()
        result=self.assemble('0'*64,expected=2)
        self.assertIn('EXTERNAL_FROZEN_FINDINGS_SHA_MISMATCH',result['reason'])
        self.assertFalse((self.project/'derived').exists())

    def test_frozen_source_tamper_is_blocked_on_resume(self):
        self.init();state_sha=self.state_sha()
        (self.project/'sources/0001.md').write_text('tampered public fixture')
        result=self.cli('resume',self.project,'--state-sha256',state_sha,expected=2)
        self.assertIn('PROJECT_FILE_BYTES_MISMATCH',result['reason'])

    def test_old_engine_project_pin_cannot_be_rewritten_silently(self):
        self.init()
        lock=json.loads((self.project/'PROJECT_LOCK.json').read_text());lock['engine_version']='older-runtime'
        raw=encoded(lock);(self.project/'PROJECT_LOCK.json').write_bytes(raw)
        state=json.loads((self.project/'STATE.json').read_text())
        state['files']['PROJECT_LOCK.json']=digest(raw)
        self.save_json('STATE.json',state)
        result=self.cli('resume',self.project,'--state-sha256',self.state_sha(),expected=2)
        self.assertIn('PROJECT_PINNED_TO_DIFFERENT_ENGINE',result['reason'])
        self.assertEqual(json.loads((self.project/'PROJECT_LOCK.json').read_text())['engine_version'],'older-runtime')

    def test_deleted_project_is_restored_from_actual_checkpoint_bytes(self):
        self.init();self.prepare_keep();frozen_sha=digest((self.project/'frozen.json').read_bytes())
        self.assemble(frozen_sha)
        expected_state=self.state_sha()
        state=json.loads((self.project/'STATE.json').read_text())
        expected={name:(self.project/name).read_bytes() for name in ['STATE.json',*state['files']]}
        snap=self.cli('checkpoint',self.project,self.work/'checkpoint','--state-sha256',expected_state)
        self.assertEqual(snap['status'],'PASS_BYTES_ONLY')
        shutil.rmtree(self.project)
        result=self.cli('restore',self.work/'checkpoint',self.work/'restored',
                        '--manifest-sha256',snap['manifest_sha256'])
        self.assertEqual(result['status'],'PASS_BYTES_ONLY')
        restored=self.work/'restored'
        for name,raw in expected.items():self.assertEqual((restored/name).read_bytes(),raw,name)
        resumed=self.cli('resume',restored,'--state-sha256',expected_state)
        self.assertEqual(resumed['phase'],'ASSEMBLED_PENDING_HUMAN')
        self.assertEqual(digest((restored/'STATE.json').read_bytes()),expected_state)

    def test_corrupt_checkpoint_cannot_create_restored_project(self):
        self.init();snap=self.cli('checkpoint',self.project,self.work/'checkpoint','--state-sha256',self.state_sha())
        (self.work/'checkpoint/files/config.json').write_text('tamper')
        result=self.cli('restore',self.work/'checkpoint',self.work/'restored',
                        '--manifest-sha256',snap['manifest_sha256'],expected=2)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertFalse((self.work/'restored').exists())

    def test_fresh_git_clone_loads_same_published_fixture_bytes(self):
        clone=self.work/'new-checkout'
        subprocess.run(['git','clone','-q','--no-hardlinks',str(self.repo),str(clone)],check=True)
        result=self.init(repo=clone,destination=self.work/'new-project')
        self.assertEqual(result['identity']['implementation_commit'],self.fixture.impl)
        self.assertEqual(result['identity']['release_record_sha256'],self.fixture.engine['release_record_sha256'])
        self.assertEqual(result['identity']['activation_commit'],self.fixture.activation)
        self.assertEqual((clone/'deepwrite/release/runtime.py').read_bytes(),(self.repo/'deepwrite/release/runtime.py').read_bytes())


    def git_at(self,repo,*args):
        cmd=['git','-C',str(repo),*args]
        result=subprocess.run(cmd,capture_output=True,text=True,check=True)
        self.commands.append({'command':cmd,'returncode':result.returncode,
                              'stdout':result.stdout,'stderr':result.stderr})
        return result.stdout.strip()

    def clone_fault_restore(self,clone,project,state_sha):
        before=self.cli('identity',repo=clone)
        self.assertEqual(before['implementation_commit'],self.fixture.impl)
        self.git_at(clone,'config','user.name','Local integration fixture')
        self.git_at(clone,'config','user.email','fixture@example.invalid')
        entry=clone/'deepwrite/release/runtime.py'
        original=entry.read_bytes()
        entry.write_bytes(original+b'\n# Deliberately unregistered engineering fault fixture.\n')
        self.git_at(clone,'add','deepwrite/release/runtime.py')
        self.git_at(clone,'commit','-qm','Known-bad runtime fixture; not a release')
        bad_commit=self.git_at(clone,'rev-parse','HEAD')
        rejected=self.cli('identity',repo=clone,expected=2)
        self.assertIn('ACTIVE_RUNNER_BYTES_MISMATCH',rejected['reason'])
        self.assertEqual(digest((project/'STATE.json').read_bytes()),state_sha)
        self.git_at(clone,'checkout','--detach',self.fixture.activation)
        after=self.cli('identity',repo=clone)
        self.assertEqual(after['implementation_commit'],before['implementation_commit'])
        self.assertEqual(entry.read_bytes(),original)
        resumed=self.cli('resume',project,'--state-sha256',state_sha,repo=clone)
        self.assertEqual(resumed['status'],'PROJECT_LOCK_AND_DECLARED_FILES_VERIFIED')
        self.assertEqual(digest((project/'STATE.json').read_bytes()),state_sha)
        self.assertEqual((self.work/'original.md').read_bytes(),self.seed)
        return {'fault_commit':bad_commit,'restored_activation_commit':self.fixture.activation,
                'fault_blocked':True,'same_project_resumed_after_checkout':True,
                'project_state_sha256':state_sha,'source_original_unchanged':True}

    def test_fresh_clone_fault_blocks_then_prior_commit_restores_same_project(self):
        clone=self.work/'fault-checkout'
        subprocess.run(['git','clone','-q','--no-hardlinks',str(self.repo),str(clone)],check=True)
        project=self.work/'cloned-project'
        result=self.init(repo=clone,destination=project)
        self.clone_fault_restore(clone,project,result['state_sha256'])


def export_fixture(destination):
    test=TestRuntimeIntegration('test_deleted_project_is_restored_from_actual_checkpoint_bytes')
    test.setUp()
    try:
        test.test_actual_guard_rejects_fake_close_then_evidenced_keep_assembles()
        state_sha=test.state_sha()
        snap=test.cli('checkpoint',test.project,test.work/'checkpoint','--state-sha256',state_sha)
        expected={name:digest((test.project/name).read_bytes())
                  for name in ['STATE.json',*json.loads((test.project/'STATE.json').read_text())['files']]}
        shutil.rmtree(test.project)
        test.cli('restore',test.work/'checkpoint',test.work/'restored','--manifest-sha256',snap['manifest_sha256'])
        for name,sha in expected.items():
            if digest((test.work/'restored'/name).read_bytes())!=sha:raise AssertionError(name)
        clone=test.work/'fresh-code'
        subprocess.run(['git','clone','-q','--no-hardlinks',str(test.repo),str(clone)],check=True)
        fresh=test.init(repo=clone,destination=test.work/'fresh-project')
        rollback=test.clone_fault_restore(clone,test.work/'fresh-project',fresh['state_sha256'])
        destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
        for name in ('checkpoint','restored','fresh-project'):
            shutil.copytree(test.work/name,destination/name)
        subprocess.run(['git','-C',str(test.repo),'bundle','create',str(destination/'fixture-source.bundle'),'--all'],check=True)
        subprocess.run(['git','-C',str(clone),'bundle','create',str(destination/'fault-and-restore.bundle'),'--all'],check=True)
        receipt={'evidence_kind':'INTEGRATION_FIXTURE_NOT_GITHUB_RELEASE',
                 'model_called':False,'private_manuscript_read':False,
                 'implementation_commit':test.fixture.impl,'activation_commit':test.fixture.activation,
                 'runtime_files':test.fixture.record['runtime_files'],
                 'release_record_sha256':test.fixture.engine['release_record_sha256'],
                 'checkpoint_manifest_sha256':snap['manifest_sha256'],
                 'deleted_project_before_restore':True,'restored_declared_files':expected,
                 'fresh_git_clone_identity_verified':True,'fault_and_checkout_restore':rollback,
                 'source_original_sha256':digest(test.seed)}
        (destination/'COMMANDS.json').write_bytes(encoded(test.commands))
        (destination/'RECEIPT.json').write_bytes(encoded(receipt))
        inventory={p.relative_to(destination).as_posix():digest(p.read_bytes())
                   for p in destination.rglob('*') if p.is_file()}
        (destination/'ARCHIVE_SHA256.json').write_bytes(encoded(inventory))
        print(json.dumps(receipt,indent=2))
    finally:test.tearDown()


if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--export-dir',type=Path)
    args,remaining=parser.parse_known_args()
    if args.export_dir:export_fixture(args.export_dir)
    else:unittest.main(argv=[sys.argv[0],*remaining])
