#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / 'posts'
INDEX = POSTS / 'index.json'

def section(body, name):
    m = re.search(rf'^###\s+{re.escape(name)}\s*$\n(.*?)(?=^###\s+|\Z)', body, re.M | re.S)
    if not m: return ''
    value = m.group(1).strip()
    if value == '_No response_': return ''
    return value

def clean_slug(value, issue_number):
    value = value.strip().lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    value = re.sub(r'-+', '-', value).strip('-')
    return value or f'post-{issue_number}'

def main():
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path: raise SystemExit('GITHUB_EVENT_PATH missing')
    event = json.loads(Path(event_path).read_text())
    issue = event['issue']
    owner = os.environ.get('GITHUB_REPOSITORY_OWNER','')
    author = issue['user']['login']
    if author.lower() != owner.lower():
        print(f'Ignoring non-owner issue from {author}')
        return 2

    body = issue.get('body') or ''
    title = section(body, '文章标题') or issue.get('title','').removeprefix('[发文] ').strip()
    deck = section(body, '摘要')
    tags_raw = section(body, '标签')
    markdown = section(body, '正文 Markdown')
    slug = clean_slug(section(body, '自定义链接（可选）'), issue['number'])
    if not title or not markdown: raise SystemExit('title/body missing')

    tags = [x.strip() for x in re.split(r'[,，、/]', tags_raw) if x.strip()][:8]
    date = datetime.now(timezone.utc).astimezone().date().isoformat()
    chars = len(re.sub(r'\s+','',markdown))
    reading = f'{max(1,(chars+649)//650)} 分钟阅读'

    POSTS.mkdir(parents=True, exist_ok=True)
    md_path = POSTS / f'{slug}.md'
    if md_path.exists(): raise SystemExit(f'slug already exists: {slug}')
    md_path.write_text(markdown.rstrip()+'\n', encoding='utf-8')

    items = json.loads(INDEX.read_text(encoding='utf-8')) if INDEX.exists() else []
    items.insert(0, {'slug':slug,'title':title,'deck':deck,'date':date,'tags':tags,'reading':reading})
    INDEX.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(slug)
    return 0

if __name__ == '__main__':
    sys.exit(main())
