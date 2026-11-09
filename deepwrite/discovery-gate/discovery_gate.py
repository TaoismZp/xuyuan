#!/usr/bin/env python3
"""Discovery Gate v0.2 deterministic STRUCTURAL validator (not a quality judge).

Usage: python3 discovery_gate.py candidate_cards.json [--report report.json]
No internet; no external dependencies; never labels ideas as original or true.
"""
import argparse, json, sys, hashlib, re
from pathlib import Path

REQUIRED = ('id','phenomenon','phenomenon_status','rivals','causal_mechanism','predictions',
            'falsifiers','domain_boundary','decision_before','decision_after','decision_test',
            'prior_art','evidence','novelty_claim','review_status')
PHENOMENON_STATUSES = {'OBSERVED_WITH_SOURCE','HYPOTHETICAL','OPEN_QUESTION'}
REVIEW_STATUSES = {'HYPOTHESIS_UNVERIFIED','RESEARCH_REQUIRED','REJECTED','HUMAN_REVIEWED'}
NOVELTY = {'NEW_TO_SOURCE','APPLICATION_VALUE_CANDIDATE','POSSIBLY_NOVEL_UNVERIFIED','NO_NOVELTY'}


def validate_card(card):
    failures = []
    for k in REQUIRED:
        if k not in card or card[k] in ('', None, [], {}):
            failures.append('MISSING_'+k)
    if failures: return failures
    if card['phenomenon_status'] not in PHENOMENON_STATUSES: failures.append('INVALID_PHENOMENON_STATUS')
    rivals = card['rivals']
    if not isinstance(rivals, list) or len(rivals) < 3: failures.append('RIVALS_LT_3')
    else:
        if any(not isinstance(v,dict) or not v.get('id') or not v.get('mechanism') or not v.get('different_prediction') for v in rivals):
            failures.append('RIVALS_INCOMPLETE')
        if len({str(v.get('mechanism','')).strip().lower() for v in rivals if isinstance(v,dict)}) < 3:
            failures.append('RIVALS_NOT_DISTINCT_TEXT')
    pred = card['predictions']
    if not isinstance(pred,list) or len(pred)<2:failures.append('PREDICTIONS_LT_2')
    elif any(not isinstance(p,dict) or not p.get('condition') or not p.get('expected_difference') or not p.get('observable_measure') for p in pred):
        failures.append('PREDICTIONS_INCOMPLETE')
    fal = card['falsifiers']
    if not isinstance(fal,list) or len(fal)<1 or any(not isinstance(f,str) or len(f.strip())<12 for f in fal):
        failures.append('FALSIFIER_REQUIRED')
    if not isinstance(card['prior_art'], list):failures.append('INVALID_PRIOR_ART')
    if not isinstance(card['evidence'],list): failures.append('INVALID_EVIDENCE')
    if card['novelty_claim'] not in NOVELTY: failures.append('INVALID_NOVELTY_CLAIM')
    if card['review_status'] not in REVIEW_STATUSES:failures.append('INVALID_REVIEW_STATUS')
    # Reject auto-claiming actual field validation / scholarly originality without an authorized human review record.
    if card['review_status']=='HUMAN_REVIEWED' and not card.get('human_review_receipt'):
        failures.append('HUMAN_REVIEW_RECEIPT_MISSING')
    if card.get('scholarly_originality') is True: failures.append('SCHOLARLY_ORIGINALITY_UNATTESTED')
    if not isinstance(card['decision_test'],dict) or not {'before','after','same_information','discriminating_reason'}.issubset(card['decision_test']):
        failures.append('DECISION_TEST_INCOMPLETE')
    return sorted(set(failures))


def validate_payload(payload):
    checks=[]
    seen=set()
    for c in payload.get('cards',[]):
        errors=validate_card(c)
        if c.get('id') in seen:errors.append('DUPLICATE_ID')
        seen.add(c.get('id'))
        checks.append({'id':c.get('id','UNKNOWN'),'structural_gate':'PASS' if not errors else 'FAIL','failures':errors,
                       'truth_gate':'UNVERIFIED' if c.get('review_status')!='HUMAN_REVIEWED' else 'REVIEW_RECEIPT_PRESENT_NOT_TRUTH_PROOF'})
    return {'schema':'discovery-structural-report/v0.2','cards_checked':len(checks),
            'structural_pass':sum(c['structural_gate']=='PASS' for c in checks),
            'structural_fail':sum(c['structural_gate']=='FAIL' for c in checks),
            'human_blind_score':'NOT_RUN','real_world_validation':'NOT_RUN','checks':checks}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input');ap.add_argument('--report')
    args=ap.parse_args(); p=Path(args.input)
    payload=json.loads(p.read_text(encoding='utf8')); out=validate_payload(payload)
    out['input_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    msg=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
    if args.report:Path(args.report).write_text(msg,encoding='utf8')
    else:print(msg,end='')
    return 1 if out['structural_fail'] else 0
if __name__=='__main__':sys.exit(main())
