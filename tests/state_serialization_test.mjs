import assert from 'node:assert/strict';
import test from 'node:test';
import { serializeCoreState } from '../web/public/emulator/mgba.state.js';

function fixture() {
    const heap = new Uint8Array(256).fill(0xa5), freed = [];
    let allocations = 0, saves = 0;
    const mod = { HEAPU8: heap, _mgbawasm_state_size: () => 16,
        _malloc() { ++allocations; return 64; },
        _mgbawasm_state_save(pointer) { ++saves; heap[pointer] = 7; heap[pointer + 8] = 42; return 1; },
        _free(pointer) { freed.push(pointer); } };
    return { mod, heap, freed, counts: () => ({ allocations, saves }) };
}

test('unwritten serializer bytes are deterministic without clearing adjacent heap', () => {
    const f = fixture(), first = serializeCoreState(f.mod);
    assert.deepEqual(Array.from(first), [7,0,0,0,0,0,0,0,42,0,0,0,0,0,0,0]);
    f.heap.fill(0xb4, 64, 80);
    assert.deepEqual(serializeCoreState(f.mod), first);
    assert.ok(f.heap.subarray(0,64).every(value => value === 0xa5));
    assert.ok(f.heap.subarray(80).every(value => value === 0xa5));
    assert.deepEqual(f.freed, [64,64]);
});

test('allocation failure never clears address zero or invokes the serializer', () => {
    const f = fixture(); f.mod._malloc = () => 0;
    assert.throws(() => serializeCoreState(f.mod), /allocate/);
    assert.ok(f.heap.every(value => value === 0xa5));
    assert.equal(f.counts().saves, 0);
    assert.deepEqual(f.freed, []);
});

test('invalid state sizes do not allocate output', () => {
    for (const size of [0,-1,NaN,Infinity,1.5]) {
        const f = fixture(); f.mod._mgbawasm_state_size = () => size;
        assert.throws(() => serializeCoreState(f.mod), /size/);
        assert.equal(f.counts().allocations, 0);
    }
});

test('serializer failure frees its output without returning partial bytes', () => {
    for (const implementation of [() => 0, () => { throw Error('Native failure'); }]) {
        const f = fixture(); f.mod._mgbawasm_state_save = implementation;
        assert.throws(() => serializeCoreState(f.mod));
        assert.deepEqual(f.freed, [64]);
    }
});
