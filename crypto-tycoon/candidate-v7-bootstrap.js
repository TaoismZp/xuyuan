import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';

if(!window.__ctProbeInstalled){
  window.__ctProbeInstalled=true;
  const render=THREE.WebGLRenderer.prototype.render;
  THREE.WebGLRenderer.prototype.render=function(scene,camera){
    if(scene?.isScene && camera?.isPerspectiveCamera){
      window.__ctLiveRenderer=this;
      window.__ctLiveCamera=camera;
      window.__ctLiveRenderScene=scene;
    }
    return render.apply(this,arguments);
  };
  const composerRender=EffectComposer.prototype.render;
  EffectComposer.prototype.render=function(){
    window.__ctLiveComposer=this;
    return composerRender.apply(this,arguments);
  };
}
