import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import MarkdownIt from 'markdown-it';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const POSTS_DIR = path.join(ROOT, 'content', 'posts');
const ESSAYS_DIR = path.join(ROOT, 'essays');
const md = new MarkdownIt({ html: false, linkify: true, typographer: false, breaks: false });
const SITE_ROOT = 'https://taoismzp.github.io/xuyuan/personal-site-v1/';
const articleUrl = (post) => SITE_ROOT + 'essays/' + encodeURIComponent(post.slug) + '/';

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const xmlEscape = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&apos;');

const tagToken = (tag) => encodeURIComponent(String(tag).trim()).replaceAll('%', 'p');
const normalizeDate = (value) => {
  if (!value) return null;
  if (typeof value === 'string') {
    const label = value.match(/^\d{4}-\d{2}-\d{2}/)?.[0];
    const date = new Date(value);
    if (!Number.isNaN(date.getTime()) && label) return { iso: date.toISOString(), label, sort: date.getTime() };
  }
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return { iso: date.toISOString(), label: date.toISOString().slice(0, 10), sort: date.getTime() };
};
const readingMinutes = (body) => {
  const cjk = (body.match(/[\u3400-\u9fff\uf900-\ufaff]/g) || []).length;
  const latin = (body.replace(/[\u3400-\u9fff\uf900-\ufaff]/g, ' ').match(/[A-Za-z0-9]+/g) || []).length;
  return Math.max(1, Math.ceil(cjk / 500 + latin / 220));
};

function readPosts() {
  fs.mkdirSync(POSTS_DIR, { recursive: true });
  const files = fs.readdirSync(POSTS_DIR).filter((name) => name.endsWith('.md')).sort();
  const seen = new Set();
  const posts = [];
  const problems = [];

  for (const file of files) {
    const full = path.join(POSTS_DIR, file);
    const parsed = matter(fs.readFileSync(full, 'utf8'));
    const data = parsed.data || {};
    const slug = String(data.slug || file.replace(/\.md$/i, '')).trim();
    const status = String(data.status || 'draft').trim();
    const title = String(data.title || '').trim();
    const summary = String(data.summary || '').trim();
    const date = normalizeDate(data.date);
    const tags = Array.isArray(data.tags) ? data.tags.map(String).map((x) => x.trim()).filter(Boolean) : [];
    const body = parsed.content.trim();

    if (!slug || seen.has(slug)) problems.push(`${file}: missing or duplicate slug "${slug}"`);
    if (!/^[\p{L}\p{N}][\p{L}\p{N}_-]*$/u.test(slug)) problems.push(`${file}: unsafe slug "${slug}"`);
    seen.add(slug);
    if (!title) problems.push(`${file}: title is required`);
    if (!date) problems.push(`${file}: valid date is required`);
    if (!['draft', 'published', 'archived'].includes(status)) problems.push(`${file}: status must be draft, published or archived`);
    if (status === 'published' && !summary) problems.push(`${file}: published posts require summary`);
    if (status === 'published' && !body) problems.push(`${file}: published posts require body`);

    posts.push({ file, slug, status, title, summary, date, tags, featured: Boolean(data.featured), body });
  }

  if (problems.length) {
    console.error('Content validation failed:\n- ' + problems.join('\n- '));
    process.exit(1);
  }

  return posts
    .filter((post) => post.status === 'published')
    .sort((a, b) => b.date.sort - a.date.sort);
}

const head = ({ title, description, depth = '', canonical = SITE_ROOT, type = 'website', publishedAt = null, tags = [] }) => {
  const articleMetadata = type === 'article'
    ? '<meta property="article:published_time" content="' + escapeHtml(publishedAt || '') + '">' +
      tags.map(tag => '<meta property="article:tag" content="' + escapeHtml(tag) + '">').join('')
    : '';
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f5f1e8"><meta name="description" content="${escapeHtml(description)}"><title>${escapeHtml(title)}</title><link rel="canonical" href="${escapeHtml(canonical)}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="TaoismZp"><meta property="og:type" content="${type}"><meta property="og:title" content="${escapeHtml(title)}"><meta property="og:description" content="${escapeHtml(description)}"><meta property="og:url" content="${escapeHtml(canonical)}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="${escapeHtml(title)}"><meta name="twitter:description" content="${escapeHtml(description)}">${articleMetadata}<link rel="alternate" type="application/rss+xml" title="TaoismZp 长文订阅" href="${SITE_ROOT}feed.xml"><link rel="stylesheet" href="${depth}assets/site.css"></head>`;
};

function siteHeader(surface) {
  const map = {
    home: { home: './', essays: 'essays/', projects: 'projects/', about: 'about/' },
    archive: { home: '../', essays: './', projects: '../projects/', about: '../about/' },
    article: { home: '../../', essays: '../', projects: '../../projects/', about: '../../about/' },
  }[surface];
  const current = surface === 'home' ? 'home' : 'essays';
  const currentAttr = (key) => current === key ? ' aria-current="page"' : '';
  return `<a class="skip-link" href="#main">跳到正文</a><header class="site-header"><div class="shell site-header__inner"><a class="site-brand" href="${map.home}"${surface === 'home' ? ' aria-current="page"' : ''} translate="no">TaoismZp</a><nav class="site-nav" aria-label="主导航"><a href="${map.home}"${currentAttr('home')}>首页</a><a href="${map.essays}"${currentAttr('essays')}>长文</a><a href="${map.projects}">项目</a><a href="${map.about}">关于</a></nav></div></header>`;
}

const footer = (depth = '', note = '长期交易，长期写作。') => `<footer class="shell site-footer"><strong translate="no">TaoismZp</strong><span>${escapeHtml(note)}</span></footer><script src="${depth}assets/site.js" defer></script>`;

function homePage(posts) {
  const latest = posts.slice(0, 3);
  const rows = latest.length
    ? latest.map((post) => `<a class="essay-line" href="essays/${encodeURIComponent(post.slug)}/"><span class="essay-line__title">${escapeHtml(post.title)}</span><time datetime="${post.date.iso}">${escapeHtml(post.date.label)}</time></a>`).join('')
    : `<div class="essay-line"><span class="essay-line__title">第一篇公开长文，会从这里开始。</span><time>—</time></div>`;

  return `${head({ title: 'TaoismZp — 长期交易，长期写作', description: 'TaoismZp 的个人网站：长期交易，长期写作。' })}<body>${siteHeader('home')}<main class="shell" id="main"><section class="hero" aria-labelledby="home-title"><h1 class="hero-title" id="home-title"><span class="hero-line">长期交易，</span><em class="hero-line">长期写作。</em></h1><p class="hero-subtitle">关于市场、概率、风险与判断。</p></section><section class="section" aria-labelledby="recent-heading"><div class="section-heading"><h2 id="recent-heading">最新长文</h2><span class="section-note">完整推演，而不是观点碎片。</span></div><div class="essay-index">${rows}</div></section><section class="section" aria-labelledby="projects-heading"><div class="section-heading"><h2 id="projects-heading">长期项目</h2></div><div class="project-minimal"><a class="project-minimal__item" href="projects/#nofold"><h3 translate="no">NO FOLD</h3><p>德州扑克 × 二级市场：一套关于赔率、纪律、等待与长期在场的交易框架。</p></a><a class="project-minimal__item" href="projects/#ruozhe"><h3>弱者的活法</h3><p>在非对称的世界里，研究普通人如何先活着，再活好、活久、活大、活明白。</p></a></div></section></main>${footer('', '长期交易，长期写作。')}</body></html>`;
}

function archivePage(posts) {
  const tags = [...new Set(posts.flatMap((post) => post.tags))].sort((a, b) => a.localeCompare(b, 'zh-CN'));
  const filters = [`<button class="filter-button" type="button" data-filter="all" aria-pressed="true">全部</button>`, ...tags.map((tag) => `<button class="filter-button" type="button" data-filter="${tagToken(tag)}" aria-pressed="false">${escapeHtml(tag)}</button>`)].join('');
  const rows = posts.length
    ? posts.map((post) => `<a class="archive-row" data-tags="${post.tags.map(tagToken).join(' ')}" href="./${encodeURIComponent(post.slug)}/"><div><span class="archive-row__meta">${escapeHtml(post.tags.slice(0, 2).join(' / ') || '长文')} · 约 ${readingMinutes(post.body)} 分钟</span><h2>${escapeHtml(post.title)}</h2></div><time class="archive-row__date" datetime="${post.date.iso}">${escapeHtml(post.date.label)}</time></a>`).join('')
    : `<p class="archive-empty">还没有公开长文。</p>`;

  return `${head({ title: '长文 — TaoismZp', description: 'TaoismZp 的长文归档。', depth: '../', canonical: SITE_ROOT + 'essays/' })}<body>${siteHeader('archive')}<main class="shell" id="main"><header class="page-head"><div class="page-head__eyebrow">ESSAYS</div><h1>把判断，<br>写到尽头。</h1><p class="page-head__desc">这里放完整推演。不是为了更新频率，而是把一个问题真正想清楚以后留下来。</p></header><section class="section" aria-labelledby="archive-heading"><div class="section-heading"><h2 id="archive-heading">全部长文</h2></div>${tags.length ? `<div class="filter-bar" aria-label="文章筛选">${filters}</div>` : ''}<div>${rows}</div></section></main>${footer('../', '长文不是日更，是归档。')}</body></html>`;
}

function articlePage(post) {
  const rendered = md.render(post.body);
  const tags = post.tags.join(' / ') || '长文';
  const safeJson = (value) => JSON.stringify(value).replaceAll('<', '\\u003c');
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.summary,
    datePublished: post.date.label,
    inLanguage: 'zh-CN',
    author: { '@type': 'Person', name: 'TaoismZp' },
    mainEntityOfPage: articleUrl(post),
    url: articleUrl(post)
  };
  const documentHead = head({
    title: `${post.title} — TaoismZp`,
    description: post.summary,
    depth: '../../',
    canonical: articleUrl(post),
    type: 'article',
    publishedAt: post.date.iso,
    tags: post.tags
  }).replace('</head>', '<link rel="stylesheet" href="../../assets/content.css"><script type="application/ld+json">' + safeJson(structuredData) + '</script></head>');
  return `${documentHead}<body><a class="skip-link" href="#main">跳到正文</a><div class="article-progress" data-reading-progress aria-hidden="true"></div><header class="site-header"><div class="shell site-header__inner"><a class="site-brand" href="../../" translate="no">TaoismZp</a><nav class="site-nav" aria-label="主导航"><a href="../../">首页</a><a href="../" aria-current="page">长文</a><a href="../../projects/">项目</a><a href="../../about/">关于</a></nav></div></header><main id="main"><header class="shell article-head"><a class="article-head__back" href="../">← 返回长文</a><div class="article-head__meta">${escapeHtml(tags)} · ${escapeHtml(post.date.label)} · 约 ${readingMinutes(post.body)} 分钟</div><h1>${escapeHtml(post.title)}</h1><p class="article-head__dek">${escapeHtml(post.summary)}</p></header><div class="shell article-layout"><aside class="article-tools" aria-label="文章工具"><span>阅读模式</span><button type="button" data-share>分享这篇</button><span class="sr-only" data-share-status aria-live="polite"></span></aside><article class="article-body">${rendered}</article></div></main>${footer('../../', '读完一个判断，再决定信不信。')}</body></html>`;
}


function rssFeed(posts) {
  const items = posts.map(post => `<item><title>${xmlEscape(post.title)}</title><link>${xmlEscape(articleUrl(post))}</link><guid isPermaLink="true">${xmlEscape(articleUrl(post))}</guid><pubDate>${new Date(post.date.iso).toUTCString()}</pubDate><description>${xmlEscape(post.summary)}</description></item>`).join('');
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>TaoismZp — 长期交易，长期写作</title><link>${SITE_ROOT}</link><description>关于市场、概率、风险与判断的长文。</description><language>zh-cn</language>${items}</channel></rss>`;
}

function sitemap(posts) {
  const urls = [SITE_ROOT, SITE_ROOT + 'essays/', SITE_ROOT + 'projects/', SITE_ROOT + 'about/', ...posts.map(articleUrl)];
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
    urls.map(url => '<url><loc>' + xmlEscape(url) + '</loc></url>').join('') + '</urlset>';
}

function cleanGeneratedArticles() {
  fs.mkdirSync(ESSAYS_DIR, { recursive: true });
  for (const entry of fs.readdirSync(ESSAYS_DIR, { withFileTypes: true })) {
    if (entry.isDirectory()) fs.rmSync(path.join(ESSAYS_DIR, entry.name), { recursive: true, force: true });
  }
}

const posts = readPosts();
if (!posts.length && process.env.ALLOW_EMPTY_BUILD !== '1') {
  console.log('No published posts: preserving the accepted static frontend until the first real publication.');
  process.exit(0);
}

cleanGeneratedArticles();
fs.writeFileSync(path.join(ROOT, 'feed.xml'), rssFeed(posts));
fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), sitemap(posts));
fs.writeFileSync(path.join(ROOT, 'index.html'), homePage(posts));
fs.writeFileSync(path.join(ESSAYS_DIR, 'index.html'), archivePage(posts));
for (const post of posts) {
  const dir = path.join(ESSAYS_DIR, post.slug);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'index.html'), articlePage(post));
}

console.log(`Built ${posts.length} published post(s).`);
