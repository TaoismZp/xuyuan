import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from master_audit_closure import verify, Hold


def b(x):
    return (json.dumps(x, ensure_ascii=False, indent=2) + '\n').encode()

def sha(x):
    return hashlib.sha256(x).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b(value) if isinstance(value, dict) else value)
    return path

class Result:
    returncode = 0
    stdout = '{"status":"SOURCE_RECEIPTS_COMPLETE_SCOPED","read_receipts_verified":1}'
    stderr = ''

class TestMasterAuditBridge(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'private'
        self.bundle = self.root / 'audit'
        self.gate = Path(__file__).resolve().parents[2] / 'master-audit/audit_gate.py'
        book = write(self.project / 'writer_project/book.md', '序言：这是冻结的样本文本。\n第一章：证据不是论证。\n尾声：保留未决。'.encode())
        digest = sha(book.read_bytes())
        self.state = {'status':'ENGINEERING_FIXTURE_ONLY_NOT_LIVE','files':{'book.md':digest}}
        self.config = {'execution_contract':{'mode':'AUTONOMOUS_FULL_DRAFT'}}
        write(self.project / 'writer_project/run_state.json', self.state)
        write(self.project / 'discovery_evidence/research/writer_config.json', self.config)
        write(self.project / 'writer_project/manifest.json', {'chapters':[{'title':'第一章'}]})
        self.result = {'status':'ENGINEERING_FIXTURE_ONLY_NOT_LIVE',
                       'writer_result': {'status':'ENGINEERING_FIXTURE_ONLY_NOT_LIVE'},
                       'bookwide_topology_recheck':{'status':'STRUCTURE_KEPT_MODEL_INTERNAL_ONLY'},
                       'writer_state_sha256': sha((self.project/'writer_project/run_state.json').read_bytes()),
                       'writer_config_sha256': sha((self.project/'discovery_evidence/research/writer_config.json').read_bytes())}
        write(self.project / 'discovery_evidence/RESULT.json', self.result)
        self.binding = {'selected_book_relative':'writer_project/book.md',
                        'selected_book_sha256':digest,'final_read_book_sha256':digest,
                        'writer_result_sha256':sha((self.project/'discovery_evidence/RESULT.json').read_bytes()),
                        'author_acceptance':'NOT_RUN','receipts':['actual_read.json']}
        self.semantic = {'book_sha256':digest,
                         'sections':[{'id':i,'book_sha256':digest,'mechanism':'这里阐明一个独立的具体因果机制，使读者可以迁移到其他场景。','counterargument':'最强反方有证据可查且可以使主结论失效，范围需要严格界定。','response_id':'fixture'} for i in ['FRONT','CH01','TAIL']],
                         'issue_clusters':[],
                         'final_read':{'book_sha256':digest,'status':'READ_CONFIRMED','response_id':'fixture','section_ids':['FRONT','CH01','TAIL']}}
        for name, obj in [('BINDING.json', self.binding),('CONTRACT.json',{}),('MANIFEST.json',{}),('SEMANTIC_LEDGER.json',self.semantic),('actual_read.json',{})]:
            write(self.bundle/name,obj)
        self.mock = patch('master_audit_closure.subprocess.run',return_value=Result())
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def run_check(self):
        return verify(self.project,self.bundle,self.gate)
    def update_binding(self):
        write(self.bundle/'BINDING.json',self.binding)
    def update_semantics(self):
        write(self.bundle/'SEMANTIC_LEDGER.json',self.semantic)
    def update_config(self):
        write(self.project/'discovery_evidence/research/writer_config.json',self.config)
        self.result['writer_config_sha256']=sha((self.project/'discovery_evidence/research/writer_config.json').read_bytes())
        self.update_result()
    def update_result(self):
        write(self.project/'discovery_evidence/RESULT.json',self.result)
        self.binding['writer_result_sha256']=sha((self.project/'discovery_evidence/RESULT.json').read_bytes())
        self.update_binding()

    def test_reject_substituted_gate(self):
        fake = write(self.root / 'candidate_gate.py', b'# fake success')
        with self.assertRaisesRegex(Hold, 'UNTRUSTED_AUDIT_GATE_IDENTITY'):
            verify(self.project, self.bundle, fake)

    def test_positive_fixture_only_not_quality(self):
        out=self.run_check()
        self.assertEqual(out['status'],'ENGINEERING_EVIDENCE_PASS_BOOK_QUALITY_UNVERIFIED')
        self.assertEqual(out['author_acceptance'],'NOT_RUN')
    def test_missing_receipts(self):
        self.binding['receipts']=[]; self.update_binding()
        with self.assertRaisesRegex(Hold,'ACTUAL_READ_RECEIPTS_REQUIRED'):self.run_check()
    def test_stale_book_after_revision(self):
        write(self.project/'writer_project/book.md',b'changed')
        with self.assertRaisesRegex(Hold,'SELECTED_BOOK_SHA_MISMATCH'):self.run_check()
    def test_final_reread_old_hash(self):
        self.semantic['final_read']['book_sha256']='a'*64; self.update_semantics()
        with self.assertRaisesRegex(Hold,'FINAL_READ_STALE'):self.run_check()
    def test_missing_section(self):
        self.semantic['sections']=self.semantic['sections'][:-1]; self.update_semantics()
        with self.assertRaisesRegex(Hold,'WHOLE_CHAPTER_SEMANTIC_COVERAGE_REQUIRED'):self.run_check()
    def test_major_open(self):
        self.semantic['issue_clusters']=[{'id':'P0','severity':'MAJOR','status':'OPEN'}];self.update_semantics()
        with self.assertRaisesRegex(Hold,'UNRESOLVED_MAJOR_ISSUE'):self.run_check()
    def test_sample_gate_not_bypassed(self):
        self.config['execution_contract']['mode']='ASSISTED_AUTHOR_GATED';self.update_config()
        with self.assertRaisesRegex(Hold,'AUTHOR_GATED_MODE_MUST_NOT_SKIP_SAMPLE'):self.run_check()
    def test_stale_result_state(self):
        self.state['status']='AWAIT_AUTHOR_REVIEW';write(self.project/'writer_project/run_state.json',self.state)
        with self.assertRaisesRegex(Hold,'WRITER_STATE_SHA_MISMATCH'):self.run_check()
    def test_wrong_replan_selection(self):
        self.result['bookwide_topology_recheck']['status']='REPLAN_DERIVATION_PENDING_HUMAN';self.update_result()
        with self.assertRaisesRegex(Hold,'REPLAN_MUST_AUDIT_DERIVED_BOOK'):self.run_check()
    def test_final_section_order_missing(self):
        self.semantic['final_read']['section_ids']=['CH01','FRONT','TAIL'];self.update_semantics()
        with self.assertRaisesRegex(Hold,'FINAL_READ_SECTION_ORDER_OR_COVERAGE_FAIL'):self.run_check()
    def test_synthetic_gate_failure(self):
        class Fail:
            returncode=2
            stderr='manifest bad'
            stdout=''
        with patch('master_audit_closure.subprocess.run',return_value=Fail()):
            with self.assertRaisesRegex(Hold,'PR26_SOURCE_AUDIT_GATE_FAILED'):self.run_check()

if __name__=='__main__':unittest.main()
