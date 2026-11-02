const $=s=>document.querySelector(s);const app=$('#app');const acts=[['ACT I','牛市亢奋','所有人都开始赚钱，最危险的是你开始把运气解释成能力。'],['ACT II','账户回撤','价格开始反着走，真正暴露的是你的损失结构。'],['ACT III','噪声震荡','消息越来越多，方向越来越少，频繁动作开始吞噬判断。'],['ACT IV','流动性收紧','你曾经相信的东西还在，但市场不给它时间兑现。'],['ACT V','Regime Shift','旧规律失灵，新规律还没形成。'],['ACT VI','最终压力测试','现在不测偏好，只测你愿意为偏好付出什么代价。']];
const Q=[
['RG','仓位连续上涨三周，你最先想到什么？','趁优势还在继续加码，让正确更值钱','先把最坏结果算清楚，确保一脚踩空也还在牌桌上','趋势强劲，但波动也在同步放大。'],
['FM','一家公司突然公布超预期数据，你更相信什么？','先看现金流、订单、利润质量这些底层证据','先看价格怎么反应，因为市场已经替很多人投了票','消息是真的，但价格交易的是预期差。'],
['SI','交易计划临盘遇到完全没预料过的消息，你会？','先按预案处理，除非触发我事先定义的例外','重新读现场，如果结构变了，计划也应该立刻变','纪律和适应性开始发生冲突。'],
['HT','你看好的资产横盘半年，逻辑没坏，你会？','继续等，时间本身也是持仓的一部分','主动换到机会成本更低、效率更高的标的','没有亏损，也可能正在支付代价。'],
['RG','你有一个自认为胜率70%的机会，怎么下？','如果赔率足够好，我愿意明显提高下注强度','就算胜率高，也先把失败成本限制住','高胜率最容易制造过度下注。'],
['FM','宏观数据和企业基本面矛盾时，你更偏向？','优先底层经营事实，宏观最终会传导回来','优先市场当前主导变量，因为价格先于报表调整','你必须决定哪种证据权重更高。'],
['SI','连续三次止损后，第四个信号再次出现，你会？','按系统继续执行，样本不会因为三次失败就失效','缩小或暂停，因为环境可能已经变了','真正难的是分辨波动与失效。'],
['HT','一笔盈利仓位已经翻倍，但仍在趋势中，你更可能？','继续让利润奔跑，不轻易打断大级别机会','主动落袋一部分，把账面利润变成可用资本','盈利也会制造心理负担。'],
['RG','市场暴跌，你最在意什么？','有没有出现赔率极端偏向我的机会','先确认自己还有没有被迫卖出的结构风险','危机里既有机会，也有强制清算。'],
['FM','你读到一份极有说服力的研报，但股价完全不配合？','先检查研报里的关键假设有没有事实支撑','先尊重价格，市场可能已经看见我没看见的东西','信息和价格发生正面冲突。'],
['SI','你已经持仓，随后新证据出现但不够确定，你会？','按原系统阈值处理，不因为模糊证据频繁改动作','动态调整仓位，让不确定性直接体现在下注上','模糊信息最考验规则颗粒度。'],
['HT','空仓两周，没有好机会，你会？','继续等，空仓不是空白，而是一种仓位','降低标准参与一些次优机会，保持市场手感','无聊会逼人制造动作。'],
['RG','你发现一个可能10倍、也可能归零的机会？','只要期望值够高，值得用小概率换巨大上行','先限制总风险暴露，不让单次尾部决定命运','赔率和生存发生冲突。'],
['FM','管理层说法很好听，但行业价格数据变差？','看长期商业模式和公司执行是否真在改善','优先相信外部价格与行为数据，嘴巴成本最低','叙事和可观察数据开始分叉。'],
['SI','你最信任的模型突然连续失准，你会？','先扩大样本，不轻易因为短期噪声推翻系统','快速降权模型，直到重新证明有效','稳定性和纠错速度无法同时最大化。'],
['HT','一个标的基本面没坏，但一年没有任何催化？','只要赔率仍然好，我可以继续拿','时间也是成本，没有催化就主动重新配置','长期持有和机会成本正面冲突。'],
['RG','如果必须在“高收益但大回撤”和“低收益但稳”二选一？','接受波动换取更高长期上限','优先控制路径，让复利不被大回撤打断','最终收益取决于你是否活得到终点。'],
['FM','当市场情绪极端一致时，你更容易？','回到底层价值，检查是否出现价格与事实的错配','顺着资金与价格结构走，直到它自己反转','逆向不等于正确，顺势也不等于盲从。'],
['SI','你交易中最不愿放弃的是什么？','一套可重复、能复盘、能验证的规则','现场判断和临场适应空间','自由度越高，对判断质量要求越高。'],
['HT','行情突然加速，你原本计划下周再买？','仍按节奏等更好的价格或确认','提前行动，避免最好的窗口已经关闭','等待和错失会同时制造压力。'],
['RG','如果一次错误会让你失去未来三年的下注资格？','仍然愿意下注，但会压缩规模保留上行','这类风险无论赔率多好都应该先回避','真正危险的是下一手消失。'],
['FM','如果所有人都在看同一份公开数据，你还会依赖它吗？','会，但只看我能否做出更深的因果解释','不会，优势必须来自市场尚未充分交易的信息','公开事实与独立判断不是一回事。'],
['SI','如果你的系统长期有效，但这次现场结构明显异常？','遵守规则，单次例外最容易演变成失控','允许例外，但必须记录并在事后审查','系统不是为了阻止思考，而是限制任性。'],
['HT','如果等待再一个月能显著提高赔率，但机会可能今天就走？','愿意牺牲一部分机会换更高确定性','先参与一部分，用行动换信息，再根据反馈追加','最后一题测的是你如何和未知相处。']
];
const titles={RFSH:'堡垒研究者',RFST:'价值守门员',RFIH:'耐心猎手',RFIT:'逆向校准者',RMSH:'稳健趋势派',RMST:'风险调度者',RMIH:'市场潜伏者',RMIT:'战术观察者',GFSH:'高确信复利者',GFST:'主动价值派',GFIH:'集中猎手',GFIT:'机会主义者',GMSH:'趋势复利者',GMST:'进攻调度者',GMIH:'动量捕手',GMIT:'市场掠食者'};
const axisInfo={RG:['R','G','生存优先','火力优先'],FM:['F','M','基本面证据','市场证据'],SI:['S','I','系统驱动','临场驱动'],HT:['H','T','等待兑现','主动调整']};
let state=JSON.parse(localStorage.getItem('finTypeState')||'null')||{i:0,s:{RG:0,FM:0,SI:0,HT:0},answers:[],started:false};
function save(){localStorage.setItem('finTypeState',JSON.stringify(state))}function reset(){state={i:0,s:{RG:0,FM:0,SI:0,HT:0},answers:[],started:false};save();render()}
function shell(body,chip='FIN·TYPE'){app.innerHTML=`<div class="shell fade"><div class="brand"><div class="logo">FIN·TYPE</div><div class="chip">${chip}</div></div>${body}</div>`}
function start(){state.started=true;save();render()}
function render(){if(!state.started)return intro();if(state.i>=Q.length)return result();question()}
function intro(){shell(`<section class="hero"><div class="eyebrow">FINANCIAL DECISION PERSONALITY</div><h1>你不是在做题。<br/>你是在暴露下注习惯。</h1><p>24个真实金融决策场景，不问“你是什么人”，只看<strong>当钱、时间、回撤和不确定性同时出现时，你会怎么选</strong>。</p></section><section class="card"><div class="start-grid"><div class="metric"><b>24</b><span>决策回合</span></div><div class="metric"><b>4</b><span>下注轴</span></div><div class="metric"><b>16</b><span>金融人格</span></div></div><button class="primary" onclick="start()">开始压力测试</button>${state.i>0?`<button class="ghost" style="width:100%;margin-top:10px" onclick="state.started=true;render()">继续上次进度</button>`:''}<div class="note">这不是投资建议，也不是心理诊断。它只是把你在不确定性下的默认动作做成一面镜子。</div></section>`)}
function question(){const q=Q[state.i],act=Math.min(5,Math.floor(state.i/4));shell(`<div class="progress-wrap"><div class="progress-top"><span>${state.i+1} / ${Q.length}</span><span>${Math.round(state.i/Q.length*100)}%</span></div><div class="bar"><i style="width:${state.i/Q.length*100}%"></i></div></div><section class="card"><div class="act"><div class="act-badge">${acts[act][0]}</div><span>${acts[act][1]}</span></div><div class="q">${q[1]}</div><div class="context">${q[4]}</div><button class="choice" onclick="pick(1)"><span class="k">A</span><b>${q[2]}</b></button><button class="choice" onclick="pick(-1)"><span class="k">B</span><b>${q[3]}</b></button><div class="footer-row">${state.i?`<button class="ghost" onclick="back()">上一题</button>`:'<span></span>'}<button class="ghost" onclick="reset()">重新开始</button></div></section>`,`第 ${act+1} 幕 · ${acts[act][1]}`)}
function pick(v){const axis=Q[state.i][0];state.s[axis]+=v;state.answers.push(v);state.i++;save();if(state.i<Q.length&&state.i%4===0){interlude(Math.min(5,state.i/4));}else render()}
function interlude(n){const a=acts[Math.min(5,n)];shell(`<section class="card interlude"><div class="eyebrow">MARKET REGIME CHANGED</div><h2>${a[1]}</h2><p>${a[2]}</p><div class="market-line"></div><button class="primary" onclick="render()">进入下一幕</button></section>`,a[0])}
function back(){if(!state.i)return;state.i--;const v=state.answers.pop();state.s[Q[state.i][0]]-=v;save();render()}
function code(){return Object.keys(axisInfo).map(k=>state.s[k]>=0?axisInfo[k][0]:axisInfo[k][1]).join('')}
function pct(k){const max=Q.filter(q=>q[0]===k).length;return Math.round((state.s[k]+max)/(max*2)*100)}
function result(){const c=code(),name=titles[c]||'未命名交易者';const letters=c.split('');const traits={R:['你天然会先保护生存与选择权。','最怕过度防守错过真正稀缺的高赔率窗口。'],G:['你愿意集中火力让正确变得昂贵。','最怕把确信感误当成客观优势。'],F:['你习惯从商业事实和底层机制出发。','最怕低估价格已经提前交易了多少。'],M:['你尊重资金、价格和群体行为。','最怕把价格本身当成真理。'],S:['你依赖规则、流程和可复盘性。','最怕环境已经变了，系统却还没更新。'],I:['你擅长读现场并快速适应。','最怕临场自由慢慢变成事后合理化。'],H:['你相信等待能把赔率变得更好。','最怕把耐心用在已经失效的判断上。'],T:['你愿意主动调整、切换和重新配置。','最怕动作本身替代了真正的信息增量。']};const edge=letters.map(x=>traits[x][0]).join(' '),blind=letters.map(x=>traits[x][1]).join(' ');const kill=letters.includes('G')?(letters.includes('T')?'高波动拥挤行情：越顺越加、越快越动，最容易把优势变成尾部风险。':'高确信单边行情：最危险的不是看错，而是仓位让你没有第二次修正机会。'):(letters.includes('H')?'慢性失效行情：逻辑没坏的错觉，会让你在时间里持续支付机会成本。':'假突破与反复震荡：频繁小错未必致命，但会持续磨损判断与耐心。');const train=letters.includes('S')?'未来30天，每次系统外交易必须先写一句：我凭什么认为这次例外值得？':'未来30天，每次临场改主意前，先写下触发变化的那条新证据。';const summary=`${name}不是“保守”或“激进”的标签，而是一套你在未知里分配资本、证据和时间的默认方式。你的优势来自四个维度的组合，而不是其中任何单独一项。`;shell(`<section class="card"><div class="eyebrow">YOUR FINANCIAL TYPE</div><div class="result-code">${c}</div><div class="result-name">${name}</div><span class="result-tag">金融决策人格</span><p class="result-summary">${summary}</p><div class="axes">${Object.keys(axisInfo).map((k,i)=>{const p=pct(k),a=axisInfo[k];return `<div class="axis"><div class="axis-top"><span>${a[2]}</span><b>${letters[i]} · ${p}%</b><span>${a[3]}</span></div><div class="axis-track"><i style="width:${p}%"></i></div></div>`}).join('')}</div><div class="grid2"><div class="insight"><small>NATURAL EDGE</small><b>你天然擅长什么</b><p>${edge}</p></div><div class="insight"><small>STRUCTURAL BLIND SPOT</small><b>你的结构性盲点</b><p>${blind}</p></div><div class="insight kill"><small>KILL ZONE</small><b>最容易死在哪种行情</b><p>${kill}</p></div><div class="insight training"><small>30-DAY COUNTER TRAINING</small><b>你的反向训练</b><p>${train}</p></div></div><div class="share-row"><button class="primary" onclick="shareResult()">分享我的人格</button><button class="ghost" onclick="reset()">重新测试</button></div><div class="note">结果反映的是当前决策偏好，而不是永久身份。真正的高手不是活成某一种类型，而是知道什么时候不能被自己的默认类型绑架。</div></section>`,c+' · '+name)}
async function shareResult(){const c=code(),text=`我的 FIN·TYPE 是 ${c} · ${titles[c]}。24个金融决策场景，测的不是性格，是下注习惯。`;if(navigator.share){try{await navigator.share({title:'FIN·TYPE 金融决策人格',text,url:location.href});return}catch(e){}}try{await navigator.clipboard.writeText(text+' '+location.href);alert('结果已复制')}catch(e){alert(text)}}
render();