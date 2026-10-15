// Private host coordinator. AudioContext is the consumer; Worker is the producer.
// It neither invents clock values nor clears, pads or trims the worklet queue.
export function createAudioLifecycle({audio,rpc,record=()=>{},timeoutMs=1500}){
  let busy=false,intendedRunning=false;
  async function audioState(method,state){
    let timer;
    const operation=Promise.resolve().then(()=>audio[method]());
    try{
      await Promise.race([operation,new Promise((_,reject)=>{
        timer=setTimeout(()=>reject(Error('AudioContext '+method+' timed out')),timeoutMs);
      })]);
      if(audio.state!==state)throw Error('AudioContext did not become '+state);
    }finally{clearTimeout(timer);}
  }
  async function failClosed(error){
    intendedRunning=false;
    // An earlier timed-out resume may still settle; a queued suspend follows it.
    const result=await Promise.allSettled([audioState('suspend','suspended'),rpc('pause')]);
    record({type:'lifecycle-failure',error:error.message,
      audioStopped:result[0].status==='fulfilled',workerStopped:result[1].status==='fulfilled'&&result[1].value.running===false});
  }
  async function operation(run){
    if(busy)throw Error('Audio lifecycle operation already in progress');
    busy=true;
    try{return await run();}catch(error){await failClosed(error);throw error;}finally{busy=false;}
  }
  return {
    pause(){return operation(async()=>{
      intendedRunning=false;
      await audioState('suspend','suspended');
      const paused=await rpc('pause');
      if(paused.running!==false)throw Error('Worker did not acknowledge pause');
      record({type:'consumer-then-producer-paused',counter:paused.counter});return paused;
    });},
    resume(data={}){return operation(async()=>{
      intendedRunning=false;
      const started=await rpc('resume',data);
      if(started.running!==true)throw Error('Worker did not acknowledge resume');
      await audioState('resume','running');
      intendedRunning=true;
      record({type:'producer-then-consumer-resumed',counter:started.counter});return started;
    });},
    // User activation can unlock suspended audio only during intended playback.
    unlock(){
      if(busy||!intendedRunning||audio.state!=='suspended')return Promise.resolve(false);
      return operation(async()=>{await audioState('resume','running');return true;});
    },
    started(){if(busy)throw Error('Lifecycle operation pending');intendedRunning=true;},
    snapshot(){return {busy,intendedRunning,audioState:audio.state};}
  };
}
