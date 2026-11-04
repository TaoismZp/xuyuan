(() => {
  'use strict';
  const form = document.querySelector('#writing-form');
  if (!form) return;
  const $ = (id) => document.getElementById(id);
  const titleInput = $('write-title');
  const summaryInput = $('write-summary');
  const dateInput = $('write-date');
  const tagsInput = $('write-tags');
  const slugInput = $('write-slug');
  const bodyInput = $('write-body');
  const featuredInput = $('write-featured');
  const previewNode = $('write-preview');
  const filenameNode = $('write-filename');
  const statusNode = $('write-status');
  const githubLink = $('write-github');
  const fallbackNode = $('write-fallback');
  const generatedNode = $('write-generated');
  const REPO_CREATE = 'https://github.com/TaoismZp/xuyuan/new/main/personal-site-v1/content/posts';
  const PUBLIC_BASE = 'https://taoismzp.github.io/xuyuan/personal-site-v1/essays/';
  let currentArtifact = null;
  // A filename-only GitHub link must never be mistaken for transfer of article body.
  let clipboardReady = false;

  const today = new Date();
  dateInput.value = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, '0'),
    String(today.getDate()).padStart(2, '0')
  ].join('-');

  const say = (message, error = false) => {
    statusNode.textContent = message;
    statusNode.dataset.error = String(error);
  };

  const valueOf = (el) => el.value.trim();
  const filenameFrom = (title, date, customSlug) => {
    const normalized = customSlug || (date + '-' + title
      .normalize('NFKC')
      .toLocaleLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 48)
      .replace(/-+$/g, ''));
    if (!/^[\p{L}\p{N}][\p{L}\p{N}_-]*$/u.test(normalized)) {
      throw new Error('文章路径只能包含中英文、数字、- 或 _，且必须以字母或数字开头。');
    }
    return normalized + '.md';
  };

  // JSON-quoted scalars are valid YAML; unlike string concatenation, user
  // input containing quotes/colons cannot break out of frontmatter fields.
  const quoted = (value) => JSON.stringify(value);
  const makeArtifact = ({ validate = true } = {}) => {
    const title = valueOf(titleInput);
    const summary = valueOf(summaryInput);
    const body = bodyInput.value.trim();
    const date = dateInput.value;
    if (!title || !summary || !body || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      if (validate) {
        say('请先填写标题、摘要、日期和完整正文。', true);
        form.reportValidity();
      }
      return null;
    }
    const tags = [...new Set(tagsInput.value
      .split(/[,，、;\n]+/)
      .map(tag => tag.trim())
      .filter(Boolean))]
      .slice(0, 12);
    let filename;
    try {
      filename = filenameFrom(title, date, valueOf(slugInput));
    } catch (error) {
      if (validate) {
        say(error.message, true);
        slugInput.focus();
      }
      return null;
    }
    const slug = filename.slice(0, -3);
    const markdown = [
      '---',
      'title: ' + quoted(title),
      'summary: ' + quoted(summary),
      'date: ' + quoted(date),
      'tags: ' + JSON.stringify(tags),
      'status: published',
      'featured: ' + (featuredInput.checked ? 'true' : 'false'),
      '---',
      '',
      body,
      ''
    ].join('\n');
    return {
      title, summary, date, tags, body, filename, slug, markdown,
      githubUrl: REPO_CREATE + '?filename=' + encodeURIComponent(filename),
      publicUrl: PUBLIC_BASE + encodeURIComponent(slug) + '/'
    };
  };

  const markFresh = () => {
    currentArtifact = null;
    clipboardReady = false;
    githubLink.setAttribute('aria-disabled', 'true');
    githubLink.setAttribute('href', REPO_CREATE);
    fallbackNode.hidden = true;
    filenameNode.textContent = '编辑内容后，请刷新预览并复制最新版本。';
    say('');
  };
  form.addEventListener('input', markFresh);
  form.addEventListener('change', markFresh);

  const prepare = () => {
    const artifact = makeArtifact();
    if (!artifact) return null;
    currentArtifact = artifact;
    filenameNode.textContent = 'GitHub 文件名：' + artifact.filename + ' · 预计文章地址：' + artifact.publicUrl;
    githubLink.href = artifact.githubUrl;
    githubLink.setAttribute('aria-disabled', clipboardReady ? 'false' : 'true');
    return artifact;
  };

  const renderPreview = () => {
    const artifact = prepare();
    if (!artifact) return;
    if (typeof window.markdownit !== 'function') {
      say('正文渲染器暂时未加载，请检查网络并刷新页面。发布稿仍可下载或复制。', true);
      return;
    }
    const renderer = window.markdownit({
      html: false, linkify: true, typographer: false, breaks: false
    });
    previewNode.replaceChildren();
    const header = document.createElement('header');
    header.className = 'write-preview-head';
    const meta = document.createElement('p');
    meta.className = 'write-preview-meta';
    meta.textContent = artifact.tags.join(' / ') + (artifact.tags.length ? ' · ' : '') + artifact.date;
    const heading = document.createElement('h3');
    heading.textContent = artifact.title;
    const description = document.createElement('p');
    description.className = 'write-preview-description';
    description.textContent = artifact.summary;
    header.append(meta, heading, description);

    const article = document.createElement('article');
    article.className = 'article-body write-preview-body';
    // The exact same pinned Markdown-it version and HTML-disabled rules
    // are used for production builds. No untrusted raw HTML is executed.
    article.innerHTML = renderer.render(artifact.body);
    previewNode.append(header, article);
    say('已生成本地预览。预览不会保存或公开文章。');
  };

  $('write-preview-button').addEventListener('click', renderPreview);

  $('write-copy').addEventListener('click', async () => {
    const artifact = prepare();
    if (!artifact) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(artifact.markdown);
      clipboardReady = true;
      githubLink.setAttribute('aria-disabled', 'false');
      fallbackNode.hidden = true;
      say('完整 Markdown 已复制。现在可以打开 GitHub，并将内容粘贴到新文件编辑框。');
    } catch {
      clipboardReady = false;
      githubLink.setAttribute('aria-disabled', 'true');
      fallbackNode.hidden = false;
      generatedNode.value = artifact.markdown;
      generatedNode.focus();
      generatedNode.select();
      say('自动复制不可用：请手动复制下方完整 Markdown，再前往 GitHub。', true);
    }
  });

  // When automatic clipboard access is blocked, let the author explicitly
  // confirm manual copying. This never reads the clipboard or uploads text.
  $('write-manual-ready').addEventListener('click', () => {
    if (!currentArtifact || fallbackNode.hidden) return;
    clipboardReady = true;
    githubLink.setAttribute('aria-disabled', 'false');
    say('已确认手动复制。去 GitHub 后仍需粘贴完整正文，再亲自 Commit。');
  });

  $('write-download').addEventListener('click', () => {
    const artifact = prepare();
    if (!artifact) return;
    const blob = new Blob([artifact.markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = artifact.filename;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    say('已生成本地 Markdown 备份。请保存在你自己的设备中。');
  });

  githubLink.addEventListener('click', (event) => {
    const artifact = prepare();
    if (!artifact) {
      event.preventDefault();
      return;
    }
    if (!clipboardReady) {
      event.preventDefault();
      say('请先复制完整发布稿；GitHub 新建文件链接只预填文件名，绝不会自动带入文章正文。', true);
      return;
    }
    // Only the filename is placed in the URL. The unpublished article body
    // never enters a GET query string, browser address history or referrer.
    if (!artifact.githubUrl.startsWith(REPO_CREATE + '?filename=')) {
      event.preventDefault();
      say('GitHub 发布链接无效。', true);
      return;
    }
    say('GitHub 会在新标签页打开：粘贴完整 Markdown，再点击 Commit changes 才会公开。');
  });

  const importFile = $('write-import');
  importFile.addEventListener('change', async () => {
    const file = importFile.files?.[0];
    if (!file) return;
    if (file.size > 4 * 1024 * 1024) {
      say('文件超过 4 MB，请先整理原稿后再导入。', true);
      importFile.value = '';
      return;
    }
    try {
      const text = await file.text();
      const front = text.match(/^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
      if (!front) {
        bodyInput.value = text;
      } else {
        bodyInput.value = text.slice(front[0].length).trim();
        const lookup = (name) => front[1].match(new RegExp('^' + name + ':\\s*(.*?)\\s*$', 'm'))?.[1] || '';
        const scalar = (name) => {
          const raw = lookup(name).trim();
          if (raw.startsWith('"')) {
            try { return JSON.parse(raw); } catch { return raw.slice(1, -1); }
          }
          return raw.replace(/^'|'$/g, '');
        };
        if (scalar('title')) titleInput.value = scalar('title');
        if (scalar('summary')) summaryInput.value = scalar('summary');
        if (/^\d{4}-\d{2}-\d{2}$/.test(scalar('date'))) dateInput.value = scalar('date');
        const tagsValue = lookup('tags');
        if (tagsValue.startsWith('[')) {
          try {
            const items = JSON.parse(tagsValue);
            if (Array.isArray(items)) tagsInput.value = items.join('，');
          } catch { /* Human should verify tags manually. */ }
        }
        featuredInput.checked = lookup('featured').trim() === 'true';
        say('已读取文件，识别了基本 Frontmatter。请核对标题、摘要、日期和标签后再发布。');
      }
      markFresh();
      say('文件已在本机读取。请核对导入内容并刷新预览；尚未上传或保存到 GitHub。');
    } catch {
      say('读取本地文件失败。请直接复制粘贴正文。', true);
    } finally {
      importFile.value = '';
    }
  });
})();
