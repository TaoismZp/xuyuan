const { chromium } = require('playwright');
const { PNG } = require('pngjs');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:8080/crypto-tycoon/candidate-v7.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

function writeRgbaPng(path,width,height,rgba){
  const src=Buffer.from(rgba,'base64');
  if(src.length!==width*height*4) throw new Error(`RGBA size mismatch ${src.length} !== ${width*height*4}`);
  const png=new PNG({width,height});
  const row=width*4;
  for(let y=0;y<height;y++) src.copy(png.data,y*row,(height-1-y)*row,(height-y)*row);
  fs.writeFileSync(path,PNG.sync.write(png));
}

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'load', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:30000 });
  await page.waitForFunction(() => ['1','error'].includes(document.documentElement.dataset.auditReady || ''), null, { timeout:30000 });

  const auditState=await page.evaluate(()=>({state:document.documentElement.dataset.auditReady,error:window.__supervisionAuditError||null}));
  if(auditState.state!=='1') throw new Error(`supervision audit failed: ${auditState.error||'unknown audit error'}`);

  const audit = await page.evaluate(() => {
    const pixels=window.__supervisionReadPixels();
    return {
      pixels,
      sceneMeta: window.__supervisionSceneMeta,
      ready: window.__cryptoSliceReady,
      title: document.title,
      viewport: { w: innerWidth, h: innerHeight },
      referenceImports: [...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
      referenceCss: getComputedStyle(document.body).backgroundImage,
      sliceVersion: document.documentElement.dataset.sliceVersion
    };
  });

  if(expectedVersion && audit.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${audit.ready.version} !== ${expectedVersion}`);
  if(audit.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(audit.referenceImports));
  if(!audit.ready || audit.ready.referencePixelsUsed !== false || audit.pixels?.referencePixelsUsed !== false) throw new Error('candidate did not prove referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));

  writeRgbaPng(`artifacts/${name}-scene.png`,audit.pixels.width,audit.pixels.height,audit.pixels.rgbaBase64);
  delete audit.pixels.rgbaBase64;
  fs.writeFileSync(`artifacts/${name}.json`, JSON.stringify(audit,null,2));

  await page.evaluate(() => {
    const c=document.querySelector('#game3d'); if(c) c.style.visibility='hidden';
    document.documentElement.style.background='transparent';
    document.body.style.background='transparent';
  });
  try {
    await page.screenshot({path:`artifacts/${name}-hud.png`,fullPage:false,animations:'disabled',omitBackground:true,timeout:10000});
  } catch(e) {
    fs.writeFileSync(`artifacts/${name}-hud-capture-error.txt`, String(e));
  }

  await context.close();
}

(async()=>{
  const launch = { headless:true, args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist'] };
  if (process.env.PW_CHANNEL) launch.channel = process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await capture(browser,{width:1672,height:941},'candidate-desktop');
  await capture(browser,{width:1194,height:834},'candidate-ipad');
  await browser.close();
  console.log('PASS candidate exact-build render-target evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});
