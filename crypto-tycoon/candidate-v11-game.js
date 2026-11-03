import * as THREE from 'three';

await import('./candidate-v9-augment.js');

const TEST=new URLSearchParams(location.search).get('test')==='1';
const root=window.__ctCapturedRoot;
const scene=window.__ctCapturedScene;
if(!root||!scene) throw new Error('v11: visual world missing');

const PLAYERS=[
  {id:0,name:'币圈玩家A',style:'human',color:0xffd66b,cash:120000},
  {id:1,name:'狗狗大佬',style:'degen',color:0x65e8ff,cash:105000},
  {id:2,name:'NFT收藏家',style:'collector',color:0xb98cff,cash:98000},
  {id:3,name:'牛市冲锋',style:'momentum',color:0x6df0a8,cash:92000}
];

const REGIMES={
  sideways:{name:'震荡市',returnPct:0,mult:1,rent:1},
  bull:{name:'牛市',returnPct:18,mult:1.18,rent:1.12},
  mania:{name:'狂热期',returnPct:25,mult:1.34,rent:1.25},
  bear:{name:'熊市',returnPct:-18,mult:.82,rent:.82},
  panic:{name:'恐慌期',returnPct:-32,mult:.66,rent:.68}
};

const ASSETS={
  BTC:{name:'BTC',sector:'CORE',cost:19000,rent:2800,vol:.6},
  ETH:{name:'ETH',sector:'CORE',cost:16000,rent:2400,vol:.75},
  USDC:{name:'USDC',sector:'CORE',cost:8500,rent:1200,vol:.2},
  SOL:{name:'SOL',sector:'BETA',cost:12000,rent:2100,vol:1.3},
  MEME:{name:'Meme币',sector:'BETA',cost:7000,rent:1900,vol:1.9},
  AI:{name:'AI',sector:'BETA',cost:13000,rent:2300,vol:1.5},
  CEX:{name:'交易所',sector:'INFRA',cost:11000,rent:1700,vol:.85},
  L2:{name:'L2',sector:'INFRA',cost:9000,rent:1500,vol:1},
  RWA:{name:'RWA',sector:'INFRA',cost:10000,rent:1600,vol:.65},
  DEFI:{name:'DeFi',sector:'YIELD',cost:10000,rent:1700,vol:1.2},
  STAKE:{name:'质押',sector:'YIELD',cost:8500,rent:1400,vol:.7},
  NFT:{name:'NFT',sector:'YIELD',cost:6500,rent:1300,vol:1.65}
};

const TILES=[
  {type:'special',name:'起点',kind:'start'},
  {type:'asset',asset:'BTC'},
  {type:'event',name:'行情波动',kind:'market'},
  {type:'asset',asset:'ETH'},
  {type:'asset',asset:'CEX'},
  {type:'asset',asset:'SOL'},
  {type:'special',name:'牛市',kind:'bull'},
  {type:'asset',asset:'MEME'},
  {type:'event',name:'机会事件',kind:'chance'},
  {type:'special',name:'金库',kind:'vault'},
  {type:'asset',asset:'DEFI'},
  {type:'special',name:'空投',kind:'airdrop'},
  {type:'special',name:'减半',kind:'halving'},
  {type:'asset',asset:'NFT'},
  {type:'event',name:'巨鲸动向',kind:'whale'},
  {type:'asset',asset:'AI'},
  {type:'special',name:'爆仓',kind:'liq'},
  {type:'asset',asset:'STAKE'},
  {type:'special',name:'熊市',kind:'bear'},
  {type:'asset',asset:'RWA'},
  {type:'special',name:'矿场',kind:'mine'},
  {type:'asset',asset:'L2'},
  {type:'event',name:'黑客攻击',kind:'hack'},
  {type:'asset',asset:'USDC'}
];

function perimeterPositions(){
  const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];
  xs.forEach(x=>a.push([x,-5.4]));
  zs.forEach(z=>a.push([5.4,z]));
  [...xs].reverse().forEach(x=>a.push([x,5.4]));
  [...zs].reverse().forEach(z=>a.push([-5.4,z]));
  return a;
}
const POS=perimeterPositions();

function findGroupNear(x,y,z,max=.7){
  let best=null,dist=Infinity;
  for(const o of root.children){
    if(!o.isGroup) continue;
    const d=(o.position.x-x)**2+(o.position.y-y)**2+(o.position.z-z)**2;
    if(d<dist){dist=d;best=o}
  }
  return dist<max*max?best:null;
}
function findTokenAt(index){
  const [x,z]=POS[index];
  let best=null,dist=Infinity;
  for(const o of root.children){
    if(!o.isGroup||o.position.y<.72||o.position.y>1.28)continue;
    const d=(o.position.x-x)**2+(o.position.z-z)**2;
    if(d<dist){dist=d;best=o}
  }
  return dist<.42?best:null;
}

// Capture the authored v9 collectibles before the full-game state relocates them to the start tile.
const tokenObjects=[17,10,13,20].map(findTokenAt);
const dice=[findGroupNear(-1.2,1.22,5.45,.7),findGroupNear(.15,1.15,5.7,.7)];
if(tokenObjects.some(x=>!x)||dice.some(x=>!x)) throw new Error('v11: authored tokens/dice not found');

const ui={
  leaderboard:document.querySelector('.leaderboard'),
  cards:[...document.querySelectorAll('.player')],
  round:document.querySelector('.round-card'),
  ticker:document.querySelector('.ticker'),
  roll:document.querySelector('.roll'),
  actions:[...document.querySelectorAll('.actions button')],
  decision:document.querySelector('.stage2-decision'),
  toast:document.querySelector('.game-toast'),
  end:document.querySelector('.end-panel'),
  endCard:document.querySelector('.end-card'),
  rankList:document.querySelector('.rank-list')
};

const money=n=>`¥${Math.round(n).toLocaleString('zh-CN')}`;
const clone=x=>JSON.parse(JSON.stringify(x));
const wait=ms=>new Promise(r=>setTimeout(r,TEST?Math.min(16,ms):ms));
let seed=246813579;
const rnd=()=>TEST?((seed=seed*48271%2147483647)/2147483647):Math.random();
const pick=a=>a[Math.floor(rnd()*a.length)];
let busy=false,modalResolver=null,ownerGroup=new THREE.Group();
ownerGroup.name='v11Ownership';root.add(ownerGroup);

const testRolls=[[2,3],[1,2],[2,2],[3,3],[1,1],[2,1],[1,3],[2,2],[1,2],[2,1],[1,1],[2,3]];

function fresh(){
  seed=246813579;
  return{
    version:'candidate-v11',round:1,maxRounds:12,turn:0,phase:'await-roll',regime:'sideways',pot:0,
    owners:{},upgrades:{},rollIndex:0,turnsCompleted:0,gameover:false,winner:null,
    players:PLAYERS.map(p=>({...p,pos:0,dead:false})),
    log:['链上开盘。真正的目标不是每一把都赢，而是十二回合后还在牌桌上。'],
    history:[],lastRoll:null
  };
}
let state=fresh();

function save(){
  window.__cryptoGameState=clone(state);
  if(TEST)return;
  try{localStorage.setItem('crypto-tycoon-v11',JSON.stringify(state))}catch{}
}
function load(){
  if(TEST)return null;
  try{
    const s=JSON.parse(localStorage.getItem('crypto-tycoon-v11'));
    if(s?.version==='candidate-v11'&&Array.isArray(s.players)&&s.players.length===4)return s;
  }catch{}
  return null;
}
function ownedTiles(pid){return Object.entries(state.owners).filter(([,o])=>o===pid).map(([i])=>+i)}
function worth(pid){
  const p=state.players[pid];
  let total=p.cash;
  for(const i of ownedTiles(pid)){
    const a=ASSETS[TILES[i].asset],u=state.upgrades[i]||0;
    total+=a.cost*REGIMES[state.regime].mult*(1+u*.36);
  }
  return Math.max(0,Math.round(total));
}
function sectorComplete(pid,sector){
  const ids=TILES.map((t,i)=>t.type==='asset'&&ASSETS[t.asset].sector===sector?i:null).filter(i=>i!==null);
  return ids.length>0&&ids.every(i=>state.owners[i]===pid);
}
function rentFor(i){
  const a=ASSETS[TILES[i].asset],u=state.upgrades[i]||0;
  let r=a.rent*REGIMES[state.regime].rent*(1+u*.6);
  if(sectorComplete(state.owners[i],a.sector))r*=1.45;
  return Math.round(r);
}
function log(text,type='info',extra={}){
  state.log.unshift(text);state.log=state.log.slice(0,18);
  state.history.push({type,text,round:state.round,turn:state.turn,...extra});
  showToast(text);save();updateHud();
}
function showToast(text,ms=TEST?80:1100){
  ui.toast.textContent=text;ui.toast.classList.add('show');
  clearTimeout(showToast.timer);showToast.timer=setTimeout(()=>ui.toast.classList.remove('show'),ms);
}

function tokenTarget(pid,tile){
  const [x,z]=POS[tile];
  const offsets=[[-.3,-.28],[.3,-.28],[-.3,.28],[.3,.28]][pid];
  return{x:x+offsets[0],y:.98,z:z+offsets[1]};
}
function placeTokens(){
  state.players.forEach((p,pid)=>{
    const t=tokenTarget(pid,p.pos),o=tokenObjects[pid];
    o.position.set(t.x,t.y,t.z);o.visible=!p.dead;
  });
}
function rebuildOwnership(){
  while(ownerGroup.children.length)ownerGroup.remove(ownerGroup.children[0]);
  for(const [raw,pid] of Object.entries(state.owners)){
    const i=+raw,[x,z]=POS[i],color=PLAYERS[pid].color;
    const mat=new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:.35,metalness:.35,roughness:.2});
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.56,.055,8,32),mat);
    ring.rotation.x=Math.PI/2;ring.position.set(x,1.18,z);ring.castShadow=false;ring.receiveShadow=false;
    ownerGroup.add(ring);
  }
}

function updateHud(){
  const title=ui.leaderboard.querySelector('.hud-title');
  const ranked=[...state.players].sort((a,b)=>worth(b.id)-worth(a.id));
  ranked.forEach((p,rank)=>{
    const card=ui.cards.find(c=>+c.dataset.player===p.id);
    if(!card)return;
    card.dataset.rank=String(rank+1);card.classList.toggle('dead',p.dead);
    card.querySelector('.identity b').textContent=p.name;
    card.querySelector('.identity small').textContent=`现金 ${money(p.cash)} · ${ownedTiles(p.id).length} 资产`;
    card.querySelector('strong').textContent=money(worth(p.id));
    ui.leaderboard.appendChild(card);
  });
  ui.leaderboard.prepend(title);
  const rg=REGIMES[state.regime];
  ui.round.querySelector('b').textContent=`第 ${String(state.round).padStart(2,'0')} 回合`;
  ui.round.querySelector('span').textContent=`/ ${state.maxRounds}`;
  ui.round.querySelector('p').innerHTML=`<i></i> ${rg.name} · ${rg.returnPct>=0?'+':''}${rg.returnPct}%`;
  ui.round.querySelector('em').textContent=state.gameover?'本局结束 · 净值排名已锁定':`第 ${state.turn+1} 位玩家行动 · ${state.phase==='await-roll'?'等待掷骰子':'回合处理中'}`;
  ui.ticker.querySelector('b').textContent=rg.name;
  const tail=ui.ticker.querySelector('span:last-child');if(tail)tail.textContent=state.log[0]||'';
  ui.roll.disabled=busy||state.gameover||state.turn!==0||state.players[0].dead||state.phase!=='await-roll';
  ui.roll.querySelector('b').textContent=state.gameover?'本局结束':busy?'回合处理中':'掷骰子';
  ui.actions.forEach(b=>b.disabled=busy&&b.dataset.action!=='history');
  rebuildOwnership();save();
}

function tween(duration,fn,proofKey){
  if(TEST){
    return new Promise(resolve=>{
      fn(.5,.5);if(proofKey)window.__v11Proof[proofKey]=(window.__v11Proof[proofKey]||0)+1;
      setTimeout(()=>{fn(1,1);if(proofKey)window.__v11Proof[proofKey]=(window.__v11Proof[proofKey]||0)+1;resolve()},8);
    });
  }
  return new Promise(resolve=>{
    const start=performance.now();
    function frame(now){
      const t=Math.min(1,(now-start)/duration),e=t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
      fn(e,t);if(proofKey)window.__v11Proof[proofKey]=(window.__v11Proof[proofKey]||0)+1;
      if(t<1)requestAnimationFrame(frame);else resolve();
    }
    requestAnimationFrame(frame);
  });
}
async function animateDice(values){
  const starts=dice.map(d=>({x:d.rotation.x,y:d.rotation.y,z:d.rotation.z,py:d.position.y}));
  await tween(TEST?20:680,(e,t)=>dice.forEach((d,i)=>{
    d.rotation.x=starts[i].x+Math.PI*(2.2+values[i]*.28)*e;
    d.rotation.y=starts[i].y+Math.PI*(2.8+i+values[i]*.2)*e;
    d.rotation.z=starts[i].z+Math.PI*(1.4+values[i]*.16)*e;
    d.position.y=starts[i].py+Math.sin(Math.PI*t)*(1.5-i*.15);
  }),'diceFrames');
}
async function moveToken(pid,steps){
  const p=state.players[pid],token=tokenObjects[pid];
  for(let s=0;s<steps;s++){
    const from=p.pos,next=(from+1)%24,a=tokenTarget(pid,from),b=tokenTarget(pid,next);
    await tween(TEST?12:165,(e)=>{
      token.position.x=a.x+(b.x-a.x)*e;token.position.z=a.z+(b.z-a.z)*e;token.position.y=.98+Math.sin(Math.PI*e)*.26;
    },pid===0?'humanMoveFrames':'botMoveFrames');
    p.pos=next;token.position.set(b.x,b.y,b.z);
    if(next===0){p.cash+=9000;state.pot+=1200;state.history.push({type:'pass-start',pid,round:state.round,amount:9000})}
  }
}
function pair(){
  if(TEST){const v=testRolls[state.rollIndex%testRolls.length];state.rollIndex++;return[...v]}
  return[1+Math.floor(Math.random()*6),1+Math.floor(Math.random()*6)];
}

function renderMetrics(items=[]){
  return items.map(([k,v])=>`<div class="metric"><small>${k}</small><b>${v}</b></div>`).join('');
}
function modal({kicker='DECISION',title='',body='',stats=[],primary='确认',secondary='跳过',one=false}){
  if(modalResolver){modalResolver('cancel');modalResolver=null}
  ui.decision.querySelector('.eyebrow').textContent=kicker;
  ui.decision.querySelector('h2').textContent=title;
  ui.decision.querySelector('p').textContent=body;
  ui.decision.querySelector('.numbers').innerHTML=renderMetrics(stats);
  const choices=ui.decision.querySelector('.choices'),buy=choices.querySelector('.buy'),pass=choices.querySelector('.pass');
  buy.textContent=primary;pass.textContent=secondary;pass.hidden=one;choices.classList.toggle('one',one);
  ui.decision.classList.add('open');ui.decision.setAttribute('aria-hidden','false');
  return new Promise(resolve=>{modalResolver=resolve});
}
function resolveModal(value){
  if(!modalResolver)return;
  const r=modalResolver;modalResolver=null;
  ui.decision.classList.remove('open');ui.decision.setAttribute('aria-hidden','true');
  r(value);
}
ui.decision.querySelector('.buy').addEventListener('click',()=>resolveModal('primary'));
ui.decision.querySelector('.pass').addEventListener('click',()=>resolveModal('secondary'));

function botWantsAsset(p,a){
  const reserve=p.style==='degen'?13000:p.style==='collector'?19000:22000;
  if(p.cash-a.cost<reserve)return false;
  if(p.style==='degen')return a.vol>1.05||rnd()>.4;
  if(p.style==='collector')return a.sector==='YIELD'||rnd()>.55;
  return state.regime==='bull'||state.regime==='mania'||a.sector==='CORE'||rnd()>.58;
}
async function assetLanding(pid,i){
  const p=state.players[pid],a=ASSETS[TILES[i].asset],owner=state.owners[i];
  if(owner===undefined){
    let buy=false;
    if(pid===0){
      state.phase='decision';updateHud();
      const q=await modal({kicker:`UNOWNED · ${a.sector}`,title:`${a.name} 生态仓位`,body:'买下后，其他玩家落在这里会向你支付过路费；集齐同板块还有组合溢价。',stats:[['建仓成本',money(a.cost)],['基础过路费',money(a.rent)],['剩余现金',money(p.cash-a.cost)]],primary:'买入仓位',secondary:'保留现金'});
      buy=q==='primary'&&p.cash>=a.cost;
    }else buy=botWantsAsset(p,a);
    if(buy){p.cash-=a.cost;state.owners[i]=pid;state.upgrades[i]=0;log(`${p.name} 买入 ${a.name}。`,'buy',{pid,tile:i,asset:TILES[i].asset,cost:a.cost})}
    else log(`${p.name} 放弃 ${a.name}，保留现金。`,'pass',{pid,tile:i,asset:TILES[i].asset});
  }else if(owner===pid){
    const level=state.upgrades[i]||0,cost=Math.round(a.cost*.42);
    if(level>=2){log(`${p.name} 的 ${a.name} 已经满级。`,'hold',{pid,tile:i});return}
    let up=false;
    if(pid===0){
      state.phase='decision';updateHud();
      const q=await modal({kicker:'YOUR ASSET',title:`继续加仓 ${a.name}`,body:'更高等级意味着更高过路费，也意味着更低的现金缓冲。',stats:[['加仓成本',money(cost)],['当前等级',`${level+1} / 3`],['现金',money(p.cash)]],primary:'继续加仓',secondary:'保持仓位'});
      up=q==='primary'&&p.cash>=cost;
    }else up=p.cash>cost+18000&&rnd()>.5;
    if(up){p.cash-=cost;state.upgrades[i]=level+1;log(`${p.name} 把 ${a.name} 加仓到 ${level+2} 级。`,'upgrade',{pid,tile:i,level:level+1,cost})}
    else log(`${p.name} 保持 ${a.name} 当前仓位。`,'hold',{pid,tile:i});
  }else{
    const fee=rentFor(i),creditor=state.players[owner];p.cash-=fee;creditor.cash+=fee;
    log(`${p.name} 落在 ${creditor.name} 的 ${a.name}，支付 ${money(fee)}。`,'rent',{pid,owner,tile:i,fee});
  }
  await ensureSolvent(pid);
}

const EVENTS={
  market:{title:'行情突然加速',body:'BTC 十分钟内剧烈波动。追随趋势，还是保留现金？',a:['追随趋势',.52,9000,-6500],b:['保持现金',1,1200,1200]},
  chance:{title:'一条“靠谱消息”',body:'你得到一条未公开的上币消息。赔率诱人，但证据只隔着一个朋友。',a:['重注一手',.38,14000,-8000],b:['当它不存在',1,800,800]},
  whale:{title:'巨鲸开始转账',body:'链上出现大额转账。你不知道它是准备卖出，还是换钱包。',a:['反向下注',.46,10000,-7000],b:['等待确认',1,1500,1500]},
  hack:{title:'协议被攻击',body:'市场传出黑客攻击。立即隔离风险，还是赌影响有限？',a:['立即隔离',1,-2800,-2800],b:['继续持有',.58,3500,-9500]}
};
async function eventLanding(pid,kind){
  const p=state.players[pid],d=EVENTS[kind];let choice;
  if(pid===0){
    state.phase='decision';updateHud();
    const q=await modal({kicker:'MARKET EVENT',title:d.title,body:d.body,stats:[['当前现金',money(p.cash)],['市场',REGIMES[state.regime].name],['链上奖池',money(state.pot)]],primary:d.a[0],secondary:d.b[0]});
    choice=q==='primary'?d.a:d.b;
  }else choice=(p.style==='degen'?rnd()>.25:p.style==='collector'?rnd()>.58:rnd()>.48)?d.a:d.b;
  const gain=rnd()<choice[1]?choice[2]:choice[3];p.cash+=gain;
  log(`${p.name} 选择“${choice[0]}”，结果 ${gain>=0?'+':''}${money(gain)}。`,'event',{pid,kind,gain,choice:choice[0]});
  await ensureSolvent(pid);
}
async function specialLanding(pid,t){
  const p=state.players[pid];
  if(t.kind==='start')return;
  if(t.kind==='bull'){state.regime='bull';p.cash+=4000;log(`${p.name} 敲响牛市钟，市场进入牛市。`,'regime',{pid,to:'bull'})}
  else if(t.kind==='bear'){state.regime='bear';p.cash-=3500;log(`${p.name} 进入熊市，现金损失 ${money(3500)}。`,'regime',{pid,to:'bear'});await ensureSolvent(pid)}
  else if(t.kind==='airdrop'){const x=3500+Math.floor(rnd()*6500);p.cash+=x;log(`${p.name} 收到空投 ${money(x)}。`,'airdrop',{pid,amount:x})}
  else if(t.kind==='halving'){state.regime=rnd()>.3?'bull':'sideways';state.players.filter(x=>!x.dead).forEach(x=>x.cash+=1800);log(`减半叙事升温，市场切换为${REGIMES[state.regime].name}，存活玩家获得区块奖励。`,'halving',{to:state.regime})}
  else if(t.kind==='vault'){const x=Math.min(4500,state.pot);p.cash+=x;state.pot-=x;log(`${p.name} 从金库取出 ${money(x)}。`,'vault',{pid,amount:x})}
  else if(t.kind==='mine'){const x=4200+Math.floor(rnd()*4200);p.cash+=x;log(`${p.name} 获得矿场收益 ${money(x)}。`,'mine',{pid,amount:x})}
  else if(t.kind==='liq'){const x=Math.max(5000,Math.round(p.cash*.2));p.cash-=x;log(`${p.name} 遭遇清算，损失 ${money(x)}。`,'liquidation',{pid,amount:x});await ensureSolvent(pid)}
}
async function ensureSolvent(pid){
  const p=state.players[pid];if(p.cash>=0)return;
  const ids=ownedTiles(pid).sort((a,b)=>ASSETS[TILES[b].asset].cost-ASSETS[TILES[a].asset].cost);
  while(p.cash<0&&ids.length){
    const i=ids.shift(),a=ASSETS[TILES[i].asset],recovery=Math.round(a.cost*.62*(1+(state.upgrades[i]||0)*.22));
    delete state.owners[i];delete state.upgrades[i];p.cash+=recovery;
    log(`${p.name} 被迫折价卖出 ${a.name}，回笼 ${money(recovery)}。`,'forced-sale',{pid,tile:i,recovery});
  }
  if(p.cash<0){p.dead=true;p.cash=0;tokenObjects[pid].visible=false;log(`${p.name} 已爆仓离场。`,'dead',{pid});if(pid===0)finish()}
}
async function land(pid){
  const i=state.players[pid].pos,t=TILES[i];
  if(t.type==='asset')await assetLanding(pid,i);
  else if(t.type==='event')await eventLanding(pid,t.kind);
  else await specialLanding(pid,t);
}

async function takeTurn(pid){
  if(state.gameover||state.players[pid].dead)return;
  state.turn=pid;state.phase='rolling';updateHud();
  const values=pair();state.lastRoll=values;state.history.push({type:'roll',pid,round:state.round,values:[...values]});save();
  if(pid===0)showToast(`掷出 ${values[0]} + ${values[1]} = ${values[0]+values[1]}`);
  await animateDice(values);
  state.phase='moving';await moveToken(pid,values[0]+values[1]);
  state.phase='landing';updateHud();await land(pid);
  state.turnsCompleted++;state.phase='turn-complete';updateHud();
}
async function nextRound(){
  state.round++;
  if(state.round>state.maxRounds||state.players.filter(p=>!p.dead).length<=1){finish();return}
  state.regime=pick(['sideways','sideways','bull','bear','mania','panic']);
  state.turn=0;state.phase='await-roll';
  log(`第 ${state.round} 回合开盘：${REGIMES[state.regime].name}。`,'round',{round:state.round,regime:state.regime});
}
async function rollFullRound(){
  if(busy||state.gameover||state.turn!==0||state.phase!=='await-roll'||state.players[0].dead)return false;
  busy=true;updateHud();
  try{
    await takeTurn(0);
    if(!state.gameover){for(let i=1;i<4;i++){await wait(90);await takeTurn(i);if(state.gameover)break}}
    if(!state.gameover)await nextRound();
  }catch(e){window.__cryptoInteractionError=String(e?.stack||e);console.error(e);throw e}
  finally{busy=false;if(!state.gameover){state.turn=0;if(state.phase!=='await-roll')state.phase='await-roll'}updateHud()}
  return true;
}

function ranking(){return[...state.players].sort((a,b)=>worth(b.id)-worth(a.id))}
function finish(){
  if(state.gameover)return;
  state.gameover=true;state.phase='gameover';busy=false;
  const r=ranking();state.winner=r[0].id;save();updateHud();
  ui.endCard.querySelector('h2').textContent=r[0].id===0?'你成为币圈大富翁':`本局冠军：${r[0].name}`;
  ui.rankList.innerHTML=r.map((p,i)=>`<div class="rank-item"><strong>#${i+1}</strong><div><b>${p.name}</b><small>现金 ${money(p.cash)} · ${ownedTiles(p.id).length} 资产${p.dead?' · 已离场':''}</small></div><div class="value">${money(worth(p.id))}</div></div>`).join('');
  ui.end.classList.add('open');ui.end.setAttribute('aria-hidden','false');
}
function start(force=false){
  if(force){try{localStorage.removeItem('crypto-tycoon-v11')}catch{}}
  state=force?fresh():(load()||fresh());busy=false;window.__cryptoInteractionError=null;window.__v11Proof={diceFrames:0,humanMoveFrames:0,botMoveFrames:0};
  ui.end.classList.remove('open');ui.end.setAttribute('aria-hidden','true');
  if(modalResolver){modalResolver('cancel');modalResolver=null}ui.decision.classList.remove('open');ui.decision.setAttribute('aria-hidden','true');
  placeTokens();updateHud();save();
}

ui.roll.addEventListener('click',()=>rollFullRound().catch(()=>{}));
ui.end.querySelector('.again').addEventListener('click',()=>start(true));
ui.end.querySelector('.board').addEventListener('click',()=>{ui.end.classList.remove('open');ui.end.setAttribute('aria-hidden','true')});

async function showPortfolio(){
  const items=ownedTiles(0).map(i=>`${ASSETS[TILES[i].asset].name} Lv.${(state.upgrades[i]||0)+1}`);
  await modal({kicker:'YOUR PORTFOLIO',title:`净值 ${money(worth(0))}`,body:items.length?items.join(' · '):'你目前还没有持有链上资产。',stats:[['现金',money(state.players[0].cash)],['持仓',String(items.length)],['市场',REGIMES[state.regime].name]],primary:'返回棋盘',one:true});
}
async function showHistory(){
  const text=state.log.slice(0,6).join('  ｜  ')||'还没有行动记录。';
  await modal({kicker:'CHAIN LOG',title:'最近发生了什么',body:text,stats:[['当前回合',`${state.round}/${state.maxRounds}`],['已完成行动',String(state.turnsCompleted)],['奖池',money(state.pot)]],primary:'返回棋盘',one:true});
}
async function showRules(){
  await modal({kicker:'HOW TO PLAY',title:'币圈大富翁规则',body:'掷两颗骰子沿 24 格棋盘移动。无人资产可以买入；别人落在你的资产上支付过路费；落在自己的资产上可以加仓。牛熊、空投、巨鲸、黑客和清算会改变现金与市场状态。十二回合后按净值排名，爆仓则提前离场。',stats:[['核心目标','留在牌桌'],['结束条件','12 回合 / 仅剩1人'],['资产板块','CORE · BETA · INFRA · YIELD']],primary:'知道了',one:true});
}

ui.actions.forEach(btn=>btn.addEventListener('click',async()=>{
  const a=btn.dataset.action;
  if(a==='portfolio')await showPortfolio();
  else if(a==='history')await showHistory();
  else if(a==='rules')await showRules();
  else if(a==='restart'&&(TEST||confirm('确定重开这一局？')))start(true);
}));

window.__cryptoFullGame={
  getState:()=>clone(state),roll:rollFullRound,restart:()=>start(true),finish,
  worth:(pid=0)=>worth(pid),tiles:TILES,assets:ASSETS,regimes:REGIMES,
  getProof:()=>clone(window.__v11Proof||{}),
  resolveDecision:resolveModal
};
window.render_game_to_text=()=>JSON.stringify({
  candidate:'candidate-v11',tiles:TILES.length,referencePixelsUsed:false,fullGameplay:true,
  state:{round:state.round,maxRounds:state.maxRounds,turn:state.turn,phase:state.phase,regime:state.regime,gameover:state.gameover,owners:state.owners,upgrades:state.upgrades,players:state.players.map(p=>({id:p.id,name:p.name,pos:p.pos,cash:p.cash,worth:worth(p.id),dead:p.dead,assets:ownedTiles(p.id).length})),history:state.history.slice(-20)},
  proof:window.__v11Proof
});

start(false);
window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v11',referencePixelsUsed:false,interactionStage:3,fullGameplay:true,repeatableTurns:true,persistence:!TEST,rounds:12};
document.documentElement.dataset.sliceVersion='v11';
document.documentElement.dataset.sliceReady='1';
