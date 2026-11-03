const waitForV13=()=>new Promise((resolve,reject)=>{
  const started=performance.now();
  (function poll(){
    if(window.__cryptoV13&&document.querySelector('.v13-sound'))return resolve(window.__cryptoV13);
    if(performance.now()-started>60000)return reject(new Error('v13 controls dependency timeout'));
    setTimeout(poll,30);
  })();
});

try{
  const api=await waitForV13();
  const oldButton=document.querySelector('.v13-sound');
  const button=oldButton.cloneNode(true);
  oldButton.replaceWith(button);

  button.addEventListener('click',()=>{
    const next=!api.getProof().muted;
    api.setMuted(next);
  });

  // A pre-roll mute decision must survive AudioContext creation on the trusted roll gesture.
  document.querySelector('.roll')?.addEventListener('click',()=>{
    const selected=api.getProof().muted;
    if(selected)queueMicrotask(()=>api.setMuted(true));
  },true);

  window.__cryptoV13ControlsReady=true;
}catch(error){
  console.error(error);
  window.__cryptoV13ControlsReady=false;
}
