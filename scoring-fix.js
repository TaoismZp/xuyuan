// Semantic scoring audit: map each option to the actual pole it represents.
function buildFinale(){
  if(s.finale)return s.finale;
  const arr=[];
  for(const k of ['RG','FM','SI','HT']){
    const positive=s.axis[k]>=0;
    const p=positive?PRESSURE[k].pos:PRESSURE[k].neg;
    // First letter means R/F/S/H. RG uses B as the first-pole choice in both variants;
    // FM/SI/HT use A when challenging from the positive side, B from the negative side.
    const firstSide=k==='RG'?'B':(positive?'A':'B');
    arr.push({...p,a:5,axis:k,firstSide});
  }
  s.finale=arr;save();return arr;
}
function questionAt(i){
  if(i<CORE.length){
    const q=CORE[i];
    return {...q,firstSide:q.axis==='RG'?'B':'A'};
  }
  return buildFinale()[i-CORE.length];
}
function pick(side){
  const q=questionAt(s.step),isA=side==='A';
  const delta=isA?q.ad:q.bd;
  const cashDelta=isA?q.ac:q.bc;
  const stress=isA?q.stressA:q.stressB;
  const vote=side===q.firstSide?1:-1;
  const pnl=s.nav*(delta/100);
  const before={nav:s.nav,cash:s.cash,stress:s.stress,peak:s.peak,maxdd:s.maxdd,axis:{...s.axis}};
  s.nav=Math.max(1000,s.nav+pnl);
  s.cash=clamp(s.cash+s.cash*(cashDelta/100),0,s.nav);
  s.stress=clamp(s.stress+stress,0,100);
  s.peak=Math.max(s.peak,s.nav);
  s.maxdd=Math.min(s.maxdd,(s.nav/s.peak-1)*100);
  s.axis[q.axis]+=vote;
  s.history.push(s.nav);
  const rec={step:s.step,side,vote,axis:q.axis,before,after:{nav:s.nav,cash:s.cash,stress:s.stress,peak:s.peak,maxdd:s.maxdd},q:q.q,choice:isA?q.A:q.B,outcome:isA?q.ao:q.bo,delta};
  s.answers.push(rec);
  if(Math.abs(delta)>=5||s.step>=CORE.length)s.moments.push(rec);
  s.overlay=rec;s.step++;save();settle(rec);
}
function code(){
  return ['RG','FM','SI','HT'].map(k=>{
    if(s.axis[k]>0)return AXES[k][0];
    if(s.axis[k]<0)return AXES[k][1];
    const last=[...s.answers].reverse().find(x=>x.axis===k);
    return last&&last.vote<0?AXES[k][1]:AXES[k][0];
  }).join('');
}
