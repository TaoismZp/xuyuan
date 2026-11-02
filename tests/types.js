// Structural reachability / combinatorial bias test for FIN·TYPE.
// This does not claim psychometric validity; it only verifies that the quiz logic
// does not make some of the 16 types unreachable or mechanically more likely.
const AXES = ['RG','FM','SI','HT'];
const coreAxes = ['RG','FM','HT','RG','SI','FM','HT','SI','FM','RG','HT','SI','FM','SI'];
const coreFirstSide = axis => axis === 'RG' ? 'B' : 'A';
function letter(axis, score, lastVote){
  const [left,right] = ({RG:['R','G'],FM:['F','M'],SI:['S','I'],HT:['H','T']})[axis];
  if(score>0) return left;
  if(score<0) return right;
  return lastVote<0 ? right : left;
}
function pressureFirstSide(axis, positive){
  if(axis==='RG') return 'B';
  return positive ? 'A' : 'B';
}
const counts = new Map();
const totalBits = 18;
const totalPaths = 1 << totalBits;
for(let mask=0; mask<totalPaths; mask++){
  const score={RG:0,FM:0,SI:0,HT:0};
  const last={RG:1,FM:1,SI:1,HT:1};
  let bit=0;
  for(const axis of coreAxes){
    const side=((mask>>bit++)&1)?'B':'A';
    const vote=side===coreFirstSide(axis)?1:-1;
    score[axis]+=vote; last[axis]=vote;
  }
  for(const axis of AXES){
    const positive=score[axis]>=0;
    const first=pressureFirstSide(axis,positive);
    const side=((mask>>bit++)&1)?'B':'A';
    const vote=side===first?1:-1;
    score[axis]+=vote; last[axis]=vote;
  }
  const code=AXES.map(a=>letter(a,score[a],last[a])).join('');
  counts.set(code,(counts.get(code)||0)+1);
}
if(counts.size!==16) throw new Error(`Expected 16 reachable types, got ${counts.size}: ${[...counts.keys()].join(',')}`);
const vals=[...counts.values()];
const min=Math.min(...vals),max=Math.max(...vals),ideal=totalPaths/16;
if(min!==ideal || max!==ideal) throw new Error(`Structural type bias: min=${min}, max=${max}, ideal=${ideal}`);
console.log(`PASS: all 16 types reachable; ${ideal} / ${totalPaths} paths each (${(100/16).toFixed(2)}%).`);
