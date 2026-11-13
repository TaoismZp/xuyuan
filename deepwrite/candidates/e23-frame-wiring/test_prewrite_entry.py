import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from prewrite_entry import prepare, verified_runner


def h(x): return hashlib.sha256(x.encode()).hexdigest()

class PrewriteEntrypointTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.root=Path(self.tmp.name)
  self.root.joinpath('prior.md').write_text('Already known that skill affects the outcome and that a participant can lose after good play.','utf-8')
  self.root.joinpath('original.md').write_text('Rules are fixed in the original domain, while outcomes depend on strategic choices and hidden states.','utf-8')
  self.root.joinpath('source.md').write_text('Source material for the original domain gives multiple payouts and rule distinctions.','utf-8')
  lens=lambda i: dict(id='L'+str(i),source_assumption='Ordinary interpretation of strategic action number '+str(i),
    counterinterpretation='Alternative explanation rejects the baseline decision problem',
    source_mechanism='The original rules force a specified settlement structure',
    source_falsifier='Some valid original situations would contradict this explanation',
    target_default='The trading market is assumed to have the same payoffs',
    target_break='Unlike fixed poker payoffs, trade outcomes differ across legal contracts '+str(i),
    decision_before='Buy because the position and nominal win rate look appealing',
    decision_after='Evaluate the legal ownership and risk premium before buying',
    target_falsifier='If legal claims are in fact identical, the distinction vanishes',
    why_book_architecture_changes='The entry question must change before the technical chapters',
    claim_type='REFRAME',source_quotes=[dict(source_index=0,quote='multiple payouts and rule distinctions')],
    prior_checks=[dict(prior_index=0,verdict='NOT_FOUND_UNVERIFIED',quote='')])
  self.manifest={'schema':'deepwrite/perspective-inversion/v0.1','source_materials':[dict(path='source.md',sha256=h(self.root.joinpath('source.md').read_text()))],
  'prior_drafts':[dict(path='prior.md',sha256=h(self.root.joinpath('prior.md').read_text()))],
  'lenses':[lens(i) for i in range(1,4)]}
  self.save_manifest()
  self.selection={'schema':'deepwrite/perspective-selection/v0.1','manifest_sha256':h(self.manifest_path.read_text()),'selected_lens_id':'L3',
  'classification':'REFRAME','why_this_frame':'It changes the interpretation of investment tasks and therefore supplies a different choice to the intended reader.',
  'strongest_counterargument':'Old manuscripts have most of these ingredients already, so it may be nothing more than a more convenient arrangement.',
  'unique_reader_decision':'The reader identifies the contract and relevant baseline before deciding whether position and range have any application.',
  'author_acceptance':'NOT_CLAIMED','semantic_novelty':'UNVERIFIED'}
  self.save_selection()
  self.config={'project_id':'SYNTHETIC','channel':'SHADOW','run_mode':'fresh','adapter':'fixture','guard':'on','model':'test','working_title':'test','wish':'test',
   'chapters':[{'artifact_id':'A','title':'A'}], 'sources':[dict(path='sources/original.md',sha256=h('test'))],
   'token_budget':2000,'per_call_output_tokens':200,'max_revision_rounds':1}
  self.config_path=self.root/'cfg.json';self.save_config()
  self.proj=self.root/'project';self.out=self.root/'derived.json'
 def tearDown(self):self.tmp.cleanup()
 def save_manifest(self):
  self.manifest_path=self.root/'manifest.json';self.manifest_path.write_text(json.dumps(self.manifest,ensure_ascii=False),'utf-8')
 def save_selection(self):
  self.selection_path=self.root/'selection.json';self.selection_path.write_text(json.dumps(self.selection,ensure_ascii=False),'utf-8')
 def save_config(self):self.config_path.write_text(json.dumps(self.config,ensure_ascii=False),'utf-8')
 def call(self):return prepare(self.config_path,self.manifest_path,self.selection_path,self.proj,self.out)
 def test_actual_wiring_prompts_runner_and_pins_sources(self):
  r=self.call();v=json.loads(self.out.read_text())
  self.assertEqual(r['status'],'PASS_PREWRITE_IDENTITY_AND_PROMPT_WIRING_ONLY')
  self.assertEqual(len(v['sources']),4)
  self.assertIn('E23 SHADOW PERSPECTIVE GOVERNANCE',v['wish'])
  self.assertIn('source-frame selection', (self.proj/'sources/e23_frame_context.md').read_text().lower())
  self.assertEqual(r['quality'],'UNVERIFIED')
 def test_recovered_cannot_drive_new_book(self):
  self.manifest['lenses'][2]['prior_checks'][0]={'prior_index':0,'verdict':'COVERED','quote':'Already known that skill affects the outcome'}
  self.manifest['lenses'][2]['claim_type']='RECOVERED';self.save_manifest();self.selection['manifest_sha256']=h(self.manifest_path.read_text());self.selection['classification']='RECOVERED';self.save_selection()
  with self.assertRaisesRegex(ValueError,'NOT_UNPROVEN_RIVAL'):self.call()
 def test_manifest_tamper(self):
  self.manifest['source_materials'][0]['sha256']='0'*64;self.save_manifest();self.selection['manifest_sha256']=h(self.manifest_path.read_text());self.save_selection()
  with self.assertRaisesRegex(ValueError,'FRAME_SOURCE_OR_PRIOR_CHECK_FAILED'):self.call()
 def test_prepared_config_does_not_live_inside_project(self):
  self.out=self.proj/'derived.json'
  with self.assertRaisesRegex(ValueError,'DERIVED_CONFIG'):self.call()
 def test_refuses_candidate_or_stable_channel(self):
  self.config['channel']='CANDIDATE_OPT_IN';self.save_config()
  with self.assertRaisesRegex(ValueError,'SHADOW_FRESH'):self.call()
 def test_no_authority_faked_by_selection(self):
  self.selection['author_acceptance']='APPROVED';self.save_selection()
  with self.assertRaisesRegex(ValueError,'NO_HUMAN_AUTH'):self.call()
 def test_shadows_only_unverified_novelty(self):
  self.selection['semantic_novelty']='PASS';self.save_selection()
  with self.assertRaisesRegex(ValueError,'UNVERIFIED'):self.call()
 def test_source_collision_stops(self):
  (self.proj/'sources').mkdir(parents=True)
  (self.proj/'sources/e23_frame_manifest.json').write_text('pretend accepted','utf-8')
  with self.assertRaisesRegex(ValueError,'COLLISION'):self.call()
 def test_reader_contract_is_frozen_as_real_downstream_source(self):
  self.config['reader_prior_knowledge_contract']={
   'schema':'deepwrite/reader-prior-contract/v1','known':['ordinary arithmetic'],
   'unknown':['the source rules'],
   'concepts':[{'id':'settlement','first_explained_in':'A','first_used_in':'A','prerequisites':[]}]}
  self.save_config();result=self.call();amended=json.loads(self.out.read_text())
  reader=(self.proj/'sources/e23_reader_prior_contract.json').read_bytes()
  self.assertEqual(result['reader_contract']['contract_sha256'],hashlib.sha256(reader).hexdigest())
  self.assertTrue(any(row['path']=='sources/e23_reader_prior_contract.json' and row['sha256']==hashlib.sha256(reader).hexdigest() for row in amended['sources']))
  self.assertEqual(amended['reader_prior_knowledge_contract'],self.config['reader_prior_knowledge_contract'])
  self.assertIn('downstream runner must call',amended['wish'])
  self.assertIn('not a semantic or human-reader PASS',amended['wish'])
 def test_invalid_declared_reader_dependencies_cannot_be_wired(self):
  self.config['reader_prior_knowledge_contract']={
   'schema':'deepwrite/reader-prior-contract/v1','known':[],'unknown':['the source rules'],
   'concepts':[{'id':'settlement','first_explained_in':'missing','first_used_in':'A','prerequisites':[]}]}
  self.save_config()
  with self.assertRaisesRegex(ValueError,'FIRST_LOCATION_REQUIRED'):self.call()
 def test_preprocess_receipt_records_actual_source_output_identities(self):
  result=self.call();amended=json.loads(self.out.read_text())
  receipt=amended['e23_preprocess_receipt']
  self.assertFalse(receipt['invocation_authenticated'])
  self.assertEqual(receipt['frame_manifest_sha256'],hashlib.sha256(self.manifest_path.read_bytes()).hexdigest())
  self.assertEqual(receipt['context_sha256'],hashlib.sha256((self.proj/'sources/e23_frame_context.md').read_bytes()).hexdigest())
  self.assertEqual(receipt['input_config_sha256'],hashlib.sha256(self.config_path.read_bytes()).hexdigest())
  self.assertEqual(receipt,result['preprocess_receipt'])
  repo=Path(__file__).resolve().parents[3]
  self.assertEqual(len(receipt['module_files']),3)
  for identity in receipt['module_files']:
   self.assertEqual(identity['sha256'],hashlib.sha256((repo/identity['path']).read_bytes()).hexdigest())
   if identity['commit'] is None:self.assertEqual(identity['commit_status'],'UNCOMMITTED_SOURCE_SHA_RECORDED')
 def test_execute_cannot_replace_e18_with_an_arbitrary_script(self):
  arbitrary=self.root/'different_runner.py';arbitrary.write_text('raise SystemExit(0)','utf-8')
  with self.assertRaisesRegex(ValueError,'CANONICAL_E18'):
   verified_runner(arbitrary,hashlib.sha256(arbitrary.read_bytes()).hexdigest())
 def test_execute_requires_actual_e18_expected_source_sha(self):
  canonical=Path(__file__).resolve().parents[2]/'tools/writing_loop_experimental.py'
  with self.assertRaisesRegex(ValueError,'EXPECTED_SHA_REQUIRED'):
   verified_runner(canonical,None)
  with self.assertRaisesRegex(ValueError,'EXPECTED_SHA_REQUIRED'):
   verified_runner(canonical,'0'*64)
  actual=verified_runner(canonical,hashlib.sha256(canonical.read_bytes()).hexdigest())
  self.assertEqual(actual['path'],'deepwrite/tools/writing_loop_experimental.py')
 def test_prewrite_cannot_publish_context_into_code_checkout(self):
  self.proj=Path(__file__).resolve().parents[3]/'prewrite-private-output-must-not-be-created'
  with self.assertRaisesRegex(ValueError,'OUTSIDE_PUBLIC_CODE'):
   self.call()
  self.assertFalse(self.proj.exists())
 def test_prepared_private_config_cannot_be_written_in_public_code_checkout(self):
  self.out=Path(__file__).resolve().parents[3]/'prewrite-private-config-must-not-be-created.json'
  with self.assertRaisesRegex(ValueError,'OUTSIDE_PUBLIC_CODE'):
   self.call()
  self.assertFalse(self.out.exists())
 def test_symlinked_sources_cannot_leak_prewrite_output(self):
  self.proj.mkdir();other=self.root/'elsewhere';other.mkdir()
  (self.proj/'sources').symlink_to(other,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'SYMLINK_REJECTED'):
   self.call()
  self.assertEqual(list(other.iterdir()),[])

if __name__=='__main__':unittest.main()
