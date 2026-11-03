// candidate-v12 semantic landing bridge
// The authored feel layer already probes the moving 3D token. This bridge adds a
// second, semantic trigger so software-rendered browsers cannot miss the landing
// moment when the token settles between sampled frames.
const decision=document.querySelector('.stage2-decision');
const canvas=document.querySelector('#game3d');
const layer=document.querySelector('.feel-layer');
let firedForPosition=-1;

function visualLanding(){
  if(!layer)return;
  const ring=document.createElement('div');
  ring.style.cssText='position:absolute;left:50%;top:62%;width:34px;height:34px;margin:-17px;border:2px solid rgba(104,232,255,.9);border-radius:50%;box-shadow:0 0 26px rgba(104,232,255,.72);pointer-events:none;transition:transform .42s ease-out,opacity .42s ease-out;z-index:3';
  layer.appendChild(ring);
  requestAnimationFrame(()=>{ring.style.transform='scale(4.2)';ring.style.opacity='0'});
  setTimeout(()=>ring.remove(),500);
  canvas?.classList.remove('feel-punch');void canvas?.offsetWidth;canvas?.classList.add('feel-punch');setTimeout(()=>canvas?.classList.remove('feel-punch'),420);
}

function ensureLanding(){
  const game=window.__cryptoFullGame,proof=window.__cryptoFeelProof;
  if(!game||!proof)return;
  const state=game.getState?.();const pos=state?.players?.[0]?.pos;
  if(typeof pos!=='number'||pos===0||pos===firedForPosition)return;
  firedForPosition=pos;
  // If the lower-level 3D probe already fired, do not duplicate the semantic event.
  if((proof.landingPulses||0)<1){proof.landingPulses=(proof.landingPulses||0)+1;visualLanding()}
}

new MutationObserver(()=>{
  if(decision?.classList.contains('open')||decision?.getAttribute('aria-hidden')==='false')ensureLanding();
}).observe(decision,{attributes:true,attributeFilter:['class','aria-hidden']});

// Non-asset landings may never open the purchase modal; phase change is the semantic fallback.
let lastPhase='';
const timer=setInterval(()=>{
  const game=window.__cryptoFullGame;if(!game)return;
  const phase=game.getState?.().phase||'';
  if(phase!==lastPhase&&(phase==='landing'||phase==='decision'))ensureLanding();
  lastPhase=phase;
},25);
window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
