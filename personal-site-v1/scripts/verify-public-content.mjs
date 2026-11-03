import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const site = (process.argv[2] || '').replace(/\/+$/, '') + '/';
if (!/^https?:\/\/[^/]+\//.test(site)) throw new Error('Supply the actual site root URL');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const postsDir = path.join(root, 'content', 'posts');
const published = [];
const unpublished = [];
for (const filename of fs.readdirSync(postsDir).filter(name => name.endsWith('.md'))) {
  const markdown = fs.readFileSync(path.join(postsDir, filename), 'utf8');
  const front = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
  if (!front) throw new Error('Missing frontmatter: ' + filename);
  const value = (key) => {
    const text = front.match(new RegExp('^' + key + ':\\s*(.*?)\\s*$', 'm'))?.[1]?.trim();
    return text?.replace(/^['"]|['"]$/g, '') || '';
  };
  const post = {
    title: value('title'),
    slug: value('slug') || filename.slice(0, -3),
    file: filename,
    status: value('status') || 'draft'
  };
  if (post.status === 'published') published.push(post);
  else unpublished.push(post);
}
async function request(url, requireSuccess = true) {
  let lastError;
  for (let attempt = 0; attempt < 6; attempt++) {
    try {
      const response = await fetch(url, { cache: 'no-store' });
      const text = await response.text();
      if (!requireSuccess || response.ok) return { status: response.status, text };
      lastError = new Error(url + ' returned HTTP ' + response.status);
    } catch (err) { lastError = err; }
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  throw lastError;
}
const home = (await request(site)).text;
const archive = (await request(site + 'essays/')).text;
if (!published.length) {
  if (!home.includes('第一篇公开长文，会从这里开始') ||
      !archive.includes('还没有公开长文')) {
    throw new Error('Empty public surface does not match zero published sources');
  }
} else {
  if (!archive.includes('class="archive-row"')) throw new Error('Published archive rows missing');
  for (const post of published) {
    const url = site + 'essays/' + encodeURIComponent(post.slug) + '/';
    const page = await request(url);
    if (!page.text.includes('<h1>') || !page.text.includes(post.title)) {
      throw new Error('Published article missing title: ' + post.file);
    }
    if (!archive.includes(post.title)) throw new Error('Archive missing published post: ' + post.file);
  }
}
for (const post of unpublished) {
  if (home.includes(post.title) || archive.includes(post.title)) {
    throw new Error('Unpublished title leaked to public listing: ' + post.file);
  }
  const article = await request(site + 'essays/' + encodeURIComponent(post.slug) + '/', false);
  if (article.status !== 404) throw new Error('Unpublished article URL accessible: ' + post.file);
}
for (const post of [...published, ...unpublished]) {
  const source = await request(site + 'content/posts/' + encodeURIComponent(post.file), false);
  if (source.status !== 404) throw new Error('Raw manuscript accessible from Pages: ' + post.file);
}
console.log('PASS: public source-to-surface verification; published=' + published.length + ', unpublished=' + unpublished.length);
