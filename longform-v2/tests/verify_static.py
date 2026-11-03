#!/usr/bin/env python3
from pathlib import Path
import json, os, shutil, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
required=["index.html","about.html","write.html","styles.css","app.js","templates/article-template.html","posts/welcome.html","posts/index.json","scripts/publish_issue.py","VISION_FIXTURE.md","BUILD_BLUEPRINT.md","PROJECT_STATE.md"]
missing=[x for x in required if not (ROOT/x).exists()]
assert not missing, f"missing files: {missing}"

home=(ROOT/"index.html").read_text(encoding="utf-8")
css=(ROOT/"styles.css").read_text(encoding="utf-8")
write=(ROOT/"write.html").read_text(encoding="utf-8")
article=(ROOT/"posts/welcome.html").read_text(encoding="utf-8")
combined="\n".join([home,css,write,article,(ROOT/"app.js").read_text(encoding="utf-8")])

assert '<meta name="viewport"' in home
assert 'GENERATED:FEATURED:START' in home and 'GENERATED:ARCHIVE:START' in home
assert 'https://github.com/TaoismZp/xuyuan/issues/new?template=publish-longform.yml' in write
assert 'token=' not in combined.lower() and 'ghp_' not in combined and 'github_pat_' not in combined
assert 'max-width' in css and '@media(max-width:760px)' in css
assert '<article class="prose">' in article and 'reading-progress' in article
assert not any(x in combined for x in ['bootstrap.min.css','tailwindcss','fonts.googleapis.com'])
items=json.loads((ROOT/"posts/index.json").read_text(encoding="utf-8"))
assert items and items[0]['url'].startswith('posts/')

# Representative publishing-loop spike in an isolated copy.
with tempfile.TemporaryDirectory() as td:
    sandbox=Path(td)/"longform-v2"
    shutil.copytree(ROOT,sandbox)
    issue=sandbox/"synthetic_issue.txt"
    issue.write_text("### 副标题\n\n这是一次真实发布链路的合成验收。\n\n### 标签（逗号分隔）\n\n测试，发布\n\n### 正文\n\n这是一段用于验收发布器的正文。它必须足够长，以确认系统会真正生成文章页面，而不是只返回成功状态。\n\n## 第二层\n\n这里继续增加内容，用来验证标题、段落、加粗 **真实生成**、引用和索引更新都能完成。\n\n> 发布不是按钮变绿，而是成品真正出现。\n",encoding="utf-8")
    env=os.environ.copy(); env.update({"ISSUE_TITLE":"[长文] 合成发布验收","ISSUE_NUMBER":"99999","ISSUE_CREATED_AT":"2026-11-03T05:00:00Z"})
    subprocess.run([sys.executable,str(sandbox/"scripts/publish_issue.py"),"--issue-body-file",str(issue),"--dry-run"],check=True,env=env,capture_output=True,text=True)
    generated=(sandbox/"posts/p-99999.html").read_text(encoding="utf-8")
    assert '合成发布验收' in generated and '<h2>第二层</h2>' in generated and '<strong>真实生成</strong>' in generated
    updated=json.loads((sandbox/"posts/index.json").read_text(encoding="utf-8"))
    assert any(x['slug']=='p-99999' for x in updated)
    updated_home=(sandbox/"index.html").read_text(encoding="utf-8")
    assert '合成发布验收' in updated_home and 'p-99999.html' in updated_home

print('longform-v2 static verification: PASS')
