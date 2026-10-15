// Pure fake-core protocol tests: no WASM, emulator, browser, audio device or timer monitor.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { webcrypto, createHash } from 'node:crypto';
import assert from 'node:assert/strict';
const source = readFileSync(new URL('../scripts/quality/experiments/worker-core.js', import.meta.url), 'utf8');
const sha = value => createHash('sha256').update(value).digest('hex');
function fixture() {
  let clock = 0, serial = 0, timerSerial = 0, counter = 0, pc = 0, initialized = false, bump = false;
  let corruptNextRestore = false, failNextState = false, holdNextHash = false, failNextHash = false, releaseHash = null;
  const heap = new Uint8Array(8 * 1024 * 1024); heap.fill(0xAA);
  let alloc = 1024 * 1024; const flash = new Uint8Array(131072), timers = new Map(), pending = new Map();
  const canonicalScratch = [], audioMessages = [], lifecycle = []; let audioFrames = 0, loads = 0;
  const mod = {
    HEAPU8: heap, HEAP16: new Int16Array(heap.buffer),
    _malloc(size) { const ptr = alloc; alloc += (size + 7) & ~7; assert.ok(alloc < heap.length); return ptr; }, _free() {},
    _mgbawasm_init() {}, _mgbawasm_set_log_level() {}, _mgbawasm_set_idle_optimization() {}, _mgbawasm_set_allow_opposing_directions() {},
    _mgbawasm_load() { loads++; counter = pc = 0; initialized = false; flash.fill(255); return 1; },
    _mgbawasm_run_frame() { counter = (counter + 1) >>> 0; initialized = true; pc++; audioFrames += 128;
      heap[1024] = counter & 255; if (bump) flash[90000] ^= 1; },
    _mgbawasm_frame_counter: () => counter,
    _mgbawasm_framerate_micro: () => 60000000, _mgbawasm_sample_rate: () => 65536,
    _mgbawasm_video_width: () => 240, _mgbawasm_video_height: () => 160, _mgbawasm_video_ptr: () => 1024,
    _mgbawasm_read_audio(ptr, max) { const n = Math.min(max, audioFrames); audioFrames -= n; return n; },
    _mgbawasm_sram_save() { if (!initialized) return 0; heap.set(flash, 512 * 1024); return flash.length; },
    _mgbawasm_sram_ptr: () => 512 * 1024,
    _mgbawasm_sram_load(ptr, size) { assert.equal(size, flash.length); flash.set(heap.subarray(ptr, ptr + size));
      if (corruptNextRestore) { flash[50000] ^= 1; corruptNextRestore = false; } return 1; },
    _mgbawasm_state_size: () => 64,
    _mgbawasm_state_save(ptr) { canonicalScratch.push(heap.slice(ptr, ptr + 64).every(v => v === 0));
      const data = new DataView(heap.buffer); data.setUint32(ptr, counter, true); data.setUint32(ptr + 4, pc, true); return 1; },
    _mgbawasm_state_load(ptr) { if (failNextState) { failNextState = false; return 0; }
      const data = new DataView(heap.buffer); counter = data.getUint32(ptr, true); pc = data.getUint32(ptr + 4, true); return 1; },
    _mgbawasm_reset() { counter = pc = 0; }, _mgbawasm_set_keys(mask) { lifecycle.push({ mask, counter }); }, _mgbawasm_unload() {},
  };
  let context;
  const port = { onmessage: null, start() {}, close() {}, postMessage(value, transfer = []) {
    const data = structuredClone(value, { transfer }); audioMessages.push(data);
    if (data?.type === 'playback-reset') queueMicrotask(() => port.onmessage({ data }));
    if (data?.type === 'diagnostics' && data.enabled === false) queueMicrotask(() => port.onmessage({ data: {
      type: 'diagnostics', epoch: data.epoch, final: true, syntheticFakePort: true } }));
  } };
  const globals = { Uint8Array, Uint8ClampedArray, Int16Array, ArrayBuffer, DataView, URL, Promise, console,
    performance: { now: () => clock, timeOrigin: 1700000000000 },
    setTimeout(fn, delay) { const id = ++timerSerial; timers.set(id, { fn, at: clock + delay }); return id; },
    clearTimeout(id) { timers.delete(id); },
    crypto: { subtle: { digest(algorithm, data) {
      if (failNextHash) { failNextHash = false; return Promise.reject(Error('Injected hash failure')); }
      const result = webcrypto.subtle.digest(algorithm, data);
      if (!holdNextHash) return result;
      holdNextHash = false; return new Promise(resolve => { releaseHash = () => result.then(resolve); });
    } } },
    importScripts() { context.createMgbaModule = async () => mod; },
    postMessage(value, transfer = []) {
      const message = structuredClone(value, { transfer });
      const entry = pending.get(message.id);
      if (!entry) throw Error('Unexpected fake Worker message: ' + JSON.stringify(message));
      pending.delete(message.id); message.ok ? entry.resolve(message.result) : entry.reject(Error(message.error));
    }, close() {},
  };
  globals.self = globals; context = vm.createContext(globals); vm.runInContext(source, context);
  const rpc = (op, data = {}) => new Promise((resolve, reject) => {
    const id = ++serial; pending.set(id, { resolve, reject }); context.onmessage({ data: { id, op, ...data } });
  });
  const advance = async duration => {
    const target = clock + duration;
    for (let n = 0; n < 10000; ++n) {
      const next = [...timers].filter(([, value]) => value.at <= target).sort((a, b) => a[1].at - b[1].at)[0];
      if (!next) break; timers.delete(next[0]); clock = Math.max(clock, next[1].at); next[1].fn();
    }
    clock = Math.max(clock, target); await Promise.resolve(); await Promise.resolve();
  };
  const battery = Uint8Array.from({ length: 131072 }, (_, i) => i * 17 & 255);
  const state = new Uint8Array(64); new DataView(state.buffer).setUint32(0, 42, true);
  const boot = () => rpc('boot', { rom: new Uint8Array([127]), battery: battery.slice(), state: state.slice(),
    audioPort: port, jsUrl: 'https://invalid.local/unchanged-core.js', wasmUrl: 'https://invalid.local/unchanged-core.wasm' });
  return { rpc, advance, boot, battery, state, flash, canonicalScratch, audioMessages, lifecycle,
    elapseWithoutTimers: duration => { clock += duration; },
    changeFlash: () => { bump = true; }, corruptRestore: () => { corruptNextRestore = true; },
    failState: () => { failNextState = true; }, holdHash: () => { holdNextHash = true; },
    releaseHash: () => { assert.ok(releaseHash); releaseHash(); }, failHash: () => { failNextHash = true; },
    get loads() { return loads; } };
}
let passed = 0;
async function test(name, run) { await run(); passed++; console.log('PASS ' + name); }
await test('canonical paused exports preserve all raw bytes and never expose internal cache ownership', async () => {
  const f = fixture(); const boot = await f.boot(); assert.equal(boot.saveEpoch, 1);
  const a = await f.rpc('export-state'), b = await f.rpc('export-state');
  assert.deepEqual(a.state, b.state); assert.ok(a.state.subarray(8).every(v => v === 0));
  assert.ok(f.canonicalScratch.every(Boolean)); assert.deepEqual(a.flash.bytes, f.battery);
  assert.equal(a.flash.sha256, sha(f.battery)); a.flash.bytes[90000] ^= 1;
  assert.deepEqual((await f.rpc('export-battery')).bytes, f.battery);
  assert.equal(a.counter, a.flash.counter); await f.rpc('destroy');
});
await test('raw revision sees incomplete-slot changes without a completed-save counter change', async () => {
  const f = fixture(); await f.boot(); const initial = await f.rpc('export-battery'); f.changeFlash();
  await f.rpc('start', { durationMs: 100 }); await f.advance(20);
  const frame = await f.rpc('video', { knownEpoch: initial.saveEpoch, knownRevision: initial.rawRevision });
  assert.equal(frame.ready, true); assert.ok(frame.flash.rawRevision > initial.rawRevision);
  assert.equal(frame.flash.bytes[0], initial.bytes[0]); assert.notEqual(frame.flash.bytes[90000], initial.bytes[90000]);
  assert.equal(frame.counter, frame.flash.counter); assert.equal(frame.rgba[0], frame.counter & 255);
  assert.equal(frame.flash.sha256, sha(frame.flash.bytes));
  await assert.rejects(f.rpc('video'), /Recycle/);
  await assert.rejects(f.rpc('export-battery'), /Pause/);
  const ack = await f.rpc('ack-flash', { frameId: frame.frameId, saveEpoch: frame.saveEpoch, rawRevision: frame.flash.rawRevision });
  assert.equal(ack.storageVerified, false);
  await f.rpc('recycle', { frameId: frame.frameId, saveEpoch: frame.saveEpoch, pixels: frame.rgba.buffer });
  const unchanged = await f.rpc('video', { knownEpoch: frame.saveEpoch, knownRevision: frame.flash.rawRevision });
  assert.equal(unchanged.flash.bytes, undefined); assert.equal(unchanged.flash.sha256, frame.flash.sha256);
  await f.rpc('pause'); const latest = await f.rpc('export-battery'); assert.deepEqual(latest.bytes, f.flash);
  await f.rpc('destroy');
});
await test('reset epochs fence delayed video/recycle/ack and stale RGBA is never presented', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 500 }); await f.advance(20);
  f.holdHash(); const oldPromise = f.rpc('video'); await f.rpc('pause');
  const loaded = await f.rpc('load-state', { state: f.state.slice(), battery: f.battery.slice() });
  assert.ok(loaded.saveEpoch > 1); assert.equal(loaded.running, false); assert.equal(loaded.videoFrameReady, false);
  assert.equal((await f.rpc('video')).ready, false);
  f.releaseHash(); const old = await oldPromise; assert.notEqual(old.saveEpoch, loaded.saveEpoch);
  await assert.rejects(f.rpc('ack-flash', { frameId: old.frameId, saveEpoch: old.saveEpoch, rawRevision: old.flash.rawRevision }), /Stale/);
  await f.rpc('resume', { durationMs: 100 }); await f.advance(20); const fresh = await f.rpc('video');
  const stale = await f.rpc('recycle', { frameId: old.frameId, saveEpoch: old.saveEpoch, pixels: old.rgba.buffer });
  assert.equal(stale.ignored, true); await assert.rejects(f.rpc('video'), /Recycle/);
  await assert.rejects(f.rpc('recycle', { frameId: fresh.frameId, saveEpoch: fresh.saveEpoch, pixels: new ArrayBuffer(0) }), /Invalid/);
  await f.rpc('recycle', { frameId: fresh.frameId, saveEpoch: fresh.saveEpoch, pixels: fresh.rgba.buffer });
  await f.rpc('destroy');
});
await test('raw import reboots retained ROM and round-trips exact bytes, failure rolls back and stays paused', async () => {
  const f = fixture(); await f.boot(); const changed = f.battery.slice(); changed[110000] ^= 255;
  const imported = await f.rpc('import-battery', { bytes: changed });
  assert.equal(imported.running, false); assert.equal(imported.batteryVerified, true); assert.ok(f.loads >= 2);
  assert.deepEqual(imported.flash.bytes, changed); const before = await f.rpc('export-state');
  f.corruptRestore(); await assert.rejects(f.rpc('import-battery', { bytes: f.battery.slice() }), /round-trip/);
  const after = await f.rpc('export-state'); assert.deepEqual(after.flash.bytes, before.flash.bytes);
  assert.deepEqual(after.state, before.state); assert.ok(after.saveEpoch > before.saveEpoch);
  assert.equal((await f.rpc('snapshot')).running, false); await f.rpc('destroy');
});
await test('canonical state load failure rolls back full Flash and native state without implicit resume', async () => {
  const f = fixture(); await f.boot(); const before = await f.rpc('export-state');
  f.failState(); await assert.rejects(f.rpc('load-state', { state: f.state.slice() }), /Native state load/);
  const after = await f.rpc('export-state'); assert.deepEqual(after.state, before.state); assert.deepEqual(after.flash.bytes, before.flash.bytes);
  await assert.rejects(f.rpc('load-state', { state: new Uint8Array(63) }), /State size/);
  await assert.rejects(f.rpc('import-battery', { bytes: new Uint8Array(32769) }), /Unsupported/);
  await f.rpc('destroy');
});
await test('finite watchdog and diagnostic reset facts stay explicit with the bridge', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 50 });
  const diagnostic = f.rpc('begin', { durationMs: 40 }); await f.advance(20); await f.rpc('pause');
  const report = await diagnostic; assert.equal(report.reason, 'pause'); assert.equal(report.saveEpoch, 1);
  assert.ok((await f.rpc('snapshot')).lifecycleFacts.some(value => value.reason === 'pause'));
  await f.rpc('resume', { durationMs: 25 }); await f.advance(26);
  const stopped = await f.rpc('snapshot'); assert.equal(stopped.running, false);
  assert.ok(stopped.lifecycleFacts.some(value => value.reason === 'run-duration'));
  await f.rpc('destroy');
});
await test('failed hashing releases only its own frame slot and never attests storage', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 100 }); await f.advance(20);
  f.failHash(); await assert.rejects(f.rpc('video'), /Injected hash/);
  const frame = await f.rpc('video'); assert.equal(frame.flash.sha256, sha(frame.flash.bytes));
  await assert.rejects(f.rpc('ack-flash', { frameId: frame.frameId, saveEpoch: frame.saveEpoch, rawRevision: frame.flash.rawRevision + 1 }), /Stale/);
  await f.rpc('pause'); const loaded = await f.rpc('load-state', { state: f.state.slice() });
  await assert.rejects(f.rpc('input', { sequence: 99, mask: 1, saveEpoch: frame.saveEpoch }), /Stale input/);
  assert.equal((await f.rpc('snapshot')).saveEpoch, loaded.saveEpoch); await f.rpc('destroy');
});
await test('a metadata hash failure after native import rolls back before reporting failure', async () => {
  const f = fixture(); await f.boot(); const before = await f.rpc('export-state');
  const changed = f.battery.slice(); changed[120000] ^= 1; f.failHash();
  await assert.rejects(f.rpc('import-battery', { bytes: changed }), /Injected hash/);
  const after = await f.rpc('export-state');
  assert.deepEqual(after.state, before.state); assert.deepEqual(after.flash.bytes, before.flash.bytes);
  assert.ok(after.saveEpoch > before.saveEpoch); assert.equal((await f.rpc('snapshot')).running, false);
  await f.rpc('destroy');
});
await test('60Hz pause at10ms retains the6.667ms deadline through1000ms suspension', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 5000 }); await f.advance(10);
  const paused = await f.rpc('pause');
  assert.ok(Math.abs(paused.pausedPhase.nextDueInMs - 1000 / 60 + 10) < 1e-9);
  assert.ok(Math.abs(paused.fractionalFrame - .6) < 1e-12); assert.equal(paused.abandonedFrames, 0);
  await f.advance(1000); const idle = await f.rpc('snapshot'); assert.equal(idle.counter, paused.counter);
  const resumed = await f.rpc('resume', { durationMs: 5000 });
  assert.equal(resumed.clockOriginMs, 1000); assert.equal(resumed.runDeadlineMs, 5000);
  await f.advance(6.6); assert.equal((await f.rpc('snapshot')).counter, paused.counter);
  // Fixed5ms polling adds <=5ms slack to the6.667ms retained deadline.
  await f.advance(4); assert.equal((await f.rpc('snapshot')).counter, paused.counter + 1);
  await f.rpc('destroy');
});
await test('earned credits between last tick and pause are executed once after resume', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 5000 }); await f.advance(5);
  f.elapseWithoutTimers(50); const paused = await f.rpc('pause');
  assert.equal(paused.earnedUnplannedFrames, 3); assert.equal(paused.due, 0); assert.equal(paused.retainedBacklog, 0);
  await f.advance(1000); assert.equal((await f.rpc('snapshot')).counter, paused.counter);
  await f.rpc('resume'); await f.advance(0);
  const resumed = await f.rpc('snapshot'); assert.equal(resumed.counter, paused.counter + 3);
  assert.equal(resumed.due, 3); assert.equal(resumed.executed, 3); assert.equal(resumed.overflowDropped, 0);
  await f.advance(5); assert.equal((await f.rpc('snapshot')).counter, paused.counter + 3);
  await f.rpc('destroy');
});
await test('three already planned debt frames survive a readonly pause without abandonment', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 5000 });
  f.elapseWithoutTimers(140); await f.advance(0); const before = await f.rpc('snapshot');
  assert.equal(before.due, 8); assert.equal(before.executed, 5); assert.equal(before.backlog, 3);
  const paused = await f.rpc('pause'); assert.equal(paused.retainedBacklog, 3); assert.equal(paused.abandonedFrames, 0);
  await f.advance(1000); await f.rpc('resume'); await f.advance(0);
  const after = await f.rpc('snapshot'); assert.equal(after.counter, before.counter + 3);
  assert.equal(after.due, 8); assert.equal(after.executed, 8); assert.equal(after.backlog, 0);
  await f.rpc('destroy');
});
await test('repeated pause is idempotent and readonly state/Flash exports preserve frozen phase', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 10000 }); await f.advance(10);
  const first = await f.rpc('pause'); await f.advance(500); const repeated = await f.rpc('pause');
  assert.equal(repeated.alreadyPaused, true); assert.equal(repeated.pausedAtMs, first.pausedAtMs);
  assert.equal(repeated.lifecycleFacts.length, first.lifecycleFacts.length);
  await f.rpc('export-state'); await f.rpc('export-battery'); await f.advance(500);
  const before = await f.rpc('snapshot'); assert.deepEqual(before.pausedPhase, first.pausedPhase); assert.equal(before.counter, first.counter);
  await f.rpc('resume'); const after = await f.rpc('snapshot'); assert.equal(after.clockOriginMs, 1000);
  await f.rpc('destroy');
});
await test('state reset explicitly discards prior debt/fraction and starts a fresh pacing phase', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 5000 });
  f.elapseWithoutTimers(140); await f.advance(0); await f.rpc('pause'); await f.advance(1000);
  const loaded = await f.rpc('load-state', { state: f.state.slice() });
  assert.equal(loaded.clockOriginMs, null); assert.equal(loaded.pausedAtMs, null);
  assert.equal(loaded.due, 0); assert.equal(loaded.backlog, 0);
  const reset = loaded.lifecycleFacts.find(value => value.reason === 'load-state');
  assert.equal(reset.abandonedBacklog, 3); assert.equal(reset.abandonedFrames, 3);
  assert.ok(Math.abs(reset.discardedFractionalFrame - .4) < 1e-12);
  assert.ok(reset.playbackReset.nextEpoch > reset.playbackReset.previousEpoch);
  await f.rpc('resume'); await f.advance(10); assert.equal((await f.rpc('snapshot')).counter, loaded.counter);
  await f.advance(10); assert.equal((await f.rpc('snapshot')).counter, loaded.counter + 1);
  await f.rpc('destroy');
});
await test('twenty fractional pauses preserve global credits and cannot extend the original wall lease', async () => {
  const f = fixture(); await f.boot(); const initial = await f.rpc('start', { durationMs: 10000 });
  for (let i = 0; i < 20; ++i) {
    await f.advance(10); const pause = await f.rpc('pause'); const counter = pause.counter;
    await f.advance(100); assert.equal((await f.rpc('snapshot')).counter, counter);
    await f.rpc('resume', { durationMs: 10000 });
  }
  const end = await f.rpc('snapshot'); assert.equal(end.runDeadlineMs, initial.runDeadlineMs);
  assert.equal(end.due, end.executed + end.overflowDropped + end.backlog);
  assert.equal(end.overflowDropped, 0); assert.equal(end.lifecycleFactOverflow, false);
  //200ms active time has earned12 credits; up to one is still unplanned at RPC.
  await f.advance(0); assert.equal((await f.rpc('snapshot')).executed, 12);
  await f.rpc('pause'); await f.advance(10000);
  assert.equal((await f.rpc('snapshot')).runExpired, true);
  await assert.rejects(f.rpc('resume', { durationMs: 10000 }), /lease expired/);
  await f.rpc('export-battery'); await f.rpc('destroy');
});
await test('binary64 frame-boundary credits cannot regress after a large fractional origin shift', async () => {
  const f = fixture(); await f.boot(); await f.rpc('start', { durationMs: 10000 });
  f.elapseWithoutTimers(1000 / 60); await f.advance(0);
  const before = await f.rpc('snapshot'); assert.equal(before.due, 1); assert.equal(before.executed, 1);
  const paused = await f.rpc('pause'); await f.advance(1000.1); await f.rpc('resume'); await f.advance(0);
  const after = await f.rpc('snapshot'); assert.equal(after.counter, paused.counter);
  assert.equal(after.due, 1); assert.equal(after.executed, 1); assert.equal(after.running, true);
  assert.equal(after.phaseAnchorElapsedMs, paused.pausedPhase.elapsedMs);
  await f.rpc('destroy');
});
await test('readonly audio watch spans pauses but excludes state mutation and other diagnostics',async()=>{
  const f=fixture();await f.boot();await f.rpc('start',{durationMs:1000});
  const opened=await f.rpc('audio-watch-start',{durationMs:500});
  await assert.rejects(f.rpc('begin',{durationMs:10}),/diagnostic window/);
  await assert.rejects(f.rpc('audio-watch-start'),/exclusive/);
  await f.advance(20);const paused=await f.rpc('pause');await f.rpc('export-battery');
  await assert.rejects(f.rpc('load-state',{state:f.state}),/readonly audio watch/);
  await f.advance(100);assert.equal((await f.rpc('snapshot')).counter,paused.counter);
  await f.rpc('resume');await f.advance(20);const report=await f.rpc('audio-watch-end');
  assert.equal(report.epoch,opened.epoch);assert.equal(report.reason,'manual');assert.equal(report.finalAcknowledged,true);
  assert.equal(report.initial.saveEpoch,report.final.saveEpoch);assert.equal(report.final.playbackEpoch,report.initial.playbackEpoch);
  await f.rpc('destroy');
});
await test('audio watch has a finite expiry and destroy does not leave diagnostics active',async()=>{
  const f=fixture();await f.boot();await f.rpc('start',{durationMs:1000});
  await assert.rejects(f.rpc('audio-watch-start',{durationMs:60001}),/duration/);
  await f.rpc('audio-watch-start',{durationMs:50});await f.advance(60);
  await assert.rejects(f.rpc('audio-watch-end'),/No active/);
  await f.rpc('audio-watch-start',{durationMs:100});await f.rpc('destroy');
  assert.equal(f.audioMessages.filter(m=>m?.type==='diagnostics'&&m.enabled===false).length,2);
});
console.log(JSON.stringify({ passed, kind: 'pure-fakecore-phase-and-save-protocol', nativeEmulation: false }));
