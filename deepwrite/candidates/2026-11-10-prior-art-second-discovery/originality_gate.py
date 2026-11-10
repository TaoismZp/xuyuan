#!/usr/bin/env python3
"""Small evidence-preserving DeepWrite candidate. Not an automatic semantic judge.

Usage: python originality_gate.py --claims claims.json --before old.md \
    --after new.md --prior oldbook.md --output result.json
All input and output files remain local; the script never transmits them.
"""
import argparse,hashlib,json,re
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nearby(s,word,radius=85):
    i=s.find(word)
    if i<0:return None
    return {'index':i,'excerpt':s[max(0,i-radius):i+len(word)+radius].replace('\n',' ')}

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--claims',type=Path,required=True)
    a.add_argument('--before',type=Path,required=True)
    a.add_argument('--after',type=Path,required=True)
    a.add_argument('--prior',type=Path,action='append',default=[])
    a.add_argument('--output',type=Path,required=True)
    args=a.parse_args()
    claims=json.loads(args.claims.read_text('utf-8'))
    if not isinstance(claims,list):raise ValueError('claims must be JSON array')
    newer=args.after.read_text('utf-8')
    old={str(p):p.read_text('utf-8') for p in args.prior}
    result={'schema':'deepwrite-prior-art-candidate/v0.1','input_sha256':{str(p):digest(p) for p in [args.claims,args.before,args.after]+args.prior},'claims':[]}
    for claim in claims:
        required=['id','claim','cause','effect','scope','failure_case','reader_decision','source_class','search_terms']
        missing=[k for k in required if not claim.get(k)]
        hits={name:[{'search_term':w,**m} for w in claim.get('search_terms',[]) if (m:=nearby(s,w))] for name,s in old.items()}
        mentioned=any(w in newer for w in claim.get('search_terms',[]))
        result['claims'].append({'id':claim.get('id'),'claim':claim.get('claim'),'missing_fields':missing,
            'candidate_mentions_any_search_term':mentioned,'prior_literal_hits':hits,
            'manual_decision':'REQUIRED_NO_AUTO_NOVELTY_JUDGMENT'})
    result['structural_complete']=all(not x['missing_fields'] and x['candidate_mentions_any_search_term'] for x in result['claims'])
    result['quality_gate']='PASS_STRUCTURAL_EVIDENCE_ONLY' if result['structural_complete'] else 'INCOMPLETE'
    result['semantic_novelty']='UNVERIFIED_MUST_COMPARE_FULL_CONTEXT'
    result['human_evaluation']='PENDING'
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result['quality_gate'],args.output)
if __name__=='__main__':main()
