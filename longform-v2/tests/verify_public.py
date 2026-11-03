#!/usr/bin/env python3
import sys, urllib.request

BASE='https://taoismzp.github.io/xuyuan/longform-v2/'
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1'

def get(path):
    req=urllib.request.Request(BASE+path,headers={'User-Agent':UA,'Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=20) as r:
        assert r.status==200, (path,r.status)
        return r.read().decode('utf-8')

home=get('')
article=get('posts/welcome.html')
write=get('write.html')
css=get('styles.css')
for text,name in [(home,'home'),(article,'article'),(write,'write')]:
    assert 'viewport-fit=cover' in text, f'{name}: missing mobile viewport'
assert 'TaoismZp' in home and '长文应该有自己的地址' in home
assert '<article class="prose">' in article and 'reading-progress' in article
assert 'issues/new?template=publish-longform.yml' in write
assert '@media(max-width:760px)' in css and 'width:min(100% - 32px' in css
assert 'github_pat_' not in home+article+write and 'ghp_' not in home+article+write
print('longform-v2 public delivery verification: PASS')
