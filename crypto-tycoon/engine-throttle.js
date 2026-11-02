const TEST=new URLSearchParams(location.search).get('test')==='1';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<400;i++){
  if(window.__chainTycoon3d&&window.__cryptoVisualV2) break;
  await sleep(25);
}
if(window.__chainTycoon3d&&window.__cryptoVisualV2){
  const legacy=window.__chainTycoon3d.renderer;
  if(legacy&&!legacy.__v2Disabled){legacy.__v2Disabled=true;legacy.render=()=>{};legacy.shadowMap.enabled=false;}
  if(TEST){
    const v2=window.__cryptoVisualV2.renderer;
    v2.setPixelRatio(1);
    v2.shadowMap.enabled=false;
    const raw=v2.render.bind(v2);let n=0;
    v2.render=(...args)=>{if((n++%2)===0)return raw(...args)};
  }
  document.documentElement.dataset.visualPipeline='v2';
}
