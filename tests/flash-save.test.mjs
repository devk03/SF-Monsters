import assert from 'node:assert/strict';
import {FLASH_SIZE, flashCounter, validateFlashSave, validateSfFlashSave} from '../web/app/flash-save.ts';

// Independently specified sector layout from the pinned Emerald save format.
const lengths = [0xf2c, 0xf80, 0xf80, 0xf80, 0xf08,
  0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0xf80, 0x7d0];
const save = new Uint8Array(FLASH_SIZE).fill(255);
function fillSlot(slot, counter, rotation) {
  for (let index = 0; index < 14; index++) {
    const id = (index + rotation) % 14;
    const view = new DataView(save.buffer, (slot * 14 + index) * 4096, 4096);
    let checksum = 0;
    for (let offset = 0; offset < lengths[id]; offset += 4) {
      const value = (id * 0x1020304 + offset * 17 + counter) >>> 0;
      view.setUint32(offset, value, true);
      checksum = (checksum + value) >>> 0;
    }
    view.setUint16(4084, id, true);
    view.setUint16(4086, ((checksum >>> 16) + checksum) & 65535, true);
    view.setUint32(4088, 0x08012025, true);
    view.setUint32(4092, counter, true);
  }
}
assert.equal(flashCounter(save), null, 'Uninitialized Flash is not a saved game');
fillSlot(0, 42, 9);
validateFlashSave(save);
assert.equal(flashCounter(save), 42, 'Rotated sectors are accepted');
fillSlot(1, 43, 4);
assert.equal(flashCounter(save), 43, 'Newest complete slot wins');
save[14 * 4096] ^= 1;
assert.equal(flashCounter(save), 42, 'A damaged newer slot falls back to the intact older slot');
save[0] ^= 1;
assert.throws(() => validateFlashSave(save), /not a valid/);
assert.throws(() => validateFlashSave(new Uint8Array(32768)), /128 KiB/);
fillSlot(0, 2, 0); fillSlot(1, 0x80000001, 1);
assert.equal(flashCounter(save), 0x80000001, 'Native uses unsigned max outside the exact wrap pair');
fillSlot(0, 44, 0); fillSlot(1, 46, 1);
assert.equal(flashCounter(save), null, 'A newest counter in the wrong physical slot is unsafe to import');
assert.throws(() => validateFlashSave(save), /not a valid/);
fillSlot(1, 0xffffffff, 3); fillSlot(0, 0, 12);
assert.equal(flashCounter(save), 0, 'Save counter wraparound preserves newest-slot order');
const wrapped = new Uint8Array(FLASH_SIZE + 7); wrapped.set(save, 7);
assert.equal(flashCounter(wrapped.subarray(7)), 0, 'Typed-array offsets are respected');
console.log('Flash slot checksums, rotation, recovery, wraparound and invalid-save rejection passed.');
assert.throws(() => validateSfFlashSave(save), /not a supported SF/);
function stampIdentity(slot, schema) {
  for (let index = 0; index < 14; index++) {
    const view = new DataView(save.buffer, (slot * 14 + index) * 4096, 4096);
    if (view.getUint16(4084, true) !== 2) continue;
    view.setUint16(0x60c, 0x5346, true); view.setUint16(0x60e, schema, true);
    let checksum = 0;
    for (let offset = 0; offset < 0xf80; offset += 4)
      checksum = (checksum + view.getUint32(offset, true)) >>> 0;
    view.setUint16(4086, ((checksum >>> 16) + checksum) & 65535, true);
  }
}
stampIdentity(0, 1); validateSfFlashSave(save);
stampIdentity(0, 2); assert.throws(() => validateSfFlashSave(save), /not a supported SF/);
stampIdentity(1, 1); assert.throws(() => validateSfFlashSave(save), /not a supported SF/,
  'An older compatible slot must not hide a newer unsupported schema');
save[0] ^= 1; validateSfFlashSave(save);
fillSlot(0, 1, 2); fillSlot(1, 1, 7);
stampIdentity(0, 2); stampIdentity(1, 1); validateSfFlashSave(save);
assert.equal(flashCounter(save), 1, 'Equal counters select the physical slot native counter%2 loads');
stampIdentity(0, 1); stampIdentity(1, 2);
assert.throws(() => validateSfFlashSave(save), /not a supported SF/,
  'An equal counter in another slot must not hide the schema native will load');
console.log('SF identity, unsupported schema and intact-slot recovery passed.');
