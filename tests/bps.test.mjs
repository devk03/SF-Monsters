import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applyBps, crc32} from '../web/app/bps.ts';

assert.equal(crc32(new TextEncoder().encode('123456789')), 0xcbf43926, 'Independent CRC-32 check vector');
const fixtures = fs.readdirSync('tests/fixtures/bps').filter(name => name.endsWith('.json'));
const bytes = hex => new Uint8Array(Buffer.from(hex, 'hex'));
for (const filename of fixtures) {
  const fixture = JSON.parse(fs.readFileSync(`tests/fixtures/bps/${filename}`, 'utf8'));
  const source = bytes(fixture.source_hex), patch = bytes(fixture.patch_hex);
  const before = source.slice(), expected = bytes(fixture.target_hex);
  assert.deepEqual(applyBps(source, patch), expected, filename);
  assert.deepEqual(source, before, 'Patching must preserve the supplied base ROM');
  // Exercise a sliced buffer, as File/typed-array integrations may use one.
  const packet = new Uint8Array(patch.length + 12);
  packet.set(patch, 7);
  assert.deepEqual(applyBps(source, packet.subarray(7, 7 + patch.length)), expected);
  const brokenPatch = patch.slice(); brokenPatch[brokenPatch.length - 1] ^= 1;
  assert.throws(() => applyBps(source, brokenPatch), /patch checksum mismatch/);
  const wrongSource = source.slice(); wrongSource[0] ^= 1;
  assert.throws(() => applyBps(wrongSource, patch), /base ROM checksum mismatch/);
}

const fixChecksum = patch => {
  new DataView(patch.buffer).setUint32(patch.length - 4, crc32(patch.subarray(0, patch.length - 4)), true);
  return patch;
};
const read = JSON.parse(fs.readFileSync('tests/fixtures/bps/source-read-literal.json', 'utf8'));
const source = bytes(read.source_hex);
const oversizedMetadata = bytes(read.patch_hex); oversizedMetadata[6] = 0xff;
assert.throws(() => applyBps(source, fixChecksum(oversizedMetadata)), /truncated metadata/);
const overrun = bytes(read.patch_hex); overrun[7] = 0xfc;
assert.throws(() => applyBps(source, fixChecksum(overrun)), /exceeds output size/);
const wrongTarget = bytes(read.patch_hex); wrongTarget[wrongTarget.length - 8] ^= 1;
assert.throws(() => applyBps(source, fixChecksum(wrongTarget)), /output checksum mismatch/);
const copy = JSON.parse(fs.readFileSync('tests/fixtures/bps/source-copy-backwards.json', 'utf8'));
const negativeSource = bytes(copy.patch_hex); negativeSource[8] = 0xff;
assert.throws(() => applyBps(bytes(copy.source_hex), fixChecksum(negativeSource)), /source copy is out of range/);
const unwrittenTarget = bytes(copy.patch_hex); unwrittenTarget[7] = 0x8f; unwrittenTarget[8] = 0x80;
assert.throws(() => applyBps(bytes(copy.source_hex), fixChecksum(unwrittenTarget)), /unwritten data/);

const [basePath, patchPath, targetPath] = process.argv.slice(2);
if (basePath || patchPath || targetPath) {
  assert.ok(basePath && patchPath && targetPath, 'Pass all three real-cartridge paths');
  const base = new Uint8Array(fs.readFileSync(basePath));
  const patch = new Uint8Array(fs.readFileSync(patchPath));
  const result = applyBps(base, patch);
  assert.deepEqual(Buffer.from(result), fs.readFileSync(targetPath), 'Browser decoder must match native Flips output');
}
console.log('BPS commands, overlapping/backward copies, integrity, bounds and input preservation passed.');
