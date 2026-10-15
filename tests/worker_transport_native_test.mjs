// Finite Node transport unit using the unchanged native core and actual checkpoint.
// No AudioContext/worklet clock is emulated; the sink only counts transferred PCM.
import { Worker, MessageChannel, parentPort, workerData } from 'node:worker_threads';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { createHash, randomUUID } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { crc32 } from '../web/app/bps.ts';
const root = fileURLToPath(new URL('../', import.meta.url));
if (workerData?.role === 'core') {
  globalThis.self = globalThis;
  globalThis.require = createRequire(import.meta.url);
  globalThis.importScripts = url => {
    const path = url.startsWith('file:') ? fileURLToPath(url) : url;
    globalThis.__filename = path;
    globalThis.__dirname = path.slice(0, path.lastIndexOf('/'));
    vm.runInThisContext(readFileSync(path, 'utf8'), { filename: path });
  };
  globalThis.postMessage = (value, transfer) => parentPort.postMessage(value, transfer);
  globalThis.close = () => parentPort.close();
  vm.runInThisContext(readFileSync(root + 'scripts/quality/experiments/worker-core.js', 'utf8'));
  parentPort.on('message', value => globalThis.onmessage({ data: value }));
} else if (workerData?.role === 'sink') {
  const rows = []; let rate = 0;
  workerData.port.on('message', data => {
    if (data?.rate) rate = data.rate;
    else if (data instanceof Int16Array) rows.push({ at: performance.timeOrigin + performance.now(), frames: data.length / 2, rate });
  });
  parentPort.on('message', message => {
    if (message === 'snapshot') parentPort.postMessage({ rows });
    if (message === 'destroy') { workerData.port.close(); parentPort.close(); }
  });
} else {
  const channel = new MessageChannel();
  const core = new Worker(new URL(import.meta.url), { workerData: { role: 'core' } });
  const sink = new Worker(new URL(import.meta.url), { workerData: { role: 'sink', port: channel.port2 }, transferList: [channel.port2] });
  const pending = new Map(); let id = 0;
  core.on('message', message => {
    const entry = pending.get(message.id);
    if (entry) { pending.delete(message.id); message.ok ? entry.resolve(message.result) : entry.reject(Error(message.error)); }
  });
  const rpc = (op, data = {}, transfer = []) => new Promise((resolve, reject) => {
    const request = ++id; pending.set(request, { resolve, reject }); core.postMessage({ id: request, op, ...data }, transfer);
  });
  const sinkSnapshot = () => new Promise(resolve => { sink.once('message', resolve); sink.postMessage('snapshot'); });
  const watchdog = setTimeout(() => { core.terminate(); sink.terminate(); throw Error('Finite transport unit exceeded10seconds'); }, 10000);
  try {
    const [romPath,statePath,requestedOutput]=process.argv.slice(2);
    if(!romPath||!statePath?.endsWith('.state'))throw Error('Pass ROM.gba and controller-only capture.state paths');
    const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
    const rom=new Uint8Array(readFileSync(romPath)),state=new Uint8Array(readFileSync(statePath));
    const battery=new Uint8Array(readFileSync(statePath.replace(/\.state$/,'.sav')));
    const metadata=JSON.parse(readFileSync(statePath.replace(/\.state$/,'.json'),'utf8'));
    const build=JSON.parse(readFileSync(root+'web/public/emulator/core-build.json','utf8'));
    assert.equal(metadata.controller_only,true);assert.equal(metadata.rom_sha256,sha(rom));
    assert.equal(metadata.mgba_revision,build.mgba_revision);assert.equal(build.mgba_revision,'26b7884bc25a5933960f3cdcd98bac1ae14d42e2');
    assert.equal(rom.length,16777216);assert.equal(state.length,0x61000);assert.equal(battery.length,131072);
    const header=new DataView(state.buffer,state.byteOffset,state.byteLength);
    assert.equal(header.getUint32(0,true),0x01000007);assert.equal(header.getUint32(8,true),crc32(rom));
    assert.deepEqual(state.subarray(16,32),rom.subarray(0xa0,0xb0));
    for(const name of ['mgba.js','mgba.wasm'])assert.equal(sha(readFileSync(root+'web/public/emulator/'+name)),build.artifacts[name]);
    const output=resolve(requestedOutput??root+'.tools/benchmarks/worker-native-'+randomUUID()+'.json');
    if(!output.startsWith(root+'.tools/'))throw Error('Keep private transport receipts under .tools');
    const boot = await rpc('boot', { rom,battery,state,
      audioPort: channel.port1, jsUrl: pathToFileURL(root + 'web/public/emulator/mgba.js').href,
      wasmUrl: root + 'web/public/emulator/mgba.wasm' }, [channel.port1]);
    assert.equal(boot.batteryVerified, true);
    await rpc('start', { durationMs: 2000 });
    await new Promise(resolve => setTimeout(resolve, 200));
    const before = await rpc('snapshot');
    const stallStart = performance.timeOrigin + performance.now();
    while (performance.timeOrigin + performance.now() - stallStart < 200) { /* Deliberate finite main-thread stall. */ }
    const stallEnd = performance.timeOrigin + performance.now();
    const after = await rpc('snapshot'); const received = await sinkSnapshot();
    const progress = (after.counter - before.counter) >>> 0;
    const sourceDuringStall = received.rows.filter(row => row.at >= stallStart && row.at <= stallEnd).reduce((n, row) => n + row.frames, 0);
    assert.ok(progress >= 8 && progress <= 20, 'Native Worker did not independently progress across main stall');
    assert.ok(sourceDuringStall > 0, 'Transferred PCM did not reach the independent sink during main stall');
    const frame = await rpc('video'); assert.equal(frame.rgba.length, 240 * 160 * 4);
    await assert.rejects(rpc('video'), /Recycle/);
    await rpc('recycle', { pixels: frame.rgba.buffer }, [frame.rgba.buffer]);
    const paused = await rpc('pause');
    const report = { kind: 'native-node-worker-transport-unit',
      identity:{rom_sha256:sha(rom),state_sha256:sha(state),battery_sha256:sha(battery),
        worker_sha256:sha(readFileSync(root+'scripts/quality/experiments/worker-core.js')),mgba_revision:build.mgba_revision},bootCounter: boot.counter, batteryVerified: boot.batteryVerified,
      stallMs: stallEnd - stallStart, guestProgress: progress, pcmSourceFramesReceivedDuringStall: sourceDuringStall,
      before, after, paused,
      scope: 'Actual unchanged core/WASM and checkpoint with independent transferred PCM sink. No browser AudioWorklet, AudioContext, audio quality, paint, or full performance claim.' };
    mkdirSync(dirname(output),{recursive:true});
    writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
    console.log(JSON.stringify({ passed: true, guestProgress: progress, pcmSourceFramesReceivedDuringStall: sourceDuringStall }));
    await rpc('destroy'); sink.postMessage('destroy');
  } finally { clearTimeout(watchdog); await core.terminate(); await sink.terminate(); }
}
