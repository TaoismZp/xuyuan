import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';

const TEST = new URLSearchParams(location.search).get('test') === '1';
const $ = s => document.querySelector(s);
const ui = {
  leaderboard: $('#leaderboard'), round: $('#roundPanel'), ticker: $('#ticker'), roll: $('#roll'),
  intro: $('#intro'), start: $('#start'), modal: $('#modal'), modalCard: $('#modalCard'), end: $('#end'),
  endCard: $('#endCard'), portfolio: $('#portfolioBtn'), rules: $('#rulesBtn'), restart: $('#restartBtn'), sr: $('#srStatus')
};

const COLORS = ['#ffd66b','#65e8ff','#b98cff','#6df0a8'];
const PLAYERS = [
  {name:'币圈玩家A', short:'A', color:COLORS[0], style:'human'},
  {name:'狗狗大佬', short:'D', color:COLORS[1], style:'degen'},
  {name:'NFT收藏家', short:'N', color:COLORS[2], style:'collector'},
  {name:'牛市冲锋', short:'B', color:COLORS[3], style:'momentum'}
];
const REGIMES = {
  sideways:{name:'震荡市',cls:'sideways',mult:1,rent:1,fg:52},
  bull:{name:'牛市',cls:'bull',mult:1.24,rent:1.18,fg:78},
  mania:{name:'狂热',cls:'bull',mult:1.48,rent:1.35,fg:92},
  bear:{name:'熊市',cls:'bear',mult:.76,rent:.8,fg:26},
  panic:{name:'恐慌',cls:'bear',mult:.58,rent:.66,fg:11}
};
const ASSETS = {
  BTC:{name:'BTC',sym:'₿',cost:620000,rent:92000,sector:'CORE',vol:.6,color:0xf4b02f},
  ETH:{name:'ETH',sym:'Ξ',cost:520000,rent:78000,sector:'CORE',vol:.75,color:0x7f8cff},
  USDC:{name:'USDC',sym:'◎',cost:280000,rent:39000,sector:'CORE',vol:.2,color:0x4a9cf7},
  SOL:{name:'SOL',sym:'S',cost:390000,rent:68000,sector:'BETA',vol:1.3,color:0x8c68ff},
  MEME:{name:'Meme币',sym:'M',cost:220000,rent:62000,sector:'BETA',vol:1.9,color:0xff6ec7},
  AI:{name:'AI',sym:'AI',cost:420000,rent:76000,sector:'BETA',vol:1.5,color:0x59d8ff},
  CEX:{name:'交易所',sym:'↔',cost:360000,rent:56000,sector:'INFRA',vol:.85,color:0xf4c34c},
  L2:{name:'L2',sym:'Ⅱ',cost:300000,rent:49000,sector:'INFRA',vol:1,color:0x53d2ff},
  RWA:{name:'RWA',sym:'▣',cost:330000,rent:52000,sector:'INFRA',vol:.65,color:0xe1b96f},
  DEFI:{name:'DeFi',sym:'◇',cost:320000,rent:54000,sector:'YIELD',vol:1.2,color:0x63e6d0},
  STAKE:{name:'质押',sym:'%',cost:270000,rent:45000,sector:'YIELD',vol:.7,color:0x4fe3a0},
  NFT:{name:'NFT',sym:'✦',cost:210000,rent:44000,sector:'YIELD',vol:1.65,color:0xc77dff}
};
const TILES = [
  {type:'special',name:'起点',sub:'领取区块奖励',kind:'start',icon:'GO'},
  {type:'asset',asset:'BTC'},{type:'event',name:'行情波动',sub:'市场突发事件',kind:'market',icon:'↗'}, {type:'asset',asset:'ETH'},
  {type:'asset',asset:'CEX',landmark:'exchange'},{type:'asset',asset:'SOL'},{type:'special',name:'牛市',sub:'全体资产上涨',kind:'bull',icon:'▲',landmark:'bull'},
  {type:'asset',asset:'MEME'},{type:'event',name:'机会事件',sub:'抽取事件卡',kind:'chance',icon:'?'},{type:'special',name:'金库',sub:'现金避险',kind:'vault',icon:'▣',landmark:'vault'},
  {type:'asset',asset:'DEFI'},{type:'special',name:'空投',sub:'随机奖励',kind:'airdrop',icon:'↓',landmark:'airdrop'},
  {type:'special',name:'减半',sub:'稀缺性冲击',kind:'halving',icon:'½',landmark:'rocket'},{type:'asset',asset:'NFT',landmark:'nft'},
  {type:'event',name:'巨鲸动向',sub:'大户改变市场',kind:'whale',icon:'W',landmark:'whale'},{type:'asset',asset:'AI'},
  {type:'special',name:'爆仓',sub:'强制平仓',kind:'liq',icon:'!',landmark:'liquidation'},{type:'asset',asset:'STAKE',landmark:'staking'},
  {type:'special',name:'熊市',sub:'全体资产回撤',kind:'bear',icon:'▼',landmark:'bear'},{type:'asset',asset:'RWA'},
  {type:'special',name:'矿场',sub:'获得挖矿收益',kind:'mine',icon:'⛏',landmark:'mine'},{type:'asset',asset:'L2'},
  {type:'event',name:'黑客攻击',sub:'协议风险',kind:'hack',icon:'×'},{type:'asset',asset:'USDC'}
];

let seed = 246813579;
const rnd = () => TEST ? ((seed = seed * 48271 % 2147483647) / 2147483647) : Math.random();
const pick = arr => arr[Math.floor(rnd()*arr.length)];
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const money=n=>'¥'+Math.round(n).toLocaleString('zh-CN');
const wait=ms=>new Promise(r=>setTimeout(r,TEST?Math.min(18,ms):ms));

let state = null;
let busy = false;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050814);
scene.fog = new THREE.FogExp2(0x060914,0.018);
const camera = new THREE.PerspectiveCamera(38,innerWidth/innerHeight,.1,140);
const renderer = new THREE.WebGLRenderer({canvas:$('#scene'),antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight,false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const hemi = new THREE.HemisphereLight(0x88aaff,0x10071b,2.5); scene.add(hemi);
const key = new THREE.DirectionalLight(0xffe2aa,4.5); key.position.set(-12,26,18); key.castShadow=true; key.shadow.mapSize.set(2048,2048); key.shadow.camera.left=-30;key.shadow.camera.right=30;key.shadow.camera.top=30;key.shadow.camera.bottom=-30;scene.add(key);
const rim = new THREE.PointLight(0x5cdcff,70,45,2); rim.position.set(14,12,-14); scene.add(rim);
const magenta = new THREE.PointLight(0xb96cff,55,38,2); magenta.position.set(-17,10,-10); scene.add(magenta);

const world = new THREE.Group(); scene.add(world);
const boardGroup = new THREE.Group(); world.add(boardGroup);
const propGroup = new THREE.Group(); world.add(propGroup);
const tokenGroup = new THREE.Group(); world.add(tokenGroup);
const fxGroup = new THREE.Group(); world.add(fxGroup);
const tileObjects=[]; const tokenObjects=[]; const ownerMarkers=[];
let dice=[]; let centerPulse=null;

function mat(color, metal=.4, rough=.38, emissive=0x000000, intensity=0){return new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive,emissiveIntensity:intensity});}
const materials={
  gold:mat(0xf3b62c,.86,.25,0x7a3b00,.18), dark:mat(0x0a1022,.7,.32), blue:mat(0x173c78,.55,.28,0x0b2e69,.35),
  purple:mat(0x4d2b72,.55,.31,0x34105a,.32), red:mat(0x7b2030,.45,.36,0x5b0617,.28), green:mat(0x145b42,.45,.36,0x063d2b,.35),
  white:mat(0xf4f1e7,.2,.3), black:mat(0x11131c,.7,.3), glass:new THREE.MeshPhysicalMaterial({color:0x7cdcff,roughness:.12,metalness:.15,transmission:.05,transparent:true,opacity:.72,emissive:0x1f8aac,emissiveIntensity:.28})
};
function roundedRectShape(w,d,r){const s=new THREE.Shape();const x=-w/2,z=-d/2;s.moveTo(x+r,z);s.lineTo(x+w-r,z);s.quadraticCurveTo(x+w,z,x+w,z+r);s.lineTo(x+w,z+d-r);s.quadraticCurveTo(x+w,z+d,x+w-r,z+d);s.lineTo(x+r,z+d);s.quadraticCurveTo(x,z+d,x,z+d-r);s.lineTo(x,z+r);s.quadraticCurveTo(x,z,x+r,z);return s;}
function roundedPrism(w,d,h,r,material,bevel=.09){const g=new THREE.ExtrudeGeometry(roundedRectShape(w,d,r),{depth:h,bevelEnabled:true,bevelThickness:bevel,bevelSize:bevel,bevelSegments:2,curveSegments:4});g.rotateX(Math.PI/2);g.translate(0,h/2,0);g.computeVertexNormals();const m=new THREE.Mesh(g,material);m.castShadow=true;m.receiveShadow=true;return m;}
function canvasTexture(draw,w=512,h=256){const c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d');draw(ctx,w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=renderer.capabilities.getMaxAnisotropy();return t;}
function labelPlane(title,sub,color='#ffffff',scale=1){const tex=canvasTexture((c,w,h)=>{c.clearRect(0,0,w,h);c.textAlign='center';c.textBaseline='middle';c.shadowColor='rgba(0,0,0,.65)';c.shadowBlur=10;c.fillStyle=color;c.font='900 74px -apple-system, PingFang SC, sans-serif';c.fillText(title,w/2,h*.39);c.shadowBlur=5;c.fillStyle='rgba(225,235,255,.72)';c.font='600 31px -apple-system, PingFang SC, sans-serif';c.fillText(sub||'',w/2,h*.71);});const m=new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false});const p=new THREE.Mesh(new THREE.PlaneGeometry(3.2*scale,1.55*scale),m);p.rotation.x=-Math.PI/2;p.renderOrder=4;return p;}
function spriteText(text,{w=700,h=200,font=84,color='#ffd86b',sub='',subColor='#8fddff'}={}){const tex=canvasTexture((c,W,H)=>{c.clearRect(0,0,W,H);c.textAlign='center';c.textBaseline='middle';c.shadowColor='rgba(0,0,0,.75)';c.shadowBlur=18;c.fillStyle=color;c.font=`1000 ${font}px -apple-system, PingFang SC, sans-serif`;c.fillText(text,W/2,H*.44);if(sub){c.shadowBlur=5;c.fillStyle=subColor;c.font='800 25px -apple-system, sans-serif';c.fillText(sub,W/2,H*.78);}},w,h);const s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthWrite:false}));s.scale.set(w/90,h/90,1);return s;}
function box(w,h,d,material){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);m.castShadow=true;m.receiveShadow=true;return m;}
function cyl(r1,r2,h,material,seg=24){const m=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),material);m.castShadow=true;m.receiveShadow=true;return m;}
function sphere(r,material,seg=24){const m=new THREE.Mesh(new THREE.SphereGeometry(r,seg,Math.max(12,seg/2)),material);m.castShadow=true;m.receiveShadow=true;return m;}
function cone(r,h,material,seg=20){const m=new THREE.Mesh(new THREE.ConeGeometry(r,h,seg),material);m.castShadow=true;m.receiveShadow=true;return m;}

function boardPositions(){const a=[];for(let c=0;c<7;c++)a.push({r:0,c});for(let r=1;r<6;r++)a.push({r,c:6});for(let c=6;c>=0;c--)a.push({r:6,c});for(let r=5;r>=1;r--)a.push({r,c:0});return a.map(({r,c})=>new THREE.Vector3((c-3)*4.25,0,(r-3)*4.25));}
const TILE_POS=boardPositions();

function buildWorld(){
  const pedestal=roundedPrism(30.4,30.4,1.15,1.7,materials.dark,.18);pedestal.position.y=-.75;boardGroup.add(pedestal);
  const edge=roundedPrism(29.75,29.75,.3,1.4,materials.gold,.06);edge.position.y=-.1;boardGroup.add(edge);
  const inset=roundedPrism(28.9,28.9,.34,1.25,mat(0x0a1230,.72,.3,0x102a6b,.22),.04);inset.position.y=.08;boardGroup.add(inset);
  TILES.forEach((t,i)=>{
    const a=t.asset?ASSETS[t.asset]:null; const typeColor=a?a.color:(t.kind==='bull'?0x2cba76:t.kind==='bear'||t.kind==='liq'?0xd94f5d:t.type==='event'?0x7d4bb3:0xb46a2c);
    const tm=mat(typeColor,.48,.3,typeColor,.09);
    const tile=roundedPrism(3.78,3.78,.68,.48,tm,.085); tile.position.copy(TILE_POS[i]); tile.position.y=.35; tile.userData.index=i; boardGroup.add(tile);
    const top=roundedPrism(3.42,3.42,.12,.36,mat(THREE.Color.NAMES.white,.05,.34,typeColor,.04),.04);top.position.copy(TILE_POS[i]);top.position.y=.77;top.material.color.set(typeColor).lerp(new THREE.Color(0xffffff),.58);boardGroup.add(top);
    const title=a?a.name:t.name,sub=a?`${money(a.cost)} · ${a.sector}`:t.sub;const lp=labelPlane(title,sub,'#0b1224',.88);lp.position.copy(TILE_POS[i]);lp.position.y=.86;
    if(i>=7&&i<=11)lp.rotation.z=Math.PI/2;else if(i>=12&&i<=18)lp.rotation.z=Math.PI;else if(i>=19)lp.rotation.z=-Math.PI/2;boardGroup.add(lp);
    tileObjects[i]={tile,top,label:lp};
    if(t.landmark){const p=createLandmark(t.landmark,typeColor);p.position.copy(TILE_POS[i]);p.position.y=.95;p.scale.setScalar(.72);propGroup.add(p);}
  });
  const core=roundedPrism(18.8,18.8,.38,1.3,mat(0x071025,.65,.28,0x15346f,.24),.08);core.position.y=.48;boardGroup.add(core);
  const ring1=new THREE.Mesh(new THREE.TorusGeometry(5.4,.11,12,80),mat(0x2ab9ff,.35,.24,0x2ab9ff,1.4));ring1.rotation.x=Math.PI/2;ring1.position.y=.8;boardGroup.add(ring1);centerPulse=ring1;
  const ring2=new THREE.Mesh(new THREE.TorusGeometry(4.4,.06,10,64),mat(0x9b6bff,.35,.25,0x9b6bff,1.2));ring2.rotation.x=Math.PI/2;ring2.position.y=.83;boardGroup.add(ring2);
  const marketDisc=cyl(3.9,4.2,.62,mat(0x0d1735,.7,.2,0x244c9b,.28),48);marketDisc.position.y=.86;boardGroup.add(marketDisc);
  const title=spriteText('币圈大富翁',{w:900,h:220,font:98,sub:'CRYPTO TYCOON'});title.position.set(0,4.15,1.6);title.scale.multiplyScalar(1.18);boardGroup.add(title);
  const crown=spriteText('♛',{w:240,h:180,font:120,color:'#ffe18a'});crown.position.set(0,6.15,1.45);crown.scale.set(2.25,1.65,1);boardGroup.add(crown);
  buildDice();buildSkyline();buildTokens();
  const floor=new THREE.Mesh(new THREE.CircleGeometry(70,80),mat(0x050914,.3,.72));floor.rotation.x=-Math.PI/2;floor.position.y=-1.45;floor.receiveShadow=true;world.add(floor);
}

function createLandmark(kind,color){const g=new THREE.Group();const cmat=mat(color,.48,.3,color,.22);const gold=materials.gold,black=materials.black;
  if(kind==='exchange'){
    const tower=box(1.5,3.5,1.5,mat(0x183d79,.7,.22,0x1150a0,.32));tower.position.y=1.75;g.add(tower);for(let y=.45;y<3.2;y+=.55){const w=box(1.56,.08,1.56,mat(0x5ae8ff,.1,.2,0x3adfff,2));w.position.y=y;g.add(w)}const sign=spriteText('交易所',{w:360,h:120,font:68,color:'#ffffff'});sign.position.set(0,2.3,.9);sign.scale.set(2.1,.7,1);g.add(sign);
  } else if(kind==='bull'||kind==='bear'){
    const isBull=kind==='bull';const body=sphere(.68,cmat);body.scale.set(1.25,.82,.8);body.position.y=.65;g.add(body);const head=sphere(.48,cmat);head.position.set(.62,1.0,0);g.add(head);for(const s of [-1,1]){const ear=cone(.16,.42,isBull?gold:cmat,12);ear.rotation.z=s*(isBull?-.8:.9);ear.position.set(.76,1.35,s*.26);g.add(ear)}if(isBull){for(const s of [-1,1]){const horn=cone(.12,.7,gold,12);horn.rotation.z=s*.9;horn.position.set(.92,1.48,s*.34);g.add(horn)}}const legs=[[-.35,.12,-.25],[-.35,.12,.25],[.38,.12,-.25],[.38,.12,.25]];legs.forEach(p=>{const l=cyl(.11,.13,.52,black,10);l.position.set(...p);g.add(l)});
  } else if(kind==='rocket'){
    const body=cyl(.3,.38,1.65,mat(0xf2f3ff,.35,.22),20);body.position.y=1.2;g.add(body);const nose=cone(.38,.75,mat(0xff9d37,.55,.22,0x7b2c00,.15),20);nose.position.y=2.4;g.add(nose);for(const s of [-1,1]){const fin=box(.16,.58,.48,mat(0xff734d,.45,.28));fin.position.set(s*.38,.58,0);fin.rotation.z=s*.25;g.add(fin)}const flame=cone(.22,.8,mat(0xffc84a,.1,.2,0xff7b00,1.7),14);flame.rotation.x=Math.PI;flame.position.y=.0;g.add(flame);
  } else if(kind==='whale'){
    const body=sphere(.85,mat(0x3da9e6,.35,.24,0x0d4f89,.32));body.scale.set(1.55,.68,.72);body.position.y=1;g.add(body);const head=sphere(.58,mat(0x4bb8ef,.3,.25,0x0d4f89,.25));head.position.set(.92,1.02,0);g.add(head);for(const s of [-1,1]){const tail=cone(.34,.8,cmat,16);tail.rotation.z=s*1.15;tail.position.set(-1.2,1.02,s*.35);g.add(tail)}const eye=sphere(.08,black,12);eye.position.set(1.36,1.22,.42);g.add(eye);
  } else if(kind==='mine'){
    for(let i=-1;i<=1;i++){const rig=box(.68,1.15,.35,mat(0x15284b,.7,.28,0x1d6ac8,.2));rig.position.set(i*.72,.72,0);g.add(rig);const fan=new THREE.Mesh(new THREE.TorusGeometry(.19,.06,8,20),materials.gold);fan.rotation.y=Math.PI/2;fan.position.set(i*.72,.75,.2);g.add(fan)}
  } else if(kind==='vault'){
    const safe=box(1.35,1.25,1.0,mat(0xb77825,.7,.28,0x6a3306,.2));safe.position.y=.7;g.add(safe);const door=cyl(.46,.46,.16,materials.gold,24);door.rotation.x=Math.PI/2;door.position.set(0,.72,.58);g.add(door);const hub=cyl(.1,.1,.28,black,16);hub.rotation.x=Math.PI/2;hub.position.set(0,.72,.71);g.add(hub);
  } else if(kind==='staking'){
    for(let i=0;i<4;i++){const coin=cyl(.52,.52,.16,materials.gold,28);coin.position.set((i%2)*.35-.18,.2+i*.16,(i%2)*.1);g.add(coin)}const lock=box(.72,.62,.3,mat(0x1f7a61,.5,.28,0x0e5b45,.35));lock.position.set(.25,1.05,0);g.add(lock);const hoop=new THREE.Mesh(new THREE.TorusGeometry(.27,.07,10,28,Math.PI),materials.gold);hoop.rotation.z=Math.PI;hoop.position.set(.25,1.42,0);g.add(hoop);
  } else if(kind==='nft'){
    const frame=box(1.2,1.45,.18,mat(0x6a3d9b,.55,.25,0x54207f,.4));frame.position.y=1.05;g.add(frame);const face=spriteText('▦',{w:220,h:220,font:120,color:'#ff7bd8'});face.position.set(0,1.05,.18);face.scale.set(1.1,1.1,1);g.add(face);
  } else if(kind==='airdrop'){
    const canopy=new THREE.Mesh(new THREE.SphereGeometry(.75,20,12,0,Math.PI*2,0,Math.PI/2),mat(0xffd786,.15,.45,0xff8e25,.1));canopy.position.y=1.85;g.add(canopy);const gift=box(.65,.55,.65,materials.gold);gift.position.y=.7;g.add(gift);for(const x of [-.45,.45]){const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x,1.7,0),new THREE.Vector3(x*.55,1.0,0)]),new THREE.LineBasicMaterial({color:0xffffff}));g.add(line)}
  } else if(kind==='liquidation'){
    const tri=new THREE.Mesh(new THREE.ConeGeometry(.82,1.35,3),mat(0xe74e54,.35,.3,0x8b0a18,.5));tri.rotation.z=Math.PI;tri.position.y=.8;g.add(tri);const ex=spriteText('!',{w:180,h:180,font:110,color:'#fff3df'});ex.position.set(0,1,.48);ex.scale.set(.65,.65,1);g.add(ex);
  }
  return g;
}

function buildSkyline(){const rng=()=>rnd();for(let i=0;i<56;i++){const ang=(i/56)*Math.PI*2+(rng()-.5)*.08;const radius=34+rng()*15;const h=3+rng()*14,w=.9+rng()*2.1;const b=box(w,h,w*(.7+rng()*.5),mat(0x09152d,.72,.38, rng()>.5?0x173b77:0x32145b,.16+rng()*.18));b.position.set(Math.cos(ang)*radius,h/2-1.3,Math.sin(ang)*radius);b.rotation.y=-ang+(rng()-.5)*.25;propGroup.add(b);if(i%3===0){const cap=box(w*.82,.07,w*.82,mat(rng()>.5?0x42dfff:0xc163ff,.1,.2,rng()>.5?0x42dfff:0xc163ff,1.8));cap.position.set(b.position.x,h-1.15,b.position.z);cap.rotation.y=b.rotation.y;propGroup.add(cap)}}
  const btc=spriteText('₿',{w:280,h:280,font:170,color:'#67ddff'});btc.position.set(22,18,-34);btc.scale.set(5.2,5.2,1);propGroup.add(btc);const eth=spriteText('◇',{w:280,h:280,font:180,color:'#a892ff'});eth.position.set(-20,16,-33);eth.scale.set(4.3,4.3,1);propGroup.add(eth);
}
function buildDice(){dice.forEach(d=>boardGroup.remove(d));dice=[];for(let i=0;i<2;i++){const g=new THREE.Group();const cube=box(1.45,1.45,1.45,materials.white);g.add(cube);for(const [x,y,z] of [[0,.73,0],[0,-.73,0],[.73,0,0],[-.73,0,0],[0,0,.73],[0,0,-.73]]){const pip=sphere(.12,materials.black,12);pip.position.set(x,y,z);g.add(pip)}g.position.set(i?1.1:-1.1,1.45,4.1);boardGroup.add(g);dice.push(g)}}
function buildTokens(){PLAYERS.forEach((p,i)=>{const c=new THREE.Color(p.color);const g=new THREE.Group();const base=cyl(.58,.68,.2,mat(c,.7,.25,c,.25),28);base.position.y=.15;g.add(base);if(i===0){const body=cyl(.32,.42,.82,materials.white,18);body.position.y=.72;g.add(body);const helmet=sphere(.42,mat(0x17213e,.75,.1,0x2f87c5,.32),24);helmet.position.y=1.36;g.add(helmet);const visor=sphere(.34,materials.glass,20);visor.scale.z=.55;visor.position.set(0,1.37,.25);g.add(visor)}else if(i===1){const body=sphere(.42,mat(c,.35,.42,c,.12));body.position.y=.75;g.add(body);const head=sphere(.36,mat(0xd49b45,.25,.48));head.position.y=1.25;g.add(head);for(const s of [-1,1]){const ear=cone(.16,.38,mat(0xd49b45,.25,.48),12);ear.position.set(s*.23,1.62,0);g.add(ear)}}else if(i===2){const body=box(.62,.72,.48,mat(c,.45,.32,c,.16));body.position.y=.68;g.add(body);const head=box(.55,.55,.55,mat(0xf0b38f,.18,.52));head.position.y=1.3;g.add(head);for(let k=0;k<4;k++){const hair=box(.14,.28,.15,mat(c,.4,.34,c,.2));hair.position.set(-.22+k*.15,1.66,(k%2)*.08);g.add(hair)}}else{const body=sphere(.46,mat(c,.4,.35,c,.15));body.position.y=.76;g.add(body);const head=sphere(.38,mat(0x6d4b35,.25,.5));head.position.y=1.3;g.add(head);for(const s of [-1,1]){const horn=cone(.1,.55,materials.gold,12);horn.rotation.z=s*.85;horn.position.set(s*.37,1.58,0);g.add(horn)}}g.scale.setScalar(.82);tokenGroup.add(g);tokenObjects.push(g)})}

function cameraFit(){const portrait=innerHeight>innerWidth*1.05;camera.fov=portrait?44:38;camera.aspect=innerWidth/innerHeight;camera.position.set(portrait?0:1.2,portrait?35:27,portrait?43:34);camera.lookAt(0,1.3,0);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);renderer.setPixelRatio(Math.min(devicePixelRatio,2));}
window.addEventListener('resize',cameraFit);cameraFit();

function freshState(){return {round:1,maxRounds:12,turn:0,regime:'sideways',pot:0,owners:{},upgrades:{},players:PLAYERS.map((p,id)=>({...p,id,pos:0,cash:2000000,dead:false})),log:['欢迎来到币圈大富翁。先活着，再发财。'],history:[100],started:true,gameover:false};}
function save(){if(state)localStorage.setItem('crypto-tycoon-premium',JSON.stringify(state));}
function load(){try{const s=JSON.parse(localStorage.getItem('crypto-tycoon-premium'));if(s?.started&&!s.gameover)return s}catch{}return null;}
function netWorth(p){let v=p.cash;for(const [idx,owner] of Object.entries(state.owners)){if(owner===p.id){const a=ASSETS[TILES[idx].asset];v+=a.cost*REGIMES[state.regime].mult*(1+(state.upgrades[idx]||0)*.45)}}return Math.max(0,Math.round(v));}
function sectorComplete(pid,sector){const ids=TILES.map((t,i)=>t.asset&&ASSETS[t.asset].sector===sector?i:null).filter(i=>i!==null);return ids.length&&ids.every(i=>state.owners[i]===pid);}
function rentFor(idx){const a=ASSETS[TILES[idx].asset],up=state.upgrades[idx]||0;let r=a.rent*REGIMES[state.regime].rent*(1+up*.68);if(sectorComplete(state.owners[idx],a.sector))r*=1.5;return Math.round(r);}
function log(msg){state.log.unshift(msg);state.log=state.log.slice(0,12);ui.sr.textContent=msg;save();renderHUD();}
function setTokenPositions(){if(!state)return;state.players.forEach((p,i)=>{const pos=TILE_POS[p.pos];const token=tokenObjects[i];token.position.set(pos.x+(i-1.5)*.18,1.03,pos.z+(i%2?-.2:.2));token.visible=!p.dead});}
function updateOwnershipVisuals(){ownerMarkers.forEach(m=>boardGroup.remove(m));ownerMarkers.length=0;if(!state)return;for(const [idxStr,owner] of Object.entries(state.owners)){const idx=+idxStr,pos=TILE_POS[idx],color=new THREE.Color(PLAYERS[owner].color);const marker=cyl(.22,.3,.42,mat(color,.65,.22,color,.5),20);marker.position.set(pos.x+1.25,1.28,pos.z-1.25);boardGroup.add(marker);ownerMarkers.push(marker);tileObjects[idx].top.material.emissive=color;tileObjects[idx].top.material.emissiveIntensity=.13}}
function renderHUD(){if(!state)return;const ranked=[...state.players].sort((a,b)=>netWorth(b)-netWorth(a));ui.leaderboard.innerHTML=ranked.map((p,i)=>`<div class="playerRow ${p.id===0?'me':''}" style="opacity:${p.dead?.38:1}"><div class="avatar" style="background:${p.color}">${i+1}</div><div><div class="pname">${p.name}</div><div class="pcash">现金 ${money(p.cash)} · ${Object.values(state.owners).filter(x=>x===p.id).length} 资产</div></div><div class="pworth">${money(netWorth(p))}</div></div>`).join('');const rg=REGIMES[state.regime];ui.round.innerHTML=`<div class="roundLine">第 ${state.round} / ${state.maxRounds} 回合</div><div class="goal">目标：成为币圈大富翁</div><div class="regime ${rg.cls}">● ${rg.name} · 情绪 ${rg.fg}</div>`;ui.ticker.innerHTML=state.log[0]||'等待开盘';ui.roll.disabled=busy||state.turn!==0||state.players[0].dead||state.gameover;updateOwnershipVisuals();}

async function animateToken(pid,toIdx){const obj=tokenObjects[pid],target=TILE_POS[toIdx];const start=obj.position.clone(),end=new THREE.Vector3(target.x+(pid-1.5)*.18,1.03,target.z+(pid%2?-.2:.2));const dur=TEST?35:180,st=performance.now();return new Promise(resolve=>{function f(now){const t=clamp((now-st)/dur,0,1),e=1-Math.pow(1-t,3);obj.position.lerpVectors(start,end,e);obj.position.y=1.03+Math.sin(Math.PI*t)*.85;if(t<1)requestAnimationFrame(f);else{obj.position.copy(end);resolve()}}requestAnimationFrame(f)})}
async function movePlayer(pid,steps){const p=state.players[pid];for(let i=0;i<steps;i++){p.pos=(p.pos+1)%24;if(p.pos===0){p.cash+=260000;state.pot+=30000;log(`${p.name} 穿越起点，获得 ${money(260000)} 区块奖励。`)}await animateToken(pid,p.pos)}save();}
async function animateDice(a,b){dice.forEach((d,i)=>{d.visible=true;d.userData.start=performance.now()+i*25;});const dur=TEST?60:720;const st=performance.now();return new Promise(resolve=>{function f(now){const t=clamp((now-st)/dur,0,1);dice.forEach((d,i)=>{d.rotation.x+=.22+i*.03;d.rotation.y+=.31+i*.02;d.position.y=1.45+Math.sin(Math.PI*t)*(2.4-i*.25);d.position.x=(i?1.1:-1.1)+Math.sin(t*8+i)*.5});if(t<1)requestAnimationFrame(f);else{dice[0].rotation.set(a*.55,a*.31,a*.17);dice[1].rotation.set(b*.52,b*.29,b*.2);dice.forEach((d,i)=>d.position.set(i?1.1:-1.1,1.45,4.1));resolve()}}requestAnimationFrame(f)})}
function rollPair(){return [1+Math.floor(rnd()*6),1+Math.floor(rnd()*6)];}

function modal({kicker='',title,body='',stats=[],actions=[]}){ui.modalCard.innerHTML=`<div class="modalKicker">${kicker}</div><h2>${title}</h2><p>${body}</p>${stats.length?`<div class="modalStats">${stats.map(s=>`<div><small>${s[0]}</small><b>${s[1]}</b></div>`).join('')}</div>`:''}<div class="modalActions">${actions.map((a,i)=>`<button type="button" data-action="${i}" class="${a.cls||'secondaryBtn'}">${a.label}</button>`).join('')}</div>`;ui.modal.classList.add('show');return new Promise(resolve=>{ui.modalCard.querySelectorAll('[data-action]').forEach(btn=>btn.addEventListener('click',()=>{const a=actions[+btn.dataset.action];ui.modal.classList.remove('show');resolve(a.value)}))})}
async function showAsset(pid,idx){const p=state.players[pid],a=ASSETS[TILES[idx].asset],owner=state.owners[idx];if(owner===undefined){if(pid!==0){if(botWants(p,a)){p.cash-=a.cost;state.owners[idx]=pid;state.upgrades[idx]=0;log(`${p.name} 买入 ${a.name}。`)}else log(`${p.name} 放弃 ${a.name}。`);return}const ans=await modal({kicker:`UNOWNED · ${a.sector}`,title:`${a.sym} ${a.name}`,body:'买下后，别人落在这里会向你支付链上过路费；集齐同板块还能获得组合溢价。',stats:[['买入价',money(a.cost)],['基础收益',money(a.rent)],['现金',money(p.cash)]],actions:[{label:'买入资产',value:'buy',cls:'primaryBtn'},{label:'保留现金',value:'pass'}]});if(ans==='buy'&&p.cash>=a.cost){p.cash-=a.cost;state.owners[idx]=0;state.upgrades[idx]=0;log(`你买入 ${a.name}，成本 ${money(a.cost)}。`)}else log(`你没有买入 ${a.name}。`);
  }else if(owner===pid){const up=state.upgrades[idx]||0,cost=Math.round(a.cost*.45);if(up>=2){log(`${p.name} 回到自己的 ${a.name}，仓位已经满级。`);return}if(pid!==0){if(p.cash>cost+450000&&rnd()>.45){p.cash-=cost;state.upgrades[idx]=up+1;log(`${p.name} 对 ${a.name} 加仓，等级 ${up+2}。`)}return}const ans=await modal({kicker:'YOUR ASSET',title:`${a.sym} ${a.name}`,body:'你回到了自己的资产，可以继续提高仓位。加仓会提高未来过路费，也会降低现金缓冲。',stats:[['加仓成本',money(cost)],['当前等级',`${up+1} / 3`],['现金',money(p.cash)]],actions:[{label:'继续加仓',value:'up',cls:'primaryBtn'},{label:'保持仓位',value:'hold'}]});if(ans==='up'&&p.cash>=cost){p.cash-=cost;state.upgrades[idx]=up+1;log(`你对 ${a.name} 加仓到 ${up+2} 级。`)}else log(`你保持 ${a.name} 当前仓位。`);
  }else{const r=rentFor(idx),op=state.players[owner];p.cash-=r;op.cash+=r;log(`${p.name} 落在 ${op.name} 的 ${a.name}，支付 ${money(r)} 链上过路费。`);}
  await solvency(pid);save();renderHUD();}
function botWants(p,a){const reserve=p.style==='degen'?280000:p.style==='collector'?360000:420000;if(p.cash-a.cost<reserve)return false;if(p.style==='degen')return a.vol>1.1||rnd()>.45;if(p.style==='collector')return a.sector==='YIELD'||rnd()>.58;if(p.style==='momentum')return state.regime==='bull'||state.regime==='mania'||a.sector==='CORE'||rnd()>.6;return rnd()>.5;}

async function special(pid,t){const p=state.players[pid];if(t.kind==='start')return;
  if(t.kind==='bull'){state.regime='bull';p.cash+=120000;log(`${p.name} 敲响牛市钟，市场进入牛市并获得 ${money(120000)}。`)}
  else if(t.kind==='bear'){state.regime='bear';p.cash-=100000;log(`${p.name} 进入熊市洞穴，市场转熊并损失 ${money(100000)}。`)}
  else if(t.kind==='airdrop'){const x=100000+Math.floor(rnd()*280000);p.cash+=x;log(`${p.name} 收到空投 ${money(x)}。`)}
  else if(t.kind==='halving'){state.regime=rnd()>.3?'bull':'sideways';state.players.forEach(q=>q.cash+=70000);log(`减半叙事升温：全体获得 ${money(70000)}，市场预期重新定价。`)}
  else if(t.kind==='vault'){const x=Math.min(120000,state.pot);p.cash+=x;state.pot-=x;log(`${p.name} 打开金库，取出 ${money(x)}。`)}
  else if(t.kind==='mine'){const x=140000+Math.floor(rnd()*160000);p.cash+=x;log(`${p.name} 获得矿场收益 ${money(x)}。`)}
  else if(t.kind==='liq'){const hit=Math.max(160000,Math.round(p.cash*.22));p.cash-=hit;log(`${p.name} 遭遇清算，损失 ${money(hit)}。`)}
  else if(t.kind==='market'||t.kind==='chance'||t.kind==='whale'||t.kind==='hack'){await eventChoice(pid,t.kind)}
  await solvency(pid);save();renderHUD();}
async function eventChoice(pid,kind){const p=state.players[pid];const defs={
    market:{title:'行情突然加速',body:'BTC 在十分钟内剧烈波动。你是追随趋势，还是保留现金？',a:['追随趋势',.52,260000,-170000],b:['保持现金',1,30000,30000]},
    chance:{title:'一条“靠谱消息”',body:'你得到一条未公开的上币消息。赔率诱人，但证据只隔着一个朋友。',a:['重注一手',.36,420000,-220000],b:['当它不存在',1,20000,20000]},
    whale:{title:'巨鲸开始转账',body:'链上出现大额转账。你不知道它是准备卖出，还是只是换钱包。',a:['反向下注',.46,300000,-190000],b:['等待确认',1,45000,45000]},
    hack:{title:'协议被攻击',body:'市场传出黑客攻击。你可以立即花钱做风险隔离，也可以赌影响有限。',a:['立即隔离风险',1,-90000,-90000],b:['继续持有',.58,70000,-260000]}
  }[kind];
  if(pid!==0){const chooseA=p.style==='degen'?rnd()>.25:p.style==='collector'?rnd()>.58:rnd()>.48;const d=chooseA?defs.a:defs.b;const gain=rnd()<d[1]?d[2]:d[3];p.cash+=gain;log(`${p.name} 在“${defs.title}”中选择${d[0]}，结果 ${gain>=0?'+':''}${money(gain)}。`);return}
  const ans=await modal({kicker:'MARKET EVENT',title:defs.title,body:defs.body,stats:[['当前现金',money(p.cash)],['市场状态',REGIMES[state.regime].name],['链上奖池',money(state.pot)]],actions:[{label:defs.a[0],value:'a',cls:'primaryBtn'},{label:defs.b[0],value:'b'}]});const d=ans==='a'?defs.a:defs.b;const gain=rnd()<d[1]?d[2]:d[3];p.cash+=gain;log(`你选择${d[0]}，结果 ${gain>=0?'+':''}${money(gain)}。`);}
async function solvency(pid){const p=state.players[pid];if(p.cash>=0)return;const owned=Object.entries(state.owners).filter(([,o])=>o===pid).map(([i])=>+i).sort((a,b)=>ASSETS[TILES[b].asset].cost-ASSETS[TILES[a].asset].cost);while(p.cash<0&&owned.length){const idx=owned.shift(),a=ASSETS[TILES[idx].asset],value=Math.round(a.cost*.62*(1+(state.upgrades[idx]||0)*.25));delete state.owners[idx];delete state.upgrades[idx];p.cash+=value;log(`${p.name} 被迫折价卖出 ${a.name}，回笼 ${money(value)}。`)}if(p.cash<0){p.dead=true;p.cash=0;tokenObjects[pid].visible=false;log(`${p.name} 已爆仓离场。`);if(pid===0)finishGame();}}

async function takeTurn(pid){if(state.gameover||state.players[pid].dead)return;state.turn=pid;renderHUD();const [a,b]=rollPair();await animateDice(a,b);await movePlayer(pid,a+b);await showLanding(pid);}
async function showLanding(pid){const t=TILES[state.players[pid].pos];if(t.type==='asset')await showAsset(pid,state.players[pid].pos);else await special(pid,t);}
async function humanRoll(){if(busy||state.turn!==0||state.gameover)return;busy=true;renderHUD();await takeTurn(0);if(!state.gameover){for(let i=1;i<4;i++){await wait(180);await takeTurn(i)}await endRound()}busy=false;renderHUD();}
async function endRound(){state.round++;if(state.round>state.maxRounds||state.players.filter(p=>!p.dead).length<=1){finishGame();return}const next=pick(['sideways','sideways','bull','bear','mania','panic']);state.regime=next;const prev=state.history[state.history.length-1]||100;const drift={sideways:0,bull:.09,bear:-.09,mania:.16,panic:-.18}[next]+(rnd()-.5)*.08;state.history.push(Math.max(35,prev*(1+drift)));state.turn=0;log(`新一轮开盘：${REGIMES[next].name}。`);save();}
function finishGame(){if(!state||state.gameover)return;state.gameover=true;busy=false;save();renderHUD();const rank=[...state.players].sort((a,b)=>netWorth(b)-netWorth(a));ui.endCard.innerHTML=`<div class="eyebrow">FINAL RANKING</div><h2>${rank[0].id===0?'你成为币圈大富翁':'本局冠军：'+rank[0].name}</h2><div class="rankList">${rank.map((p,i)=>`<div class="rankItem"><b>#${i+1}</b><div><b>${p.name}</b><small>现金 ${money(p.cash)} · ${Object.values(state.owners).filter(x=>x===p.id).length} 资产</small></div><div class="rankValue">${money(netWorth(p))}</div></div>`).join('')}</div><div class="endActions"><button id="again" class="primaryBtn">再开一局</button><button id="closeEnd" class="secondaryBtn">看看棋盘</button></div>`;ui.end.classList.add('show');$('#again').onclick=()=>startGame(true);$('#closeEnd').onclick=()=>ui.end.classList.remove('show');}
function startGame(force=false){state=force?freshState():(load()||freshState());busy=false;ui.intro.classList.remove('show');ui.end.classList.remove('show');state.gameover=false;setTokenPositions();renderHUD();save();log('链上开盘。每位玩家获得 ¥2,000,000 初始资金。');}

ui.start.addEventListener('click',()=>startGame(false));
ui.roll.addEventListener('click',humanRoll);
ui.restart.addEventListener('click',()=>{if(confirm('确定重开这一局？'))startGame(true)});
ui.rules.addEventListener('click',async()=>{await modal({kicker:'HOW TO PLAY',title:'币圈大富翁规则',body:'掷两颗骰子沿 24 格 3D 棋盘移动。无人资产可以买入；别人落在你的资产上要付过路费；落在自己的资产上可以加仓。牛熊、空投、巨鲸、黑客与清算会改变现金和市场状态。12 回合后按净值排名，爆仓则提前离场。',actions:[{label:'知道了',value:'ok',cls:'primaryBtn'}]})});
ui.portfolio.addEventListener('click',async()=>{if(!state)return;const p=state.players[0],owned=Object.entries(state.owners).filter(([,o])=>o===0).map(([i])=>`${ASSETS[TILES[i].asset].name} Lv.${(state.upgrades[i]||0)+1}`);await modal({kicker:'YOUR PORTFOLIO',title:`净值 ${money(netWorth(p))}`,body:owned.length?owned.join(' · '):'你目前还没有持有链上资产。',stats:[['现金',money(p.cash)],['持仓',owned.length],['市场',REGIMES[state.regime].name]],actions:[{label:'返回牌桌',value:'ok',cls:'primaryBtn'}]})});

buildWorld();
let last=performance.now();function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;centerPulse.rotation.z+=dt*.28;dice.forEach((d,i)=>{if(!busy)d.rotation.y+=dt*(.18+i*.05)});propGroup.children.forEach((o,i)=>{if(o.type==='Sprite')o.material.rotation=Math.sin(now*.0002+i)*.01});renderer.render(scene,camera);requestAnimationFrame(loop)}requestAnimationFrame(loop);

window.render_game_to_text=()=>JSON.stringify(state?{round:state.round,regime:state.regime,turn:state.turn,gameover:state.gameover,tiles:TILES.length,players:state.players.map(p=>({id:p.id,name:p.name,pos:p.pos,cash:p.cash,worth:netWorth(p),dead:p.dead,assets:Object.values(state.owners).filter(x=>x===p.id).length})),log:state.log.slice(0,5)}:{started:false,tiles:TILES.length});
window.advanceTime=ms=>new Promise(r=>setTimeout(r,TEST?Math.min(ms,10):ms));
window.__chainTycoon3d={getState:()=>state,start:()=>startGame(true),finish:()=>finishGame(),roll:()=>humanRoll(),tiles:TILES,renderer};

if(TEST){seed=246813579;}
