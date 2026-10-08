/* Compare the same cartridge/controller route at the native and WASM boundary. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = require('node:path');
const [romPath, inputPath, nativeDirectory, batteryPath, runtimeDirectory, audioMode] = process.argv.slice(2);
assert.ok(romPath && inputPath && nativeDirectory, 'Pass ROM, controller CSV and native capture directory');
const base = path.resolve(runtimeDirectory || 'web/public/emulator') + '/';
const sandbox = {require, process, console, __dirname: base, __filename: base + 'mgba.js',
  exports: {}, module: {exports: {}}, TextDecoder, TextEncoder, WebAssembly,
  Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array,
  Float32Array, Float64Array, ArrayBuffer, setTimeout, clearTimeout};
vm.runInNewContext(fs.readFileSync(base + 'mgba.js', 'utf8'), sandbox);

(async () => {
  const native = JSON.parse(fs.readFileSync(path.join(nativeDirectory, 'capture.json'), 'utf8'));
  assert.ok(native.runtime?.startsWith('native mGBA'), 'Reference must be an independent native capture');
  const rom = fs.readFileSync(romPath);
  const hash = crypto.createHash('sha256').update(rom).digest('hex');
  assert.equal(hash, native.rom_sha256, 'Comparison must use the identical cartridge');
  const core = await sandbox.module.exports({wasmBinary: fs.readFileSync(base + 'mgba.wasm')});
  core._mgbawasm_init();
  const pointer = core._malloc(rom.length);
  core.HEAPU8.set(rom, pointer);
  assert.equal(core._mgbawasm_load(pointer, rom.length, 0, 0, 0, 0, 1), 1);
  core._free(pointer);
  core._mgbawasm_run_frame(); // Same initial frame alignment as native capture.
  if (batteryPath && batteryPath !== '-') {
    const battery = fs.readFileSync(batteryPath);
    const pointer = core._malloc(battery.length);
    core.HEAPU8.set(battery, pointer);
    assert.equal(core._mgbawasm_sram_load(pointer, battery.length), 1);
    core._free(pointer);
    assert.equal(core._mgbawasm_sram_save(), battery.length);
    const address = core._mgbawasm_sram_ptr();
    assert.ok(Buffer.from(core.HEAPU8.subarray(address, address + battery.length)).equals(battery));
    core._mgbawasm_reset(); core._mgbawasm_run_frame();
  }
  let frames = 0;
  const compareAudio = audioMode === 'audio';
  const audioHash = compareAudio ? crypto.createHash('sha256') : null;
  const audioPointer = compareAudio ? core._malloc(8192 * 4) : 0;
  let audioPairs = 0;
  const drainAudio = record => {
    let available = core._mgbawasm_audio_available();
    while (available > 0) {
      const count = core._mgbawasm_read_audio(audioPointer, Math.min(available, 8192));
      assert.ok(count > 0, 'Available audio must be drainable');
      if (record) {
        audioHash.update(Buffer.from(core.HEAPU8.subarray(audioPointer, audioPointer + count * 4)));
        audioPairs += count;
      }
      available = core._mgbawasm_audio_available();
    }
  };
  if (compareAudio) drainAudio(false); // Match native capture's post-startup boundary.
  for (const row of fs.readFileSync(inputPath, 'utf8').trim().split('\n')) {
    const [keys, duration] = row.split(',').map(Number);
    core._mgbawasm_set_keys(keys);
    for (let n = 0; n < duration; n++) {
      core._mgbawasm_run_frame();
      if (compareAudio) drainAudio(true);
    }
    frames += duration;
  }
  assert.equal(frames, native.frames, 'Entire controller route must execute');
  assert.equal(core._mgbawasm_video_width(), 240);
  assert.equal(core._mgbawasm_video_height(), 160);
  const address = core._mgbawasm_video_ptr();
  const actual = Buffer.from(core.HEAPU8.subarray(address, address + 240 * 160 * 4));
  const expected = fs.readFileSync(path.join(nativeDirectory, 'capture.final.rgba'));
  let differingPixels = 0;
  for (let n = 0; n < actual.length; n += 4) {
    if (actual[n] !== expected[n] || actual[n + 1] !== expected[n + 1] ||
        actual[n + 2] !== expected[n + 2]) differingPixels++;
  }
  if (differingPixels) {
    // Preserve the actual rendering for diagnosis; never mask a failed comparison.
    const diagnostic = path.join(nativeDirectory, `wasm-mismatch-${Date.now()}.rgba`);
    fs.writeFileSync(diagnostic, actual, {flag: 'wx'});
    console.error(`WASM diagnostic: ${diagnostic}`);
  }
  // Alpha is a frontend presentation convention; compare actual RGB game pixels.
  assert.equal(differingPixels, 0, 'Native and WASM final field state/rendering must match');
  if (compareAudio) {
    core._free(audioPointer);
    assert.equal(audioPairs, native.audio_samples, 'Raw stereo sample count must match');
    const expectedAudio = crypto.createHash('sha256').update(fs.readFileSync(path.join(nativeDirectory, 'capture.pcm'))).digest('hex');
    assert.equal(audioHash.digest('hex'), expectedAudio, 'Every raw audio sample must match native output');
    console.log(`Native/WASM raw audio: ${audioPairs} identical stereo sample pairs.`);
  }
  if (batteryPath && batteryPath !== '-') {
    const length = core._mgbawasm_sram_save(), address = core._mgbawasm_sram_ptr();
    const exported = Buffer.from(core.HEAPU8.subarray(address, address + length));
    assert.ok(exported.equals(fs.readFileSync(path.join(nativeDirectory, 'capture.sav'))), 'Battery bytes must match native execution');
    fs.writeFileSync(path.join(nativeDirectory, 'wasm-export.sav'), exported);
  }
  console.log(`Foundation native/WASM route: ${frames} frames, identical final RGB pixels.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
