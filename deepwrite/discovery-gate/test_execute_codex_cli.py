import unittest, tempfile, sys, json
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from execute_codex_cli import read_json_reply,parse_events,run,save
from trial_harness import get_prompts, sha_file

class CodexAdapterTests(unittest.TestCase):
    def test_event_usage(self):
        x='\n'.join([
          json.dumps({'type':'thread.started','thread_id':'tid'}),
          json.dumps({'type':'turn.completed','usage':{'input_tokens':170,'cached_input_tokens':30,'output_tokens':50,'reasoning_output_tokens':10}})])
        self.assertEqual(parse_events(x)['usage']['output_tokens'],50)
    def test_missing_usage_fails(self):
        x='\n'.join([json.dumps({'type':'thread.started','thread_id':'t'}),json.dumps({'type':'turn.completed','usage':{}})])
        with self.assertRaisesRegex(ValueError,'MISSING_USAGE'):parse_events(x)
    def test_invalid_json(self):
        with self.assertRaises(Exception):read_json_reply('not JSON')
    def test_markdown_json(self):
        self.assertEqual(read_json_reply('```json\n{"cards":[]}\n```'),[])
    def test_dry_run_with_frozen_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);prompts=d/'prompts';prompts.mkdir()
            pack={'topic_id':'T01','problem':'TEST ONLY'}
            # Actual frozen topic content does not matter for dry-run manifest gate.
            pm={'input_sha256':'a'*64,'prompts':{}}
            for t in ('T01','T02','T03'):
                for arm,s in get_prompts(pack).items():
                    name=t+'_'+arm+'.txt';(prompts/name).write_text(s,encoding='utf8')
                    pm['prompts'][name]=sha_file(prompts/name)
            manifest=d/'manifest.json';save(manifest,pm)
            args=SimpleNamespace(manifest=manifest,prompts=prompts,out=d/'out',model='test',codex_bin='codex',timeout=600,max_total_tokens=12000,dry_run=True)
            self.assertEqual(run(args),0)
            self.assertFalse(args.out.exists())
    def test_prompt_tamper_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);pp=d/'prompts';pp.mkdir();pm={'input_sha256':'a'*64,'prompts':{}}
            for t in ('T01','T02','T03'):
                for arm in ('A','B'):
                    name=f'{t}_{arm}.txt';(pp/name).write_text('frozen',encoding='utf8');pm['prompts'][name]=sha_file(pp/name)
            m=d/'m.json';save(m,pm)
            (pp/'T01_A.txt').write_text('modified',encoding='utf8')
            a=SimpleNamespace(manifest=m,prompts=pp,out=d/'out',model='model',codex_bin='codex',timeout=3,max_total_tokens=12000,dry_run=True)
            with self.assertRaisesRegex(ValueError,'FROZEN_PROMPT_MISMATCH'):run(a)

if __name__=='__main__': unittest.main()

class SyntheticCliIntegration(unittest.TestCase):
    def test_synthetic_six_process_calls_and_seal(self):
        """Synthetic executable only: checks workflow plumbing, NOT a real model study."""
        import os
        from execute_codex_cli import run
        from trial_harness import seal, load, save, sha_file, get_prompts
        with tempfile.TemporaryDirectory() as td:
            d=Path(td); pp=d/'prompts';pp.mkdir()
            pm={'input_sha256':'a'*64,'prompts':{}}
            for t in ('T01','T02','T03'):
                for a,s in get_prompts({'topic_id':t,'problem':'SYNTHETIC TEST ONLY'}).items():
                    f=pp/f'{t}_{a}.txt';f.write_text(s,encoding='utf8');pm['prompts'][f.name]=sha_file(f)
            manifest=d/'m.json';save(manifest,pm)
            # Safe test-only executable: writes a fixed fixture, returns synthetic JSONL.
            stub=d/'fake_codex'
            stub.write_text('''#!/usr/bin/env python3
import sys,json,uuid,pathlib
if sys.argv[1:3]==['login','status']:sys.exit(0)
assert sys.argv[1]=='exec'
content=sys.stdin.read()
path=pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1])
card={'id':'01','body':'测'*700,'phenomenon':'SYNTHETIC TEST ONLY', 'rivals':[{'id':c} for c in 'ABC'],
  'causal_mechanism':'dummy', 'predictions':[{},{}], 'falsifiers':['dummy'], 'domain_boundary':'dummy',
  'decision_before':'A','decision_after':'B','decision_test':{},'prior_art':[],'evidence':[],
  'novelty_claim':'NO_NOVELTY','review_status':'HYPOTHESIS_UNVERIFIED'}
path.write_text(json.dumps({'cards':[card,card,card]},ensure_ascii=False))
print(json.dumps({'type':'thread.started','thread_id':str(uuid.uuid4())}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':450,'cached_input_tokens':0}}))
''',encoding='utf8')
            stub.chmod(0o755)
            params=SimpleNamespace(manifest=manifest,prompts=pp,out=d/'actual',model='synthetic-test-model',
                codex_bin=str(stub),timeout=60,max_total_tokens=12000,dry_run=False)
            self.assertEqual(run(params),0)
            files=list((d/'actual'/'inbox').glob('T*_?.json'))
            self.assertEqual(len(files),6)
            audit=load(d/'actual'/'CODEX_RUN_AUDIT_PRIVATE.json')
            self.assertEqual(audit['status'],'SIX_EXECUTION_RECEIPTS_PROVISIONAL_PENDING_EXTERNAL_AUDIT_AND_HUMAN_REVIEW')
            self.assertEqual(len(audit['execution_order']),6)
            # Use the ACTUAL validator on this synthetic fixture, not a fake PASS.
            pack=d/'pack.json';save(pack,{'topics':[{'topic_id':t} for t in ('T01','T02','T03')]})
            # Seal must reject because this synthetic pack does not hash to frozen source.
            with self.assertRaises(AssertionError):
                seal(SimpleNamespace(pack=pack,manifest=manifest,inbox=d/'actual'/'inbox',out=d/'sealed'))
