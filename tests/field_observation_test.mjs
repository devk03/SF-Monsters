import assert from 'node:assert/strict';
import test from 'node:test';
import {createFieldObservation} from '../scripts/quality/field_observation.mjs';

function fixture(){
    let time=10;
    const observer=createFieldObservation(()=>time);
    return {observer,time(value){time=value;}};
}

test('mapped synthetic replay and trusted input remain distinguishable',()=>{
    const {observer,time}=fixture();observer.start();
    observer.keyboard({type:'keydown',code:'ArrowRight',isTrusted:false});
    time(14);observer.keyboard({type:'keydown',code:'ArrowRight',isTrusted:true,repeat:true});
    time(16);observer.keyboard({type:'keyup',code:'ArrowRight',isTrusted:false});
    const report=observer.stop(10,20);
    assert.deepEqual(report.events,[
        {type:'keydown',atMs:10,code:'ArrowRight',trusted:false,repeat:false},
        {type:'keydown',atMs:14,code:'ArrowRight',trusted:true,repeat:true},
        {type:'keyup',atMs:16,code:'ArrowRight',trusted:false,repeat:false}]);
    assert.deepEqual(report.counts,{keydown:2,keyup:1});
    assert.match(report.scope,/Not SDK mask transitions/);
});

test('unmapped typing and inactive input are never collected',()=>{
    const {observer}=fixture();
    observer.keyboard({type:'keydown',code:'ArrowRight'});
    observer.start();
    for(const event of [{type:'keydown',code:'KeyP'},{type:'paste',code:'KeyX'},
            {type:'input',data:'private text'}])observer.keyboard(event);
    assert.deepEqual(observer.stop(10,20).events,[]);
});

test('window blurs and long tasks retain time without claiming causation',()=>{
    const {observer,time}=fixture();observer.start();
    time(12);observer.focus('blur');
    time(15);observer.focus('focus');observer.focus('click');
    observer.longTask({startTime:13,duration:358.4});
    for(const invalid of [{startTime:9,duration:60},{startTime:NaN,duration:1},
            {startTime:13,duration:-1}])observer.longTask(invalid);
    const report=observer.stop(10,400);
    assert.deepEqual(report.counts,{blur:1,focus:1,longtask:1});
    assert.equal(report.events[2].durationMs,358.4);
    assert.match(report.scope,/causal proof/);
});

test('only events inside the exact diagnostic clock interval are retained',()=>{
    const {observer,time}=fixture();observer.start();
    time(11);observer.focus('blur');time(20);observer.focus('focus');
    time(30);observer.focus('blur');
    assert.deepEqual(observer.stop(15,25).events,[{type:'focus',atMs:20}]);
    assert.throws(()=>observer.stop(15,25));
});

test('overflow is explicit and a new measurement cannot inherit old events',()=>{
    const {observer}=fixture();observer.start();
    for(let i=0;i<2100;++i)observer.focus('blur');
    const report=observer.stop(10,20);
    assert.equal(report.events.length,2048);assert.equal(report.droppedEvents,52);
    assert.equal(report.counts.blur,2048);
    observer.start();assert.deepEqual(observer.stop(10,20).events,[]);
});

test('failed and overlapping measurements cannot silently share observations',()=>{
    const {observer}=fixture();observer.start();assert.throws(()=>observer.start());
    assert.throws(()=>observer.stop(20,10));observer.cancel();
    observer.start();assert.deepEqual(observer.stop(10,20).events,[]);
});
