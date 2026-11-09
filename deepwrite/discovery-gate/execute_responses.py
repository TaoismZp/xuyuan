#!/usr/bin/env python3
"""Run frozen A/B prompts as SIX stateless OpenAI Responses API calls.
This is an opt-in runner: requires --model and OPENAI_API_KEY in the runtime.
Does not know previous chat history and sends public study packets only.
No retry/replacement: preserves failures as deviations instead of cherry-picking.
"""
import argparse, json, os, random, secrets, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
from trial_harness import ARMS, TASK_IDS, load, save, sha_file

API_URL='https://api.openai.com/v1/responses'

def extract_text(resp):
    chunks=[]
    for item in resp.get('output',[]):
        if item.get('type')=='message' and item.get('role')=='assistant':
            for c in item.get('content',[]):
                if c.get('type')=='output_text' and isinstance(c.get('text'),str):chunks.append(c['text'])
    return '\n'.join(chunks)

def call_api(key,model,prompt,max_output_tokens,timeout):
    request_data={'model':model, 'input':prompt, 'max_output_tokens':max_output_tokens,'store':False}
    req=urllib.request.Request(API_URL,data=json.dumps(request_data).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as resp:return json.load(resp)

def run(args):
    if args.dry_run:
        print('DRY_RUN_NO_API_CALLS. 6 independent calls would be made, each at most 12k total tokens.')
        return 0
    key=os.environ.get('OPENAI_API_KEY','')
    if not key:
        print('BLOCKED_NO_OPENAI_API_KEY: no requests made; do not include API keys in chat or files.',file=sys.stderr)
        return 3
    if not args.model.strip():
        print('BLOCKED_MODEL_UNSPECIFIED',file=sys.stderr);return 3
    pm=load(args.manifest)
    prompts=Path(args.prompts)
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    order=[f'{t}_{a}' for t in TASK_IDS for a in ARMS]
    secrets.SystemRandom().shuffle(order)
    order_path=out/'EXECUTION_ORDER_AUDIT_PRIVATE.json'
    save(order_path,{'status':'SEALED_RUN_STARTED','model':args.model,'run_order':order,
                     'started_at':datetime.now(timezone.utc).isoformat(),
                     'max_output_tokens':args.max_output_tokens,'max_total_tokens':args.max_total_tokens})
    failures=[]
    for name in order:
        outpath=out/(name+'.json')
        if outpath.exists():
            failures.append(name+':OUTPUT_EXISTS_NO_OVERWRITE');continue
        fname=name+'.txt'
        path=prompts/fname
        if not path.is_file() or sha_file(path)!=pm['prompts'][fname]:
            failures.append(name+':PROMPT_CHANGED_OR_MISSING');continue
        try:
            result=call_api(key,args.model,path.read_text(encoding='utf8'),args.max_output_tokens,args.timeout)
            usage=result.get('usage') or {}
            text=extract_text(result)
            if result.get('status')!='completed':raise ValueError('RESPONSE_NOT_COMPLETED_'+str(result.get('status')))
            cards=json.loads(text)['cards']
            receipt={'provider':'OpenAI Responses API','model':result.get('model',args.model),
                 'timestamp':datetime.now(timezone.utc).isoformat(),
                 'input_tokens':usage.get('input_tokens'), 'output_tokens':usage.get('output_tokens'),
                 'total_tokens':usage.get('total_tokens'),'max_output_tokens':args.max_output_tokens,
                 'max_total_tokens':args.max_total_tokens,'independent_context':True,
                 'execution_isolation_mechanism':'fresh stateless request with store=false, no previous_response_id, no conversation',
                 'response_id':result.get('id'), 'prompt_sha256':pm['prompts'][fname],
                 'source_sha256':pm['input_sha256'], 'tool_log':[]}
            save(outpath,{'schema':'deepwrite/dg-submission/v0.1','cards':cards,'execution_receipt':receipt})
            # Only public research is sent to provider. Raw response retained privately for audit.
            save(out/(name+'.RAW_PRIVATE.json'),result)
            if receipt['total_tokens'] is None or receipt['total_tokens']>args.max_total_tokens:
                failures.append(name+':TOTAL_TOKEN_BUDGET_DEVIATION')
        except Exception as e:
            msg=f'{name}:{type(e).__name__}:{str(e)[:200]}'
            failures.append(msg)
            save(out/(name+'.FAILURE_PRIVATE.json'),{'error':msg,'no_rerun':True,'when':datetime.now(timezone.utc).isoformat()})
    audit=load(order_path);audit['ended_at']=datetime.now(timezone.utc).isoformat();audit['failures']=failures
    audit['status']='ALL_SIX_CALLS_COMPLETED_NOT_HUMAN_REVIEWED' if not failures else 'PROTOCOL_DEVIATION_OR_FAILURE'
    save(order_path,audit)
    print(json.dumps({'status':audit['status'],'failure_count':len(failures),'files':[x.name for x in out.glob('T*_?.json')]},ensure_ascii=False))
    return 2 if failures else 0

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--prompts',required=True);p.add_argument('--out',required=True)
    p.add_argument('--model',default='');p.add_argument('--max-output-tokens',type=int,default=9000)
    p.add_argument('--max-total-tokens',type=int,default=12000)
    p.add_argument('--timeout',type=int,default=200);p.add_argument('--dry-run',action='store_true')
    args=p.parse_args()
    if args.max_output_tokens>args.max_total_tokens: p.error('max output exceeds total cap')
    sys.exit(run(args))
