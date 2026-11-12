import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from activation import resolve
from release_verify import verify


def h(x): return hashlib.sha256(x.encode()).hexdigest()

class TestActivation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for d in ('deepwrite/versions','wish-delivery','deepwrite/tools','deepwrite/releases'):
            (self.root/d).mkdir(parents=True,exist_ok=True)
        (self.root/'deepwrite/versions/v0.1.md').write_text('Stable old workbench\n',encoding='utf-8')
        (self.root/'wish-delivery/CURRENT.json').write_text(json.dumps({'active_version':'v7.6'}),encoding='utf-8')
        self.current={'schema':'deepwrite/current/v1','active_workbench_version':'v0.1',
            'active_workbench_spec':'deepwrite/versions/v0.1.md',
            'capability_status':{'automatic_full_book_generation':'NOT_IMPLEMENTED'}}
        self._current()

    def tearDown(self): self.temp.cleanup()
    def _current(self):
        (self.root/'deepwrite/CURRENT.json').write_text(json.dumps(self.current,sort_keys=True),encoding='utf-8')

    def test_v01_truthful_not_implemented(self):
        r=resolve(self.root)
        self.assertEqual(r['status'],'WORKBENCH_ONLY_NO_LIVE_AUTONOMOUS_RUNNER')
        self.assertIsNone(r['runner'])

    def test_project_pin_does_not_automigrate(self):
        (self.root/'project.json').write_text(json.dumps({'resolved_deepwrite_version':'v0.0'}),encoding='utf-8')
        r=resolve(self.root,self.root/'project.json')
        self.assertEqual(r['project_alignment'],'PINNED_DIFFERENT_VERSION_REQUIRES_MIGRATION')

    def test_lying_active_runner_rejected(self):
        self.current['capability_status']['automatic_full_book_generation']='IMPLEMENTED'
        self._current()
        with self.assertRaisesRegex(ValueError,'CONTRADICTION'): resolve(self.root)

    def test_unmerged_or_tampered_runner_rejected(self):
        p=self.root/'deepwrite/tools/run.py';p.write_text('print(1)\n')
        r=self.root/'deepwrite/releases/record.json'
        r.write_text(json.dumps({'status':'ACTIVE_RELEASE','version':'v0.2','runner_sha256':'x'}))
        self.current['active_workbench_version']='v0.2'
        self.current['active_runner']={'path':'deepwrite/tools/run.py','sha256':h('wrong'),
                'release_channel':'STABLE','release_record':'deepwrite/releases/record.json'}
        self._current()
        with self.assertRaisesRegex(ValueError,'BYTES_MISMATCH'): resolve(self.root)

    def test_fake_release_record_rejected(self):
        payload='print(1)\n';p=self.root/'deepwrite/tools/run.py';p.write_text(payload)
        (self.root/'deepwrite/releases/record.json').write_text(json.dumps({'status':'DRAFT','version':'v0.2','runner_sha256':h(payload)}))
        self.current['active_workbench_version']='v0.2'
        self.current['active_runner']={'path':'deepwrite/tools/run.py','sha256':h(payload),
                'release_channel':'STABLE','release_record':'deepwrite/releases/record.json'}
        self._current()
        with self.assertRaisesRegex(ValueError,'RECORD_MISMATCH'): resolve(self.root)

    def test_approved_active_path_can_resolve_without_claiming_book_quality(self):
        payload='print(1)\n';(self.root/'deepwrite/tools/run.py').write_text(payload)
        (self.root/'deepwrite/releases/record.json').write_text(json.dumps({'status':'ACTIVE_RELEASE','version':'v0.2','runner_sha256':h(payload)}))
        self.current['active_workbench_version']='v0.2'
        self.current['active_runner']={'path':'deepwrite/tools/run.py','sha256':h(payload),
                'release_channel':'STABLE','release_record':'deepwrite/releases/record.json'}
        self._current()
        self.assertEqual(resolve(self.root)['status'],'ACTIVE_RUNNER_BYTES_VERIFIED_CONTENT_QUALITY_NOT_IMPLIED')

    def _promotion(self):
        spec='New specification\n'; runner='print("new")\n'
        (self.root/'deepwrite/versions/v0.2.md').write_text(spec)
        (self.root/'deepwrite/tools/run_new.py').write_text(runner)
        return {'schema':'deepwrite/promotion-request/v1','base_version':'v0.1',
                'base_current_sha256':hashlib.sha256((self.root/'deepwrite/CURRENT.json').read_bytes()).hexdigest(),
                'parent_wish_version':'v7.6','new_version':'v0.2',
                'release_channel':'STABLE','change_scope':'QUALITY_BEHAVIOR_CHANGE',
                'candidate_commit':'a'*40,'rollback_commit':'b'*40,
                'spec':{'path':'deepwrite/versions/v0.2.md','sha256':h(spec)},
                'runner':{'path':'deepwrite/tools/run_new.py','sha256':h(runner)},
                'old_artifact_preserved':True,
                'gates': {k:'PASS' for k in ('engineering','content_quality','author_acceptance','independent_validation','rollback_test','non_regression')},
                'evidence':{**{k:'private_ref_'+k for k in ('engineering','content_quality','author_acceptance','independent_validation','rollback_test','non_regression')}, 'independent_topic_count':3,'reader_count':2},
                'human_authorization_evidence':{'verification':'GITHUB_PROTECTED_PR_APPROVAL_REQUIRED'}}

    def test_promotion_gate_cannot_authorize_human_by_itself(self):
        result=verify(self.root,self._promotion())
        self.assertEqual(result['status'],'STRUCTURAL_READY_NEEDS_GITHUB_AUTHENTICATED_REVIEW')
        self.assertFalse(result['author_identity_verified_by_script'])

    def test_engineering_patch_can_release_with_narrower_evidence(self):
        x=self._promotion();x['change_scope']='ENGINEERING_PATCH'
        x['gates']['author_acceptance']='PENDING'
        x['gates']['content_quality']='PENDING'
        x['gates']['independent_validation']='NOT_RUN'
        x['evidence']['independent_topic_count']=0
        x['evidence']['reader_count']=0
        x['evidence']['no_quality_behavior_change_rationale']='Only repaired source identity readback; no new prompt or selection semantics.'
        self.assertEqual(verify(self.root,x)['status'],'STRUCTURAL_READY_NEEDS_GITHUB_AUTHENTICATED_REVIEW')

    def test_engineering_patch_cannot_ignore_known_failed_content(self):
        x=self._promotion();x['change_scope']='ENGINEERING_PATCH'
        x['evidence']['no_quality_behavior_change_rationale']='Only release metadata changes.'
        x['gates']['content_quality']='FAIL'
        self.assertIn('PATCH_CANNOT_BYPASS_KNOWN_CONTENT_FAILURE',verify(self.root,x)['reasons'])

    def test_engineering_patch_requires_real_regression_evidence(self):
        x=self._promotion();x['change_scope']='ENGINEERING_PATCH'
        x['evidence']['no_quality_behavior_change_rationale']='Only release metadata changes.'
        x['gates']['non_regression']='PENDING'
        self.assertIn('PROMOTION_GATE_NOT_PASS_NON_REGRESSION',verify(self.root,x)['reasons'])

    def test_missing_author_evidence_blocks(self):
        x=self._promotion();x['human_authorization_evidence']=None
        self.assertIn('NO_HUMAN_RELEASE_AUTHORITY',verify(self.root,x)['reasons'])

    def test_stale_current_blocks(self):
        x=self._promotion();x['base_current_sha256']='0'*64
        self.assertIn('STALE_ACTIVE_CURRENT_BYTES',verify(self.root,x)['reasons'])

    def test_missing_reader_reviews_blocks(self):
        x=self._promotion();x['evidence']['reader_count']=1
        self.assertIn('NOT_ENOUGH_INDEPENDENT_READERS',verify(self.root,x)['reasons'])

    def test_missing_real_file_blocks(self):
        x=self._promotion();x['runner']['path']='../../private/work.py'
        self.assertIn('RUNNER_MISSING_OR_UNSAFE',verify(self.root,x)['reasons'])

    def test_failed_quality_gate_blocks_even_if_engineering_passes(self):
        x=self._promotion();x['gates']['content_quality']='PENDING'
        self.assertIn('PROMOTION_GATE_NOT_PASS_CONTENT_QUALITY',verify(self.root,x)['reasons'])

if __name__=='__main__': unittest.main()
