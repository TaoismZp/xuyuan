"""One purely synthetic regression test; no private writing."""
import subprocess,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).parent
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'before.md').write_text('An old draft.','utf-8')
 (p/'prior.md').write_text('Earlier research says: queue stability depends on available service capacity.','utf-8')
 (p/'after.md').write_text('We propose that queue stability depends on available service capacity.','utf-8')
 (p/'claims.json').write_text(json.dumps([{'id':'A','claim':'Queue capacity limits stability','cause':'higher arrivals','effect':'unstable backlog','scope':'single server','failure_case':'spare workers','reader_decision':'plan headroom','source_class':'prior-writing','search_terms':['service capacity']}]),'utf-8')
 subprocess.run([sys.executable,str(ROOT/'originality_gate.py'),'--claims',str(p/'claims.json'),'--before',str(p/'before.md'),'--after',str(p/'after.md'),'--prior',str(p/'prior.md'),'--output',str(p/'result.json')],check=True)
 obj=json.loads((p/'result.json').read_text('utf-8'))
 assert obj['quality_gate']=='PASS_STRUCTURAL_EVIDENCE_ONLY'
 assert obj['claims'][0]['prior_literal_hits'][str(p/'prior.md')]
 assert obj['semantic_novelty']=='UNVERIFIED_MUST_COMPARE_FULL_CONTEXT'
 print('SYNTHETIC_TEST_PASS')
