import json, unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discovery_gate import validate_card,validate_payload
D = {
'id':'T1','phenomenon':'Does cost reduction shift value capture?','phenomenon_status':'OPEN_QUESTION',
'rivals':[{'id':k,'mechanism':f'mechanism {k}','different_prediction':f'outcome {k}'} for k in 'ABC'],
'causal_mechanism':'entry->competition->pricing','predictions':[{'condition':'x','expected_difference':'y','observable_measure':'z'}, {'condition':'not x','expected_difference':'not y','observable_measure':'w'}],
'falsifiers':['If entrant supply did not respond across a measured period'],
'domain_boundary':'non-exclusive standardized markets','decision_before':'launch','decision_after':'validate channel','decision_test':{'before':'A','after':'B','same_information':True,'discriminating_reason':'profit capture'},
'prior_art':['Teece 1986'],'evidence':['https://doi.org/10.1016/0048-7333(86)90027-2'],
'novelty_claim':'APPLICATION_VALUE_CANDIDATE','review_status':'HYPOTHESIS_UNVERIFIED'}
class TestGate(unittest.TestCase):
 def test_valid(self): self.assertFalse(validate_card(D))
 def test_reject_weak_rivals(self):
  c=dict(D,rivals=[D['rivals'][0]]);self.assertIn('RIVALS_LT_3',validate_card(c))
 def test_reject_no_falsifier(self):
  c=dict(D,falsifiers=[]);self.assertIn('MISSING_falsifiers',validate_card(c))
 def test_reject_no_human_receipt(self):
  c=dict(D,review_status='HUMAN_REVIEWED');self.assertIn('HUMAN_REVIEW_RECEIPT_MISSING',validate_card(c))
 def test_reject_scholarly_originality_claim(self):
  c=dict(D,scholarly_originality=True);self.assertIn('SCHOLARLY_ORIGINALITY_UNATTESTED',validate_card(c))
 def test_report(self):
  r=validate_payload({'cards':[D]});self.assertEqual(r['structural_pass'],1);self.assertEqual(r['real_world_validation'],'NOT_RUN')
if __name__=='__main__':unittest.main()
