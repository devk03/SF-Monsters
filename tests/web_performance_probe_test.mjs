import assert from 'node:assert/strict';
import test from 'node:test';
import { createPerformanceProbe, validateFinalAudioSnapshot } from '../web/public/emulator/mgba.performance.js';

function fixture(options = {}) {
    let time = 100;
    const scheduled = [], cancelled = [], reports = [];
    const probe = createPerformanceProbe({ ...options, onReport: (report) => reports.push(report) }, {
        now: () => time,
        setTimeout: (fn, delay) => { scheduled.push({ fn, delay }); return scheduled.length; },
        clearTimeout: (id) => cancelled.push(id),
    });
    return { probe, scheduled, cancelled, reports, time: (value) => { time = value; } };
}

const tick = (extra = {}) => ({
    rafGapMs: 16, requestedFrames: 1, executedFrames: 1, actualVideoFrames: 1,
    discardedFrames: 0, runMs: 2, renderMs: 1, renderSubmissions: 1,
    visibility: 'visible', ...extra,
});
const audio = (extra = {}) => ({
    warmupOutputFrames: 10, underrunOutputFrames: 2, droppedSourceFrames: 3,
    renderedOutputFrames: 100, processQuanta: 1, queueDepthFrames: 20,
    observedThroughOutputFrame: 112, final: false, ...extra,
});

test('records capped frame demand, real video increments and hidden ticks separately', () => {
    const { probe } = fixture();
    probe.start({ rom: 'immutable-test-ROM' });
    assert.equal(probe.record('tick', tick({ requestedFrames: 9, executedFrames: 5,
        actualVideoFrames: 4, discardedFrames: 4, rafGapMs: 150 })), true);
    probe.record('tick', tick({ visibility: 'hidden', runMs: 4 }));
    probe.record('visibility', { state: 'hidden' });
    const report = probe.stop();
    assert.equal(report.valid, true);
    assert.equal(report.ticks.requestedFrames, 10);
    assert.equal(report.ticks.executedFrames, 6);
    assert.equal(report.ticks.actualVideoFrames, 5);
    assert.equal(report.ticks.discardedFrames, 4);
    assert.equal(report.ticks.videoFrameMismatchTicks, 1);
    assert.equal(report.ticks.renderSubmissions, 2);
    assert.equal(report.ticks.hidden, 1);
    assert.equal(report.ticks.visible, 1);
    assert.equal(report.scope.foregroundOnly, false);
    assert.equal(report.scope.actualPaintProven, false);
});

test('cumulative worklet snapshots use final maxima, not a sum of snapshots', () => {
    const { probe } = fixture();
    probe.start();
    probe.record('audio', audio());
    probe.record('audio', audio({ underrunOutputFrames: 7, renderedOutputFrames: 200,
        observedThroughOutputFrame: 217, processQuanta: 2, queueDepthFrames: 12, final: true }));
    const report = probe.stop();
    assert.equal(report.audio.underrunOutputFrames, 7);
    assert.equal(report.audio.warmupOutputFrames, 10);
    assert.equal(report.audio.droppedSourceFrames, 3);
    assert.equal(report.audio.renderedOutputFrames, 200);
    assert.equal(report.audio.processQuanta, 2);
    assert.equal(report.audio.minQueueDepthFrames, 12);
    assert.equal(report.audio.maxQueueDepthFrames, 20);
    assert.equal(report.audio.observedThroughOutputFrame, 217);
    assert.equal(report.audio.final, true);
});

test('unknown initial rAF gap is excluded without losing tick or frame totals', () => {
    const { probe } = fixture();
    probe.start();
    probe.record('tick', tick({ rafGapMs: 0, rafGapMeasured: false }));
    probe.record('tick', tick({ rafGapMs: 20, rafGapMeasured: true }));
    const report = probe.stop();
    assert.equal(report.ticks.count, 2);
    assert.equal(report.ticks.executedFrames, 2);
    assert.equal(report.ticks.runMs.count, 2);
    assert.equal(report.ticks.renderMs.count, 2);
    assert.deepEqual(report.ticks.rafGapMs, {
        count: 1, min: 20, max: 20, mean: 20, p50: 20, p95: 20, p99: 20,
    });
});

test('creates no timer before explicit start; expires once and stops idempotently', () => {
    let closes = 0;
    const f = fixture({ onClose() { ++closes; } });
    assert.equal(f.probe.active, false);
    assert.equal(f.scheduled.length, 0);
    assert.equal(f.probe.stop(), null);
    f.probe.start();
    assert.equal(f.scheduled.length, 1);
    assert.equal(f.scheduled[0].delay, 10000);
    f.time(10100);
    f.scheduled[0].fn();
    const report = f.probe.stop('again');
    assert.equal(report.reason, 'duration');
    assert.equal(report.elapsedMs, 10000);
    assert.equal(f.probe.active, false);
    assert.equal(f.reports.length, 1);
    assert.equal(f.probe.stop(), report);
    assert.equal(closes, 1);
    assert.deepEqual(f.cancelled, [1]);
    assert.equal(f.probe.record('tick', tick()), false);
    assert.throws(() => f.probe.start(), /new probe/);
});

test('manual stop cancels timeout; a late timer cannot publish a second report', () => {
    const f = fixture({ durationMs: 600000 });
    f.probe.start();
    const report = f.probe.stop('complete');
    f.scheduled[0].fn();
    assert.equal(f.scheduled[0].delay, 600000);
    assert.equal(f.reports.length, 1);
    assert.equal(f.reports[0], report);
    assert.deepEqual(f.cancelled, [1]);
});

test('reentrant reporting sees the same closed report and publishes once', () => {
    let probe, calls = 0;
    probe = createPerformanceProbe({ onReport: (report) => {
        ++calls;
        assert.equal(probe.active, false);
        assert.equal(probe.stop('reentrant'), report);
    } }, { now: () => 100, setTimeout: () => 1, clearTimeout: () => {} });
    probe.start();
    probe.stop();
    assert.equal(calls, 1);
});

test('onClose captures the boundary before reporting and is idempotent under reentry', () => {
    const order = [];
    let f;
    f = fixture({ onClose(close) {
        order.push('close');
        assert.equal(f.probe.active, false);
        assert.equal(f.probe.record('tick', tick()), false);
        assert.equal(f.probe.stop('reentrant'), null);
        assert.equal(f.reports.length, 0);
        assert.equal(close.reason, 'complete');
        assert.equal(close.endedAtMs, 200);
        assert.equal(close.elapsedMs, 100);
        f.time(5000); // Application close work cannot extend the recorded epoch.
    } });
    f.probe.start();
    f.probe.record('tick', tick());
    f.time(200);
    const report = f.probe.stop('complete');
    order.push('report');
    assert.equal(f.reports[0], report);
    assert.equal(report.endedAtMs, 200);
    assert.equal(report.elapsedMs, 100);
    assert.equal(report.ticks.count, 1);
    assert.equal(f.probe.stop(), report);
    f.scheduled[0].fn();
    assert.deepEqual(order, ['close', 'report']);
    assert.equal(f.reports.length, 1);
    assert.deepEqual(f.cancelled, [1]);
});

test('onClose failure invalidates the report but still delivers it exactly once', () => {
    for (const failure of [new Error('Close failed'), 'Close failed']) {
        let closes = 0;
        const f = fixture({ onClose() { ++closes; throw failure; } });
        f.probe.start();
        const report = f.probe.stop();
        f.scheduled[0].fn();
        assert.equal(report.valid, false);
        assert.equal(report.scope.valid, false);
        assert.equal(report.error, 'Close failed');
        assert.equal(closes, 1);
        assert.equal(f.reports.length, 1);
        assert.equal(f.probe.stop(), report);
    }
    for (const onClose of [null, 1, 'callback', {}]) {
        assert.throws(() => createPerformanceProbe({ onClose }), /onClose/);
    }
});

test('delayed timeout cannot extend the accepted sample window', () => {
    const f = fixture({ durationMs: 50 });
    f.probe.start();
    f.time(151);
    assert.equal(f.probe.record('tick', tick()), false);
    assert.equal(f.reports[0].ticks.count, 0);
    assert.equal(f.reports[0].reason, 'duration');
});

test('nearest-rank percentiles preserve tail samples and optional input stages', () => {
    const { probe } = fixture();
    probe.start();
    for (let value = 1; value <= 100; ++value) probe.record('tick', tick({ runMs: value }));
    probe.record('input', { domToDispatchMs: 3, supersededBeforeFrame: false });
    probe.record('input', { dispatchToFrameMs: 5, dispatchToSubmitMs: 8, supersededBeforeFrame: false });
    probe.record('input', { supersededBeforeFrame: true });
    const report = probe.stop();
    assert.deepEqual(report.ticks.runMs, { count: 100, min: 1, max: 100,
        mean: 50.5, p50: 50, p95: 95, p99: 99 });
    assert.equal(report.input.domToDispatchMs.count, 1);
    assert.equal(report.input.dispatchToFrameMs.p99, 5);
    assert.equal(report.input.dispatchToSubmitMs.p99, 8);
    assert.equal(report.input.supersededBeforeFrame, 1);
    assert.equal(report.scope.guestKeyConsumptionProven, false);
});

test('duplicate-heavy samples retain exact rank weights and accurate means', () => {
    const { probe } = fixture();
    probe.start();
    // 1000 observations: 900 at.1, 50 at.2, 40 at.3, 10 at3.3.
    // The 500th/950th/990th observations must be.1/.2/.3 respectively.
    for (const [value, count] of [[.3, 40], [3.3, 10], [.1, 900], [.2, 50]]) {
        for (let i = 0; i < count; ++i) probe.record('tick', tick({ runMs: value }));
    }
    const report = probe.stop();
    assert.equal(report.ticks.runMs.count, 1000);
    assert.equal(report.ticks.runMs.min, .1);
    assert.equal(report.ticks.runMs.max, 3.3);
    assert.equal(report.ticks.runMs.p50, .1);
    assert.equal(report.ticks.runMs.p95, .2);
    assert.equal(report.ticks.runMs.p99, .3);
    assert.ok(Math.abs(report.ticks.runMs.mean - .145) < 1e-15);
});

test('distinct adjacent Number values remain distinct in timing distributions', () => {
    const { probe } = fixture();
    probe.start();
    probe.record('input', { domToDispatchMs: .30000000000000004, supersededBeforeFrame: false });
    probe.record('input', { domToDispatchMs: .3, supersededBeforeFrame: false });
    const report = probe.stop();
    assert.equal(report.input.domToDispatchMs.count, 2);
    assert.equal(report.input.domToDispatchMs.min, .3);
    assert.equal(report.input.domToDispatchMs.max, .30000000000000004);
    assert.equal(report.input.domToDispatchMs.p50, .3);
    assert.equal(report.input.domToDispatchMs.p95, .30000000000000004);
    assert.equal(report.input.domToDispatchMs.p99, .30000000000000004);
});

test('invalid and missing event values close the epoch without partial acceptance', () => {
    const cases = [
        ['tick', {}], ['tick', tick({ runMs: NaN })],
        ['tick', tick({ discardedFrames: 1 })], ['tick', tick({ executedFrames: 0.5 })],
        ['tick', tick({ visibility: 'unknown' })],
        ['tick', tick({ rafGapMeasured: 'false' })],
        ['input', { domToDispatchMs: -1, supersededBeforeFrame: false }],
        ['input', { supersededBeforeFrame: false }], ['input', { domToDispatchMs: 1 }],
        ['audio', {}], ['audio', audio({ final: undefined })],
        ['audio', audio({ queueDepthFrames: Infinity })], ['visibility', { state: 'unknown' }],
        ['unrecognized', {}],
    ];
    for (const [kind, value] of cases) {
        const f = fixture();
        f.probe.start();
        assert.equal(f.probe.record(kind, value), false, kind);
        assert.equal(f.probe.active, false);
        assert.equal(f.reports.length, 1);
        assert.equal(f.reports[0].valid, false);
        assert.equal(f.reports[0].reason, 'invalid-data');
        assert.equal(f.reports[0].ticks.count, 0);
        assert.equal(f.reports[0].input.count, 0);
        assert.equal(f.reports[0].audio.snapshots, 0);
    }
});

test('counter regressions and post-final audio cannot become plausible totals', () => {
    for (const next of [audio({ underrunOutputFrames: 1 }), audio({ observedThroughOutputFrame: 111 })]) {
        const f = fixture();
        f.probe.start();
        f.probe.record('audio', audio());
        assert.equal(f.probe.record('audio', next), false);
        assert.equal(f.reports[0].valid, false);
        assert.equal(f.reports[0].audio.underrunOutputFrames, 2);
    }
    const f = fixture();
    f.probe.start();
    f.probe.record('audio', audio({ final: true }));
    assert.equal(f.probe.record('audio', audio()), false);
});

test('pause/reset terminate and invalidate uninterrupted measurement scope', () => {
    for (const kind of ['pause', 'reset']) {
        const f = fixture();
        f.probe.start();
        assert.equal(f.probe.record(kind, {}), true);
        assert.equal(f.reports[0].scope.valid, false);
        assert.equal(f.reports[0].scope.invalidations[kind], 1);
        assert.equal(f.reports[0].reason, kind);
    }
});

test('capacity overflow invalidates the report instead of silently dropping samples', () => {
    const f = fixture();
    f.probe.start();
    for (let i = 0; i < 160000; ++i) assert.equal(f.probe.record('tick', tick()), true);
    assert.equal(f.probe.record('tick', tick()), false);
    assert.equal(f.reports[0].ticks.count, 160000);
    assert.equal(f.reports[0].valid, false);
    assert.match(f.reports[0].error, /capacity/);
});

test('invalid duration and clock values fail closed', () => {
    for (const durationMs of [0, -1, Infinity, NaN, 600001, '100']) {
        assert.throws(() => createPerformanceProbe({ durationMs }), /durationMs/);
    }
    const f = fixture();
    f.probe.start();
    f.time(99);
    assert.equal(f.probe.record('tick', tick()), false);
    assert.equal(f.reports[0].valid, false);
    assert.equal(f.reports[0].elapsedMs, 0);
});

test('initially hidden context cannot become a foreground-only report without hidden ticks', () => {
    const f = fixture();
    f.probe.start({ visibility: 'hidden' });
    f.probe.record('tick', tick());
    assert.equal(f.probe.stop().scope.foregroundOnly, false);
});

test('final audio tail requires exact epoch, nonregressing counters and a contiguous output interval', () => {
    const previous = audio();
    const final = { ...audio({ renderedOutputFrames: 128, processQuanta: 2,
        observedThroughOutputFrame: 256, final: true }), type: 'diagnostics',
        epoch: 7, firstOutputFrame: 128, outputSampleRate: 48000 };
    assert.equal(validateFinalAudioSnapshot(final, previous, 7), final);
    for (const changed of [{epoch: 6}, {final: 'true'}, {underrunOutputFrames: 1},
        {queueDepthFrames: NaN}, {renderedOutputFrames: 127}, {outputSampleRate: 0},
        {droppedSourceFrames: undefined}, {processQuanta: -1}]) {
        assert.throws(() => validateFinalAudioSnapshot({ ...final, ...changed }, previous, 7));
    }
});
