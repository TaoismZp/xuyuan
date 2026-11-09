import json, tempfile, unittest
from pathlib import Path
from trial_harness import prepare, validate_submission, seal, blind, aggregate, load, save, hanzi
from types import SimpleNamespace

class TrialHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name)
        self.pack=self.r/'pack.json'
        save(self.pack,{'trial_id':'synthetic-unit-test','topics':[{'topic_id':f'T{i:02d}','problem':'SYNTHETIC TEST ONLY'} for i in range(1,4)]})
        prepare(SimpleNamespace(pack=self.pack,out=self.r/'prepared'))
        self.pm=load(self.r/'prepared'/'PROMPT_MANIFEST.json')
    def tearDown(self):self.temp.cleanup()
    def card(self):
        return {'id':'001','body':'测'*700,'phenomenon':'SYNTHETIC TEST','phenomenon_status':'HYPOTHETICAL',
        'rivals':[{'id':k,'mechanism':'mechanism '+k,'different_prediction':'differing '+k} for k in 'ABC'],
        'causal_mechanism':'synthetic x affects y','predictions':[{'condition':'a','expected_difference':'b','observable_measure':'c'}, {'condition':'not a','expected_difference':'not b','observable_measure':'d'}],
        'falsifiers':['A synthetic observed exception'], 'domain_boundary':'synthetic','decision_before':'A','decision_after':'B',
        'decision_test':{'before':'A','after':'B','same_information':True,'discriminating_reason':'dummy'},
        'prior_art':[],'evidence':[], 'novelty_claim':'NO_NOVELTY', 'review_status':'HYPOTHESIS_UNVERIFIED'}
    def submission(self,topic,arm):
        return {'cards':[self.card() for _ in range(3)],'execution_receipt':{'provider':'MOCK','model':'mock-v1','timestamp':'2099-01-01T00:00Z','input_tokens':100,'output_tokens':200,'total_tokens':300,'max_total_tokens':12000,'independent_context':True,'tool_log':[],
        'prompt_sha256':self.pm['prompts'][f'{topic}_{arm}.txt'],'source_sha256':self.pm['input_sha256']}}
    def test_six_separate_prompts(self): self.assertEqual(len(self.pm['prompts']),6)
    def test_different_prompt_methods(self):
        a=(self.r/'prepared'/'T01_A.txt').read_text();b=(self.r/'prepared'/'T01_B.txt').read_text()
        self.assertNotEqual(a,b);self.assertIn('冻结题目包',a);self.assertIn('冻结题目包',b)
    def test_missing_submission_blocks(self):
        rc=seal(SimpleNamespace(pack=self.pack,manifest=self.r/'prepared'/'PROMPT_MANIFEST.json',inbox=self.r/'inbox',out=self.r/'prepared'))
        self.assertEqual(rc,2);self.assertEqual(load(self.r/'prepared'/'SEAL_REPORT.json')['status'],'BLOCKED_INCOMPLETE_OR_INVALID')
    def test_invalid_receipt_blocks(self):
        s=self.submission('T01','A');s['execution_receipt']['prompt_sha256']='FAKE'
        self.assertIn('PROMPT_SHA_MISMATCH',validate_submission(s,'T01','A',self.pm,self.r))
    def test_hanzi_bounds(self):
        s=self.submission('T01','A');s['cards'][0]['body']='测'*699
        self.assertTrue(any('LENGTH' in x for x in validate_submission(s,'T01','A',self.pm,self.r)))
    def test_seal_and_blind_on_synthetic_only(self):
        (self.r/'inbox').mkdir()
        for t in ('T01','T02','T03'):
            for arm in ('A','B'):save(self.r/'inbox'/f'{t}_{arm}.json',self.submission(t,arm))
        rc=seal(SimpleNamespace(pack=self.pack,manifest=self.r/'prepared'/'PROMPT_MANIFEST.json',inbox=self.r/'inbox',out=self.r/'prepared'))
        self.assertEqual(rc,0)
        blind(SimpleNamespace(sealed=self.r/'prepared'/'SEALED_RESPONSES.json',sealreport=self.r/'prepared'/'SEAL_REPORT.json',out=self.r/'blind',keydir=self.r/'secret'))
        rev=load(self.r/'blind'/'REVIEWER_ANONYMOUS_CARDS.json')
        self.assertEqual(len(rev['cards']),18)
        self.assertNotIn('arm',json.dumps(rev))
        self.assertEqual(len(load(self.r/'secret'/'SECRET_BLIND_MAP_DO_NOT_SEND.json')),18)
        self.assertFalse((self.r/'blind'/'SECRET_BLIND_MAP_DO_NOT_SEND.json').exists())
        cards=rev['cards']
        for reader in ('reader-one','reader-two'):
            scores=[]
            for card in cards:
                scores.append({'blind_code':card['blind_code'],'scores':{k:3 for k in ('mechanism','divergent_prediction','falsifier','evidence','decision_delta')},
                  'excerpt':card['body'][:15],'decision_before':'A','decision_after':'B','reason':'synthetic test only'})
            save(self.r/f'{reader}.json',{'reviewer_id':reader,'attestation':{'human_independent':True,'blind_to_arm':True,'seen_other_answers':False},'reviews':scores})
        aggregate(SimpleNamespace(packet=self.r/'blind'/'REVIEWER_ANONYMOUS_CARDS.json',key=self.r/'secret'/'SECRET_BLIND_MAP_DO_NOT_SEND.json',reviews=[self.r/'reader-one.json',self.r/'reader-two.json'],out=self.r/'mock_aggregate.json'))
        self.assertEqual(load(self.r/'mock_aggregate.json')['overall_difference_B_minus_A'],0)
        self.assertEqual(load(self.r/'mock_aggregate.json')['status'],'PROVISIONAL_SELF_ATTESTED_EXTERNAL_AUDIT_PENDING')

if __name__=='__main__':unittest.main()
