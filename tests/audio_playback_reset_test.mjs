/* Presentation queues must not replay pre-checkpoint PCM after a playback reset. */
import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import { discardPendingAudio } from '../web/public/emulator/mgba.audio-reset.js';
import { WORKLET_SOURCE } from '../web/public/emulator/mgba.audio-worklet.js';

const MAX_PENDING_FRAMES = 65536;
const POINTER = 4096;

function queuedCore(initialFrames) {
    let remaining = initialFrames, calls = 0, runs = 0, forwarded = 0;
    const mod = {
        _mgbawasm_read_audio(pointer, capacity) {
            assert.equal(pointer, POINTER);
            ++calls;
            const count = Math.min(remaining, capacity);
            remaining -= count;
            return count;
        },
        _mgbawasm_run_frame() { ++runs; throw Error('Discard must not advance guest execution'); },
        postMessage() { ++forwarded; throw Error('Discard must not forward stale PCM'); },
    };
    return { mod, counts: () => ({ remaining, calls, runs, forwarded }) };
}

test('discards empty, partial and full shim queues through an explicit empty sentinel', () => {
    for (const [queued, capacity] of [[0, 4096], [7, 4096], [4097, 4096],
        [65536, 4096], [65536, 65536], [65536, 7]]) {
        const fake = queuedCore(queued);
        const discarded = discardPendingAudio(fake.mod, POINTER, capacity);
        assert.equal(discarded, queued, `queued=${queued}, capacity=${capacity}`);
        assert.deepEqual(fake.counts(), {
            remaining: 0, calls: Math.ceil(queued / capacity) + 1, runs: 0, forwarded: 0,
        });
        assert.ok(Number.isSafeInteger(discarded));
    }
});

test('invalid native audio read counts fail before they can become valid discard totals', () => {
    for (const value of [-1, 4097, 0.5, NaN, Infinity, '1', undefined, null]) {
        let calls = 0;
        const mod = { _mgbawasm_read_audio() { ++calls; return value; } };
        assert.throws(() => discardPendingAudio(mod, POINTER, 4096));
        assert.equal(calls, 1);
    }
});

test('a queue larger than the shim bound fails within one sentinel read', () => {
    const fake = queuedCore(MAX_PENDING_FRAMES + 1);
    assert.throws(() => discardPendingAudio(fake.mod, POINTER, 4096));
    assert.equal(fake.counts().calls, 17);
    assert.equal(fake.counts().runs, 0);
    assert.equal(fake.counts().forwarded, 0);
});

test('a native reader that never reaches empty cannot keep reset draining indefinitely', () => {
    for (const count of [1, 4096]) {
        let calls = 0;
        const mod = { _mgbawasm_read_audio() {
            ++calls;
            // Keep a broken implementation from hanging the test process itself.
            if (calls > 18) throw Error('Unbounded drain');
            return count;
        } };
        assert.throws(() => discardPendingAudio(mod, POINTER, 4096));
        assert.ok(calls <= 17, `Nonterminating count=${count} exceeded the read budget`);
    }
});

test('invalid scratch capacity is rejected without making a native read', () => {
    for (const capacity of [0, -1, 0.5, NaN, Infinity, 65537, '4096']) {
        let calls = 0;
        const mod = { _mgbawasm_read_audio() { ++calls; return 0; } };
        assert.throws(() => discardPendingAudio(mod, POINTER, capacity));
        assert.equal(calls, 0);
    }
});

function worklet() {
    let Sink;
    class Processor {
        constructor() {
            this.port = { messages: [], postMessage(value) { this.messages.push(value); } };
        }
    }
    const context = {
        AudioWorkletProcessor: Processor, Float32Array, sampleRate: 48000, currentFrame: 0,
        registerProcessor(name, Constructor) { assert.equal(name, 'mgba-sink'); Sink = Constructor; },
    };
    vm.runInNewContext(WORKLET_SOURCE, context);
    const instance = new Sink();
    return {
        send(data) { instance.port.onmessage({ data }); },
        render(frames) {
            const left = new Float32Array(frames), right = new Float32Array(frames);
            instance.process([], [[left, right]]);
            context.currentFrame += frames;
            return [Array.from(left), Array.from(right)];
        },
        messages: instance.port.messages,
    };
}

function marker(frames, left, right) {
    const samples = new Int16Array(frames * 2);
    for (let i = 0; i < frames; ++i) {
        samples[i * 2] = left;
        samples[i * 2 + 1] = right;
    }
    return samples;
}

test('playback reset acknowledges its epoch and removes stale PCM and consumption position', () => {
    const sink = worklet();
    sink.send({ rate: 48000 });
    sink.send(marker(4096, 8192, 16384));
    const before = sink.render(1536);
    assert.ok(before[0].every(value => value === .25));
    assert.ok(before[1].every(value => value === .5));
    assert.equal(sink.messages.filter(value => typeof value === 'number').at(-1), 1536);

    sink.send({ type: 'playback-reset', epoch: 1 });
    const ack = sink.messages.at(-1);
    assert.equal(ack.type, 'playback-reset');
    assert.equal(ack.epoch, 1);
    assert.deepEqual(sink.render(16), [Array(16).fill(0), Array(16).fill(0)]);
    assert.equal(sink.messages.at(-1), ack, 'An empty reset queue does not emit stale consumption');

    sink.send(marker(2048, -8192, -16384));
    const after = sink.render(1024);
    assert.ok(after[0].every(value => value === -.25), 'Only new left-channel PCM survives');
    assert.ok(after[1].every(value => value === -.5), 'Only new right-channel PCM survives');
    assert.equal(sink.messages.filter(value => typeof value === 'number').at(-1), 1024,
        'Fresh consumption starts at zero and resets its last-post threshold');
});

test('starting a diagnostic epoch observes already queued PCM without flushing playback', () => {
    const sink = worklet();
    sink.send({ rate: 48000 });
    sink.send(marker(8, 8192, -8192));
    assert.deepEqual(sink.render(1), [[.25], [-.25]]);
    sink.send({ type: 'diagnostics', enabled: true, epoch: 9 });
    assert.deepEqual(sink.render(4), [Array(4).fill(.25), Array(4).fill(-.25)]);
    sink.send({ type: 'diagnostics', enabled: false, epoch: 9 });
    const report = sink.messages.at(-1);
    assert.equal(report.type, 'diagnostics');
    assert.equal(report.epoch, 9);
    assert.equal(report.warmupOutputFrames, 0);
    assert.equal(report.underrunOutputFrames, 0);
    assert.equal(report.queueDepthFrames, 3);
    assert.equal(sink.messages.filter(value => value?.type === 'playback-reset').length, 0);
});

// Rejection of delayed playback-reset ACKs belongs to the SDK pending-epoch
// coordinator, not this worklet. These tests do not claim that SDK coverage.
