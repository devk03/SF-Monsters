import test from 'node:test';
import assert from 'node:assert/strict';
import {createAudioLifecycle} from '../scripts/quality/experiments/audio-lifecycle.mjs';
function fixture(){
  const events=[],facts=[];let running=true,failResume=false,failPause=false,holdSuspend;
  const audio={state:'running',async suspend(){events.push('suspend');if(holdSuspend)await holdSuspend;this.state='suspended';},
    async resume(){events.push('audio-resume');if(failResume)throw Error('Audio denied');this.state='running';}};
  const rpc=async op=>{events.push(op);if(op==='pause'){if(failPause)throw Error('Worker denied');running=false;}
    if(op==='resume')running=true;return {running,counter:42};};
  const lifecycle=createAudioLifecycle({audio,rpc,record:fact=>facts.push(fact)});lifecycle.started();
  return {events,facts,audio,lifecycle,failResume:()=>{failResume=true;},failPause:()=>{failPause=true;},
    hold(){let release;holdSuspend=new Promise(resolve=>{release=resolve;});return release;}};
}
test('ordinary pause freezes consumer first and resumes producer first without resetting audio',async()=>{
  const f=fixture();await f.lifecycle.pause();await f.lifecycle.resume({durationMs:100});
  assert.deepEqual(f.events,['suspend','pause','resume','audio-resume']);
  assert.equal(f.lifecycle.snapshot().intendedRunning,true);
  assert.deepEqual(f.facts.map(x=>x.type),['consumer-then-producer-paused','producer-then-consumer-resumed']);
});
test('pointer activation cannot wake audio during paused storage review',async()=>{
  const f=fixture();await f.lifecycle.pause();assert.equal(await f.lifecycle.unlock(),false);
  assert.deepEqual(f.events,['suspend','pause']);assert.equal(f.audio.state,'suspended');
});
test('resume denial freezes both sides and leaves intended playback disabled',async()=>{
  const f=fixture();await f.lifecycle.pause();f.failResume();await assert.rejects(f.lifecycle.resume(),/Audio denied/);
  assert.deepEqual(f.events.slice(0,4),['suspend','pause','resume','audio-resume']);
  assert.deepEqual(f.events.slice(4).sort(),['pause','suspend']);
  assert.equal(f.lifecycle.snapshot().intendedRunning,false);assert.equal(f.audio.state,'suspended');
  assert.equal(f.facts.at(-1).workerStopped,true);assert.equal(await f.lifecycle.unlock(),false);
});
test('pause acknowledgement failure keeps consumer frozen and records uncertain producer stop',async()=>{
  const f=fixture();f.failPause();await assert.rejects(f.lifecycle.pause(),/Worker denied/);
  assert.equal(f.audio.state,'suspended');assert.equal(f.facts.at(-1).workerStopped,false);
  assert.equal(f.lifecycle.snapshot().intendedRunning,false);
});
test('overlapping controls and activation cannot race a pending suspend',async()=>{
  const f=fixture(),release=f.hold(),pending=f.lifecycle.pause();
  await assert.rejects(f.lifecycle.resume(),/already in progress/);assert.equal(await f.lifecycle.unlock(),false);
  release();await pending;assert.deepEqual(f.events,['suspend','pause']);
});
test('activation resumes suspended audio only when ordinary playback is intended',async()=>{
  const f=fixture();f.audio.state='suspended';assert.equal(await f.lifecycle.unlock(),true);
  assert.deepEqual(f.events,['audio-resume']);
});

test('a stalled AudioContext operation has a finite failure path and cannot enable playback',async()=>{
  const events=[],audio={state:'suspended',suspend:async()=>{},resume:()=>new Promise(()=>{})};
  const lifecycle=createAudioLifecycle({audio,timeoutMs:10,rpc:async op=>{events.push(op);return {running:op==='resume'};}});
  await assert.rejects(lifecycle.resume(),/timed out/);
  assert.deepEqual(events,['resume','pause']);assert.equal(lifecycle.snapshot().intendedRunning,false);
});
