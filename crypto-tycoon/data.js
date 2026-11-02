(()=>{
const COLORS=['#9df7c6','#f7c66a','#b99cff','#83daf8'];
const PLAYER_DEFS=[
 {name:'你',icon:'YOU',color:COLORS[0],ai:false,style:'player'},
 {name:'巨鲸',icon:'W',color:COLORS[1],ai:true,style:'whale'},
 {name:'量化',icon:'Q',color:COLORS[2],ai:true,style:'quant'},
 {name:'钻石手',icon:'D',color:COLORS[3],ai:true,style:'diamond'},
];
const REGIMES={
 bull:{name:'BULL RUN',cn:'牛市',mult:1.22,rent:1.2,fg:78,class:'bull'},
 sideways:{name:'CHOP',cn:'震荡',mult:1,rent:1,fg:51,class:'sideways'},
 bear:{name:'BEAR',cn:'熊市',mult:.78,rent:.82,fg:24,class:'bear'},
 mania:{name:'MANIA',cn:'狂热',mult:1.45,rent:1.38,fg:92,class:'bull'},
 panic:{name:'PANIC',cn:'恐慌',mult:.62,rent:.7,fg:11,class:'bear'}
};
const ASSETS={
 BTC:{name:'BTC',sym:'₿',cost:66000,rent:8200,sector:'CORE',vol:.7},
 ETH:{name:'ETH',sym:'Ξ',cost:52000,rent:6900,sector:'CORE',vol:.85},
 USDC:{name:'USDC',sym:'◉',cost:26000,rent:3600,sector:'CORE',vol:.25},
 SOL:{name:'SOL',sym:'S',cost:39000,rent:6400,sector:'BETA',vol:1.25},
 MEME:{name:'MEME',sym:'◎',cost:22000,rent:5900,sector:'BETA',vol:1.9},
 AI:{name:'AI',sym:'AI',cost:42000,rent:7600,sector:'BETA',vol:1.45},
 CEX:{name:'CEX',sym:'↔',cost:36000,rent:5600,sector:'INFRA',vol:.9},
 L2:{name:'L2',sym:'Ⅱ',cost:29000,rent:4800,sector:'INFRA',vol:1},
 RWA:{name:'RWA',sym:'▣',cost:33000,rent:5100,sector:'INFRA',vol:.65},
 DEFI:{name:'DeFi',sym:'◇',cost:31000,rent:5200,sector:'YIELD',vol:1.2},
 STAKE:{name:'STAKE',sym:'%',cost:27000,rent:4400,sector:'YIELD',vol:.75},
 NFT:{name:'NFT',sym:'✦',cost:21000,rent:4300,sector:'YIELD',vol:1.65},
};
const TILES=[
 {type:'special',name:'GENESIS',sym:'⛓',kind:'start'},
 {type:'asset',asset:'BTC'},{type:'event',name:'AIRDROP',sym:'🎁',kind:'airdrop'},{type:'asset',asset:'ETH'},
 {type:'special',name:'GAS SPIKE',sym:'⛽',kind:'gas'},{type:'asset',asset:'SOL'},{type:'special',name:'BULL BELL',sym:'▲',kind:'bull'},
 {type:'asset',asset:'MEME'},{type:'event',name:'RUG ALERT',sym:'⚠',kind:'rug'},{type:'asset',asset:'DEFI'},
 {type:'asset',asset:'CEX'},{type:'event',name:'HACK',sym:'☠',kind:'hack'},{type:'special',name:'HALVING',sym:'½',kind:'halving'},
 {type:'asset',asset:'L2'},{type:'event',name:'ETF DESK',sym:'ETF',kind:'etf'},{type:'asset',asset:'NFT'},
 {type:'special',name:'BEAR CAVE',sym:'▼',kind:'bear'},{type:'asset',asset:'USDC'},{type:'event',name:'WHALE',sym:'🐋',kind:'whale'},
 {type:'asset',asset:'AI'},{type:'special',name:'LIQUIDATION',sym:'✕',kind:'liq'},{type:'asset',asset:'STAKE'},
 {type:'asset',asset:'RWA'},{type:'event',name:'BRIDGE',sym:'⇄',kind:'bridge'},
];
const EVENTS=[
 {title:'监管突袭',quote:'交易所突然收到监管调查。你可以花钱提前降风险，也可以赌事情没有那么严重。',choices:[
   {label:'先付 ¥1.2万 做风险隔离',hint:'确定损失，换取安稳',cash:-12000,stress:-4,trait:'survive'},
   {label:'不动，继续吃收益',hint:'50% 无事发生；50% 再亏 ¥2.8万',risk:[8000,-28000],stress:7,trait:'degen'}]},
 {title:'MEME 狂潮',quote:'整个时间线都在刷同一个新币。赔率很诱人，信息却极少。',choices:[
   {label:'拿 ¥1.5万 参与一手',hint:'40% 翻倍；60% 亏掉 70%',risk:[15000,-10500],cash:-15000,stress:6,trait:'degen'},
   {label:'不碰，保留火力',hint:'没有收益，也没有故事',cash:0,stress:-2,trait:'survive'}]},
 {title:'稳定币脱锚',quote:'USDC 突然跌到 0.91。你相信它会回锚，但市场正在抢跑。',choices:[
   {label:'抄底 ¥2万',hint:'60% 回锚赚 ¥1.2万；40% 继续脱锚亏 ¥1.6万',cash:-20000,risk:[32000,4000],stress:5,trait:'contrarian'},
   {label:'保持现金',hint:'错过赔率，也保留确定性',cash:0,stress:-3,trait:'survive'}]},
 {title:'黑天鹅传闻',quote:'群里开始传“某大所资不抵债”。没有证据，但提款队伍在变长。',choices:[
   {label:'先撤一半风险仓',hint:'损失机会成本，换取抗冲击',cash:-6000,stress:-5,trait:'survive'},
   {label:'等证据再说',hint:'55% 虚惊；45% 额外损失 ¥2.4万',risk:[4000,-24000],stress:6,trait:'system'}]},
 {title:'内幕感',quote:'你收到一条“非常靠谱”的未公开上币消息。来源只隔了一层朋友。',choices:[
   {label:'重注 ¥2万',hint:'35% +¥3.5万；65% -¥1.8万',cash:-20000,risk:[55000,2000],stress:8,trait:'degen'},
   {label:'当它不存在',hint:'让证据质量先过关',cash:0,stress:-2,trait:'system'}]},
 {title:'闪崩',quote:'BTC 10 分钟跌 14%，你最看好的资产也跟着砸。',choices:[
   {label:'加仓 ¥1.8万',hint:'50% V 型反弹 +¥2.8万；50% 再跌 -¥1.6万',cash:-18000,risk:[46000,2000],stress:7,trait:'contrarian'},
   {label:'不加也不砍',hint:'把“我不知道”当成一个有效动作',cash:0,stress:-4,trait:'survive'}]},
];
const sectorAssets=s=>Object.keys(ASSETS).filter(k=>ASSETS[k].sector===s);
const coords=(()=>{let a=[];for(let c=1;c<=7;c++)a.push([1,c]);for(let r=2;r<=6;r++)a.push([r,7]);for(let c=7;c>=1;c--)a.push([7,c]);for(let r=6;r>=2;r--)a.push([r,1]);return a;})();

window.CTDATA={COLORS,PLAYER_DEFS,REGIMES,ASSETS,TILES,EVENTS,coords};
})();
