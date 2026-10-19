/* Public world SDK pacing and unchanged real AudioWorklet source, with a fake core. */
import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {load} from '../web/public/emulator/world.sdk.js';
import {load as loadSunset} from '../web/public/emulator/mgba.sdk.js';
import {WORKLET_SOURCE} from '../web/public/emulator/mgba.audio-worklet.js';

async function fixture(loader = load, initialRate = 65536, real = null) {
    const saved = new Map();
    const install = (key, value) => {
        saved.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
        Object.defineProperty(globalThis, key, {configurable: true, writable: true, value});
    };
    let now = 1000, raf, coreRate = initialRate, counter = 0, pending = 0, produced = 0;
    let nextPointer = 4096, sink;
    const events = [], audioMessages = [], timers = new Map();
    let nextTimer = 1;
    const bytes = new Uint8Array(2 * 1024 * 1024);
    const sramPointer = 1024 * 1024;
    bytes.fill(0x5a, sramPointer, sramPointer + 131072);
    const core = {
        HEAPU8: bytes, HEAP16: new Int16Array(bytes.buffer),
        _malloc(size) { const p = nextPointer; nextPointer += (size + 7) & ~7; return p; },
        _free() {}, _mgbawasm_init() {}, _mgbawasm_unload() {},
        lengthBytesUTF8: value => Buffer.byteLength(value),
        stringToUTF8(value, pointer) { bytes.set(new TextEncoder().encode(value + '\0'), pointer); },
        _mgbawasm_set_log_level() {}, _mgbawasm_set_keys() {},
        _mgbawasm_set_idle_optimization() {}, _mgbawasm_set_allow_opposing_directions() {},
        _mgbawasm_load() { counter = pending = produced = 0; return 1; },
        _mgbawasm_reset() { counter = pending = produced = 0; },
        _mgbawasm_platform: () => 0, _mgbawasm_has_bios: () => 0,
        _mgbawasm_framerate_micro: () => 60000000, _mgbawasm_sample_rate: () => coreRate,
        _mgbawasm_frame_counter: () => counter,
        _mgbawasm_run_frame() {
            counter++;
            const total = Math.floor(counter * coreRate / 60);
            pending += total - produced; produced = total;
            bytes[256] = counter & 255;
        },
        _mgbawasm_read_audio(pointer, capacity) {
            const count = Math.min(pending, capacity); pending -= count;
            core.HEAP16.fill(8192, pointer / 2, pointer / 2 + count * 2);
            return count;
        },
        _mgbawasm_video_width: () => 240, _mgbawasm_video_height: () => 160,
        _mgbawasm_video_ptr: () => 512,
        _mgbawasm_sram_save: () => 131072, _mgbawasm_sram_ptr: () => sramPointer,
        _mgbawasm_sram_load(pointer, size) { bytes.copyWithin(sramPointer, pointer, pointer + size); return 1; },
    };
    class Processor {
        constructor() { this.port = {postMessage: data => sink.port.onmessage?.({data})}; }
    }
    const context = {AudioWorkletProcessor: Processor, Float32Array, sampleRate: 48000,
        currentFrame: 0, registerProcessor(_name, Class) { context.Sink = Class; }};
    vm.runInNewContext(WORKLET_SOURCE, context);
    class Worklet {
        constructor() {
            sink = this;
            this.processor = new context.Sink();
            this.port = {postMessage: data => {
                audioMessages.push(data);
                this.processor.port.onmessage({data});
            }};
        }
        connect() { return {connect() {}}; } disconnect() {}
    }
    class Audio {
        state = 'suspended'; sampleRate = 48000;
        get currentTime() { return now / 1000; }
        audioWorklet = {async addModule() {}};
        createGain() { return {gain: {value: 1}, disconnect() {}}; }
        async resume() { this.state = 'running'; } async suspend() { this.state = 'suspended'; }
        async close() {}
    }
    install('performance', {now: () => now});
    install('AudioContext', Audio); install('AudioWorkletNode', Worklet);
    install('window', {addEventListener() {}, removeEventListener() {}});
    install('document', {visibilityState: 'visible', addEventListener() {}, removeEventListener() {},
        createElement: () => ({}), head: {appendChild: node => queueMicrotask(() => node.onload())}});
    install('navigator', {getGamepads: () => [], userAgent: 'world-speed-test'});
    install('requestAnimationFrame', callback => { raf = callback; return 1; });
    install('cancelAnimationFrame', () => { raf = null; });
    install('setTimeout', callback => { const id = nextTimer++; timers.set(id, callback); return id; });
    install('clearTimeout', id => timers.delete(id));
    let activeCore = core;
    install('createMgbaModule', async () => {
        activeCore = real ? await real.factory() : core;
        return activeCore;
    });
    const canvas = {style: {setProperty() {}}, getContext: () => ({
        createImageData: (w, h) => ({data: new Uint8ClampedArray(w * h * 4)}), putImageData() {},
    })};
    let engine;
    try {
        engine = await loader({canvasEl: canvas, assets: {rom: real?.rom ?? new Uint8Array([1, 2, 3, 4])},
            persist: null, onEvent: event => events.push(event), options: {idleOptimization: 'ignore'}});
    } catch (error) { restore(); throw error; }
    function restore() {
        for (const [key, descriptor] of saved) {
            if (descriptor) Object.defineProperty(globalThis, key, descriptor);
            else Reflect.deleteProperty(globalThis, key);
        }
    }
    return {
        engine, core: activeCore, events, audioMessages, sink: () => sink.processor,
        setRate(value) { coreRate = value; counter = produced = pending = 0; },
        count: () => activeCore._mgbawasm_frame_counter(),
        tick(delta = 1000 / 60, renderAudio = false) {
            now += delta; assert.ok(raf, 'The SDK must have scheduled its next frame'); raf(now);
            if (renderAudio) {
                const count = Math.round(delta * 48);
                sink.processor.process([], [[new Float32Array(count), new Float32Array(count)]]);
                context.currentFrame += count;
            }
        },
        close() { engine.destroy(); restore(); },
    };
}

test('default 1x preserves Sunset frame batches, PCM and battery at irregular timestamps', async () => {
    const trace = [1, 16, 18, 7, 31, 100, 16, 16, 19, 10, 16];
    const run = async loader => {
        const f = await fixture(loader);
        try {
            f.engine.start(); const frames = [];
            for (const delta of trace) { f.tick(delta); frames.push(f.count()); }
            return {frames, audio: f.audioMessages.map(m => m instanceof Int16Array ? Array.from(m) : m),
                battery: f.engine.exportBattery()};
        } finally { f.close(); }
    };
    assert.deepEqual(await run(load), await run(loadSunset));
});

test('optional private cartridge: 1x regression and 2x reach identical actual guest frames/video/battery',
    {skip: !process.env.SF_WORLD_SPEED_ROM}, async () => {
        const runtime = path.resolve('web/public/emulator');
        const require = createRequire(import.meta.url);
        const sandbox = {require, process, console, __dirname: runtime, __filename: runtime + '/mgba.js',
            module: {exports: {}}, exports: {}, TextDecoder, TextEncoder, WebAssembly,
            Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array,
            Float32Array, Float64Array, ArrayBuffer, setTimeout, clearTimeout};
        vm.runInNewContext(fs.readFileSync(runtime + '/mgba.js', 'utf8'), sandbox);
        const wasmBinary = fs.readFileSync(runtime + '/mgba.wasm');
        const real = {rom: new Uint8Array(fs.readFileSync(process.env.SF_WORLD_SPEED_ROM)),
            factory: () => sandbox.module.exports({wasmBinary})};
        const results = [];
        for (const [loader, speed, ticks] of [[loadSunset, 1, 100], [load, 1, 100], [load, 2, 50]]) {
            const f = await fixture(loader, 65536, real);
            try {
                if (loader === load) {
                    const before = await f.engine.saveState();
                    f.engine.setSpeed(speed);
                    assert.deepEqual(await f.engine.saveState(), before, 'Toggling cannot mutate actual core state');
                }
                f.engine.start(); f.tick(0);
                for (let n = 0; n < ticks; n++) f.tick(20);
                const ptr = f.core._mgbawasm_video_ptr();
                results.push({frames: f.count(), battery: f.engine.exportBattery(),
                    video: createHash('sha256').update(f.core.HEAPU8.subarray(ptr, ptr + 240 * 160 * 4)).digest('hex')});
            } finally { f.close(); }
        }
        assert.deepEqual(results[1], results[0], 'World 1x retains actual Sunset guest execution');
        assert.deepEqual(results[2], results[0], 'World 2x reaches the same guest result in half the elapsed time');
        assert.ok(results[0].frames >= 119);
        console.log(`Actual cartridge: ${results[0].frames} matching guest frames; video ${results[0].video}`);
    });

test('2x doubles guest execution and source consumption through the actual worklet', async () => {
    for (const rate of [32768, 65536]) {
        const runs = [];
        for (const speed of [1, 2]) {
            const f = await fixture(load, rate);
            try {
                assert.equal(f.engine.getSpeed(), 1);
                f.engine.setSpeed(speed); f.engine.start();
                // Establish the SDK wall anchor before a two-second continuous run.
                f.tick(0);
                f.sink().port.onmessage({data: {type: 'diagnostics', enabled: true, epoch: 1}});
                for (let n = 0; n < 120; n++) f.tick(1000 / 60, true);
                const sink = f.sink();
                assert.equal(sink.ratio, rate * speed / 48000);
                assert.equal(sink.prefillFrames, Math.ceil(rate * speed * .04));
                assert.equal(sink.diagnostics.droppedSourceFrames, 0);
                assert.equal(sink.diagnostics.underrunOutputFrames, 0);
                assert.ok(sink.started, 'Rendered audio must actually start');
                assert.ok(sink.pos > rate * speed * 1.8, 'Audio must consume at the selected rate');
                runs.push({frames: f.count(), consumed: sink.pos});
            } finally { f.close(); }
        }
        assert.ok(Math.abs(runs[0].frames - 120) <= 1);
        assert.ok(Math.abs(runs[1].frames - 240) <= 1);
        assert.ok(Math.abs(runs[1].consumed / runs[0].consumed - 2) < .02);
    }
});

test('speed changes neither run/reset the guest nor modify battery and reject unsupported values', async () => {
    const f = await fixture();
    try {
        f.engine.start(); f.tick(); f.tick();
        const before = f.core.HEAPU8.slice(), counter = f.count();
        const audioBefore = {w: f.sink().w, pos: f.sink().pos, started: f.sink().started};
        for (const value of [0, 3, -1, NaN, Infinity, '2', null, undefined, true]) {
            assert.throws(() => f.engine.setSpeed(value), RangeError);
            assert.equal(f.engine.getSpeed(), 1);
        }
        assert.equal(f.engine.setSpeed(2), 2); assert.equal(f.engine.setSpeed(2), 2);
        assert.equal(f.count(), counter); assert.deepEqual(f.core.HEAPU8, before);
        assert.deepEqual({w: f.sink().w, pos: f.sink().pos, started: f.sink().started}, audioBefore,
            'Changing rate must not flush or re-prime the existing audio queue');
        f.tick(1000 / 60); assert.ok(f.count() - counter <= 2, 'No old elapsed-time catch-up burst');
        const after = f.count(); f.engine.setSpeed(1); f.tick(1000 / 60);
        assert.ok(f.count() - after <= 1);
    } finally { f.close(); }
});

test('reset, reboot, import and paused controls retain selected speed; new instances default to 1x', async () => {
    const f = await fixture();
    try {
        const battery = f.engine.exportBattery();
        f.engine.setSpeed(2);
        f.engine.reset(); assert.equal(f.engine.getSpeed(), 2);
        assert.equal(f.audioMessages.filter(m => m?.rate).at(-1).rate, 131072);
        assert.equal(f.engine.config.write('gbModel', 'cgb'), true); f.engine.reset();
        assert.equal(f.engine.getSpeed(), 2);
        f.engine.importBattery(battery);
        assert.deepEqual(f.engine.exportBattery(), battery);
        assert.equal(f.engine.getSpeed(), 2);
        assert.equal(f.audioMessages.filter(m => m?.rate).at(-1).rate, 131072);
        f.engine.start(); f.engine.pause(); f.engine.setSpeed(1);
        assert.equal(f.engine.getSpeed(), 1); f.engine.resume();
        f.tick(); f.tick(); assert.ok(f.count() <= 2);
        f.setRate(32768); f.engine.setSpeed(2); f.tick();
        assert.equal(f.audioMessages.filter(m => m?.rate).at(-1).rate, 65536);
    } finally { f.close(); }
    const fresh = await fixture();
    try { assert.equal(fresh.engine.getSpeed(), 1); } finally { fresh.close(); }
});
