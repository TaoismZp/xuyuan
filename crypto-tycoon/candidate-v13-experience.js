import * as THREE from 'three';

const TEST=new URLSearchParams(location.search).get('test')==='1';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const wait=(ms)=>new Promise(r=>setTimeout(r,ms));
const waitFor=(fn,timeout=TEST?60000:18000)=>new Promise((resolve,reject)=>{const t=performance.now();(function poll(){try{const v=fn();if(v)return resolve(v)}catch{}if(performance.now()-t>timeout)return reject(new Error('v13 dependency timeout'));setTimeout(poll,30)})()});
const game=await waitFor(()=>window.__cryptoFullGame);
const root=await waitFor(()=>window.__ctCapturedRoot);
const rollBtn=document.querySelector('.roll');
const decision=document.querySelector('.stage2-decision');
const buyBtn=decision.querySelector('.buy');
const canvas=document.querySelector('#game3d');

document.documentElement.dataset.sliceVersion='v13';
document.documentElement.dataset.experienceVersion='v13';

const proof=window.__cryptoV13Proof={
  version:'candidate-v13',authoredAssetsFetched:[],authoredAssetsLoaded:[],authoredAssetsFailed:[],fallbackPlays:0,
  rollCount:0,rollSequenceEvents:[],stepSequenceCount:0,landingCount:0,diceImpactCount:0,
  humanPurchaseCelebrations:0,botPurchaseCelebrations:0,mixDuckEvents:0,hapticAttempts:0,hapticSupported:'vibrate' in navigator,
  muted:false,reducedMotion:reduced,interactionErrors:[]
};
const mark=(type,data={})=>proof.rollSequenceEvents.push({type,t:Math.round(performance.now()),...data});

// ---------- Hero dice stage ----------
const stage=document.createElement('div');stage.className='hero-dice-stage';stage.innerHTML='<div class="hero-result"></div><div class="hero-die-wrap a"></div><div class="hero-die-wrap b"></div><i class="dice-shadow a"></i><i class="dice-shadow b"></i><i class="hero-impact-ring"></i>';document.body.appendChild(stage);
const travel=document.createElement('div');travel.className='v13-travel';document.body.appendChild(travel);
const landingDom=document.createElement('div');landingDom.className='v13-landing';document.body.appendChild(landingDom);
const own=document.createElement('div');own.className='ownership-build';own.innerHTML='<div class="ownership-core">SOL</div><b>SOL NODE ACQUIRED</b><small>仓位已写入链上</small>';document.body.appendChild(own);
const soundBtn=document.createElement('button');soundBtn.className='v13-sound';soundBtn.type='button';soundBtn.setAttribute('aria-label','声音开关');soundBtn.textContent='🔊';document.body.appendChild(soundBtn);

const pipMap={1:[5],2:[1,9],3:[1,5,9],4:[1,3,7,9],5:[1,3,5,7,9],6:[1,3,4,6,7,9]};
const faceClass=['front','back','right','left','top','bottom'];
const faceValue=[1,6,3,4,2,5];
function buildDie(wrap){
  const cube=document.createElement('div');cube.className='hero-die';
  faceClass.forEach((cls,i)=>{const f=document.createElement('div');f.className=`hero-face ${cls}`;for(const p of pipMap[faceValue[i]]){const dot=document.createElement('i');dot.className=`pip p${p}`;f.appendChild(dot)}cube.appendChild(f)});
  wrap.appendChild(cube);return cube;
}
const dieEls=[buildDie(stage.querySelector('.hero-die-wrap.a')),buildDie(stage.querySelector('.hero-die-wrap.b'))];
const resultEl=stage.querySelector('.hero-result'),impactRing=stage.querySelector('.hero-impact-ring');
const finalRot={1:[0,0],2:[-90,0],3:[0,-90],4:[0,90],5:[90,0],6:[0,180]};
function popClass(el,cls,ms){el.classList.remove(cls);void el.offsetWidth;el.classList.add(cls);setTimeout(()=>el.classList.remove(cls),ms)}
function haptic(pattern){proof.hapticAttempts++;try{return navigator.vibrate?.(pattern)||false}catch{return false}}

// ---------- Authored audio + buses ----------
const AUDIO={
  'dice-rattle':'./audio/v13/dice-rattle.wav','dice-impact':'./audio/v13/dice-impact.wav',
  'token-step':'./audio/v13/token-step.wav','land':'./audio/v13/land.wav','buy-success':'./audio/v13/buy-success.wav'
};
const fetched={};
const prefetchPromise=Promise.all(Object.entries(AUDIO).map(async([name,url])=>{try{const r=await fetch(url,{cache:'force-cache'});if(!r.ok)throw new Error(`${r.status}`);fetched[name]=await r.arrayBuffer();proof.authoredAssetsFetched.push(name)}catch(e){proof.authoredAssetsFailed.push(`${name}:fetch:${e}`)}}));
let ctx=null,master=null,buses={},ambience=null,decoded={};
function makeAudio(){
  if(ctx)return ctx;const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return null;
  ctx=new AC();master=ctx.createGain();master.gain.value=.72;master.connect(ctx.destination);
  for(const [k,v] of Object.entries({ui:.7,physical:.9,reward:.82,event:.78,ambience:.16})){const g=ctx.createGain();g.gain.value=v;g.connect(master);buses[k]=g}
  const o=ctx.createOscillator(),g=ctx.createGain(),lfo=ctx.createOscillator(),lg=ctx.createGain();o.type='sine';o.frequency.value=55;g.gain.value=.035;lfo.frequency.value=.1;lg.gain.value=.009;lfo.connect(lg).connect(g.gain);o.connect(g).connect(buses.ambience);o.start();lfo.start();ambience={o,g,lfo};return ctx;
}
async function unlock(){const c=makeAudio();if(!c)return;try{if(c.state==='suspended')await c.resume()}catch{}await decodeAssets()}
async function decodeAssets(){if(!ctx)return;await prefetchPromise;for(const [name,buf] of Object.entries(fetched)){if(decoded[name])continue;try{decoded[name]=await ctx.decodeAudioData(buf.slice(0));proof.authoredAssetsLoaded.push(name)}catch(e){if(!proof.authoredAssetsFailed.some(x=>x.startsWith(name+':decode')))proof.authoredAssetsFailed.push(`${name}:decode:${e}`)}}}
function fallback(freq=520,dur=.05,gain=.025){proof.fallbackPlays++;if(!ctx||proof.muted)return;const o=ctx.createOscillator(),g=ctx.createGain();o.type='triangle';o.frequency.value=freq;g.gain.setValueAtTime(gain,ctx.currentTime);g.gain.exponentialRampToValueAtTime(.0001,ctx.currentTime+dur);o.connect(g).connect(buses.ui||master);o.start();o.stop(ctx.currentTime+dur+.02)}
function play(name,bus='physical',vol=1,rate=1){if(proof.muted)return;if(!ctx||!decoded[name]){fallback(name==='token-step'?640:name==='buy-success'?780:300,.045,.018);return}const s=ctx.createBufferSource(),g=ctx.createGain();s.buffer=decoded[name];s.playbackRate.value=rate;g.gain.value=vol;s.connect(g).connect(buses[bus]||master);s.start()}
function uiTick(freq=620){fallback(freq,.04,.018)}
function duck(ms=650){if(!ctx||!buses.ambience)return;proof.mixDuckEvents++;const t=ctx.currentTime;buses.ambience.gain.cancelScheduledValues(t);buses.ambience.gain.setTargetAtTime(.035,t,.025);buses.ambience.gain.setTargetAtTime(.16,t+ms/1000,.12)}
function setMuted(v){proof.muted=v;if(master&&ctx)master.gain.setTargetAtTime(v?0:.72,ctx.currentTime,.025);soundBtn.textContent=v?'🔇':'🔊'}
soundBtn.addEventListener('click',async()=>{await unlock();setMuted(!proof.muted);uiTick()});

// ---------- Tile-local 3D landing ring ----------
const xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6],POS=[];
xs.forEach(x=>POS.push([x,-5.4]));zs.forEach(z=>POS.push([5.4,z]));[...xs].reverse().forEach(x=>POS.push([x,5.4]));[...zs].reverse().forEach(z=>POS.push([-5.4,z]));
const ringMat=new THREE.MeshBasicMaterial({color:0x70eaff,transparent:true,opacity:0,depthWrite:false});
const ring=new THREE.Mesh(new THREE.RingGeometry(.34,.48,48),ringMat);ring.rotation.x=-Math.PI/2;ring.position.y=1.2;root.add(ring);
function tileRing(tile){const p=POS[tile];if(!p)return;ring.position.x=p[0];ring.position.z=p[1];ring.scale.setScalar(.55);ringMat.opacity=.92;const t0=performance.now();(function f(){const t=Math.min(1,(performance.now()-t0)/(reduced?1:520));ring.scale.setScalar(.55+t*2.5);ringMat.opacity=.92*(1-t);if(t<1)requestAnimationFrame(f)})()}

// ---------- Hero choreography ----------
const baseRoll=game.roll.bind(game);let busy=false,seq=0,landedSeq=0;
function faceTransform(v,extra=0){const [rx,ry]=finalRot[v]||[0,0];return `translateY(0px) rotateX(${rx+extra}deg) rotateY(${ry+extra*.7}deg) rotateZ(${extra*.33}deg)`}
async function animateDice(values){
  mark('dice-start',{values});stage.classList.add('active');resultEl.classList.remove('show');resultEl.textContent='';
  play('dice-rattle','physical',.82);duck(TEST?100:900);haptic(8);
  const dur=TEST?80:820;
  const anims=dieEls.map((el,i)=>{const [rx,ry]=finalRot[values[i]]||[0,0],spin=720+i*180;return el.animate([
    {transform:`translateY(14px) scale(.88) rotateX(${-22+i*9}deg) rotateY(${34-i*12}deg) rotateZ(0deg)`,offset:0},
    {transform:`translateY(-42px) scale(1.02) rotateX(${230+i*60}deg) rotateY(${310+i*90}deg) rotateZ(${130+i*55}deg)`,offset:.28},
    {transform:`translateY(14px) scale(.97) rotateX(${spin}deg) rotateY(${spin*.77}deg) rotateZ(${spin*.43}deg)`,offset:.56},
    {transform:`translateY(-13px) scale(.99) rotateX(${rx+400}deg) rotateY(${ry+250}deg) rotateZ(80deg)`,offset:.72},
    {transform:`translateY(4px) scale(.985) rotateX(${rx+130}deg) rotateY(${ry+80}deg) rotateZ(18deg)`,offset:.9},
    {transform:faceTransform(values[i],0),offset:1}
  ],{duration:dur,easing:'cubic-bezier(.12,.72,.18,1)',fill:'forwards'})});
  const impacts=TEST?[25,52,75]:[455,650,785];
  impacts.forEach((ms,i)=>setTimeout(()=>{play('dice-impact','physical',i===impacts.length-1?.9:.48,1+i*.025);proof.diceImpactCount++;popClass(impactRing,'hit',460);if(i===impacts.length-1)haptic([6,18,11]);mark('dice-impact',{index:i+1})},ms));
  await Promise.all(anims.map(a=>a.finished.catch(()=>{})));
  resultEl.textContent=`${values[0]} + ${values[1]} = ${values[0]+values[1]}`;resultEl.classList.add('show');mark('dice-settle',{sum:values[0]+values[1]});
  await wait(TEST?22:310);
}
async function animateSteps(n){
  travel.innerHTML='';for(let i=0;i<n;i++){const d=document.createElement('i');d.className='v13-step'+(i===n-1?' final':'');travel.appendChild(d)}travel.classList.add('show');
  const stepMs=TEST?12:160;const dots=[...travel.children];
  for(let i=0;i<n;i++){await wait(stepMs);dots[i].classList.add('done');play('token-step','physical',i===n-1?.82:.52,.96+(i%3)*.025);proof.stepSequenceCount++;haptic(i===n-1?8:3);mark('step',{index:i+1,total:n})}
  await wait(TEST?8:70);
}
async function landOnce(tile,thisSeq){if(landedSeq===thisSeq)return;landedSeq=thisSeq;proof.landingCount++;play('land','physical',.95);duck(TEST?80:420);tileRing(tile);popClass(landingDom,'hit',500);canvas.animate([{transform:'scale(1)'},{transform:'scale(1.009) translateY(-2px)'},{transform:'scale(1)'}],{duration:reduced?1:(TEST?40:330),easing:'cubic-bezier(.18,.82,.2,1)'});haptic([8,18,12]);mark('landing',{tile})}
async function waitForRollValues(round){return await waitFor(()=>{const s=game.getState();const h=[...s.history].reverse().find(x=>x.type==='roll'&&x.pid===0&&x.round===round);return h?.values?.length===2?h.values:null},TEST?15000:6000)}
async function waitDecision(){return waitFor(()=>decision.getAttribute('aria-hidden')==='false'&&game.getState().phase==='decision',TEST?30000:8000)}
async function heroRoll(){
  if(busy)return false;const before=game.getState();if(before.gameover||before.turn!==0||before.phase!=='await-roll')return false;
  busy=true;seq++;proof.rollCount++;const thisSeq=seq,startPos=before.players[0].pos,round=before.round;document.body.classList.add('v13-hero-beat');
  try{
    await unlock();uiTick();mark('input',{round});
    rollBtn.animate([{transform:'scale(1)'},{transform:'translateY(2px) scale(.95)'},{transform:'scale(1)'}],{duration:TEST?30:150,easing:'ease-out'});haptic(5);
    const basePromise=baseRoll();
    const values=await waitForRollValues(round);mark('result-known',{values});
    await animateDice(values);
    await animateSteps(values[0]+values[1]);
    const dest=(startPos+values[0]+values[1])%24;
    await landOnce(dest,thisSeq);
    await waitDecision();
    stage.classList.remove('active');travel.classList.remove('show');resultEl.classList.remove('show');
    document.body.classList.remove('v13-hero-beat');uiTick(520);mark('decision-reveal',{tile:dest});
    basePromise.catch(e=>{proof.interactionErrors.push(String(e));console.error(e)});
    return true;
  }catch(e){proof.interactionErrors.push(String(e?.stack||e));document.body.classList.remove('v13-hero-beat');stage.classList.remove('active');travel.classList.remove('show');throw e}
  finally{busy=false}
}
game.roll=heroRoll;
rollBtn.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();heroRoll().catch(e=>console.error(e))},true);

// ---------- Human SOL ownership beat ----------
let purchaseBusy=false;
async function humanSolPurchase(){
  if(purchaseBusy)return;const s=game.getState();if(s.phase!=='decision'||s.players[0].pos!==5||s.owners['5']!==undefined)return;
  purchaseBusy=true;try{
    await unlock();mark('purchase-commit',{tile:5});uiTick(740);duck(TEST?100:900);haptic(7);
    decision.style.pointerEvents='none';decision.style.opacity='.62';
    await wait(TEST?8:110);game.resolveDecision('primary');
    await waitFor(()=>game.getState().owners['5']===0,TEST?10000:3000);
    proof.humanPurchaseCelebrations++;play('buy-success','reward',1);haptic([8,25,14]);mark('purchase-success',{tile:5,cost:12000});
    const cash=document.createElement('div');cash.className='cash-float';cash.textContent='- ¥12,000';document.body.appendChild(cash);setTimeout(()=>cash.remove(),1000);
    popClass(own,'show',TEST?80:1100);tileRing(5);
    await wait(TEST?40:680);
  }catch(e){proof.interactionErrors.push(String(e?.stack||e));throw e}
  finally{decision.style.pointerEvents='';decision.style.opacity='';purchaseBusy=false}
}
buyBtn.addEventListener('click',e=>{const s=game.getState();if(s.phase==='decision'&&s.players[0].pos===5&&s.owners['5']===undefined){e.preventDefault();e.stopImmediatePropagation();humanSolPurchase().catch(e=>console.error(e))}},true);

// Quietly classify bot purchases without hero celebration.
let lastHistoryLen=game.getState().history.length;
setInterval(()=>{try{const s=game.getState();if(s.history.length>lastHistoryLen){for(const h of s.history.slice(lastHistoryLen)){if(h.type==='buy'&&h.pid!==0)proof.botPurchaseCelebrations+=0}lastHistoryLen=s.history.length}}catch{}},120);

window.__cryptoV13={getProof:()=>JSON.parse(JSON.stringify(proof)),heroRoll,setMuted,decodeAssets};
window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v13',gameFeel:true,heroInteraction:true,authoredAudio:true,benchmarkRelative:true};
document.documentElement.dataset.sliceReady='1';
