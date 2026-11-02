import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';

const waitForGame=()=>new Promise(resolve=>{const tick=()=>window.__chainTycoon3d?resolve(window.__chainTycoon3d):setTimeout(tick,20);tick();});
const api=await waitForGame();
const {scene}=api;

const group=new THREE.Group();
group.name='reference-fixture-polish';
scene.add(group);

const std=(color,metal=.45,rough=.25,em=0,ei=0)=>new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive:em,emissiveIntensity:ei});
const gold=std(0xf2b52d,.82,.2,0x6f3600,.14);
const purple=std(0x29154f,.55,.22,0x47147a,.28);
const dark=std(0x071127,.7,.24);
const green=std(0x43e39b,.16,.24,0x127146,.72);
const red=std(0xff6480,.16,.24,0x8c1532,.72);

function box(w,h,d,m){const x=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);x.castShadow=true;x.receiveShadow=true;return x;}
function cyl(r,h,m){const x=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,28),m);x.castShadow=true;x.receiveShadow=true;return x;}
function canvasTexture(draw,w=1200,h=300){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');draw(x,w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;}

// Central hero plaque: the reference image reads first as a game product, then as a board.
const outer=box(12.8,2.8,.55,gold);outer.position.set(0,4.8,1.75);group.add(outer);
const inner=box(12.05,2.15,.66,purple);inner.position.set(0,4.8,2.0);group.add(inner);
const titleTex=canvasTexture((c,w,h)=>{
  c.clearRect(0,0,w,h);c.textAlign='center';c.textBaseline='middle';
  c.shadowColor='rgba(84,39,0,.9)';c.shadowBlur=10;c.lineWidth=12;c.strokeStyle='#8d4d00';
  c.font='1000 150px "PingFang SC","Microsoft YaHei",sans-serif';c.strokeText('币圈大富翁',w/2,h*.44);c.fillStyle='#ffe78d';c.fillText('币圈大富翁',w/2,h*.44);
  c.shadowBlur=3;c.fillStyle='#9be6ff';c.font='900 38px -apple-system,sans-serif';c.fillText('CRYPTO TYCOON',w/2,h*.8);
});
const titlePlane=new THREE.Mesh(new THREE.PlaneGeometry(11.5,2.45),new THREE.MeshBasicMaterial({map:titleTex,transparent:true,depthWrite:false}));
titlePlane.position.set(0,4.8,2.36);titlePlane.renderOrder=90;group.add(titlePlane);

const crownBase=box(2.0,.26,.45,gold);crownBase.position.set(0,6.5,1.95);group.add(crownBase);
for(let i=-2;i<=2;i++){
  const h=i===0?1.25:(Math.abs(i)===1?.95:.72);
  const spike=new THREE.Mesh(new THREE.ConeGeometry(.25,h,18),gold);spike.position.set(i*.42,6.55+h*.48,1.98);spike.castShadow=true;group.add(spike);
}
const gemMat=std(0x70ddff,.2,.12,0x30a9ff,1.4);
for(const x of [-.75,0,.75]){const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.14),gemMat);gem.position.set(x,6.52,2.25);group.add(gem)}

// Candlestick market strip under the plaque, bringing the finance world into the center.
const candles=[[-4.5,.6,1],[-3.9,1.1,0],[-3.3,.72,1],[-2.7,1.35,1],[-2.1,.85,0],[-1.5,1.45,1],[-.9,1.0,1],[-.3,1.62,0],[.3,1.15,1],[.9,1.8,1],[1.5,1.25,0],[2.1,1.95,1],[2.7,1.55,1],[3.3,2.1,0],[3.9,1.72,1],[4.5,2.25,1]];
for(const [x,h,up] of candles){
  const m=up?green:red,body=box(.24,h*.42,.26,m);body.position.set(x,1.25+h*.18,2.0);group.add(body);
  const wick=box(.055,h*.8,.055,m);wick.position.set(x,1.25+h*.2,2.0);group.add(wick);
}

// Large coin medallion in front of the center stage.
const coin=cyl(.92,.22,gold);coin.rotation.x=Math.PI/2;coin.position.set(0,1.55,5.25);group.add(coin);
const btcTex=canvasTexture((c,w,h)=>{c.clearRect(0,0,w,h);c.textAlign='center';c.textBaseline='middle';c.fillStyle='#5d3300';c.font='1000 210px sans-serif';c.fillText('₿',w/2,h/2)},300,300);
const btc=new THREE.Mesh(new THREE.PlaneGeometry(1.35,1.35),new THREE.MeshBasicMaterial({map:btcTex,transparent:true,depthWrite:false}));btc.position.set(0,1.55,5.39);btc.renderOrder=95;group.add(btc);

// Extra chip/coin clusters to remove prototype-like dead zones.
for(const side of [-1,1]){
  for(let i=0;i<8;i++){
    const x=side*(5.4+(i%3)*.48),z=4.5+Math.floor(i/3)*.38;
    const c=cyl(.34,.11,i%2?gold:std(0x7047c9,.42,.22,0x3a176f,.25));c.position.set(x,1.06+(i%3)*.12,z);group.add(c);
  }
}

const warm=new THREE.PointLight(0xffc44f,55,18,2);warm.position.set(0,7,4);group.add(warm);
const cyan=new THREE.PointLight(0x58dfff,38,16,2);cyan.position.set(0,3,-2);group.add(cyan);
