// Direct native-step RCA only: zero keys, unchanged core/WASM/shim, no guest RAM writes.
import { Worker, parentPort, workerData } from 'node:worker_threads';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root = fileURLToPath(new URL('../', import.meta.url));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
if (!workerData) {
  const [romPath,statePath,frames='600',referenceLiveStatePath]=process.argv.slice(2);
  if(!romPath||!statePath)throw Error('Pass ROM.gba and controller-only capture.state paths; optional frame count and reference live state');
  const child = new Worker(new URL(import.meta.url), { workerData: { run: true, frames:Number(frames),romPath,statePath,referenceLiveStatePath } });
  const timer = setTimeout(() => { child.terminate(); console.error('RCA unit exceeded14seconds'); process.exitCode = 1; }, 14000);
  child.on('message', value => console.log(JSON.stringify(value)));
  child.on('error', error => { console.error(error); process.exitCode = 1; });
  child.on('exit', code => { clearTimeout(timer); if (code) process.exitCode = code; });
} else {
  const total = workerData.frames;
  assert.ok(Number.isSafeInteger(total) && total >= 5 && total <= 600);
  const out = root + '.tools/benchmarks/native-state-continuation-' + randomUUID() + '/'; mkdirSync(out);
  const preserve = (name, bytes) => writeFileSync(out + name, bytes, { flag: 'wx' });
  const coreDir = root + 'web/public/emulator/';
  const build = JSON.parse(readFileSync(coreDir + 'core-build.json'));
  const loader = readFileSync(coreDir + 'mgba.js'); const wasm = readFileSync(coreDir + 'mgba.wasm');
  assert.equal(build.mgba_revision, '26b7884bc25a5933960f3cdcd98bac1ae14d42e2');
  assert.equal(sha(loader), build.artifacts['mgba.js']); assert.equal(sha(wasm), build.artifacts['mgba.wasm']);
  globalThis.require = createRequire(import.meta.url); globalThis.__filename = coreDir + 'mgba.js'; globalThis.__dirname = coreDir;
  vm.runInThisContext(loader.toString(), { filename: globalThis.__filename });
  const mod = await globalThis.createMgbaModule({ locateFile: name => name.endsWith('.wasm') ? coreDir + 'mgba.wasm' : coreDir + name });
  mod._mgbawasm_init(); mod._mgbawasm_set_log_level(1);
  const {romPath,statePath}=workerData;
  const rom = new Uint8Array(readFileSync(romPath)), coldState = new Uint8Array(readFileSync(statePath));
  const coldFlash = new Uint8Array(readFileSync(statePath.replace('.state', '.sav')));
  const metadata = JSON.parse(readFileSync(statePath.replace('.state', '.json')));
  assert.equal(rom.length,16777216);assert.equal(coldState.length,0x61000);assert.equal(coldFlash.length,131072);
  assert.equal(metadata.controller_only, true); assert.equal(metadata.rom_sha256, sha(rom)); assert.equal(metadata.mgba_revision, build.mgba_revision);
  const copyIn = (bytes, action) => { const ptr = mod._malloc(bytes.length); try { mod.HEAPU8.set(bytes, ptr); return action(ptr); } finally { mod._free(ptr); } };
  const counter = () => mod._mgbawasm_frame_counter() >>> 0;
  const audioPtr = mod._malloc(4096 * 4);
  function drain() {
    const chunks = []; let frames = 0;
    for (let i = 0; i < 32; ++i) {
      const n = mod._mgbawasm_read_audio(audioPtr, 4096); if (!n) return { pcm: Buffer.concat(chunks), frames };
      assert.ok(n > 0 && n <= 4096); frames += n;
      chunks.push(Buffer.from(mod.HEAPU8.slice(audioPtr, audioPtr + n * 4)));
    }
    throw Error('Unbounded shim PCM drain');
  }
  function flash() {
    const size = mod._mgbawasm_sram_save(); assert.equal(size, 131072);
    const ptr = mod._mgbawasm_sram_ptr(); return mod.HEAPU8.slice(ptr, ptr + size);
  }
  function state() {
    const size = mod._mgbawasm_state_size(); assert.equal(size, 0x61000); const ptr = mod._malloc(size);
    try { mod.HEAPU8.fill(0, ptr, ptr + size); assert.equal(mod._mgbawasm_state_save(ptr), 1); return mod.HEAPU8.slice(ptr, ptr + size); }
    finally { mod._free(ptr); }
  }
  function load(rawState, rawFlash) {
    assert.equal(copyIn(rom, ptr => mod._mgbawasm_load(ptr, rom.length, 0, 0, -1, 0, 1)), 1);
    mod._mgbawasm_set_idle_optimization(1); mod._mgbawasm_set_allow_opposing_directions(0);
    let ready = false;
    for (let frame = 0; frame < 120; ++frame) { mod._mgbawasm_run_frame(); if (mod._mgbawasm_sram_save() === rawFlash.length) { ready = true; break; } }
    assert.ok(ready); assert.equal(copyIn(rawFlash, ptr => mod._mgbawasm_sram_load(ptr, rawFlash.length)), 1);
    assert.deepEqual(flash(), rawFlash); mod._mgbawasm_reset(); mod._mgbawasm_set_idle_optimization(1);
    assert.equal(copyIn(rawState, ptr => mod._mgbawasm_state_load(ptr)), 1); mod._mgbawasm_set_keys(0);
    return drain();
  }
  function advance() {
    const before = counter(); mod._mgbawasm_run_frame(); assert.equal((counter() - before) >>> 0, 1); return drain();
  }
  const checkpoints = [...new Set([1, 2, 5, total])].sort((a, b) => a - b);
  const initialDrain = load(coldState, coldFlash);
  const warmup = []; for (let i = 0; i < 24; ++i) warmup.push(advance().pcm);
  const A = state(), AFlash = flash(), aCounter = counter();
  assert.deepEqual(state(), A); preserve('A-live.state', A); preserve('A-live.sav', AFlash); preserve('warmup.pcm', Buffer.concat(warmup));
  const frozen = workerData.referenceLiveStatePath ? new Uint8Array(readFileSync(workerData.referenceLiveStatePath)) : null;
  const reference = new Map(), ratesB = [], pcmB = [];
  for (let i = 1; i <= total; ++i) {
    const sample = advance(); pcmB.push(sample.pcm); ratesB.push({ frame: counter(), sourceFrames: sample.frames, sampleRate: mod._mgbawasm_sample_rate() });
    if (checkpoints.includes(i)) {
      const s = state(), f = flash(), pcm = Buffer.concat(pcmB); reference.set(i, { s, f, pcm, counter: counter() });
      preserve(`B-${i}.state`, s); preserve(`B-${i}.sav`, f); preserve(`B-${i}.pcm`, pcm);
    }
  }
  const reloadDrain = load(A, AFlash), loadedA = state(); preserve('A-loaded.state', loadedA);
  preserve('load-discarded.pcm', reloadDrain.pcm); assert.equal(counter(), aCounter); assert.deepEqual(flash(), AFlash);
  const pcmC = [], ratesC = [], comparisons = [];
  const ranges = [['cpu', 0x20, 0x130], ['psg', 0x130, 0x18c], ['audioOther', 0x18c, 0x1f0],
    ['io', 0x400, 0x800], ['palette', 0x800, 0xc00], ['oam', 0xc00, 0x1000], ['vram', 0x1000, 0x19000],
    ['iwram', 0x19000, 0x21000], ['ewram', 0x21000, 0x61000]];
  const offsets = (a, b) => { const result = []; for (let i = 0; i < a.length; ++i) if (a[i] !== b[i]) result.push(i); return result; };
  for (let i = 1; i <= total; ++i) {
    const sample = advance(); pcmC.push(sample.pcm); ratesC.push({ frame: counter(), sourceFrames: sample.frames, sampleRate: mod._mgbawasm_sample_rate() });
    if (!checkpoints.includes(i)) continue;
    const s = state(), f = flash(), pcm = Buffer.concat(pcmC), b = reference.get(i), diffs = offsets(b.s, s);
    preserve(`C-${i}.state`, s); preserve(`C-${i}.sav`, f); preserve(`C-${i}.pcm`, pcm);
    let firstPcmDifference = -1; const common = Math.min(b.pcm.length, pcm.length);
    for (let j = 0; j < common; ++j) if (b.pcm[j] !== pcm[j]) { firstPcmDifference = j; break; }
    comparisons.push({ nativeFrames: i, referenceCounter: b.counter, restoredCounter: counter(), wholeStateEqual: diffs.length === 0,
      changedOffsets: diffs, regions: Object.fromEntries(ranges.map(([name, start, end]) => [name, diffs.filter(off => off >= start && off < end).length])),
      flashExact: Buffer.from(b.f).equals(f), pcmExact: b.pcm.equals(pcm), referencePcmBytes: b.pcm.length,
      restoredPcmBytes: pcm.length, firstPcmDifference, referencePcmSha256: sha(b.pcm), restoredPcmSha256: sha(pcm) });
  }
  const report = { kind: 'direct-native-continuation-rca', coreRevision: build.mgba_revision,
    artifacts: { rom: sha(rom), loader: sha(loader), wasm: sha(wasm), coldState: sha(coldState), coldFlash: sha(coldFlash) },
    warmupNativeFrames: 24, liveCounter: aCounter, matchesProvidedLiveReference: frozen ? Buffer.from(A).equals(frozen) : null,
    canonicalARepeatedExact: true, loadedAWholeStateEqual: Buffer.from(A).equals(loadedA), loadedAChangedOffsets: offsets(A, loadedA),
    initialBootDrainSourceFrames: initialDrain.frames, reloadedDrainSourceFrames: reloadDrain.frames,
    perFrameAudioCountsAndRatesEqual: JSON.stringify(ratesB) === JSON.stringify(ratesC), ratesB, ratesC, comparisons,
    scope: 'Uninterrupted paused-live-A native continuation versus retained-ROM+full-Flash+state-A restore followed by the same exact N native frames and zero keys. Raw core-generated PCM after explicit load-ring drain; no normalization, memory patches, real-time/DOM/audio-device/performance gate claim.' };
  preserve('report.json', JSON.stringify(report, null, 2) + '\n');
  for(const result of comparisons){
    assert.equal(result.referenceCounter,result.restoredCounter);assert.equal(result.flashExact,true);assert.equal(result.pcmExact,true);
    for(const [name,count]of Object.entries(result.regions))if(name!=='psg')assert.equal(count,0,'Functional state domain differs: '+name);
  }
  assert.equal(report.perFrameAudioCountsAndRatesEqual,true);
  mod._free(audioPtr); mod._mgbawasm_unload();
  parentPort.postMessage({ output: out, ...report, ratesB: `${ratesB.length} rows preserved in report`, ratesC: `${ratesC.length} rows preserved in report` });
}
