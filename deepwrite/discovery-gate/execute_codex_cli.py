#!/usr/bin/env python3
"""Optional independent Codex CLI runner for a frozen DeepWrite Discovery Gate trial.

Six fresh Codex `exec` processes with separate empty workdirs, read-only sandbox,
no project config and ephemeral sessions. No API key is read by this script.

IMPORTANT: logged-in Codex execution consumes the user's allowed plan quota.
This runner does NOT prove budget parity or reviewers' independence. The existing
`trial_harness.py seal` still validates the resulting submissions.
No retry/replace: any failed attempt is sealed as a protocol deviation.
"""
import argparse
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile

TASKS = ('T01', 'T02', 'T03')
ARMS = ('A', 'B')
ORDER = tuple(f'{t}_{a}' for t in TASKS for a in ARMS)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf8')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json_reply(raw):
    s = raw.strip()
    if s.startswith('```'):
        s = re.sub(r'^```(?:json)?\s*', '', s, count=1)
        s = re.sub(r'\s*```$', '', s, count=1)
    payload = json.loads(s)
    if not isinstance(payload, dict) or not isinstance(payload.get('cards'), list):
        raise ValueError('RESPONSE_NOT_JSON_CARDS')
    return payload['cards']


def parse_events(stdout):
    events=[]
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            raise ValueError('NON_JSON_CODEX_EVENT')
    threads=[e.get('thread_id') for e in events if e.get('type')=='thread.started']
    done=[e.get('usage') for e in events if e.get('type')=='turn.completed']
    failures=[e for e in events if e.get('type') in ('turn.failed','error')]
    tool_events=[e for e in events if e.get('type') in ('item.started','item.completed')
                 and e.get('item',{}).get('type') in ('command_execution','web_search','mcp_tool_call','file_change')]
    if len(threads)!=1 or not threads[0]:
        raise ValueError('MISSING_UNIQUE_THREAD_ID')
    if len(done)!=1 or not isinstance(done[0],dict):
        raise ValueError('MISSING_UNIQUE_TURN_COMPLETION_USAGE')
    if failures:
        raise ValueError('CODEX_EMITTED_FAILURE_EVENT')
    u=done[0]
    for k in ('input_tokens','output_tokens'):
        if not isinstance(u.get(k),int) or u[k]<0:
            raise ValueError('MISSING_USAGE_'+k)
    return {'thread_id':threads[0], 'usage':u,
            'tool_event_types':[e['item'].get('type') for e in tool_events],
            'event_count':len(events)}


def preflight(cli_bin, dry_run):
    resolved=shutil.which(cli_bin)
    if not resolved:
        return 'BLOCKED_CODEX_CLI_NOT_INSTALLED'
    if dry_run:
        return None
    status=subprocess.run([resolved,'login','status'],stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,timeout=20,check=False)
    if status.returncode!=0:
        return 'BLOCKED_CODEX_NOT_LOGGED_IN'
    return None


def run(args):
    expected=load(args.manifest)
    prompts=Path(args.prompts)
    packsha=expected.get('input_sha256')
    if not re.fullmatch(r'[0-9a-f]{64}',str(packsha)):
        raise ValueError('MISSING_FROZEN_SOURCE_SHA')
    for name in ORDER:
        f=prompts/(name+'.txt')
        if not f.is_file() or sha(f)!=expected.get('prompts',{}).get(name+'.txt'):
            raise ValueError('FROZEN_PROMPT_MISMATCH_'+name)
    out=Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise ValueError('OUTPUT_DIRECTORY_NOT_EMPTY_USE_NEW_DIRECTORY_NO_RERUN')
    if args.dry_run:
        print('DRY_RUN_ONLY; six independent Codex exec processes planned; no model calls; no files written')
        return 0
    if not args.model or not args.model.strip():
        print('BLOCKED_EXPLICIT_MODEL_REQUIRED_FOR_MODEL_PARITY', file=sys.stderr)
        return 3
    blocker=preflight(args.codex_bin,False)
    if blocker:
        print(blocker,file=sys.stderr)
        return 3
    if args.max_total_tokens<=0:
        raise ValueError('BAD_TOKEN_CAP')
    out.mkdir(parents=True,exist_ok=True)
    (out/'inbox').mkdir()
    cli=shutil.which(args.codex_bin)
    audit={'schema':'deepwrite/codex-cli-attempt/v0.1','status':'RUN_STARTED',
        'started_at':now(),'model_requested':args.model,'max_total_tokens':args.max_total_tokens,
        'method':'6 fresh codex exec --ephemeral --ignore-user-config --sandbox read-only',
        'source_sha256':packsha,'attempts':[],'guarantees':{
        'context_isolation':'NEW_CLI_PROCESS_AND_EMPTY_WORKSPACE_PER_ARM_SELF_ATTESTED',
        'exact_equal_token_budget':'NOT_ENFORCEABLE_BY_CODEX_CLI_REVIEW_ACTUAL_USAGE',
        'independent_human_review':'NOT_RUN','fair_preregistered_ab':'UNVERIFIED'}}
    # Lock randomized A/B execution order before the first model call.
    execution_order=list(ORDER)
    secrets.SystemRandom().shuffle(execution_order)
    audit['execution_order']=execution_order
    save(out/'CODEX_RUN_AUDIT_PRIVATE.json',audit)
    for name in execution_order:
        task={'name':name,'started_at':now(), 'prompt_sha256':expected['prompts'][name+'.txt']}
        print('RUNNING '+name,flush=True)
        with tempfile.TemporaryDirectory(prefix='dg-codex-'+name+'-') as isolated:
            final=out/(name+'.last_message.txt')
            cmd=[cli,'exec','--json','--ephemeral','--ignore-user-config',
                 '--sandbox','read-only','--skip-git-repo-check','--cd',isolated,
                 '--model',args.model,'--output-last-message',str(final.absolute()),'-']
            try:
                proc=subprocess.run(cmd,input=(prompts/(name+'.txt')).read_text(encoding='utf8'),
                    capture_output=True,text=True,timeout=args.timeout,check=False,env=os.environ.copy())
                (out/(name+'.CODEX_EVENTS_PRIVATE.jsonl')).write_text(proc.stdout,encoding='utf8')
                (out/(name+'.CODEX_STDERR_PRIVATE.txt')).write_text(proc.stderr,encoding='utf8')
                task['returncode']=proc.returncode
                if proc.returncode!=0:
                    raise ValueError('CODEX_EXEC_NONZERO_'+str(proc.returncode))
                parsed=parse_events(proc.stdout)
                if not final.is_file():
                    raise ValueError('CODEX_NO_LAST_MESSAGE')
                cards=read_json_reply(final.read_text(encoding='utf8'))
                u=parsed['usage']
                total=u['input_tokens']+u['output_tokens']
                receipt={'provider':'Codex CLI / ChatGPT login','model':args.model,
                   'timestamp':now(),'input_tokens':u['input_tokens'],
                   'output_tokens':u['output_tokens'],'total_tokens':total,
                   'cached_input_tokens':u.get('cached_input_tokens'),
                   'reasoning_output_tokens':u.get('reasoning_output_tokens'),
                   'max_total_tokens':args.max_total_tokens,'independent_context':True,
                   'execution_isolation_mechanism':'fresh process, ephemeral, empty directory, read-only, ignore-user-config',
                   'thread_id':parsed['thread_id'],'prompt_sha256':task['prompt_sha256'],
                   'source_sha256':packsha,'tool_log':parsed['tool_event_types'],
                   'receipts_reviewer_status':'UNVERIFIED_EXTERNAL'}
                save(out/'inbox'/(name+'.json'),{'schema':'deepwrite/dg-submission/v0.1',
                   'cards':cards,'execution_receipt':receipt})
                task.update({'status':'RUN_COMPLETED_PROVISIONAL','thread_id':parsed['thread_id'],
                    'tokens':total,'cards':len(cards),'tool_event_types':parsed['tool_event_types']})
                if total>args.max_total_tokens:
                    task['status']='BUDGET_CAP_EXCEEDED_PROTOCOL_DEVIATION'
                if parsed['tool_event_types']:
                    task['status']='TOOLS_USED_CHECK_ISOLATION_MANUALLY'
            except Exception as exc:
                task['status']='RUN_FAILED_NOT_RETRIED'
                task['error']=type(exc).__name__+':'+str(exc)[:200]
                save(out/(name+'.FAILURE_PRIVATE.json'),task)
            task['ended_at']=now()
            audit['attempts'].append(task)
            save(out/'CODEX_RUN_AUDIT_PRIVATE.json',audit)
    if len(audit['attempts'])==6 and all(x.get('status')=='RUN_COMPLETED_PROVISIONAL' for x in audit['attempts']):
        audit['status']='SIX_EXECUTION_RECEIPTS_PROVISIONAL_PENDING_EXTERNAL_AUDIT_AND_HUMAN_REVIEW'
    else:
        audit['status']='PROTOCOL_DEVIATION_OR_FAILURE_NO_RERUN'
    audit['completed_at']=now()
    save(out/'CODEX_RUN_AUDIT_PRIVATE.json',audit)
    print(json.dumps({'status':audit['status'],'attempts':len(audit['attempts']),
          'completed':sum(x['status']=='RUN_COMPLETED_PROVISIONAL' for x in audit['attempts']),
          'next':'trial_harness.py seal --pack ... --manifest ... --inbox OUT/inbox --out SEALED' },ensure_ascii=False))
    return 0 if audit['status'].startswith('SIX_EXECUTION_RECEIPTS') else 2


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--prompts',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--model',required=False,default='')
    ap.add_argument('--codex-bin',default='codex')
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--max-total-tokens',type=int,default=12000)
    ap.add_argument('--dry-run',action='store_true')
    return run(ap.parse_args())

if __name__=='__main__':
    sys.exit(main())
