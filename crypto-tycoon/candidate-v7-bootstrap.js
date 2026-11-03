import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';

if(!window.__ctProbeInstalled){
  window.__ctProbeInstalled=true;

  // Capture from the two objects that explicitly own the resources we need.
  // This is more stable than intercepting WebGLRenderer internals.
  const composerRender=EffectComposer.prototype.render;
  EffectComposer.prototype.render=function(){
    window.__ctLiveComposer=this;
    if(this.renderer) window.__ctLiveRenderer=this.renderer;
    return composerRender.apply(this,arguments);
  };

  const passRender=RenderPass.prototype.render;
  RenderPass.prototype.render=function(renderer,writeBuffer,readBuffer,deltaTime,maskActive){
    window.__ctLiveRenderer=renderer || window.__ctLiveRenderer;
    if(this.scene?.isScene) window.__ctLiveRenderScene=this.scene;
    if(this.camera?.isCamera) window.__ctLiveCamera=this.camera;
    return passRender.apply(this,arguments);
  };
}
