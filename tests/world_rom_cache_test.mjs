import assert from 'node:assert/strict';
import {readWorldRom, rememberWorldRom, forgetWorldRom} from '../web/app/world-rom-cache.ts';

// Cache API boundary: a return visit must get the original bytes, not a patched
// cartridge, and forgetting that ROM must not erase an unrelated cached file.
const entries = new Map([['/unrelated', new Response('keep')]]);
globalThis.fetch = () => { throw new Error('ROM storage must not use the network'); };
globalThis.caches = {open: async () => ({
  match: async key => entries.get(key)?.clone(),
  put: async (key, value) => { entries.set(key, value.clone()); },
  delete: async key => entries.delete(key),
})};
assert.equal(await readWorldRom(), null);
const original = new Uint8Array([0, 255, 15, 128]);
assert.equal(await rememberWorldRom(original), true);
const restored = await readWorldRom();
assert.deepEqual(restored, original);
restored[0] = 42;
assert.deepEqual(await readWorldRom(), original);
assert.equal(await forgetWorldRom(), true);
assert.equal(await readWorldRom(), null);
assert.equal(await entries.get('/unrelated').text(), 'keep');

globalThis.caches = {open: async () => { throw new DOMException('Quota exceeded', 'QuotaExceededError'); }};
assert.equal(await readWorldRom(), null);
assert.equal(await rememberWorldRom(original), false);
assert.equal(await forgetWorldRom(), false);
delete globalThis.caches;
assert.equal(await readWorldRom(), null);
assert.equal(await rememberWorldRom(original), false);
console.log('Local ROM roundtrip, isolated removal, no-network and unavailable-storage fallback pass.');
