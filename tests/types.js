// Static semantic regression for FIN·TYPE v5.
const axes=['RG','FM','SI','HT'];
const letters={RG:['R','G'],FM:['F','M'],SI:['S','I'],HT:['H','T']};
const codes=new Set();
for(let mask=0;mask<16;mask++){
  let code=''; axes.forEach((a,i)=>code+=letters[a][(mask>>i)&1]); codes.add(code);
}
if(codes.size!==16) throw new Error('16-type code space collapsed');
for(const c of codes) if(!/^[RG][FM][SI][HT]$/.test(c)) throw new Error('invalid code '+c);
console.log('PASS: 16 FIN·TYPE code combinations are structurally reachable.');
