/* Run the actual WebAssembly core against our compiled cartridge and native save. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const base = `${process.cwd()}/web/public/emulator/`;
const sandbox = { require, process, console, __dirname: base, __filename: `${base}mgba.js`,
  exports: {}, module: { exports: {} }, TextDecoder, TextEncoder, WebAssembly,
  Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array,
  Float32Array, Float64Array, ArrayBuffer, setTimeout, clearTimeout };
vm.runInNewContext(fs.readFileSync(`${base}mgba.js`, 'utf8'), sandbox);
(async () => {
  const core = await sandbox.module.exports({ wasmBinary: fs.readFileSync(`${base}mgba.wasm`) });
  core._mgbawasm_init();
  const rom = fs.readFileSync('web/public/game/sf-mini-monsters.gba');
  const pointer = core._malloc(rom.length);
  core.HEAPU8.set(rom, pointer);
  assert.equal(core._mgbawasm_load(pointer, rom.length, 0, 0, 0, 0, 1), 1);
  core._free(pointer);
  let initialized = false;
  for (let frame = 0; frame < 120; frame++) {
    core._mgbawasm_run_frame();
    if (core._mgbawasm_sram_save() === 32768) { initialized = true; break; }
  }
  assert.ok(initialized, 'ROM must initialize actual SRAM before import');
  const fixture = fs.readFileSync('build/save-fixture.sav');
  const savePointer = core._malloc(fixture.length);
  core.HEAPU8.set(fixture, savePointer);
  assert.equal(core._mgbawasm_sram_load(savePointer, fixture.length), 1);
  core._free(savePointer);
  const snapshot = () => {
    assert.equal(core._mgbawasm_sram_save(), 32768);
    const address = core._mgbawasm_sram_ptr();
    return Buffer.from(core.HEAPU8.subarray(address, address + 32768));
  };
  assert.ok(snapshot().equals(fixture), 'battery save must round-trip byte for byte');
  core._mgbawasm_reset();
  const frames = count => { for (let n = 0; n < count; n++) core._mgbawasm_run_frame(); };
  const press = mask => { core._mgbawasm_set_keys(mask); frames(12); core._mgbawasm_set_keys(0); frames(12); };
  frames(30); press(1); // Continue from title.
  press(128); // Down in restored world; triggers cartridge autosave.
  const result = snapshot();
  const a = result.subarray(0, 360), b = result.subarray(2048, 2408);
  const record = a.readUInt32LE(12) > b.readUInt32LE(12) ? a : b;
  assert.equal(record.readUInt32LE(0), 0x53464d4d, 'resumed game must write the next save bank');
  assert.equal(record.readUInt16LE(26), 222, 'restored currency survives game execution');
  assert.equal(record[32], 13, 'restored player moves down from y=12');
  assert.equal(record.readUInt16LE(20) & 2, 2, 'prototype quest survives cartridge restart');
  console.log('WebAssembly cartridge boot, input, SRAM restore/resume/export passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
