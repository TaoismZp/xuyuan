const oldButton=document.querySelector('.v13-sound');
if(oldButton&&window.__cryptoV13){
  const button=oldButton.cloneNode(true);
  oldButton.replaceWith(button);
  button.addEventListener('click',()=>{
    const current=window.__cryptoV13.getProof().muted;
    window.__cryptoV13.setMuted(!current);
  });
  // If the user mutes before the first roll, the hero-roll gesture creates the AudioContext.
  // Re-apply the already-selected mute state after that synchronous creation point.
  document.querySelector('.roll')?.addEventListener('click',()=>{
    if(window.__cryptoV13.getProof().muted){
      queueMicrotask(()=>window.__cryptoV13.setMuted(true));
    }
  },true);
}
