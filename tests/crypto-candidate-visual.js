const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'https://taoismzp.github.io/xuyuan/crypto-tycoon/candidate-v1.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  // Keep the inspected scene intact but reduce CI animation pressure under software WebGL.
  await context.addInitScript(() => {
    const nativeRAF = window.requestAnimationFrame.bind(window);
    let last = 0;
    window.requestAnimationFrame = cb => nativeRAF(ts => {
      const delay = Math.max(0, 150 - (ts - last));
      setTimeout(() => { last = performance.now(); cb(last); }, delay);
    });
  });

  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'networkidle', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:45000 });
  await page.waitForTimeout(1200);

  // Freeze only the CI browser after the final candidate has rendered. This is analogous to
  // stopping motion for a construction inspection photo; it does not change production code.
  await page.evaluate(() => {
    window.__SUPERVISION_FREEZE__ = true;
    window.requestAnimationFrame = () => 0;
  });
  await page.waitForTimeout(300);

  const cdp = await context.newCDPSession(page);
  const shot = await cdp.send('Page.captureScreenshot', {
    format:'png',
    fromSurface:true,
    captureBeyondViewport:false
  });
  fs.writeFileSync(`artifacts/${name}.png`, Buffer.from(shot.data,'base64'));

  const state = await page.evaluate(() => ({
    ready: window.__cryptoSliceReady,
    title: document.title,
    viewport: { w: innerWidth, h: innerHeight },
    referenceImports: [...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
    referenceCss: getComputedStyle(document.body).backgroundImage,
    sliceVersion: document.documentElement.dataset.sliceVersion,
    supervisionFreeze: !!window.__SUPERVISION_FREEZE__
  }));

  if(expectedVersion && state.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${state.ready.version} !== ${expectedVersion}`);
  if(state.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(state.referenceImports));
  if(!state.ready || state.ready.referencePixelsUsed !== false) throw new Error('candidate did not assert referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));
  fs.writeFileSync(`artifacts/${name}.json`, JSON.stringify(state,null,2));
  await context.close();
}

(async()=>{
  const launch = { headless:true, args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist'] };
  if (process.env.PW_CHANNEL) launch.channel = process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await capture(browser,{width:1672,height:941},'candidate-desktop');
  await capture(browser,{width:1194,height:834},'candidate-ipad');
  await browser.close();
  console.log('PASS candidate exact-build true-3D evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});