import * as THREE from 'three';

const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  for(let i=0;i<500 && window.__cryptoSliceReady?.version!=='candidate-v7';i++) await new Promise(r=>setTimeout(r,20));
  if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
  const scene=window.__ctCapturedScene;
  if(!scene) throw new Error('audit: captured scene missing');

  window.__supervisionReadPixels=()=>{
    const scale=.5;
    const width=Math.max(320,Math.round(innerWidth*scale));
    const height=Math.max(240,Math.round(innerHeight*scale));
    const renderer=new THREE.WebGLRenderer({antialias:false,powerPreference:'low-power'});
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.18;
    renderer.shadowMap.enabled=false;
    renderer.setPixelRatio(1);
    renderer.setSize(width,height,false);

    const camera=new THREE.PerspectiveCamera(34,width/height,.1,100);
    if(width/height<1.25){camera.position.set(15.8,14.8,20.8);camera.fov=38}
    else if(width/height<1.5){camera.position.set(14.3,13.6,19.1);camera.fov=36}
    else{camera.position.set(12.8,12.6,17.2);camera.fov=34}
    camera.updateProjectionMatrix();camera.lookAt(0,.75,0);

    const target=new THREE.WebGLRenderTarget(width,height,{depthBuffer:true,stencilBuffer:false});
    renderer.setRenderTarget(target);
    renderer.render(scene,camera);
    const pixels=new Uint8Array(width*height*4);
    renderer.readRenderTargetPixels(target,0,0,width,height,pixels);
    renderer.setRenderTarget(null);
    target.dispose();renderer.dispose();

    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk){binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)))}
    return {
      width,height,
      rgbaBase64:btoa(binary),
      version:'candidate-v7',
      referencePixelsUsed:false,
      source:'half-res-structural-render-target',
      purpose:'stage-1 composition/forms/density supervision; final acceptance still requires real delivery surface'
    };
  };

  window.__supervisionSceneMeta={
    cssWidth:innerWidth,cssHeight:innerHeight,
    scale:.5,
    version:'candidate-v7',
    referencePixelsUsed:false,
    source:'half-res-structural-render-target'
  };
  document.documentElement.dataset.auditReady='1';
}
