/* Compare the same cartridge/controller route at the native and WASM boundary. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = require('node:path');
const [romPath, inputPath, nativeDirectory] = process.argv.slice(2);
assert.ok(romPath && inputPath && nativeDirectory, 'Pass ROM, controller CSV and native capture directory');
const base = path.resolve('web/public/emulator') + '/';
const sandbox = {require, process, console, __dirname: base, __filename: base + 'mgba.js',
  exports: {}, module: {exports: {}}, TextDecoder, TextEncoder, WebAssembly,
  Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array,
  Float32Array, Float64Array, ArrayBuffer, setTimeout, clearTimeout};
vm.runInNewContext(fs.readFileSync(base + 'mgba.js', 'utf8'), sandbox);

(async () => {
  const native = JSON.parse(fs.readFileSync(path.join(nativeDirectory, 'capture.json'), 'utf8'));
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
  let frames = 0;
  for (const row of fs.readFileSync(inputPath, 'utf8').trim().split('\n')) {
    const [keys, duration] = row.split(',').map(Number);
    core._mgbawasm_set_keys(keys);
    for (let n = 0; n < duration; n++) core._mgbawasm_run_frame();
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
  // Alpha is a frontend presentation convention; compare actual RGB game pixels.
  assert.equal(differingPixels, 0, 'Native and WASM final field state/rendering must match');
  console.log(`Foundation native/WASM route: ${frames} frames, identical final RGB pixels.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
