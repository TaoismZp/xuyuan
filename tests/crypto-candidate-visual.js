const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:8080/crypto-tycoon/candidate-v7.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'load', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:30000 });
  await page.waitForTimeout(300);

  const audit = await page.evaluate(() => ({
    ready:window.__cryptoSliceReady,
    title:document.title,
    viewport:{w:innerWidth,h:innerHeight},
    canvas:{
      width:document.querySelector('#game3d')?.width||0,
      height:document.querySelector('#game3d')?.height||0,
      cssWidth:document.querySelector('#game3d')?.clientWidth||0,
      cssHeight:document.querySelector('#game3d')?.clientHeight||0
    },
    referenceImports:[...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
    referenceCss:getComputedStyle(document.body).backgroundImage,
    sliceVersion:document.documentElement.dataset.sliceVersion,
    evidenceSource:'cdp-page-capture-screenshot',
    referencePixelsUsed:false
  }));

  if(expectedVersion && audit.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${audit.ready.version} !== ${expectedVersion}`);
  if(audit.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(audit.referenceImports));
  if(!audit.ready || audit.ready.referencePixelsUsed !== false || audit.referencePixelsUsed !== false) throw new Error('candidate did not prove referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));

  // Freeze future animation after the accepted v7 frame is visible, then use the CDP capture path
  // already proven stable by this repository's Premium visual tests.
  await page.evaluate(() => { window.requestAnimationFrame = () => 0; });
  await page.waitForTimeout(180);
  const cdp=await context.newCDPSession(page);
  const shot=await cdp.send('Page.captureScreenshot',{
    format:'png',
    fromSurface:true,
    captureBeyondViewport:false
  });
  if(!shot?.data || shot.data.length<10000) throw new Error(`CDP screenshot invalid length=${shot?.data?.length||0}`);
  fs.writeFileSync(`artifacts/${name}.png`,Buffer.from(shot.data,'base64'));
  fs.writeFileSync(`artifacts/${name}.json`,JSON.stringify(audit,null,2));

  await context.close();
}

(async()=>{
  const launch = { headless:true, args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist'] };
  if (process.env.PW_CHANNEL) launch.channel = process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await capture(browser,{width:1672,height:941},'candidate-desktop');
  await capture(browser,{width:1194,height:834},'candidate-ipad');
  await browser.close();
  console.log('PASS candidate exact-build CDP visual evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});
