import { webkit } from 'playwright';
import fs from 'node:fs';

const base='https://taoismzp.github.io/xuyuan/longform-v2/';
fs.mkdirSync('longform-v2/evidence',{recursive:true});
const browser=await webkit.launch();
const profiles=[
  {name:'iphone',viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:3},
  {name:'ipad',viewport:{width:834,height:1194},isMobile:true,hasTouch:true,deviceScaleFactor:2},
  {name:'desktop',viewport:{width:1440,height:1000},isMobile:false,hasTouch:false,deviceScaleFactor:1}
];
for(const p of profiles){
  const ctx=await browser.newContext({viewport:p.viewport,isMobile:p.isMobile,hasTouch:p.hasTouch,deviceScaleFactor:p.deviceScaleFactor,colorScheme:'light'});
  const page=await ctx.newPage();
  for(const path of ['', 'posts/welcome.html', 'write.html']){
    const res=await page.goto(base+path,{waitUntil:'networkidle'});
    if(!res||!res.ok()) throw new Error(`${p.name} ${path} HTTP ${res&&res.status()}`);
    const metrics=await page.evaluate(()=>({
      overflow:document.documentElement.scrollWidth-window.innerWidth,
      h1:!!document.querySelector('h1'),
      bodyFont:parseFloat(getComputedStyle(document.body).fontSize),
      proseFont:document.querySelector('.prose')?parseFloat(getComputedStyle(document.querySelector('.prose')).fontSize):null,
      title:document.title
    }));
    if(metrics.overflow>1) throw new Error(`${p.name} ${path} horizontal overflow ${metrics.overflow}`);
    if(!metrics.h1) throw new Error(`${p.name} ${path} missing h1`);
    if(path.includes('welcome') && metrics.proseFont<18) throw new Error(`${p.name} article prose too small: ${metrics.proseFont}`);
    const label=(path||'home').replaceAll('/','-').replace('.html','');
    await page.screenshot({path:`longform-v2/evidence/${p.name}-${label}.png`,fullPage:true});
  }
  await ctx.close();
}
await browser.close();
console.log('longform-v2 WebKit same-surface emulation: PASS');
