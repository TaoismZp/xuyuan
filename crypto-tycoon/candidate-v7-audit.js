import * as THREE from 'three';

const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  try{
    for(let i=0;i<500 && (window.__cryptoSliceReady?.version!=='candidate-v7' || !window.__ctCapturedScene);i++){
      await new Promise(r=>setTimeout(r,20));
    }
    if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
    const scene=window.__ctCapturedScene;
    if(!scene) throw new Error('audit: captured scene missing');

    const cssW=innerWidth,cssH=innerHeight;
    const width=Math.max(320,Math.round(cssW*.42));
    const height=Math.max(240,Math.round(cssH*.42));
    const camera=new THREE.PerspectiveCamera(34,width/height,.1,100);
    if(width/height<1.25){camera.position.set(15.8,14.8,20.8);camera.fov=38}
    else if(width/height<1.5){camera.position.set(14.3,13.6,19.1);camera.fov=36}
    else{camera.position.set(12.8,12.6,17.2);camera.fov=34}
    camera.updateProjectionMatrix();
    camera.lookAt(0,.75,0);

    const canvas=document.createElement('canvas');
    canvas.width=width;canvas.height=height;
    const renderer=new THREE.WebGLRenderer({canvas,antialias:false,alpha:false,powerPreference:'low-power'});
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.18;
    renderer.shadowMap.enabled=false;
    renderer.setPixelRatio(1);
    renderer.setSize(width,height,false);

    const target=new THREE.WebGLRenderTarget(width,height,{depthBuffer:true,stencilBuffer:false});
    renderer.setRenderTarget(target);
    renderer.clear();
    renderer.render(scene,camera);
    const pixels=new Uint8Array(width*height*4);
    renderer.readRenderTargetPixels(target,0,0,width,height,pixels);
    renderer.setRenderTarget(null);

    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk){
      binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)));
    }

    window.__supervisionReadPixels=()=>({
      width,height,
      rgbaBase64:btoa(binary),
      version:'candidate-v7',
      referencePixelsUsed:false,
      source:'independent-lowres-render-target',
      purpose:'Stage-1 composition/forms/density supervision only'
    });
    window.__supervisionSceneMeta={
      cssWidth:cssW,cssHeight:cssH,width,height,
      version:'candidate-v7',referencePixelsUsed:false,
      source:'independent-lowres-render-target'
    };
    document.documentElement.dataset.auditReady='1';

    target.dispose();
    renderer.dispose();
  }catch(error){
    window.__supervisionAuditError=String(error?.stack||error);
    document.documentElement.dataset.auditReady='error';
    console.error('[supervision-audit]',error);
  }
}
