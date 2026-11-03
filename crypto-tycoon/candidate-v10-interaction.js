await import('./candidate-v9-augment.js');

const TEST=new URLSearchParams(location.search).get('test')==='1';
const root=window.__ctCapturedRoot;
if(!root) throw new Error('v10: root missing');

function perimeterPositions(){
  const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];
  xs.forEach(x=>a.push([x,-5.4]));
  zs.forEach(z=>a.push([5.4,z]));
  [...xs].reverse().forEach(x=>a.push([x,5.4]));
  [...zs].reverse().forEach(z=>a.push([-5.4,z]));
  return a;
}
const tilePos=perimeterPositions();

function findToken(tileIndex){
  const [x,z]=tilePos[tileIndex];let best=null,dist=1e9;
  for(const o of root.children){
    if(!o.isGroup||o.position.y<.72||o.position.y>1.28)continue;
    const d=(o.position.x-x)**2+(o.position.z-z)**2;
    if(d<dist){dist=d;best=o}
  }
  return dist<.42?best:null;
}
function findGroupNear(x,y,z,max=.5){
  let best=null,dist=1e9;
  for(const o of root.children){
    if(!o.isGroup)continue;
    const d=(o.position.x-x)**2+(o.position.y-y)**2+(o.position.z-z)**2;
    if(d<dist){dist=d;best=o}
  }
  return dist<max*max?best:null;
}

const humanToken=findToken(17);
const botToken=findToken(10);
const dice=[findGroupNear(-1.2,1.22,5.45,.65),findGroupNear(.15,1.15,5.7,.65)];
if(!humanToken||!botToken||dice.some(d=>!d)) throw new Error('v10: interactive scene objects not found');

const state={
  version:'candidate-v10',
  phase:'await-roll',
  round:6,
  human:{tile:17,cash:120000,netWorth:168400,holdings:[]},
  bot:{tile:10,cash:104800,netWorth:154900},
  market:{id:'bull',label:'牛市',returnPct:18},
  lastRoll:null,
  decision:null,
  turnsCompleted:0,
  stage2Complete:false,
  history:[]
};

const players=[...document.querySelectorAll('.player')];
const roundCard=document.querySelector('.round-card');
const ticker=document.querySelector('.ticker');
const rollButton=document.querySelector('.roll');
const decision=document.querySelector('.stage2-decision');
const buyButton=decision.querySelector('.buy');
const passButton=decision.querySelector('.pass');
const toast=document.querySelector('.stage2-toast');

const money=n=>`¥${Math.round(n).toLocaleString('zh-CN')}`;
function snapshot(){return JSON.parse(JSON.stringify(state))}
function persist(){
  window.__cryptoGameState=snapshot();
  try{localStorage.setItem('crypto-tycoon-stage2-v10',JSON.stringify(window.__cryptoGameState))}catch{}
}
function updateHud(){
  players[0].querySelector('.identity small').textContent=`现金 ${money(state.human.cash)}`;
  players[0].querySelector('strong').textContent=money(state.human.netWorth);
  players[1].querySelector('.identity small').textContent=`现金 ${money(state.bot.cash)}`;
  players[1].querySelector('strong').textContent=money(state.bot.netWorth);
  roundCard.querySelector('b').textContent=`第 ${String(state.round).padStart(2,'0')} 回合`;
  roundCard.querySelector('p').innerHTML=`<i></i> ${state.market.label} · ${state.market.returnPct>=0?'+':''}${state.market.returnPct}%`;
  roundCard.querySelector('em').textContent=state.stage2Complete?'Stage 2 · 最小交互闭环完成':'目标 · 活下来并让资产复利';
  ticker.querySelector('b').textContent=state.market.id==='mania'?'SOL +8.0%':'BTC +7.2%';
  const tail=ticker.querySelector('span:last-child');
  if(tail) tail.textContent=state.market.id==='mania'?'狂热期 · 风险偏好拉满 · 仓位重新定价':'ETF 资金流 ↑ · 风险偏好上升 · GAS -12%';
  persist();
}
function showToast(text,ms=TEST?180:900){
  toast.textContent=text;toast.classList.add('show');
  clearTimeout(showToast.timer);showToast.timer=setTimeout(()=>toast.classList.remove('show'),ms);
}
function showDecision(){decision.classList.add('open');decision.setAttribute('aria-hidden','false')}
function hideDecision(){decision.classList.remove('open');decision.setAttribute('aria-hidden','true')}
function ease(t){return t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2}
function tween(duration,fn){
  return new Promise(resolve=>{
    const start=performance.now();
    function frame(now){const t=Math.min(1,(now-start)/duration);fn(ease(t),t);if(t<1)requestAnimationFrame(frame);else resolve()}
    requestAnimationFrame(frame);
  });
}

async function animateDice(values){
  const starts=dice.map(d=>({x:d.rotation.x,y:d.rotation.y,z:d.rotation.z}));
  const targets=values.map((v,i)=>({x:starts[i].x+Math.PI*(2.5+v*.28),y:starts[i].y+Math.PI*(3+i+v*.22),z:starts[i].z+Math.PI*(1.5+v*.18)}));
  await tween(TEST?180:720,(e)=>dice.forEach((d,i)=>{
    d.rotation.x=starts[i].x+(targets[i].x-starts[i].x)*e;
    d.rotation.y=starts[i].y+(targets[i].y-starts[i].y)*e;
    d.rotation.z=starts[i].z+(targets[i].z-starts[i].z)*e;
  }));
}

async function moveToken(token,startIndex,steps,label){
  let current=startIndex;
  for(let s=0;s<steps;s++){
    const next=(current+1)%24;
    const [sx,sz]=tilePos[current], [ex,ez]=tilePos[next];
    await tween(TEST?70:170,e=>{
      token.position.x=sx+(ex-sx)*e;
      token.position.z=sz+(ez-sz)*e;
      token.position.y=.98+Math.sin(e*Math.PI)*.28;
    });
    token.position.set(ex,.98,ez);current=next;
  }
  showToast(`${label} → 第 ${current+1} 格`);
  return current;
}

function fixedOrRandomRoll(){return TEST?[2,3]:[1+Math.floor(Math.random()*6),1+Math.floor(Math.random()*6)]}

async function roll(){
  if(state.phase!=='await-roll'||state.stage2Complete)return false;
  state.phase='rolling';rollButton.disabled=true;rollButton.querySelector('b').textContent='骰子滚动中';
  const values=fixedOrRandomRoll();state.lastRoll=values;state.history.push({type:'roll',values:[...values]});persist();
  showToast(`掷出 ${values[0]} + ${values[1]} = ${values[0]+values[1]}`);
  await animateDice(values);

  state.phase='moving';
  const from=state.human.tile;
  state.human.tile=await moveToken(humanToken,from,values[0]+values[1],'你');
  state.history.push({type:'move',from,to:state.human.tile});

  state.phase='decision';
  state.decision={asset:'SOL',cost:12000,tile:state.human.tile};
  rollButton.querySelector('b').textContent='等待决策';
  updateHud();showDecision();
  return true;
}

async function resolveDecision(action){
  if(state.phase!=='decision')return false;
  hideDecision();
  const d=state.decision;
  if(action==='buy'&&state.human.cash>=d.cost){
    state.human.cash-=d.cost;
    state.human.holdings.push({symbol:d.asset,cost:d.cost,value:d.cost});
    state.history.push({type:'buy',asset:d.asset,cost:d.cost,tile:d.tile});
    showToast(`买入 ${d.asset} · ${money(d.cost)}`);
  }else{
    state.history.push({type:'pass',asset:d.asset,tile:d.tile});showToast('跳过本次建仓');
  }
  state.decision=null;state.phase='bot';updateHud();

  await new Promise(r=>setTimeout(r,TEST?80:320));
  const botSteps=TEST?4:2+Math.floor(Math.random()*5);
  const botFrom=state.bot.tile;
  state.bot.tile=await moveToken(botToken,botFrom,botSteps,'Bot');
  state.history.push({type:'bot-turn',from:botFrom,to:state.bot.tile,steps:botSteps});

  state.phase='market';
  await new Promise(r=>setTimeout(r,TEST?80:360));
  const previous=state.market.id;
  state.market={id:'mania',label:'狂热期',returnPct:25};
  for(const h of state.human.holdings) h.value=Math.round(h.value*1.08);
  state.human.netWorth=168400+state.human.holdings.reduce((sum,h)=>sum+(h.value-h.cost),0);
  state.round=7;
  state.history.push({type:'market-transition',from:previous,to:'mania',holdingMarkPct:8});
  state.turnsCompleted=1;state.stage2Complete=true;state.phase='stage2-complete';
  rollButton.disabled=true;rollButton.querySelector('b').textContent='本轮完成';
  showToast('市场切换：狂热期 · 仓位重新定价',TEST?240:1200);updateHud();
  return true;
}

rollButton.addEventListener('click',()=>{roll().catch(e=>{window.__cryptoInteractionError=String(e?.stack||e);console.error(e)})});
buyButton.addEventListener('click',()=>{resolveDecision('buy').catch(e=>{window.__cryptoInteractionError=String(e?.stack||e);console.error(e)})});
passButton.addEventListener('click',()=>{resolveDecision('pass').catch(e=>{window.__cryptoInteractionError=String(e?.stack||e);console.error(e)})});

window.__cryptoStage2={state,roll,buy:()=>resolveDecision('buy'),pass:()=>resolveDecision('pass'),getState:snapshot};
window.render_game_to_text=()=>JSON.stringify({candidate:'candidate-v10',tiles:24,state:snapshot(),referencePixelsUsed:false});
updateHud();
window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v10',referencePixelsUsed:false,interactionStage:2,interactionReady:true,humanTile:state.human.tile,botTile:state.bot.tile};
document.documentElement.dataset.sliceVersion='v10';
document.documentElement.dataset.sliceReady='1';
