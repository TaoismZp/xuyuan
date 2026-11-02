import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<400&&!window.__cryptoVisualV2;i++) await sleep(25);
const api=window.__cryptoVisualV2;
if(!api) throw new Error('visual v2 unavailable');
const {scene,camera,renderer}=api;
renderer.toneMappingExposure=1.72;
scene.fog.density=.0115;
scene.add(new THREE.AmbientLight(0x8aa8ff,1.15));
const gold=new THREE.MeshPhysicalMaterial({color:0xffc94c,metalness:.72,roughness:.14,clearcoat:1,emissive:0x8a4900,emissiveIntensity:.18});
const deep=new THREE.MeshPhysicalMaterial({color:0x3b183d,metalness:.38,roughness:.19,clearcoat:1,emissive:0x351020,emissiveIntensity:.16});
const cyan=new THREE.MeshStandardMaterial({color:0x60e5ff,metalness:.05,roughness:.18,emissive:0x21bde9,emissiveIntensity:2.4});
const violet=new THREE.MeshStandardMaterial({color:0xb57cff,metalness:.04,roughness:.18,emissive:0x7136e7,emissiveIntensity:1.7});
const pink=new THREE.MeshStandardMaterial({color:0xff6fcf,metalness:.04,roughness:.18,emissive:0xdb2b98,emissiveIntensity:1.8});
const box=(w,h,d,m)=>{const x=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);x.castShadow=true;x.receiveShadow=true;return x};
const cyl=(r,h,m,seg=32)=>{const x=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,seg),m);x.castShadow=true;x.receiveShadow=true;return x};
function texture(draw,w=900,h=260){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
function sprite(text,{w=800,h=230,size=100,color='#ffd96b',stroke='#713c00',sub=''}={}){const t=texture((c,W,H)=>{c.clearRect(0,0,W,H);c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';c.font=`1000 ${size}px -apple-system,"PingFang SC",sans-serif`;c.lineWidth=Math.max(7,size*.1);c.strokeStyle=stroke;c.strokeText(text,W/2,H*.43);c.fillStyle=color;c.fillText(text,W/2,H*.43);if(sub){c.font='900 28px sans-serif';c.lineWidth=4;c.strokeStyle='rgba(4,10,34,.9)';c.strokeText(sub,W/2,H*.81);c.fillStyle='#8ce8ff';c.fillText(sub,W/2,H*.81)}},w,h);const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,depthWrite:false}));s.scale.set(w/100,h/100,1);s.renderOrder=120;return s}

// 1) Camera: show the whole board like the locked 16:9 key art instead of cropping it.
function refCamera(){const portrait=innerHeight>innerWidth*1.05;camera.fov=portrait?47:34;camera.position.set(portrait?0:1.4,portrait?28.5:22.2,portrait?34:31.8);camera.lookAt(0,1.35,0);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix()}
refCamera();window.addEventListener('resize',refCamera);

// 2) Remove the prototype-like giant center bar/crown, then rebuild an ornate floating logo plaque.
scene.traverse(o=>{if(!o.position)return;const x=Math.abs(o.position.x),z=o.position.z,y=o.position.y;if(x<1.8&&z>-0.2&&z<1.5&&y>3.45&&y<6.3&&(o.isMesh||o.isSprite))o.visible=false});
const badge=new THREE.Group();badge.name='reference-logo-v3';
const back=box(9.1,1.72,.48,gold);back.position.set(0,3.95,.28);badge.add(back);
const face=box(8.48,1.32,.58,deep);face.position.set(0,3.95,.52);badge.add(face);
for(const side of [-1,1])for(let i=0;i<3;i++){const feather=new THREE.Mesh(new THREE.ConeGeometry(.18,.85,18),gold);feather.rotation.z=side*(1.02+i*.12);feather.position.set(side*(4.65+i*.34),3.65-i*.12,.38);badge.add(feather)}
const title=sprite('币圈大富翁',{w:1050,h:245,size:126,color:'#ffe38a',stroke:'#8d4e00',sub:'CRYPTO TYCOON'});title.position.set(0,4.0,1.0);title.scale.set(9.4,2.18,1);badge.add(title);
const crownBase=box(1.9,.2,.25,gold);crownBase.position.set(0,5.05,.65);badge.add(crownBase);
for(let i=-2;i<=2;i++){const h=i===0?.95:Math.abs(i)===1?.72:.56;const p=new THREE.Mesh(new THREE.ConeGeometry(.18,h,18),gold);p.position.set(i*.38,5.1+h*.46,.65);badge.add(p)}
for(const x of [-.55,0,.55]){const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.11),x?cyan:violet);gem.position.set(x,5.05,.82);badge.add(gem)}
scene.add(badge);

// 3) Put the financial city back into the composition: large chart billboard, neon signs and practical lights.
const worldKit=new THREE.Group();worldKit.name='reference-city-polish';
const panel=box(8.6,4.2,.28,new THREE.MeshPhysicalMaterial({color:0x101b45,metalness:.45,roughness:.16,clearcoat:1}));panel.position.set(-.6,8.0,-15.3);worldKit.add(panel);
const chartTex=texture((c,w,h)=>{c.fillStyle='#112453';c.fillRect(0,0,w,h);c.strokeStyle='rgba(79,210,255,.18)';c.lineWidth=2;for(let y=35;y<h;y+=45){c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.stroke()}for(let i=0;i<13;i++){const x=40+i*62,up=i%4!==1,base=80+((i*43)%120),hh=58+((i*37)%95);c.fillStyle=up?'#42f3b1':'#ff5aa9';c.fillRect(x,base,28,hh);c.fillRect(x+11,base-25,6,hh+50)}},900,430);
const chart=new THREE.Mesh(new THREE.PlaneGeometry(8.1,3.75),new THREE.MeshBasicMaterial({map:chartTex}));chart.position.set(-.6,8.0,-15.12);worldKit.add(chart);
const btcRing=new THREE.Mesh(new THREE.TorusGeometry(1.8,.14,14,64),cyan);btcRing.position.set(10.2,8.4,-14.6);worldKit.add(btcRing);const btc=sprite('₿',{w:260,h:260,size:185,color:'#67ecff',stroke:'#0b4d79'});btc.position.set(10.2,8.4,-14.2);btc.scale.set(3.2,3.2,1);worldKit.add(btc);
const eth=new THREE.Mesh(new THREE.OctahedronGeometry(1.3,0),violet);eth.scale.y=1.55;eth.position.set(6.0,9.1,-15.2);worldKit.add(eth);
const neon1=sprite('CRYPTO',{w:420,h:140,size:72,color:'#ff7ad9',stroke:'#521b75'});neon1.position.set(-10.4,8.2,-15.0);neon1.scale.set(3.4,1.05,1);worldKit.add(neon1);
for(const [x,c] of [[-11,0xff5fc8],[-6,0x4fdcff],[5,0x8d6cff],[11,0x4ee8ff]]){const l=new THREE.PointLight(c,46,13,2);l.position.set(x,7,-11);worldKit.add(l)}
scene.add(worldKit);

// 4) Cover dark dead zones with foreground finance props and stronger depth anchors.
function coinStack(x,z,n,mat=gold){const g=new THREE.Group();for(let i=0;i<n;i++){const c=cyl(.28,.13,mat,24);c.position.y=i*.12;g.add(c)}g.position.set(x,.98,z);scene.add(g)}
coinStack(-6.3,4.2,7);coinStack(-5.7,4.5,5,violet);coinStack(5.8,4.15,7);coinStack(6.35,4.45,5,cyan);coinStack(-11.1,-2.7,7);coinStack(11.0,2.4,6);
for(const x of [-8.8,8.8]){const ring=new THREE.Mesh(new THREE.TorusGeometry(.72,.08,10,38),x<0?pink:cyan);ring.rotation.x=Math.PI/2;ring.position.set(x,1.2,5.85);scene.add(ring)}

// Stronger warm/cool separation like the key art.
const warm=new THREE.PointLight(0xffb938,96,24,2);warm.position.set(-5,9,7);scene.add(warm);const cool=new THREE.PointLight(0x58dfff,92,25,2);cool.position.set(8,8,-2);scene.add(cool);const mag=new THREE.PointLight(0xff65d2,55,20,2);mag.position.set(-9,5,0);scene.add(mag);

window.__cryptoVisualTune={version:'v2.1-reference-composition'};
