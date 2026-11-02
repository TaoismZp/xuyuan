import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v5-augment.js');
const scene=window.__ctCapturedScene, root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v6 scene missing');

const gold=new THREE.MeshPhysicalMaterial({color:0xf6bf45,metalness:.78,roughness:.13,clearcoat:1,clearcoatRoughness:.05});
const goldLite=new THREE.MeshPhysicalMaterial({color:0xffe28a,metalness:.58,roughness:.12,clearcoat:1,clearcoatRoughness:.05});
const navy=new THREE.MeshPhysicalMaterial({color:0x101f45,metalness:.4,roughness:.2,clearcoat:.88,clearcoatRoughness:.08});
const dark=new THREE.MeshPhysicalMaterial({color:0x10182d,metalness:.58,roughness:.26,clearcoat:.5});
const cyan=new THREE.MeshStandardMaterial({color:0x62eaff,emissive:0x0e7795,emissiveIntensity:.72,metalness:.12,roughness:.2});
const purple=new THREE.MeshStandardMaterial({color:0xb56cff,emissive:0x53186d,emissiveIntensity:.45,metalness:.08,roughness:.23});
const green=new THREE.MeshPhysicalMaterial({color:0x63e99c,metalness:.08,roughness:.24,clearcoat:.72});
const red=new THREE.MeshPhysicalMaterial({color:0xff6e73,metalness:.08,roughness:.25,clearcoat:.72});
const cream=new THREE.MeshPhysicalMaterial({color:0xfff0cf,metalness:.02,roughness:.3,clearcoat:.65});

function cast(m,receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sph(r,mat,s=24){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(12,s/2)),mat))}
function cone(r,h,mat,s=20){return cast(new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat))}
function plane(w,h,tex){const m=new THREE.MeshBasicMaterial({map:tex,toneMapped:false,side:THREE.DoubleSide});return new THREE.Mesh(new THREE.PlaneGeometry(w,h),m)}

function roundedRect(ctx,x,y,w,h,r){ctx.beginPath();ctx.roundRect(x,y,w,h,r);}
function titleTexture(){
  const c=document.createElement('canvas');c.width=1800;c.height=620;const x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);
  const bg=x.createLinearGradient(0,0,0,620);bg.addColorStop(0,'#2d173f');bg.addColorStop(.45,'#3b1d50');bg.addColorStop(1,'#15102d');
  x.fillStyle=bg;roundedRect(x,18,18,1764,584,110);x.fill();
  x.strokeStyle='#f7c657';x.lineWidth=30;roundedRect(x,30,30,1740,560,100);x.stroke();
  x.strokeStyle='rgba(255,244,189,.7)';x.lineWidth=6;roundedRect(x,60,58,1680,504,82);x.stroke();
  const g=x.createLinearGradient(0,145,0,430);g.addColorStop(0,'#fff9c9');g.addColorStop(.24,'#ffe58a');g.addColorStop(.62,'#f7b62e');g.addColorStop(1,'#c9780a');
  x.textAlign='center';x.textBaseline='middle';x.lineJoin='round';
  x.font='1000 255px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif';x.lineWidth=34;x.strokeStyle='#6d3408';x.strokeText('币圈大富翁',900,300);x.fillStyle=g;x.fillText('币圈大富翁',900,300);
  x.font='900 54px Arial,sans-serif';x.letterSpacing='10px';x.fillStyle='#fff1bd';x.fillText('CRYPTO TYCOON · SURVIVE THE CYCLE',900,500);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
function panelTexture(title,sub,bg){
  const c=document.createElement('canvas');c.width=900;c.height=720;const x=c.getContext('2d');
  x.fillStyle=bg;roundedRect(x,18,18,864,684,70);x.fill();
  const shine=x.createLinearGradient(0,20,0,700);shine.addColorStop(0,'rgba(255,255,255,.55)');shine.addColorStop(.38,'rgba(255,255,255,.13)');shine.addColorStop(1,'rgba(255,255,255,.02)');x.fillStyle=shine;roundedRect(x,18,18,864,684,70);x.fill();
  x.strokeStyle='rgba(255,232,154,.98)';x.lineWidth=24;roundedRect(x,23,23,854,674,64);x.stroke();
  x.textAlign='center';x.textBaseline='middle';x.fillStyle='#10172a';x.font='1000 112px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif';x.fillText(title,450,295);
  x.fillStyle='#28354f';x.font='800 49px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif';x.fillText(sub,450,440);
  x.fillStyle='rgba(255,255,255,.7)';x.fillRect(255,535,390,10);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
function signTexture(title,sub,accent='#ffe07b'){
 const c=document.createElement('canvas');c.width=900;c.height=500;const x=c.getContext('2d');
 const g=x.createLinearGradient(0,0,900,500);g.addColorStop(0,'#08132e');g.addColorStop(1,'#122b59');x.fillStyle=g;x.fillRect(0,0,900,500);x.strokeStyle=accent;x.lineWidth=22;x.strokeRect(18,18,864,464);
 x.textAlign='center';x.textBaseline='middle';x.fillStyle=accent;x.font='1000 112px "Noto Sans CJK SC","PingFang SC",Arial,sans-serif';x.fillText(title,450,205);x.fillStyle='#e8f3ff';x.font='800 44px "Noto Sans CJK SC","PingFang SC",Arial,sans-serif';x.fillText(sub,450,345);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}

// A. Central physical title monument: the reference's strongest focal hierarchy, rebuilt as live geometry + generated text texture.
const monument=new THREE.Group();root.add(monument);
const back=rb(7.9,2.3,.56,gold,.28,5);back.position.set(0,3.5,2.02);monument.add(back);
const core=rb(7.48,1.98,.62,navy,.24,5);core.position.set(0,3.5,2.12);monument.add(core);
const face=plane(7.2,1.76,titleTexture());face.position.set(0,3.5,2.45);monument.add(face);
const crownBase=rb(1.72,.2,.38,goldLite,.07,3);crownBase.position.set(0,4.86,2.12);monument.add(crownBase);
for(let i=-2;i<=2;i++){const h=i===0?1.02:(Math.abs(i)===1?.82:.62);const sp=cone(.19,h,goldLite,18);sp.position.set(i*.34,5.28+(i===0?.13:0),2.1);monument.add(sp)}
for(const s of [-1,1]) for(let i=0;i<7;i++){
  const leaf=cone(.11,.48,goldLite,5);leaf.rotation.z=s*(.95-i*.075);leaf.rotation.y=s*.2;leaf.position.set(s*(4.05+i*.13),2.92+i*.18,2.08);monument.add(leaf);
}
const titleGlow=new THREE.PointLight(0xffc85b,7.5,9,2);titleGlow.position.set(0,4.1,5.1);root.add(titleGlow);

// B. Turn the actual physical board tiles into large Chinese decision surfaces.
const tileData=[
 ['交易所','买入卖出 · 调整仓位','#bfa9ff'],['牛市','全线上涨 · 资产+50%','#72e19b'],['矿场','算力挖矿 · 获得BTC','#e7b16a'],['空投','领取代币 · 随机奖励','#d1a7ff'],['减半','供应冲击 · 长期利好','#e9b570'],['NFT','铸造交易 · 稀有收藏','#c99cff'],
 ['DeFi','流动性挖矿 · 赚取收益','#a3d8ff'],['巨鲸动向','大户操作 · 市场剧烈波动','#b3d8ff'],['爆仓','强制平仓 · 资产-50%','#ff8b91'],['熊市','市场下跌 · 资产-50%','#ff8588'],['质押','锁仓生息 · 稳定收益','#8bded8'],['Meme币','暴涨或暴跌 · 高风险','#ffc38a'],
 ['事件卡','抽取事件 · 机会或风险','#b9a6ff'],['金库','存取资产 · 保值避险','#f0c879'],['Gas费','支付费用 · 链上成本','#a8d5ff'],['ETF','资金流入 · 风险偏好','#97e2bd'],['DEX','链上兑换 · 即时成交','#b8a7ff'],['L2','低费扩容 · 效率提升','#8edee6'],
 ['AI叙事','热门赛道 · 情绪溢价','#c7a0ff'],['资金费率','支付或收取 · 杠杆成本','#f0b492'],['起点','领取初始资金 +2,000,000','#a173f1'],['黑客攻击','损失现金 · 安全事件','#ff8f96'],['清算','被迫卖出 · 流动性危机','#ff858e'],['收益池','持续收入 · 复利资产','#a7df9d']
];
const tileGroups=root.children.filter(o=>o.isGroup && Math.abs(o.position.y-.68)<.05 && (Math.abs(Math.abs(o.position.x)-5.4)<.22 || Math.abs(Math.abs(o.position.z)-5.4)<.22));
tileGroups.slice(0,24).forEach((g,i)=>{
 const [title,sub,bg]=tileData[i];const tex=panelTexture(title,sub,bg);const p=plane(1.46,1.18,tex);p.rotation.x=-Math.PI/2;p.position.set(0,.478,0);p.renderOrder=12;g.add(p);
});

// C. Foreground card decks and finance props — real geometry, not HUD decoration.
function cardDeck(x,z,title,sub,color){
 const g=new THREE.Group();
 for(let i=0;i<10;i++){const m=i===9?new THREE.MeshPhysicalMaterial({color,roughness:.28,clearcoat:.68}):new THREE.MeshPhysicalMaterial({color:i%2?0xefe2ca:0x2b3150,roughness:.38,clearcoat:.3});const b=rb(1.8,.08,1.25,m,.1,3);b.position.y=.78+i*.07;g.add(b)}
 const top=plane(1.55,.98,signTexture(title,sub,'#ffe69c'));top.rotation.x=-Math.PI/2;top.position.y=1.52;g.add(top);g.position.set(x,0,z);return g;
}
const eventDeck=cardDeck(-8.0,5.55,'事件卡','机会 / 风险',0x5e3b91);eventDeck.rotation.y=-.2;root.add(eventDeck);
const marketDeck=cardDeck(-6.9,7.1,'行情卡','涨跌 / 市场',0x6537a2);marketDeck.rotation.y=.18;root.add(marketDeck);
function coinTower(x,z,n=7,accent=cyan){for(let i=0;i<n;i++){const c=cyl(.3,.085,i%3===0?accent:goldLite,36);c.position.set(x+(i%2)*.03,.83+i*.078,z);root.add(c)}}
coinTower(-5.9,5.3,8,purple);coinTower(-5.35,5.15,6,gold);coinTower(4.45,5.55,7,cyan);coinTower(4.95,5.35,5,gold);
function btcCoin(x,y,z,scale=1){const g=new THREE.Group();const d=cyl(.42*scale,.12*scale,goldLite,42);d.rotation.x=Math.PI/2;g.add(d);const t=plane(.58*scale,.58*scale,signTexture('₿','','#3d2207'));t.position.z=.07*scale;g.add(t);g.position.set(x,y,z);root.add(g)}
btcCoin(-2.6,1.45,3.5,.72);btcCoin(2.55,1.42,3.4,.72);

// D. Replace the 'box wall' impression with a few authored financial towers in near/mid layers.
function steppedTower(label,sub,accent,matColor=0x183364){
 const g=new THREE.Group();const bodyMat=new THREE.MeshPhysicalMaterial({color:matColor,metalness:.48,roughness:.22,clearcoat:.55});
 const widths=[2.2,1.82,1.48],heights=[2.4,1.7,1.25];let y=0;
 widths.forEach((w,i)=>{const b=rb(w,heights[i],1.35-i*.15,bodyMat,.1,3);b.position.y=y+heights[i]/2;g.add(b);for(let r=.38;r<heights[i]-.12;r+=.43){const strip=rb(w*.82,.045,1.38-i*.15,i%2?purple:cyan,.015,1);strip.position.set(0,y+r,(1.35-i*.15)/2+.035);g.add(strip)}y+=heights[i]-.08});
 const cap=new THREE.Mesh(new THREE.OctahedronGeometry(.66,0),new THREE.MeshPhysicalMaterial({color:accent,metalness:.35,roughness:.12,clearcoat:1,emissive:accent,emissiveIntensity:.18}));cap.scale.y=1.3;cap.position.y=y+.72;cap.castShadow=true;g.add(cap);
 const frame=rb(2.28,.98,.15,gold,.1,3);frame.position.set(0,2.05,.76);g.add(frame);const s=plane(2.05,.78,signTexture(label,sub,'#ffe28a'));s.position.set(0,2.05,.845);g.add(s);return g;
}
const exTower=steppedTower('交易所','买卖 · 交易 · 上市',0xffc64d);exTower.position.set(-8.0,-.68,-8.25);exTower.rotation.y=.08;root.add(exTower);
const defiTower=steppedTower('DeFi','TVL ↑ · YIELD',0x5cecff,0x143760);defiTower.position.set(8.25,-.68,-8.6);defiTower.rotation.y=-.1;exTower.scale.setScalar(1.04);root.add(defiTower);
const etfTower=steppedTower('ETF','FLOW +12%',0x62eea2,0x133758);etfTower.scale.set(.78,.82,.78);etfTower.position.set(10.2,-.68,-6.5);etfTower.rotation.y=-.28;root.add(etfTower);
const hashTower=steppedTower('算力','HASH POWER',0xb56cff,0x1d2758);hashTower.scale.set(.74,.78,.74);hashTower.position.set(-10.0,-.68,-6.5);hashTower.rotation.y=.27;root.add(hashTower);

// E. Lift existing four player tokens into collectible-toy prominence and add unique badges.
function perimeterPositions(){const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];xs.forEach(x=>a.push([x,-5.4]));zs.forEach(z=>a.push([5.4,z]));[...xs].reverse().forEach(x=>a.push([x,5.4]));[...zs].reverse().forEach(z=>a.push([-5.4,z]));return a}
const pos=perimeterPositions(), tokenIndices=[17,10,13,20], badgeColors=[0xffd66d,0xff8b63,0x75b6ff,0x66eba1];
let tokenBoosted=0;
for(let i=0;i<tokenIndices.length;i++){
 const [x,z]=pos[tokenIndices[i]];let best=null,bd=1e9;
 for(const o of root.children){if(!o.isGroup||o.position.y<.78||o.position.y>1.18)continue;const d=(o.position.x-x)**2+(o.position.z-z)**2;if(d<bd){bd=d;best=o}}
 if(best&&bd<.3){best.scale.multiplyScalar(1.11);const med=cyl(.14,.05,goldLite,24);med.rotation.x=Math.PI/2;med.position.set(0,1.0,.42);best.add(med);const halo=new THREE.Mesh(new THREE.TorusGeometry(.58,.035,8,32),new THREE.MeshBasicMaterial({color:badgeColors[i],transparent:true,opacity:.8}));halo.rotation.x=Math.PI/2;halo.position.set(x,1.08,z);root.add(halo);tokenBoosted++}
}

// F. Brighter commercial-toy value range without washing out the stable v4 lighting.
scene.add(new THREE.HemisphereLight(0xcde7ff,0x331c35,.22));
const polishKey=new THREE.DirectionalLight(0xffe0aa,.62);polishKey.position.set(-4,10,8);scene.add(polishKey);
const boardFill=new THREE.PointLight(0x6eeaff,3.6,16,2);boardFill.position.set(0,5.5,5.0);scene.add(boardFill);
const warmFill=new THREE.PointLight(0xffbd62,3.4,14,2);warmFill.position.set(-5,4.2,4.5);scene.add(warmFill);

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v6',referencePixelsUsed:false,constructionProtocol:'wish-delivery-v7.4',chineseTilePanels:tileGroups.length,tokenBoosted,centralMonument:true,signatureTowers:4,foregroundDecks:2};
document.documentElement.dataset.sliceVersion='v6';
document.documentElement.dataset.sliceReady='1';
