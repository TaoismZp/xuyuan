#!/usr/bin/env python3
import argparse, datetime as dt, html, json, math, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION_RE = re.compile(r"^###\s+(.+?)\s*$\n+(.*?)(?=\n###\s+|\Z)", re.M | re.S)

def inline(text: str) -> str:
    s = html.escape(text, quote=True)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2" rel="noopener noreferrer">\1</a>', s)
    return s

def render_markdown(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out, para = [], []
    list_mode = None
    in_code = False
    code = []
    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para = []
    def close_list():
        nonlocal list_mode
        if list_mode:
            out.append(f"</{list_mode}>")
            list_mode = None
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            flush_para(); close_list()
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = []; in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code.append(raw); continue
        if not line.strip():
            flush_para(); close_list(); continue
        if re.fullmatch(r"\s*(---|\*\*\*)\s*", line):
            flush_para(); close_list(); out.append("<hr>"); continue
        m = re.match(r"^(#{2,3})\s+(.+)$", line)
        if m:
            flush_para(); close_list(); level = len(m.group(1)); out.append(f"<h{level}>{inline(m.group(2))}</h{level}>"); continue
        if line.startswith("> "):
            flush_para(); close_list(); out.append("<blockquote><p>" + inline(line[2:]) + "</p></blockquote>"); continue
        m = re.match(r"^[-*]\s+(.+)$", line)
        if m:
            flush_para()
            if list_mode != "ul": close_list(); out.append("<ul>"); list_mode = "ul"
            out.append("<li>" + inline(m.group(1)) + "</li>"); continue
        m = re.match(r"^\d+[.)]\s+(.+)$", line)
        if m:
            flush_para()
            if list_mode != "ol": close_list(); out.append("<ol>"); list_mode = "ol"
            out.append("<li>" + inline(m.group(1)) + "</li>"); continue
        para.append(line)
    flush_para(); close_list()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
    return "".join(out)

def section_map(body: str):
    return {k.strip(): v.strip() for k, v in SECTION_RE.findall(body or "")}

def replace_generated(text: str, name: str, content: str) -> str:
    start = f"<!-- GENERATED:{name}:START -->"
    end = f"<!-- GENERATED:{name}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    replacement = start + "\n" + content.rstrip() + "\n      " + end
    if not pattern.search(text):
        raise RuntimeError(f"missing marker {name}")
    return pattern.sub(replacement, text, count=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-body-file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.issue_body_file:
        issue_body = Path(args.issue_body_file).read_text(encoding="utf-8")
    else:
        issue_body = os.environ.get("ISSUE_BODY", "")
    title = os.environ.get("ISSUE_TITLE", "").strip()
    title = re.sub(r"^\[长文\]\s*", "", title).strip()
    number = os.environ.get("ISSUE_NUMBER", "0").strip()
    created = os.environ.get("ISSUE_CREATED_AT", "")[:10] or dt.date.today().isoformat()
    sec = section_map(issue_body)
    deck = sec.get("副标题", "").strip()
    tags_raw = sec.get("标签", sec.get("标签（逗号分隔）", ""))
    md = sec.get("正文", "").strip()
    if not title or len(md) < 50:
        raise SystemExit("title missing or body too short")
    tags = [x.strip() for x in re.split(r"[,，、]", tags_raw) if x.strip()][:6] or ["长文"]
    slug = f"p-{number}" if number and number != "0" else "preview"
    date_display = created.replace("-", ".")
    chars = len(re.sub(r"\s+", "", md))
    minutes = max(1, math.ceil(chars / 450))
    reading_time = f"{minutes} 分钟阅读"
    body_html = render_markdown(md)
    template = (ROOT / "templates" / "article-template.html").read_text(encoding="utf-8")
    article = template
    repl = {
        "{{DESCRIPTION}}": html.escape(deck or title, quote=True),
        "{{TITLE}}": html.escape(title),
        "{{DATE_DISPLAY}}": html.escape(date_display),
        "{{READING_TIME}}": html.escape(reading_time),
        "{{DECK}}": html.escape(deck or ""),
        "{{TAGS}}": html.escape(" · ".join(tags)),
        "{{BODY}}": body_html,
    }
    for a,b in repl.items(): article = article.replace(a,b)
    posts_dir = ROOT / "posts"; source_dir = ROOT / "source"
    posts_dir.mkdir(exist_ok=True); source_dir.mkdir(exist_ok=True)
    (posts_dir / f"{slug}.html").write_text(article, encoding="utf-8")
    source = f"---\ntitle: {title}\ndate: {created}\ntags: {', '.join(tags)}\n---\n\n{md}\n"
    (source_dir / f"{slug}.md").write_text(source, encoding="utf-8")
    index_path = posts_dir / "index.json"
    items = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    item = {"slug":slug,"title":title,"deck":deck,"date":created,"date_display":date_display,"reading_time":reading_time,"tags":tags,"url":f"posts/{slug}.html"}
    items = [x for x in items if x.get("slug") != slug] + [item]
    items.sort(key=lambda x:(x.get("date",""),x.get("slug","")), reverse=True)
    index_path.write_text(json.dumps(items,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    latest = items[0]
    featured = f'''<article class="featured">\n        <p class="issue">最新 · {html.escape(latest['date_display'])}</p>\n        <h1 id="hero-title"><a href="{html.escape(latest['url'],quote=True)}">{html.escape(latest['title'])}</a></h1>\n        <p class="deck">{html.escape(latest.get('deck') or '')}</p>\n        <p class="meta">{html.escape(latest['reading_time'])} · <span>{'</span> <span>'.join(html.escape(t) for t in latest['tags'])}</span></p>\n      </article>'''
    rows=[]
    for x in items:
        search=" ".join([x['title'],x.get('deck',''),*x.get('tags',[])])
        rows.append(f'''<a class="archive-row" href="{html.escape(x['url'],quote=True)}" data-search="{html.escape(search,quote=True)}">\n          <time datetime="{html.escape(x['date'])}">{html.escape(x['date_display'])}</time>\n          <span class="archive-title">{html.escape(x['title'])}</span>\n          <span class="archive-tags">{html.escape(' · '.join(x.get('tags',[])))}</span>\n        </a>''')
    home_path = ROOT / "index.html"
    home = home_path.read_text(encoding="utf-8")
    home = replace_generated(home,"FEATURED",featured)
    home = replace_generated(home,"ARCHIVE","\n        ".join(rows))
    home_path.write_text(home,encoding="utf-8")
    print(json.dumps(item,ensure_ascii=False))

if __name__ == "__main__":
    main()
