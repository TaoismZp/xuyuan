const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'https://taoismzp.github.io/xuyuan/crypto-tycoon/candidate-v1.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  // Supervision must inspect the same scene, not benchmark animation throughput.
  // Limit requestAnimationFrame only inside the CI browser so software WebGL cannot starve screenshot capture.
  await context.addInitScript(() => {
    const nativeRAF = window.requestAnimationFrame.bind(window);
    let last = 0;
    window.requestAnimationFrame = cb => nativeRAF(ts => {
      const delay = Math.max(0, 125 - (ts - last));
      setTimeout(() => { last = performance.now(); cb(last); }, delay);
    });
  });
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });
  await page.goto(target, { waitUntil:'networkidle', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:45000 });
  await page.waitForTimeout(700);
  await page.screenshot({ path:`artifacts/${name}.png`, fullPage:false, animations:'disabled', timeout:20000 });
  const state = await page.evaluate(() => ({
    ready: window.__cryptoSliceReady,
    title: document.title,
    viewport: { w: innerWidth, h: innerHeight },
    referenceImports: [...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
    referenceCss: getComputedStyle(document.body).backgroundImage
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
  console.log('PASS candidate true-3D capture',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});
