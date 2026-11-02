(()=>{
  // Safety stop: once the human player is bankrupt, end the session instead of
  // allowing the autonomous bot turn chain to continue indefinitely.
  const timer=setInterval(()=>{
    const api=window.__chainTycoon;
    const s=api?.getState?.();
    if(!s||s.gameover)return;
    if(s.players?.[0]?.dead){
      s.players.slice(1).forEach(p=>p.dead=true);
      api.finish();
      clearInterval(timer);
    }
  },80);
})();
