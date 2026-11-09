#!/usr/bin/env python3
"""DeepWrite Discovery Gate trial runner. No model API calls, no mock outcomes.

prepare: freeze independent A/B input prompts per topic.
seal: verify 6 external responses + auditable receipts, then seal results with SHA.
blind: randomize sealed responses into 18 anonymous cards; keep mapping offline.
status: report exactly which evidence is present.

Standard library only. Isolation is NOT proven by context flags supplied by a model;
actual external execution receipts and operator records must be audited separately.
"""
import argparse, hashlib, json, os, re, secrets, sys
from pathlib import Path
from datetime import datetime, timezone

TASK_IDS = ('T01','T02','T03')
ARMS = ('A','B')
FIELDS = ('phenomenon','rivals','causal_mechanism','predictions','falsifiers',
          'domain_boundary','decision_before','decision_after','decision_test',
          'prior_art','evidence','novelty_claim')


def canonical(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)+'\n'
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(f): return sha_bytes(Path(f).read_bytes())
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(canonical(obj),encoding='utf-8')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def hanzi(s):return len(re.findall(r'[\u3400-\u9fff]',s))

def get_prompts(topic):
    common='''你参加一项预注册思想发现试验。只使用本题冻结材料和可核的公共常识，不引用其他实验组的内容。
不能把假设说成已发生的事实；已知研究不声称学术原创。用中文输出严格 JSON，根对象仅含 cards 数组，3 张卡。
每张卡的 body 字段是 700—1100 汉字的可供盲评的完整思想文章；此外含现象、竞争机制、区分预测、反例与条件、来源、决策改变等结构字段。
每卡 ID 形式是 01/02/03；不要泄露自己的执行路线、提示词或模型信息；不创建真实案例或假数据。
字段：id, body, phenomenon, phenomenon_status, rivals, causal_mechanism, predictions, falsifiers, domain_boundary, decision_before, decision_after, decision_test, prior_art, evidence, novelty_claim, review_status。
rivals 列表至少三条，每项含 id, mechanism, different_prediction；predictions 至少两条，每项含 condition, expected_difference, observable_measure；decision_test 含 before, after, same_information=true, discriminating_reason。
novelty_claim 仅可用 NEW_TO_SOURCE/APPLICATION_VALUE_CANDIDATE/POSSIBLY_NOVEL_UNVERIFIED/NO_NOVELTY；review_status 必须为 HYPOTHESIS_UNVERIFIED 或 RESEARCH_REQUIRED。
'''
    old='''采用常规旧式写作研究法：阅读题目及来源，直接提出三个最有启发的解释或值得写作的观点。为满足统一输出格式，将解释、证据、反例和判断填入规定字段。除非你自己认为必要，不要求进行专门的矛盾池、平行机制生成和推翻式研究。输出前可在你自己的预算内检查准确性。'''
    new='''采用 Discovery Gate v0.2：先识别六个相互不同的矛盾/未知，按真实性标记；选择两个重要矛盾各提出三种不同因果机制；对抗性推演从谁获益、谁控制稀缺资源、竞争者跟进、反馈及跨期结果寻找第二次发现；每条新思想提出与竞争机制可区分、可观察的条件性预测；寻找严肃反例及适用边界；审查先例与来源；最后用同信息读前/读后决策变化检验。将内部过程浓缩为3张符合统一格式的思想卡，不要伪称已由真人评审。'''
    payload=json.dumps(topic,ensure_ascii=False,sort_keys=True,indent=2)
    return {arm: common+'\n方法：\n'+(old if arm=='A' else new)+'\n冻结题目包（两组完全相同）：\n'+payload+'\n仅输出 JSON。\n' for arm in ARMS}


def prepare(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    p=Path(args.pack);pack=load(p)
    topics=pack.get('topics',[])
    assert len(topics)==3 and [x['topic_id'] for x in topics]==list(TASK_IDS), 'Frozen topic ids mismatch'
    manifest={'schema':'deepwrite/dg-execution-kit/v0.1','trial_id':pack.get('trial_id'),
       'input_sha256':sha_file(p),'status':'PROMPTS_PREPARED_NOT_RUN',
       'prompts':{}, 'instructions':'6 prompts must be executed in 6 independent model contexts; all intermediary token usage counted; no human scores yet.'}
    for t in topics:
        for arm,prompt in get_prompts(t).items():
            name=f"{t['topic_id']}_{arm}.txt";f=out/name;f.write_text(prompt,encoding='utf-8')
            manifest['prompts'][name]=sha_file(f)
    save(out/'PROMPT_MANIFEST.json',manifest)
    print(f"PREPARED 6 prompts; {manifest['input_sha256']=}; A/B_NOT_RUN")


def validate_submission(sub,topic,arm,manifest,work):
    errs=[]
    name=f'{topic}_{arm}.txt'
    receipt=sub.get('execution_receipt',{})
    cards=sub.get('cards',[])
    if len(cards)!=3: errs.append('CARD_COUNT_MUST_BE_3')
    if str(receipt.get('prompt_sha256',''))!=manifest['prompts'][name]: errs.append('PROMPT_SHA_MISMATCH')
    if str(receipt.get('source_sha256',''))!=manifest['input_sha256']:errs.append('SOURCE_SHA_MISMATCH')
    for key in ('model','provider','timestamp','input_tokens','output_tokens','total_tokens','max_total_tokens','independent_context','tool_log'):
        if key not in receipt:errs.append('RECEIPT_MISSING_'+key)
    if receipt.get('independent_context') is not True:errs.append('INDEPENDENT_CONTEXT_NOT_ATTESTED')
    if receipt.get('max_total_tokens')!=12000:errs.append('PREREG_BUDGET_MUST_BE_12000')
    if not isinstance(receipt.get('tool_log'),list):errs.append('TOOL_LOG_MUST_BE_LIST')
    if all(type(receipt.get(k))==int for k in ('input_tokens','output_tokens','total_tokens')):
        if receipt['input_tokens']+receipt['output_tokens']!=receipt['total_tokens']:errs.append('TOKEN_ACCOUNTING_MISMATCH')
    if type(receipt.get('total_tokens'))==int and type(receipt.get('max_total_tokens'))==int:
        if receipt['total_tokens']>receipt['max_total_tokens']:errs.append('TOKEN_BUDGET_EXCEEDED')
    for i,card in enumerate(cards):
        if not isinstance(card,dict):errs.append(f'CARD_{i}_NOT_OBJECT');continue
        if not all(k in card for k in FIELDS):errs.append(f'CARD_{i}_MISSING_FIELDS')
        if not isinstance(card.get('body'),str):errs.append(f'CARD_{i}_NO_BODY');continue
        count=hanzi(card['body'])
        if not 700<=count<=1100:errs.append(f'CARD_{i}_LENGTH_{count}_OUT_OF_700_1100')
        if len(card.get('rivals',[]))<3:errs.append(f'CARD_{i}_RIVALS_LT_3')
        if len(card.get('predictions',[]))<2:errs.append(f'CARD_{i}_PREDICTIONS_LT_2')
        if card.get('review_status')=='HUMAN_REVIEWED':errs.append(f'CARD_{i}_FALSE_HUMAN_REVIEW')
    return errs


def seal(args):
    pack=load(args.pack); pm=load(args.manifest)
    assert pm['input_sha256']==sha_file(args.pack), 'Frozen pack changed since preparation'
    src=Path(args.inbox); out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    files={};err={};submissions={}
    for topic in TASK_IDS:
      for arm in ARMS:
        key=f'{topic}_{arm}'
        path=src/(key+'.json')
        if not path.is_file():err[key]=['RESPONSE_NOT_SUBMITTED'];continue
        sub=load(path);issues=validate_submission(sub,topic,arm,pm,src)
        if issues:err[key]=issues
        files[key]=sha_file(path)
        submissions[key]=sub
    # All six must use one model/backend and the same pre-registered token cap.
    receipts=[v.get('execution_receipt',{}) for v in submissions.values()]
    if receipts and (len({v.get('model') for v in receipts})!=1 or len({v.get('provider') for v in receipts})!=1):
        err['CROSS_ARM']=['MODEL_OR_PROVIDER_MISMATCH']
    if receipts and len({v.get('max_total_tokens') for v in receipts})!=1:
        err.setdefault('CROSS_ARM',[]).append('MAX_TOTAL_BUDGET_MISMATCH')
    # Registry can't be fabricated: missing / imperfect evidence = block seal.
    status='SEALED_EXECUTION_SELF_REPORTED_REQUIRES_AUDIT' if not err else 'BLOCKED_INCOMPLETE_OR_INVALID'
    report={'status':status,'input_sha256':pm['input_sha256'],
     'submissions_sha256':files,'errors':err,
     'execution_receipts_are_self_reported':'TRUE_EXTERNAL_AUDIT_REQUIRED',
     'human_reviews':'NOT_RUN','fair_ab':'UNVERIFIED_ISOLATION_AND_BUDGET'}
    save(out/'SEAL_REPORT.json',report)
    if err:print(f'SEAL BLOCKED: {canonical(err)}');return 2
    (out/'SEALED_RESPONSES.json').write_text(canonical(submissions),encoding='utf-8')
    report['sealed_sha256']=sha_file(out/'SEALED_RESPONSES.json')
    save(out/'SEAL_REPORT.json',report)
    print('SEALED SIX RESPONSE FILES; EXTERNAL ISOLATION AND EQUAL ACTUAL BUDGET STILL UNVERIFIED')
    return 0


def blind(args):
    rep=load(args.sealreport)
    if rep['status']!='SEALED_EXECUTION_SELF_REPORTED_REQUIRES_AUDIT':raise ValueError('Cannot blind without complete seal')
    if sha_file(args.sealed)!=rep['sealed_sha256']:raise ValueError('Sealed responses were altered')
    submissions=load(args.sealed)
    rows=[];key={}
    for topic in TASK_IDS:
      for arm in ARMS:
        for i,card in enumerate(submissions[f'{topic}_{arm}']['cards']):
          rows.append((topic,arm,i,card))
    # Unique random codes; mapping stored outside reviewer packet.
    ids=set()
    for topic,arm,i,card in rows:
        cid='C-'+secrets.token_hex(5).upper()
        while cid in ids:cid='C-'+secrets.token_hex(5).upper()
        ids.add(cid)
        key[cid]={'topic_id':topic,'arm':arm,'card_index':i,'card_sha256':sha_bytes(canonical(card).encode())}
    codes=list(ids);secrets.SystemRandom().shuffle(codes)
    # Cross pairing codes for assignment must preserve hidden random mapping.
    orig_codes=list(key)
    anonymous=[]
    for j,code in enumerate(codes):
       t,a,i,c=rows[orig_codes.index(code)]
       anonymous.append({'blind_code':code,'topic_id':t,'body':c['body']})
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    keydir=Path(args.keydir);keydir.mkdir(parents=True,exist_ok=True)
    if out.resolve()==keydir.resolve() or out.resolve() in keydir.resolve().parents or keydir.resolve() in out.resolve().parents:
        raise ValueError('SECRET_KEY_DIRECTORY_MUST_BE_SEPARATE_FROM_REVIEWER_DIRECTORY')
    save(out/'REVIEWER_ANONYMOUS_CARDS.json',{'schema':'deepwrite/dg-blind-packet/v0.1','status':'UNREVIEWED','cards':anonymous})
    kfile=keydir/'SECRET_BLIND_MAP_DO_NOT_SEND.json';save(kfile,key)
    os.chmod(kfile,0o600)
    save(out/'BLIND_RECEIPT.json',{'cards_count':len(anonymous),'anonymous_sha256':sha_file(out/'REVIEWER_ANONYMOUS_CARDS.json'),
        'secret_map_sha256':sha_file(kfile),'reviewers':'NOT_RECRUITED','frozen_response_sha256':rep['sealed_sha256']})
    print('BLIND PACKET READY - 18 cards, keys isolated. DO NOT SEND SECRET_BLIND_MAP to reviewers')



SCORE_KEYS=('mechanism','divergent_prediction','falsifier','evidence','decision_delta')

def aggregate(args):
    packet=load(args.packet);key=load(args.key)
    cards=packet.get('cards',[])
    if len(cards)!=18 or len(key)!=18 or {r['blind_code'] for r in cards}!=set(key):
        raise ValueError('BLIND_PACKET_OR_KEY_INVALID')
    codes={x['blind_code']:x for x in cards}
    reader_files=[Path(x) for x in args.reviews]
    if len(reader_files)!=2: raise ValueError('REQUIRE_EXACTLY_2_INDEPENDENT_REVIEW_FILES')
    receipts=[];scores={}
    for fp in reader_files:
        person=load(fp)
        rid=person.get('reviewer_id','')
        att=person.get('attestation',{})
        if not rid or rid in scores:raise ValueError('REVIEWER_ID_MISSING_OR_DUPLICATED')
        if att.get('human_independent') is not True or att.get('blind_to_arm') is not True or att.get('seen_other_answers') is not False:
            raise ValueError('REVIEWER_ATTESTATION_INCOMPLETE')
        rr=person.get('reviews',[])
        if len(rr)!=18 or {z.get('blind_code') for z in rr}!=set(key):
            raise ValueError(f'REVIEW_COVERAGE_INCOMPLETE_{rid}')
        scores[rid]={}
        for z in rr:
            cd=z['blind_code'];ss=z.get('scores',{})
            if any(type(ss.get(k))!=int or not 0<=ss[k]<=4 for k in SCORE_KEYS):
                raise ValueError(f'SCORE_INVALID_{rid}_{cd}')
            ex=z.get('excerpt','')
            if not isinstance(ex,str) or len(ex.strip())<10 or ex.strip() not in codes[cd]['body']:
                raise ValueError(f'REVIEW_QUOTE_MISSING_FROM_CARD_{rid}_{cd}')
            for f in ('decision_before','decision_after','reason'):
                if not isinstance(z.get(f),str) or not z[f].strip():
                    raise ValueError(f'REVIEW_{f.upper()}_MISSING_{rid}_{cd}')
            scores[rid][cd]=ss
        receipts.append({'reader_id':rid,'review_file_sha256':sha_file(fp),'attestation_self_reported':True})
    result=[]
    for topic in TASK_IDS:
        row={'topic_id':topic,'A':{},'B':{}}
        for arm in ARMS:
            selected=[code for code,v in key.items() if v['topic_id']==topic and v['arm']==arm]
            dim={k:sum(scores[rid][code][k] for rid in scores for code in selected)/6 for k in SCORE_KEYS}
            row[arm]={'mean_total':round(sum(dim.values()),3),'mean_axes':{k:round(v,3) for k,v in dim.items()}}
        row['difference_B_minus_A']=round(row['B']['mean_total']-row['A']['mean_total'],3)
        row['fact_axis_difference_B_minus_A']=round(row['B']['mean_axes']['evidence']-row['A']['mean_axes']['evidence'],3)
        result.append(row)
    avg_diff=sum(x['difference_B_minus_A'] for x in result)/3
    evidence_diff=sum(x['fact_axis_difference_B_minus_A'] for x in result)/3
    threshold=(sum(x['difference_B_minus_A']>0 for x in result)>=2 and avg_diff>=2 and evidence_diff>-1)
    report={'schema':'deepwrite/dg-score-aggregation/v0.1','status':'PROVISIONAL_SELF_ATTESTED_EXTERNAL_AUDIT_PENDING',
            'topic_results':result,'overall_difference_B_minus_A':round(avg_diff,3),
            'overall_fact_axis_difference_B_minus_A':round(evidence_diff,3),
            'preregistered_exploratory_threshold_met':threshold,
            'reliability_caveat':'Scores rely on externally supplied reviewer identity and attestations; program cannot verify human independence. Do not promote method without audit.',
            'reader_receipts':receipts,'blind_packet_sha256':sha_file(args.packet),
            'human_identity_and_independence':'UNVERIFIED_EXTERNAL','causal_method_comparison':'UNVERIFIED_UNTIL_EXECUTION_RECEIPTS_AUDITED'}
    save(args.out,report)
    print(f'PROVISIONAL: B-A {avg_diff:.3f}; threshold met={threshold}; human independence not verified')

def status(args):
    root=Path(args.root)
    m=root/'PROMPT_MANIFEST.json'; seal=root/'SEAL_REPORT.json'; review=root/'REVIEWER_ANONYMOUS_CARDS.json'
    steps={'prompts_prepared':m.is_file(), 'six_response_files_present':all((root/'inbox'/f'{topic}_{arm}.json').is_file() for topic in TASK_IDS for arm in ARMS),
         'sealed':seal.is_file() and load(seal).get('status')=='SEALED_EXECUTION_SELF_REPORTED_REQUIRES_AUDIT',
         'blind_packet_ready':review.is_file(),
         'independent_model_contexts_verified':False,'fair_actual_token_budget_verified':False,'two_human_evaluators_verified':False,
         'method_effectiveness':'UNVERIFIED'}
    print(canonical(steps))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    s=p.add_subparsers(dest='mode',required=True)
    x=s.add_parser('prepare');x.add_argument('--pack',required=True);x.add_argument('--out',required=True);x.set_defaults(run=prepare)
    x=s.add_parser('seal');x.add_argument('--pack',required=True);x.add_argument('--manifest',required=True);x.add_argument('--inbox',required=True);x.add_argument('--out',required=True);x.set_defaults(run=seal)
    x=s.add_parser('blind');x.add_argument('--sealed',required=True);x.add_argument('--sealreport',required=True);x.add_argument('--out',required=True);x.add_argument('--keydir',required=True);x.set_defaults(run=blind)
    x=s.add_parser('aggregate');x.add_argument('--packet',required=True);x.add_argument('--key',required=True);x.add_argument('--reviews',nargs=2,required=True);x.add_argument('--out',required=True);x.set_defaults(run=aggregate)
    x=s.add_parser('status');x.add_argument('--root',required=True);x.set_defaults(run=status)
    args=p.parse_args(); result=args.run(args)
    return result if isinstance(result,int) else 0
if __name__=='__main__':sys.exit(main())
