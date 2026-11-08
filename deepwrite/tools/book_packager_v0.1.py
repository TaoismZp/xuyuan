#!/usr/bin/env python3
"""Read-only verified assembler for Markdown books.

This utility does NOT generate chapters or perform AI/editorial supervision.
It validates all source SHA256s, writes a new derivative book artifact,
checks chapter order, and records source identities. Original inputs remain read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load_source(path, expected):
    raw = Path(path).read_bytes()
    actual = sha(raw)
    if actual != expected:
        raise SystemExit(f'FAIL SHA256 mismatch for {path}: expected {expected}; got {actual}')
    return raw.decode('utf-8')

def clean_first_h1(text):
    lines=text.splitlines(keepends=True)
    if lines and lines[0].startswith('# '):
        return ''.join(lines[1:]).lstrip('\n')
    return text

def assemble(m, root, output, report):
    chapters=m['chapters']
    assert len(chapters) == m['expected_chapters']
    assert [x['number'] for x in chapters]==list(range(1,len(chapters)+1))
    section_data=[]
    for x in chapters:
        p=root/x['relative_path']
        text=load_source(p,x['sha256'])
        section_data.append((x,clean_first_h1(text)))
    front=load_source(root/m['front']['relative_path'],m['front']['sha256'])
    tail=load_source(root/m['tail']['relative_path'],m['tail']['sha256'])
    title=m.get('working_title','Book candidate')
    parts=m.get('parts',{})
    content=[f'# {title}\n\n', f'> 候选汇编（未获独立编辑/作者终校签收）。编排派生稿，不修改原稿。\n\n', '## 目录\n\n','- 序言\n']
    for x,_ in section_data: content.append(f"- 第{x['number']:02d}章｜{x['title']}\n")
    content+=['- 尾声\n\n','---\n\n',front.strip(),'\n\n---\n\n']
    for x,body in section_data:
        if str(x['number']) in parts:
            content.append(f"\n# {parts[str(x['number'])]}\n\n")
        content.append(f"\n## 第{x['number']:02d}章｜{x['title']}\n\n")
        content.append(body.strip())
        content.append('\n\n---\n\n')
    content += [tail.strip(), '\n']
    output.parent.mkdir(parents=True,exist_ok=True)
    packed=''.join(content)
    output.write_text(packed,encoding='utf-8')
    result={
       'schema':'verified-markdown-book/v0.1',
       'generated_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
       'title':title,
       'chapters':len(chapters),
       'sha256':sha(output.read_bytes()),
       'bytes':output.stat().st_size,
       'chapter_source_digests':[{k:x[k] for k in ('number','relative_path','sha256','bytes')} for x in chapters],
       'front_sha256':m['front']['sha256'],
       'tail_sha256':m['tail']['sha256'],
       'gates':{'source_files':'PASS_EXACT_DIGEST','book_draft':'CANDIDATE','human_edit':'PENDING','appendices':'PENDING'},
       'note':'Source chapter bodies copied into a new derivative; original files untouched'
    }
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS_SOURCES','book_path':str(output),'sha256':result['sha256'],'bytes':result['bytes'],'chapters':len(chapters)},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',required=True)
    p.add_argument('--root',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--report',required=True)
    a=p.parse_args()
    m=json.loads(Path(a.manifest).read_text(encoding='utf-8'))
    assemble(m,Path(a.root),Path(a.output),Path(a.report))
if __name__=='__main__':main()
