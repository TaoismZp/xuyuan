import * as THREE from 'three';

const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  try{
    window.__supervisionAuditStage='waiting-live-renderer';
    for(let i=0;i<500 && (
      window.__cryptoSliceReady?.version!=='candidate-v7' ||
      !window.__ctLiveRenderer ||
      !window.__ctLiveCamera ||
      !window.__ctLiveRenderScene
    );i++){
      await new Promise(r=>setTimeout(r,20));
    }
    if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
    const renderer=window.__ctLiveRenderer;
    const camera=window.__ctLiveCamera;
    const scene=window.__ctLiveRenderScene;
    if(!renderer||!camera||!scene) throw new Error('audit: live renderer/camera/scene missing');

    const cssW=innerWidth,cssH=innerHeight;
    const width=Math.max(320,Math.round(cssW*.36));
    const height=Math.max(240,Math.round(cssH*.36));
    const target=new THREE.WebGLRenderTarget(width,height,{depthBuffer:true,stencilBuffer:false});
    const previousTarget=renderer.getRenderTarget();

    window.__supervisionAuditStage='rendering';
    renderer.setRenderTarget(target);
    renderer.clear();
    renderer.render(scene,camera);

    window.__supervisionAuditStage='reading-pixels';
    const pixels=new Uint8Array(width*height*4);
    renderer.readRenderTargetPixels(target,0,0,width,height,pixels);
    renderer.setRenderTarget(previousTarget);

    window.__supervisionAuditStage='encoding';
    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk){
      binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)));
    }
    const encoded=btoa(binary);

    window.__supervisionReadPixels=()=>({
      width,height,
      rgbaBase64:encoded,
      version:'candidate-v7',
      referencePixelsUsed:false,
      source:'existing-live-renderer-lowres-target',
      purpose:'Stage-1 composition/forms/density supervision only'
    });
    window.__supervisionSceneMeta={
      cssWidth:cssW,cssHeight:cssH,width,height,
      version:'candidate-v7',referencePixelsUsed:false,
      source:'existing-live-renderer-lowres-target'
    };
    window.__supervisionAuditStage='ready';
    document.documentElement.dataset.auditReady='1';
    target.dispose();
  }catch(error){
    window.__supervisionAuditError=String(error?.stack||error);
    document.documentElement.dataset.auditReady='error';
    console.error('[supervision-audit]',window.__supervisionAuditStage,error);
  }
}
