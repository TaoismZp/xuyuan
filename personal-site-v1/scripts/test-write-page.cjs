const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const base = process.env.WRITER_BASE || 'http://127.0.0.1:4175/personal-site-v1/write/';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const output = 'personal-site-v1/writer-evidence';
  fs.mkdirSync(output, { recursive: true });
  for (const [name, width, height, mobile] of [
    ['iphone-small', 320, 750, true],
    ['iphone', 390, 844, true],
    ['ipad', 1024, 1366, true],
    ['desktop', 1440, 1000, false]
  ]) {
    const context = await browser.newContext({
      viewport: { width, height }, isMobile: mobile,
      hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1,
      acceptDownloads: true,
      permissions: ['clipboard-read', 'clipboard-write']
    });
    const page = await context.newPage();
    const externalRequests = [];
    page.on('request', request => {
      const url = new URL(request.url());
      if (url.hostname !== '127.0.0.1' && url.hostname !== 'localhost') externalRequests.push(request.url());
    });
    await page.goto(base, { waitUntil: 'networkidle' });
    assert(await page.title() === '写作与发布 — TaoismZp', name + ': wrong writing surface');
    assert(await page.locator('input#write-title').count() === 1, name + ': missing writing fields');
    assert(await page.evaluate(() => typeof window.markdownit) === 'function', name + ': production Markdown-it bundle not loaded');
    assert(!await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth), name + ': initial overflow');
    const heroLines = await page.locator('.write-intro h1').evaluate(el =>
      el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight));
    assert(heroLines > 1.8 && heroLines < 2.2, name + ': authored hero broken into ' + heroLines.toFixed(2) + ' lines instead of two');

    assert(externalRequests.length === 0, name + ': writing page made external requests before user confirms: ' + externalRequests);
    await page.screenshot({ path: output + '/' + name + '-empty.png', fullPage: false });

    const inputBody = '我想先把文章写完整。\n\n## 第二层发现\n\n这是第二段。\n\n<script>window.__injected = true</script>\n\n**有用的判断**。';
    await page.locator('#write-title').fill('一个真正的交易问题');
    await page.locator('#write-summary').fill('完整推演如何改善长期交易，不只是解释一次成功。');
    await page.locator('#write-date').fill('2026-11-04');
    await page.locator('#write-tags').fill('交易，概率');
    await page.locator('#write-body').fill(inputBody);
    await page.locator('#write-featured').check();
    await page.locator('#write-preview-button').click();

    assert((await page.locator('.write-preview-head h3').innerText()) === '一个真正的交易问题', name + ': preview title mismatch');
    assert((await page.locator('.write-preview-body h2').innerText()) === '第二层发现', name + ': markdown heading mismatch');
    assert(await page.locator('.write-preview-body script').count() === 0, name + ': raw script injected into preview');
    assert(!await page.evaluate(() => window.__injected === true), name + ': untrusted article executed script');
    const link = await page.locator('#write-github').getAttribute('href');
    assert(link.startsWith('https://github.com/TaoismZp/xuyuan/new/main/personal-site-v1/content/posts?filename='), name + ': GitHub create path wrong');
    assert(!link.includes('value=') && !link.includes(encodeURIComponent(inputBody)) && link.length < 500, name + ': private article leaked into URL');
    assert(link.includes('2026-11-04-'), name + ': file slug missing date');
    assert(await page.locator('#write-github').getAttribute('aria-disabled') === 'true', name + ': link was enabled before copying');
    const prematureNavigation = await page.evaluate(() => document.querySelector('#write-github').dispatchEvent(new MouseEvent('click', { bubbles:true, cancelable:true })));
    assert(!prematureNavigation, name + ': GitHub navigation was not blocked before copying');
    assert((await page.locator('#write-status').innerText()).includes('请先复制'), name + ': missing truthful handoff warning');
    assert(!await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth), name + ': editor overflow');
    await page.screenshot({ path: output + '/' + name + '-preview.png', fullPage: false });

    await page.locator('#write-copy').click();
    assert(await page.locator('#write-github').getAttribute('aria-disabled') === 'false', name + ': link not enabled after copy');
    const clipboard = await page.evaluate(async () => navigator.clipboard.readText());
    assert(clipboard.startsWith('---\ntitle: "一个真正的交易问题"'), name + ': clipboard YAML title wrong');
    assert(clipboard.includes('status: published'), name + ': content not set to published');
    assert(clipboard.includes('featured: true'), name + ': featured toggle lost');
    assert(clipboard.includes('tags: ["交易","概率"]'), name + ': tags malformed');
    assert(clipboard.endsWith(inputBody + '\n'), name + ': source text not preserved');
    assert(!clipboard.includes('github_pat_'), name + ': credentials marker in clipboard');

    const downloadPromise = page.waitForEvent('download');
    await page.locator('#write-download').click();
    const download = await downloadPromise;
    assert(download.suggestedFilename().endsWith('.md'), name + ': downloaded filename invalid');
    const disk = fs.readFileSync(await download.path(), 'utf8');
    assert(disk === clipboard, name + ': local file does not equal copy/preview source');
    const nav = await page.locator('nav.site-nav a').evaluateAll(links => links.map(el => {
      const range = document.createRange();
      range.selectNodeContents(el);
      return [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0).length;
    }));
    assert(nav.every(n => n === 1), name + ': header navigation wraps into orphan glyphs');

    // A subsequent edit invalidates the previously copied Markdown.
    await page.locator('#write-summary').fill('修改了摘要，因此需要重新复制。');
    assert(await page.locator('#write-github').getAttribute('aria-disabled') === 'true', name + ': stale clipboard was treated as fresh');
    const staleNavigation = await page.evaluate(() => document.querySelector('#write-github').dispatchEvent(new MouseEvent('click', { bubbles:true, cancelable:true })));
    assert(!staleNavigation, name + ': stale content could navigate to GitHub');

    await page.reload({ waitUntil: 'networkidle' });
    assert((await page.locator('#write-title').inputValue()) === '', name + ': content unexpectedly auto-stored after reload');
    await page.locator('#write-import').setInputFiles({
      name: 'source.md', mimeType: 'text/markdown',
      buffer: Buffer.from('我已有的第一段。\n\n## 第一处观点\n\n无网络上传。', 'utf8')
    });
    assert((await page.locator('#write-body').inputValue()).includes('第一处观点'), name + ': local file import failed');
    assert(externalRequests.length === 0, name + ': external request from local writing page: ' + externalRequests);
    await context.close();
  }
  await browser.close();
  console.log('PASS: local-only longform composition, Markdown preview, clipboard, .md export, GitHub filename-only link and responsive surfaces');
})().catch(error => { console.error(error.stack || error); process.exit(1); });
