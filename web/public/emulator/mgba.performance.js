/** Explicit, one-shot browser diagnostics. No guest-consumption or paint claims. */
const MAX_TICK_SAMPLES = 160000; // Ten minutes at up to240Hz, with bounded margin.
const MAX_INPUT_SAMPLES = 40000;
const MAX_DURATION_MS = 600000;
const AUDIO_COUNTERS = [
    'warmupOutputFrames', 'underrunOutputFrames', 'droppedSourceFrames',
    'renderedOutputFrames', 'processQuanta', 'observedThroughOutputFrame',
];
const INPUT_TIMES = ['domToDispatchMs', 'dispatchToFrameMs', 'dispatchToSubmitMs'];
const TICK_TIMES = ['rafGapMs', 'runMs', 'renderMs'];
const FRAME_COUNTS = [
    'requestedFrames', 'executedFrames', 'actualVideoFrames',
    'discardedFrames', 'renderSubmissions',
];

function nonnegative(value, name, integer = false) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 ||
        (integer && !Number.isSafeInteger(value))) {
        throw new TypeError(`Invalid ${name}`);
    }
}

function distribution(values) {
    if (!values.length) return { count: 0 };
    const sorted = [...values].sort((a, b) => a - b);
    const percentile = (percent) => sorted[Math.ceil(percent * sorted.length / 100) - 1];
    return {
        count: sorted.length, min: sorted[0], max: sorted[sorted.length - 1],
        mean: sorted.reduce((mean, value, index) => mean + (value - mean) / (index + 1), 0),
        p50: percentile(50), p95: percentile(95), p99: percentile(99),
    };
}

/** Validate the asynchronous final audio tail after the timed probe has closed. */
export function validateFinalAudioSnapshot(snapshot, previous, epoch) {
    if (!snapshot || snapshot.type !== 'diagnostics' || snapshot.final !== true || snapshot.epoch !== epoch) {
        throw new TypeError('Invalid final audio epoch or marker');
    }
    for (const name of AUDIO_COUNTERS) {
        nonnegative(snapshot[name], name, true);
        if (snapshot[name] < previous[name]) throw new TypeError(`Final audio counter regressed: ${name}`);
    }
    nonnegative(snapshot.firstOutputFrame, 'firstOutputFrame', true);
    nonnegative(snapshot.outputSampleRate, 'outputSampleRate', true);
    nonnegative(snapshot.queueDepthFrames, 'queueDepthFrames');
    if (!snapshot.outputSampleRate || snapshot.observedThroughOutputFrame - snapshot.firstOutputFrame !== snapshot.renderedOutputFrames) {
        throw new TypeError('Invalid final audio output interval');
    }
    return snapshot;
}

/**
 * start(context), record(type, data), stop(reason): a single diagnostic epoch.
 * Malformed active records stop with valid=false and return false. Inactive
 * records return false. Reports contain aggregates only, never unbounded logs.
 * Input latency fields are optional; supersededBeforeFrame is required.
 * Audio counters are cumulative since this epoch began, never per-message deltas.
 */
export function createPerformanceProbe(options = {}, environment = {}) {
    if (!options || typeof options !== 'object' || !environment || typeof environment !== 'object') {
        throw new TypeError('Probe options and environment must be objects');
    }
    const durationMs = options.durationMs === undefined ? 10000 : options.durationMs;
    if (typeof durationMs !== 'number' || !Number.isFinite(durationMs) ||
        durationMs <= 0 || durationMs > MAX_DURATION_MS) {
        throw new RangeError('durationMs must be positive and at most 600000');
    }
    if (options.onReport !== undefined && typeof options.onReport !== 'function') {
        throw new TypeError('onReport must be a function');
    }
    const onReport = options.onReport;
    const now = environment.now ?? (() => performance.now());
    const schedule = environment.setTimeout ?? ((fn, delay) => globalThis.setTimeout(fn, delay));
    const cancel = environment.clearTimeout ?? ((id) => globalThis.clearTimeout(id));
    if ([now, schedule, cancel].some((fn) => typeof fn !== 'function')) {
        throw new TypeError('Invalid probe clock or timer');
    }

    let state = 'new', timer, report, context, startedAtMs, lastTime;
    let valid = true, error = null;
    const ticks = { count: 0, visible: 0, hidden: 0, videoFrameMismatchTicks: 0 };
    const frameTotals = Object.fromEntries(FRAME_COUNTS.map((name) => [name, 0]));
    const tickTimes = Object.fromEntries(TICK_TIMES.map((name) => [name, []]));
    const inputs = { count: 0, supersededBeforeFrame: 0 };
    const inputTimes = Object.fromEntries(INPUT_TIMES.map((name) => [name, []]));
    const visibility = { visible: 0, hidden: 0 };
    const invalidations = { pause: 0, reset: 0 };
    const audio = {
        snapshots: 0, final: false, queueDepthFrames: null,
        minQueueDepthFrames: null, maxQueueDepthFrames: null,
        ...Object.fromEntries(AUDIO_COUNTERS.map((name) => [name, 0])),
    };

    function stop(reason = 'manual') {
        if (report) return report;
        if (state !== 'active') return null;
        // Close before invoking application code, including a reentrant onReport.
        state = 'stopped';
        cancel(timer);
        if (typeof reason !== 'string' || !reason.length || reason.length > 128) {
            valid = false;
            error ??= 'Invalid stop reason';
            reason = 'invalid-data';
        }
        let endedAtMs = lastTime;
        try {
            endedAtMs = now();
            nonnegative(endedAtMs, 'clock');
            if (endedAtMs < lastTime) throw new TypeError('Clock regressed');
        } catch (failure) {
            valid = false;
            error ??= failure.message;
            endedAtMs = lastTime;
        }
        report = {
            schema: 1, reason, valid, error, context, durationMs,
            startedAtMs, endedAtMs, elapsedMs: endedAtMs - startedAtMs,
            ticks: {
                ...ticks, ...frameTotals,
                ...Object.fromEntries(TICK_TIMES.map((name) => [name, distribution(tickTimes[name])])),
            },
            input: {
                ...inputs,
                ...Object.fromEntries(INPUT_TIMES.map((name) => [name, distribution(inputTimes[name])])),
            },
            audio: { ...audio }, visibility: { ...visibility },
            scope: {
                valid: valid && !invalidations.pause && !invalidations.reset,
                uninterrupted: !invalidations.pause && !invalidations.reset,
                foregroundOnly: ticks.hidden === 0 && visibility.hidden === 0,
                invalidations: { ...invalidations },
                guestKeyConsumptionProven: false, actualPaintProven: false,
                mobilePerformanceProven: false,
            },
            limits: [
                'Browser diagnostic epoch; frame counts are not game update counts',
                'Input timings end at dispatch, completed core batch upper bound, or render submission',
                'Render submissions do not prove physical presentation',
                'Audio counters cover only reported worklet observations; final=false is incomplete',
                'Nearest-rank percentiles; at most 160000 tick and 40000 input records',
            ],
        };
        onReport?.(report);
        return report;
    }

    function reject(failure) {
        valid = false;
        error = failure.message;
        stop('invalid-data');
        return false;
    }

    function record(type, data = {}) {
        if (state !== 'active') return false;
        try {
            const time = now();
            nonnegative(time, 'clock');
            if (time < lastTime) throw new TypeError('Clock regressed');
            lastTime = time;
            // A delayed browser timer must not extend the sample window.
            if (time - startedAtMs >= durationMs) {
                stop('duration');
                return false;
            }
            if (!data || typeof data !== 'object') throw new TypeError('Missing event data');
            if (type === 'tick') {
                if (ticks.count === MAX_TICK_SAMPLES) throw new RangeError('Tick sample capacity exceeded');
                for (const name of TICK_TIMES) nonnegative(data[name], name);
                for (const name of FRAME_COUNTS) nonnegative(data[name], name, true);
                if (data.rafGapMeasured !== undefined && typeof data.rafGapMeasured !== 'boolean') {
                    throw new TypeError('Invalid rafGapMeasured flag');
                }
                if (data.visibility !== 'visible' && data.visibility !== 'hidden') {
                    throw new TypeError('Invalid tick visibility');
                }
                if (data.requestedFrames !== data.executedFrames + data.discardedFrames) {
                    throw new TypeError('Requested frames must equal executed plus discarded frames');
                }
                for (const name of FRAME_COUNTS) {
                    if (!Number.isSafeInteger(frameTotals[name] + data[name])) {
                        throw new RangeError('Frame total overflow');
                    }
                }
                ++ticks.count;
                ++ticks[data.visibility];
                if (data.actualVideoFrames !== data.executedFrames) ++ticks.videoFrameMismatchTicks;
                for (const name of FRAME_COUNTS) frameTotals[name] += data[name];
                for (const name of TICK_TIMES) {
                    if (name !== 'rafGapMs' || data.rafGapMeasured !== false) {
                        tickTimes[name].push(data[name]);
                    }
                }
            } else if (type === 'input') {
                if (inputs.count === MAX_INPUT_SAMPLES) throw new RangeError('Input sample capacity exceeded');
                if (typeof data.supersededBeforeFrame !== 'boolean') {
                    throw new TypeError('Missing input supersededBeforeFrame');
                }
                const present = INPUT_TIMES.filter((name) => data[name] !== undefined);
                if (!present.length && !data.supersededBeforeFrame) {
                    throw new TypeError('Input record lacks latency or supersession');
                }
                for (const name of present) nonnegative(data[name], name);
                ++inputs.count;
                if (data.supersededBeforeFrame) ++inputs.supersededBeforeFrame;
                for (const name of present) inputTimes[name].push(data[name]);
            } else if (type === 'audio') {
                if (audio.final) throw new TypeError('Audio received after final snapshot');
                for (const name of AUDIO_COUNTERS) {
                    nonnegative(data[name], name, true);
                    if (data[name] < audio[name]) throw new TypeError(`Audio counter regressed: ${name}`);
                }
                nonnegative(data.queueDepthFrames, 'queueDepthFrames');
                if (typeof data.final !== 'boolean') throw new TypeError('Missing audio final flag');
                for (const name of AUDIO_COUNTERS) audio[name] = data[name];
                ++audio.snapshots;
                audio.final = data.final;
                audio.queueDepthFrames = data.queueDepthFrames;
                audio.minQueueDepthFrames = Math.min(audio.minQueueDepthFrames ?? Infinity, data.queueDepthFrames);
                audio.maxQueueDepthFrames = Math.max(audio.maxQueueDepthFrames ?? 0, data.queueDepthFrames);
            } else if (type === 'visibility') {
                if (data.state !== 'visible' && data.state !== 'hidden') {
                    throw new TypeError('Invalid visibility state');
                }
                ++visibility[data.state];
            } else if (type === 'pause' || type === 'reset') {
                ++invalidations[type];
                stop(type);
            } else {
                throw new TypeError('Unknown performance event type');
            }
            return true;
        } catch (failure) {
            // An application onReport error is not malformed measurement data.
            if (state !== 'active') throw failure;
            return reject(failure);
        }
    }

    return {
        get active() { return state === 'active'; },
        start(value = {}) {
            if (state !== 'new') throw new Error('Create a new probe for each diagnostic epoch');
            const time = now();
            nonnegative(time, 'clock');
            const serialized = JSON.stringify(value);
            if (serialized === undefined || serialized.length > 16384) {
                throw new TypeError('Diagnostic context must be bounded JSON');
            }
            context = JSON.parse(serialized);
            if (context?.visibility === 'hidden') ++visibility.hidden;
            startedAtMs = lastTime = time;
            state = 'active';
            timer = schedule(() => stop('duration'), durationMs);
            return true;
        },
        record, stop,
    };
}
