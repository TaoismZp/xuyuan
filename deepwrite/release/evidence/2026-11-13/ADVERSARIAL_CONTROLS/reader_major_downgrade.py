#!/usr/bin/env python3
"""Actual scripted engineering replay; no semantic/model/human quality claim."""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path('/workspace/deepwrite-release')
source = REPO/'deepwrite/tools/tests/test_writing_loop_experimental.py'
spec = importlib.util.spec_from_file_location('audit_fixture', source)
m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m)

class Adversary(m.ScriptedModel):
    def __init__(self):
        super().__init__(clean=True); self.beta_reads = 0
    def generate(self, instructions, prompt, max_output_tokens=6000):
        req=json.loads(prompt); p=req['payload']; role=req['role']
        if role=='reader_source_review':
            report=m.reader_report(p)
            if p['chapter_id']=='beta':
                self.beta_reads+=1
                if self.beta_reads==2:
                    quote=p['manuscript'].split('\n\n')[1]
                    report['findings']=[{'code':'READER_PREREQUISITE_ASSUMED','severity':'MAJOR',
                        'status':'OPEN','paragraph':2,'quote':quote,'reason':'New reader prerequisite remains unexplained.'}]
                    report['reader_checks'][0].update(verdict='REWORK',rationale='Unexplained prerequisite remains.')
            text=json.dumps(report)
        elif role=='review':
            text=json.dumps({'findings':[
                {'id':'cross_alpha','artifact_id':'alpha','kind':'model_review','severity':'MAJOR',
                    'status':'OPEN','issue':'Supply an independent mechanism','evidence':'Paragraph two lacks the mechanism.','paragraph':2},
                {'id':'cross_beta','artifact_id':'beta','kind':'computable','severity':'NOTE','status':'KEEP',
                    'issue':'Keep correct arithmetic','evidence':'Correct calculation visible.','paragraph':2,'reason':'Correct original',
                    'assertion':{'op':'not_contains','value':'ERROR'}}]})
        elif role=='revise':
            text='# Arithmetic fixture\n\nA calculation gives 2 + 2 = 4 because both disjoint pairs are counted once; this added explanation supplies an independent mechanism.\n\nA reader needs a justified decision.\n'
        elif role=='recheck':
            text=json.dumps({'findings':[
                {'id':'cross_alpha','status':'CLOSED','paragraph':2,'evidence':'The mechanism is now explained.'},
                {'id':'cross_beta','status':'KEEP','paragraph':2,'reason':'Correct original','evidence':'Keep arithmetic.'}]})
        else:
            return super().generate(instructions,prompt,max_output_tokens)
        self.calls.append(role)
        return m.loop.transport.ModelResult('audit-'+str(len(self.calls)),'fixture-model',text,
            {'input_tokens':10,'output_tokens':10},'scripted_fixture')

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/'project'; cfg=m.config(root)
        cfg['chapters'].append({'artifact_id':'beta','title':'Second'})
        model=Adversary(); obj=m.loop.WritingLoop(root,cfg,model=model)
        obj.write('chapters/alpha.md',m.CORRECT); obj.write('chapters/beta.md',m.CORRECT)
        try:
            obj.review_cycle('cross',{'alpha':'chapters/alpha.md','beta':'chapters/beta.md'})
            last=json.loads((root/'reviews/cross.1.json').read_text())
            result={'status':'REPRODUCED_FALSE_PASS','reader_major_reported':model.beta_reads==2,
                'guard_status':last['guard']['status'],
                'beta_finding_after_recheck':next(f for f in last['record']['findings'] if f['artifact_id']=='beta'),
                'review_cycle_returned_normally':True}
        except Exception as error:
            result={'status':'BLOCKED_AFTER_PATCH','exception':type(error).__name__,'message':str(error),
                'beta_reader_calls':model.beta_reads}
    result['evidence_kind']='ACTUAL_ENGINEERING_FIXTURE_NOT_MODEL_OR_READER_QUALITY'
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
