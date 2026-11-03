(() => {
  const $ = (q, root=document) => root.querySelector(q);
  const $$ = (q, root=document) => [...root.querySelectorAll(q)];
  const base = new URL('.', window.location.href);

  function escapeHtml(s='') { return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function inline(s='') {
    let x = escapeHtml(s);
    x = x.replace(/`([^`]+)`/g,'<code>$1</code>')
         .replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>')
         .replace(/\*([^*]+)\*/g,'<em>$1</em>')
         .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
    return x;
  }
  function renderMarkdown(md='') {
    const lines = md.replace(/\r/g,'').split('\n');
    let out=[], para=[], list=null, code=false, codeLines=[];
    const flushPara=()=>{ if(para.length){ out.push(`<p>${inline(para.join(' '))}</p>`); para=[]; } };
    const flushList=()=>{ if(list){ out.push(`</${list}>`); list=null; } };
    for(const raw of lines){
      const line=raw.trimEnd();
      if(line.startsWith('```')){ flushPara(); flushList(); if(!code){code=true;codeLines=[];}else{out.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);code=false;} continue; }
      if(code){codeLines.push(raw);continue;}
      if(!line.trim()){flushPara();flushList();continue;}
      if(/^---+$/.test(line.trim())){flushPara();flushList();out.push('<hr>');continue;}
      let m;
      if((m=line.match(/^###\s+(.+)/))){flushPara();flushList();out.push(`<h3>${inline(m[1])}</h3>`);continue;}
      if((m=line.match(/^##\s+(.+)/))){flushPara();flushList();out.push(`<h2>${inline(m[1])}</h2>`);continue;}
      if((m=line.match(/^#\s+(.+)/))){flushPara();flushList();out.push(`<h2>${inline(m[1])}</h2>`);continue;}
      if((m=line.match(/^>\s?(.*)/))){flushPara();flushList();out.push(`<blockquote>${inline(m[1])}</blockquote>`);continue;}
      if((m=line.match(/^[-*]\s+(.+)/))){flushPara(); if(list!=='ul'){flushList();list='ul';out.push('<ul>');} out.push(`<li>${inline(m[1])}</li>`);continue;}
      if((m=line.match(/^\d+\.\s+(.+)/))){flushPara(); if(list!=='ol'){flushList();list='ol';out.push('<ol>');} out.push(`<li>${inline(m[1])}</li>`);continue;}
      para.push(line.trim());
    }
    flushPara();flushList(); if(code) out.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
    return out.join('\n');
  }
  function readTime(text=''){ const chars=text.replace(/\s/g,'').length; return `${Math.max(1,Math.ceil(chars/650))} 分钟阅读`; }
  function prettyDate(s){ const d=new Date(`${s}T00:00:00`); return Number.isNaN(d.valueOf())?s:new Intl.DateTimeFormat('zh-CN',{year:'numeric',month:'long',day:'numeric'}).format(d); }

  const savedTheme = localStorage.getItem('longform-theme');
  if(savedTheme) document.documentElement.dataset.theme=savedTheme;
  $('#themeToggle')?.addEventListener('click',()=>{
    const next=document.documentElement.dataset.theme==='dark'?'light':'dark';
    document.documentElement.dataset.theme=next; localStorage.setItem('longform-theme',next);
  });
  $('#year') && ($('#year').textContent = new Date().getFullYear());

  async function loadManifest(){
    const r=await fetch(new URL('posts/index.json',base),{cache:'no-store'}); if(!r.ok) throw new Error('manifest'); return r.json();
  }

  async function home(){
    const list=$('#articleList'); if(!list) return;
    let posts=[]; try{ posts=await loadManifest(); }catch{ list.innerHTML='<div class="loading">文章目录暂时没有加载成功。</div>'; return; }
    let active='全部', query='';
    const allTags=['全部',...new Set(posts.flatMap(p=>p.tags||[]))];
    const filters=$('#tagFilters');
    filters.innerHTML=allTags.map((t,i)=>`<button class="tag-filter${i===0?' active':''}" data-tag="${escapeHtml(t)}">${escapeHtml(t)}</button>`).join('');
    function draw(){
      const q=query.trim().toLowerCase();
      const shown=posts.filter(p=>(active==='全部'||(p.tags||[]).includes(active))&&(!q||`${p.title} ${p.deck} ${(p.tags||[]).join(' ')}`.toLowerCase().includes(q)));
      $('#emptyState').hidden=shown.length!==0;
      list.innerHTML=shown.map((p,i)=>`<a class="article-card" href="article.html?slug=${encodeURIComponent(p.slug)}">
        <span class="article-index">${String(i+1).padStart(2,'0')}</span>
        <div><h3>${escapeHtml(p.title)}</h3><p>${escapeHtml(p.deck||'')}</p><div class="card-tags">${(p.tags||[]).map(t=>`<span class="card-tag"># ${escapeHtml(t)}</span>`).join('')}</div></div>
        <div class="card-meta">${prettyDate(p.date)}<br>${escapeHtml(p.reading||'')}</div>
      </a>`).join('');
    }
    filters.addEventListener('click',e=>{ const b=e.target.closest('[data-tag]'); if(!b)return; active=b.dataset.tag; $$('.tag-filter',filters).forEach(x=>x.classList.toggle('active',x===b)); draw(); });
    $('#searchToggle')?.addEventListener('click',()=>{ $('#searchPanel').hidden=false; $('#searchInput').focus(); });
    $('#searchClose')?.addEventListener('click',()=>{ $('#searchPanel').hidden=true; query=''; $('#searchInput').value=''; draw(); });
    $('#searchInput')?.addEventListener('input',e=>{query=e.target.value;draw();});
    draw();
  }

  async function article(){
    if(!$('#article')) return;
    const slug=new URLSearchParams(location.search).get('slug');
    try{
      const posts=await loadManifest(); const p=posts.find(x=>x.slug===slug); if(!p) throw new Error('missing');
      const r=await fetch(new URL(`posts/${encodeURIComponent(slug)}.md`,base),{cache:'no-store'}); if(!r.ok) throw new Error('missing'); const md=await r.text();
      document.title=`${p.title} · 长文`; $('#metaDescription').content=p.deck||p.title;
      $('#articleTitle').textContent=p.title; $('#articleDeck').textContent=p.deck||''; $('#articleDate').textContent=prettyDate(p.date);
      $('#articleReadTime').textContent=p.reading||readTime(md); $('#articleTags').innerHTML=(p.tags||[]).map(t=>`<span># ${escapeHtml(t)}</span>`).join('');
      $('#articleBody').innerHTML=renderMarkdown(md); $('#article').hidden=false;
    }catch{ $('#articleError').hidden=false; }
    const progress=$('#readingProgress');
    if(progress) addEventListener('scroll',()=>{ const d=document.documentElement; const max=d.scrollHeight-d.clientHeight; progress.style.width=`${max?Math.min(100,scrollY/max*100):0}%`; },{passive:true});
    $('#shareButton')?.addEventListener('click',async()=>{ try{ if(navigator.share) await navigator.share({title:document.title,url:location.href}); else {await navigator.clipboard.writeText(location.href); $('#shareButton').textContent='已复制';} }catch{} });
  }

  function writer(){
    if(!$('#composer')) return;
    const t=$('#draftTitle'), d=$('#draftDeck'), tags=$('#draftTags'), body=$('#draftBody');
    const refresh=()=>{ $('#previewTitle').textContent=t.value||'你的标题会出现在这里'; $('#previewDeck').textContent=d.value||'摘要会出现在这里。'; $('#previewBody').innerHTML=body.value?renderMarkdown(body.value):'<p>正文会随着你输入即时排版。</p>'; $('#previewReadTime').textContent=readTime(body.value); };
    [t,d,tags,body].forEach(x=>x.addEventListener('input',refresh)); refresh();
    $('#copyDraft').addEventListener('click',async()=>{
      const payload=`标题：${t.value.trim()}\n\n摘要：${d.value.trim()}\n\n标签：${tags.value.trim()}\n\n正文：\n${body.value.trim()}`;
      try{await navigator.clipboard.writeText(payload); $('#copyHint').textContent='已复制。打开 GitHub 发文表单，把对应内容粘贴进去即可。';}catch{$('#copyHint').textContent='复制失败，请手动复制输入框内容。';}
    });
  }

  home(); article(); writer();
  window.Longform={renderMarkdown,readTime};
})();
