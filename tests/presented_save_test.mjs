import assert from 'node:assert/strict';
import test from 'node:test';
import { createHash } from 'node:crypto';
import { createPresentedSaveStore, encodeRaw, decodeRaw } from '../scripts/quality/experiments/presented-save.mjs';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const raw=()=>Uint8Array.from({length:131072},(_,i)=>i*17&255);
function fixture(options={}){
    const events=[],map=new Map();let serial=0,quota=false,readFailure=false;
    const storage={setItem(key,value){events.push('write');if(quota)throw Error('QuotaExceededError');map.set(key,value);},
        getItem(key){events.push('read');if(readFailure)throw Error('SecurityError');return map.get(key)??null;}};
    const store=createPresentedSaveStore({storage,key:'private-unit',epoch:1,...options});
    const frame=(bytes=raw(),revision=1,epoch=1)=>({ready:true,frameId:++serial,saveEpoch:epoch,counter:100+serial,
        flash:{available:true,saveEpoch:epoch,counter:100+serial,rawRevision:revision,size:bytes.length,sha256:sha(bytes),bytes}});
    const callbacks={acknowledge:async id=>{events.push('ack');return {...id,receiptAcknowledged:true,storageVerified:false};},
        draw:()=>{events.push('draw');}};
    return {store,frame,callbacks,events,map,quota:()=>{quota=true;},readFailure:(value=true)=>{readFailure=value;}};
}
test('all raw bytes round-trip and write/read/ACK precede synchronous canvas submission',async()=>{
    const f=fixture(),bytes=raw();assert.deepEqual(decodeRaw(encodeRaw(bytes)),bytes);
    const result=await f.store.present(f.frame(bytes),f.callbacks);
    assert.deepEqual(f.events,['write','read','ack','draw']);assert.equal(result.storageReadbackVerified,true);
    assert.deepEqual(decodeRaw(f.map.get('private-unit')),bytes);assert.equal(result.physicalPaintProven,false);
    const cached=f.store.cachedPresented();cached.bytes[120000]^=1;
    assert.deepEqual(f.store.cachedPresented().bytes,bytes);assert.equal(f.store.snapshot().writeSerial,1);
});
test('unchanged payload omissions reuse verified bytes; unused-byte changes still write',async()=>{
    const f=fixture(),bytes=raw();await f.store.present(f.frame(bytes),f.callbacks);f.events.length=0;
    const unchanged=f.frame(bytes);delete unchanged.flash.bytes;
    const reused=await f.store.present(unchanged,f.callbacks);
    assert.deepEqual(f.events,['ack','draw']);assert.equal(reused.writeSerial,1);assert.equal(reused.wrote,false);
    const changed=bytes.slice();changed[120000]^=7;f.events.length=0;
    const next=await f.store.present(f.frame(changed,2),f.callbacks);
    assert.deepEqual(f.events,['write','read','ack','draw']);assert.equal(next.writeSerial,2);
    assert.deepEqual(decodeRaw(f.map.get('private-unit')),changed);
});
test('quota failure preserves previous bytes and does not ACK or draw the failed frame',async()=>{
    const f=fixture();await f.store.present(f.frame(),f.callbacks);const old=f.map.get('private-unit');
    f.events.length=0;f.quota();const changed=raw();changed[80000]^=1;
    await assert.rejects(f.store.present(f.frame(changed,2),f.callbacks),/Quota/);
    assert.deepEqual(f.events,['write']);assert.equal(f.map.get('private-unit'),old);
    assert.equal(f.store.snapshot().drawCount,1);assert.deepEqual(f.store.cachedPresented().bytes,raw());
});
test('readback failure is explicit and never claims a rollback or successful presentation',async()=>{
    const f=fixture();f.readFailure();await assert.rejects(f.store.present(f.frame(),f.callbacks),/Security/);
    assert.deepEqual(f.events,['write','read']);assert.equal(f.store.cachedPresented(),null);
    assert.equal(f.store.snapshot().drawCount,0);
});
test('uncertain readback after an earlier success revokes omitted-payload ownership',async()=>{
    const f=fixture(),a=raw(),b=a.slice();b[120000]^=1;
    await f.store.present(f.frame(a),f.callbacks);f.readFailure();
    await assert.rejects(f.store.present(f.frame(b,2),f.callbacks),/Security/);
    assert.deepEqual(f.store.known(),{});assert.deepEqual(f.store.cachedPresented().bytes,a);
    f.readFailure(false);const stale=f.frame(a);delete stale.flash.bytes;
    await assert.rejects(f.store.present(stale,f.callbacks),/Omitted/);
    assert.deepEqual(decodeRaw(f.map.get('private-unit')),b);assert.equal(f.store.snapshot().drawCount,1);
    await f.store.present(f.frame(b,2),f.callbacks);assert.deepEqual(f.store.cachedPresented().bytes,b);
});
test('hash, counter, omitted payload and false worker storage attestations are rejected',async()=>{
    for(const change of [p=>p.flash.bytes[10]^=1,p=>p.flash.counter++,p=>{delete p.flash.bytes;},p=>p.flash.size--]){
        const f=fixture(),packet=f.frame();change(packet);
        await assert.rejects(f.store.present(packet,f.callbacks));assert.deepEqual(f.events,[]);
    }
    const f=fixture();await assert.rejects(f.store.present(f.frame(),{...f.callbacks,
        acknowledge:async id=>({...id,receiptAcknowledged:true,storageVerified:true})}),/falsely/);
    assert.equal(f.events.includes('draw'),false);
});
test('epoch fences reject delayed hashing before any write and allow a fresh generation',async()=>{
    let release,hold=true;const f=fixture({hash:bytes=>hold?new Promise(resolve=>{release=()=>resolve(sha(bytes));}):Promise.resolve(sha(bytes))});
    const old=f.store.present(f.frame(),f.callbacks);await Promise.resolve();
    f.store.fence(2);hold=false;
    await f.store.present(f.frame(raw(),1,2),f.callbacks);const successful=f.map.get('private-unit');
    release();await assert.rejects(old,/Stale/);
    assert.equal(f.map.get('private-unit'),successful);assert.equal(f.store.cachedPresented().saveEpoch,2);
    assert.equal(f.store.snapshot().lastFailure,null);
});
test('a reset during ACK cannot draw old pixels or clear a newer in-flight presentation',async()=>{
    const f=fixture();let release;
    const old=f.store.present(f.frame(),{...f.callbacks,acknowledge:id=>new Promise(resolve=>{
        release=()=>resolve({...id,receiptAcknowledged:true,storageVerified:false});})});
    while(!release)await new Promise(resolve=>setImmediate(resolve));
    f.store.fence(2);await f.store.present(f.frame(raw(),1,2),f.callbacks);
    const last=f.store.cachedPresented();release();await assert.rejects(old,/Stale/);
    assert.equal(f.store.cachedPresented().frameId,last.frameId);assert.equal(f.events.filter(x=>x==='draw').length,1);
});
test('one presentation per generation and a new epoch require explicit full data ownership',async()=>{
    const f=fixture();const packet=f.frame();await f.store.present(packet,f.callbacks);
    await assert.rejects(f.store.present(packet,f.callbacks),/replayed/);
    f.store.fence(2);const missing=f.frame(raw(),1,2);delete missing.flash.bytes;
    await assert.rejects(f.store.present(missing,f.callbacks),/Omitted/);
    const pending=f.store.present(f.frame(raw(),1,2),f.callbacks);
    await assert.rejects(f.store.present(f.frame(raw(),1,2),f.callbacks),/One save/);
    await pending;
});

test('caller metadata mutation during hashing cannot rewrite the acknowledged frame identity',async()=>{
    let release;const f=fixture({hash:bytes=>new Promise(resolve=>{release=()=>resolve(sha(bytes));})});
    const packet=f.frame(),original=packet.frameId;let acknowledged,drawn;
    const pending=f.store.present(packet,{acknowledge:async id=>{acknowledged=id;return {...id,receiptAcknowledged:true,storageVerified:false};},draw:frame=>{drawn=frame.frameId;}});
    packet.frameId=999;packet.counter=999;packet.flash.counter=999;packet.flash.sha256='0'.repeat(64);
    release();const result=await pending;
    assert.equal(acknowledged.frameId,original);assert.equal(drawn,original);assert.equal(result.frameId,original);
});
test('trusted synchronous draw callback cannot reenter an epoch reset',async()=>{
    const f=fixture();await assert.rejects(f.store.present(f.frame(),{...f.callbacks,draw:()=>f.store.fence(2)}),/reenter/);
    assert.equal(f.store.snapshot().expectedEpoch,1);assert.equal(f.store.cachedPresented(),null);
});
