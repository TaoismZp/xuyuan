import * as THREE from 'three';

const TEST=new URLSearchParams(location.search).get('test')==='1';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const waitFor=(fn,timeout=10000)=>new Promise((resolve,reject)=>{const t=performance.now();(function loop(){const v=fn();if(v)return resolve(v);if(performance.now()-t>timeout)return reject(new Error('v12 feel dependency timeout'));setTimeout(loop,30)})()});

const game=await waitFor(()=>window.__cryptoFullGame);
const root=await waitFor(()=>window.__ctCapturedRoot);
const canvas=document.querySelector('#game3d');
const roll=document.querySelector('.roll');
const toast=document.querySelector('.game-toast');
const decision=document.querySelector('.stage2-decision');

const proof=window.__cryptoFeelProof={
  version:'candidate-v12',audioUnlocked:false,muted:false,reducedMotion:reduced,
  cueCounts:{},diceImpacts:0,stepCues:0,landingPulses:0,positiveBursts:0,negativeBursts:0,
  interactionErrors:[]
};

// ---------- presentation layer ----------
const layer=document.createElement('div');
layer.className='feel-layer';layer.innerHTML='<div class="feel-flash"></div>';document.body.appendChild(layer);
const regimeBanner=document.createElement('div');regimeBanner.className='feel-regime';document.body.appendChild(regimeBanner);
const soundToggle=document.createElement('button');soundToggle.type='button';soundToggle.className='sound-toggle';soundToggle.setAttribute('aria-label','声音开关');soundToggle.innerHTML='<span>🔊</span><small>SOUND</small>';document.body.appendChild(soundToggle);

document.documentElement.dataset.feelVersion='v12';

function pulseClass(el,name,ms=360){if(reduced)return;el.classList.remove(name);void el.offsetWidth;el.classList.add(name);setTimeout(()=>el.classList.remove(name),ms)}
function flash(kind,ms=250){layer.classList.remove('positive','negative','event');layer.classList.add(kind);setTimeout(()=>layer.classList.remove(kind),ms)}
function floatText(text,loss=false){if(reduced)return;const el=document.createElement('div');el.className='feel-float'+(loss?' loss':'');el.textContent=text;layer.appendChild(el);setTimeout(()=>el.remove(),1100)}
function burst(kind='positive',count=14){if(reduced)return;layer.classList.add(kind);for(let i=0;i<count;i++){const p=document.createElement('i');p.className='feel-particle';const a=(Math.PI*2*i/count)+(Math.random()-.5)*.22,r=70+Math.random()*120;p.style.setProperty('--x',`${Math.cos(a)*r}px`);p.style.setProperty('--y',`${Math.sin(a)*r-55}px`);p.style.setProperty('--d',`${520+Math.random()*420}ms`);layer.appendChild(p);setTimeout(()=>p.remove(),1000)}setTimeout(()=>layer.classList.remove(kind),320)}
function showRegime(text){regimeBanner.textContent=text;pulseClass(regimeBanner,'show',1200)}

// ---------- audio engine ----------
let ctx=null,master=null,ambience=null;
function ensureAudio(){
  if(ctx)return ctx;
  const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return null;
  ctx=new AC();master=ctx.createGain();master.gain.value=.62;master.connect(ctx.destination);startAmbience();return ctx;
}
function unlockAudio(){
  try{const c=ensureAudio();if(!c)return;if(c.state==='suspended')c.resume();proof.audioUnlocked=true}catch(e){proof.interactionErrors.push(String(e))}
}
function now(){return ctx?.currentTime||0}
function tone(freq=440,dur=.08,type='sine',gain=.045,delay=0,endFreq=null){if(!ctx||proof.muted)return;const o=ctx.createOscillator(),g=ctx.createGain();o.type=type;o.frequency.setValueAtTime(freq,now()+delay);if(endFreq)o.frequency.exponentialRampToValueAtTime(Math.max(30,endFreq),now()+delay+dur);g.gain.setValueAtTime(.0001,now()+delay);g.gain.exponentialRampToValueAtTime(gain,now()+delay+.008);g.gain.exponentialRampToValueAtTime(.0001,now()+delay+dur);o.connect(g).connect(master);o.start(now()+delay);o.stop(now()+delay+dur+.02)}
function noise(dur=.08,gain=.025,delay=0,cutoff=1800){if(!ctx||proof.muted)return;const len=Math.ceil(ctx.sampleRate*dur),buf=ctx.createBuffer(1,len,ctx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);const src=ctx.createBufferSource(),f=ctx.createBiquadFilter(),g=ctx.createGain();src.buffer=buf;f.type='lowpass';f.frequency.value=cutoff;g.gain.setValueAtTime(gain,now()+delay);g.gain.exponentialRampToValueAtTime(.0001,now()+delay+dur);src.connect(f).connect(g).connect(master);src.start(now()+delay)}
function cue(name){
  proof.cueCounts[name]=(proof.cueCounts[name]||0)+1;
  if(!ctx||proof.muted)return;
  const s=(f,d=.07,t='triangle',g=.035,dl=0,e=null)=>tone(f,d,t,g,dl,e);
  if(name==='ui'){s(620,.045,'triangle',.03,0,760)}
  else if(name==='charge'){s(170,.14,'sine',.038,0,420);s(330,.1,'triangle',.022,.04,580)}
  else if(name==='dice-rattle'){for(let i=0;i<6;i++){noise(.035,.018,i*.055,2500);s(180+Math.random()*120,.035,'square',.012,i*.055)}}
  else if(name==='dice-impact'){noise(.11,.045,0,900);s(92,.16,'sine',.07,0,54);s(210,.08,'triangle',.025,.01,140)}
  else if(name==='step'){s(420+Math.random()*90,.035,'triangle',.018,0,310);noise(.025,.007,0,2100)}
  else if(name==='land'){s(150,.11,'sine',.045,0,110);s(300,.08,'triangle',.02,.015,250)}
  else if(name==='event'){s(280,.12,'triangle',.034,0,420);s(560,.12,'sine',.02,.08,700)}
  else if(name==='buy'){[440,660,880].forEach((f,i)=>s(f,.12,'triangle',.032,i*.055,f*1.04))}
  else if(name==='reward'){[523,659,784,1047].forEach((f,i)=>s(f,.13,'sine',.03,i*.06,f*1.01))}
  else if(name==='loss'){s(260,.18,'sawtooth',.034,0,128);s(130,.22,'sine',.045,.08,72)}
  else if(name==='bull'){[392,523,659].forEach((f,i)=>s(f,.18,'triangle',.032,i*.07,f*1.08))}
  else if(name==='bear'){[330,247,165].forEach((f,i)=>s(f,.2,'sine',.035,i*.065,f*.9))}
  else if(name==='finish'){[392,523,659,784].forEach((f,i)=>s(f,.24,'triangle',.033,i*.1,f*1.02))}
}
function startAmbience(){
  if(!ctx||ambience)return;
  const g=ctx.createGain();g.gain.value=.012;g.connect(master);
  const o1=ctx.createOscillator(),o2=ctx.createOscillator(),lfo=ctx.createOscillator(),lg=ctx.createGain();o1.type='sine';o2.type='triangle';o1.frequency.value=55;o2.frequency.value=82.5;lfo.frequency.value=.12;lg.gain.value=.004;lfo.connect(lg).connect(g.gain);o1.connect(g);o2.connect(g);o1.start();o2.start();lfo.start();ambience={g,o1,o2,lfo}
}
function setRegimeAudio(regime){if(!ambience)return;const map={sideways:[55,82.5],bull:[65.4,98],mania:[73.4,110],bear:[49,73.4],panic:[43.7,65.4]},v=map[regime]||map.sideways;ambience.o1.frequency.setTargetAtTime(v[0],now(),.18);ambience.o2.frequency.setTargetAtTime(v[1],now(),.18)}
function toggleMute(){proof.muted=!proof.muted;if(master)master.gain.setTargetAtTime(proof.muted?0:.62,now(),.03);soundToggle.querySelector('span').textContent=proof.muted?'🔇':'🔊';soundToggle.querySelector('small').textContent=proof.muted?'MUTED':'SOUND'}
soundToggle.addEventListener('click',()=>{unlockAudio();toggleMute();cue('ui')});

// ---------- richer roll staging ----------
const baseRoll=game.roll.bind(game);let feelBusy=false;
async function feelRoll(){
  if(feelBusy)return false;const s=game.getState();if(s.gameover||s.turn!==0||s.phase!=='await-roll')return false;
  feelBusy=true;unlockAudio();cue('ui');roll.classList.add('feel-pressed');setTimeout(()=>roll.classList.remove('feel-pressed'),90);roll.classList.add('feel-charge');cue('charge');flash('event',150);
  await new Promise(r=>setTimeout(r,TEST?8:145));roll.classList.remove('feel-charge');cue('dice-rattle');
  try{return await baseRoll()}finally{feelBusy=false}
}
game.roll=feelRoll;
roll.addEventListener('click',e=>{if(e.__v12Handled)return;e.preventDefault();e.stopImmediatePropagation();feelRoll().catch(err=>{proof.interactionErrors.push(String(err));console.error(err)})},true);
for(const b of document.querySelectorAll('button:not(.roll)'))b.addEventListener('pointerdown',()=>{unlockAudio();cue('ui')},{passive:true});

// ---------- 3D object probes ----------
function perimeterPositions(){const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];xs.forEach(x=>a.push([x,-5.4]));zs.forEach(z=>a.push([5.4,z]));[...xs].reverse().forEach(x=>a.push([x,5.4]));[...zs].reverse().forEach(z=>a.push([-5.4,z]));return a}
const POS=perimeterPositions();
function findGroupNear(x,y,z,max=.75){let best=null,dist=Infinity;for(const o of root.children){if(!o.isGroup)continue;const d=(o.position.x-x)**2+(o.position.y-y)**2+(o.position.z-z)**2;if(d<dist){dist=d;best=o}}return dist<max*max?best:null}
const dice=[findGroupNear(-1.2,1.22,5.45),findGroupNear(.15,1.15,5.7)].filter(Boolean),diceBase=dice.map(d=>d.position.y),diceAir=dice.map(()=>false);
function humanTarget(tile){const [x,z]=POS[tile];return{x:x-.3,z:z-.28}}
function findHumanToken(){const st=game.getState(),t=humanTarget(st.players[0].pos);let best=null,dist=Infinity;for(const o of root.children){if(!o.isGroup||o.position.y<.72||o.position.y>1.3)continue;const d=(o.position.x-t.x)**2+(o.position.z-t.z)**2;if(d<dist){dist=d;best=o}}return dist<.8?best:null}
const humanToken=findHumanToken();

const pulseMat=new THREE.MeshBasicMaterial({color:0x7feaff,transparent:true,opacity:0,depthWrite:false});const pulseRing=new THREE.Mesh(new THREE.RingGeometry(.38,.48,48),pulseMat);pulseRing.rotation.x=-Math.PI/2;pulseRing.position.y=1.22;root.add(pulseRing);
function landingPulse(){proof.landingPulses++;cue('land');pulseClass(canvas,'feel-punch',390);if(!humanToken)return;const st=game.getState(),[x,z]=POS[st.players[0].pos];pulseRing.position.x=x;pulseRing.position.z=z;pulseRing.scale.setScalar(.6);pulseMat.opacity=.7;const started=performance.now();(function anim(){const t=Math.min(1,(performance.now()-started)/(reduced?1:420));pulseRing.scale.setScalar(.6+t*2.2);pulseMat.opacity=.7*(1-t);if(t<1)requestAnimationFrame(anim)})()}

let lastToken=humanToken?humanToken.position.clone():null,travel=0,wasMoving=false,stillFrames=0;
function objectMonitor(){
  if(humanToken&&lastToken){const d=humanToken.position.distanceTo(lastToken);if(d>.008){travel+=d;wasMoving=true;stillFrames=0;if(travel>.55){travel=0;proof.stepCues++;cue('step')}}else if(wasMoving){stillFrames++;if(stillFrames>4){wasMoving=false;stillFrames=0;landingPulse()}}lastToken.copy(humanToken.position)}
  dice.forEach((d,i)=>{const base=diceBase[i];if(!diceAir[i]&&d.position.y>base+.12)diceAir[i]=true;else if(diceAir[i]&&d.position.y<=base+.035){diceAir[i]=false;proof.diceImpacts++;cue('dice-impact');pulseClass(canvas,'feel-punch',330)}});
  requestAnimationFrame(objectMonitor)
}
requestAnimationFrame(objectMonitor);

// ---------- semantic feedback from game results ----------
let lastRegime=game.getState().regime,lastGameover=false,lastToast='';
function positive(text,cueName='reward'){cue(cueName);proof.positiveBursts++;flash('positive',260);burst('positive',16);floatText(text);pulseClass(canvas,'feel-punch',380)}
function negative(text){cue('loss');proof.negativeBursts++;flash('negative',300);burst('negative',10);floatText(text,true);pulseClass(canvas,'feel-negative-punch',430)}
function onToast(text){if(!text||text===lastToast)return;lastToast=text;
  if(/买入|加仓/.test(text))positive('仓位建立','buy');
  else if(/空投|收益|取出|获得|区块奖励/.test(text))positive('收益到账','reward');
  else if(/支付|损失|清算|爆仓|折价卖出/.test(text))negative('风险兑现');
  else if(/事件|消息|巨鲸|黑客|行情/.test(text)){cue('event');flash('event',260)}
}
new MutationObserver(()=>onToast(toast.textContent.trim())).observe(toast,{childList:true,subtree:true,characterData:true});
new MutationObserver(()=>{if(decision.classList.contains('open')){cue('event');flash('event',180)}}).observe(decision,{attributes:true,attributeFilter:['class']});

setInterval(()=>{
  try{const s=game.getState();
    if(s.regime!==lastRegime){lastRegime=s.regime;setRegimeAudio(s.regime);const bullish=s.regime==='bull'||s.regime==='mania';cue(bullish?'bull':'bear');showRegime(s.regime==='mania'?'狂热期 · MANIA':s.regime==='bull'?'牛市 · BULL':s.regime==='bear'?'熊市 · BEAR':s.regime==='panic'?'恐慌期 · PANIC':'震荡市 · SIDEWAYS');flash(bullish?'positive':'negative',320)}
    if(s.gameover&&!lastGameover){lastGameover=true;cue('finish');positive('本局结算','finish')}
    if(!s.gameover)lastGameover=false;
  }catch(e){proof.interactionErrors.push(String(e))}
},80);

window.__cryptoFeel={cue,positive,negative,toggleMute,getProof:()=>JSON.parse(JSON.stringify(proof)),unlockAudio};
window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v12',gameFeel:true,benchmark:'GAME_FEEL_BENCHMARK',audioLayer:'web-audio-procedural-slice',motionLayer:'v12-feel'};
document.documentElement.dataset.sliceVersion='v12';
document.documentElement.dataset.sliceReady='1';
