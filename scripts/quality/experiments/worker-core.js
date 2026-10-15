/* Private feasibility proof only. Classic Worker; unchanged core/WASM/worklet. */
'use strict';
const LIMITS = Object.freeze({ durationMs: 600000, runDurationMs: 900000, ticks: 160000, inputs: 40000, audioSnapshots: 32000 });
let mod = null, port = null, audioPtr = 0, fps = 0, coreRate = 0, booting = false;
let running = false, loopTimer = null, stopTimer = null, origin = null;
let due = 0, backlog = 0, executed = 0, dropped = 0, playbackEpoch = 0;
let enqueued = 0, consumed = 0, lastAudio = null, lastAudioAt = null;
let measurement = null, closing = null, finalTimer = null, lastReport = null, epoch = 0;
let latestSequence = -1, latestMask = 0, pendingInput = null, videoInFlight = false, recycled = null;
let bootDiscardedSourceFrames = 0, batteryVerified = false;
let playbackAcknowledged = false;
const now = () => performance.now();
const absoluteNow = () => performance.timeOrigin + now();
const counter = () => mod._mgbawasm_frame_counter() >>> 0;
function finite(value, name, max = Number.MAX_VALUE) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > max) throw new Error('Invalid ' + name);
  return value;
}
function integer(value, name, max = Number.MAX_SAFE_INTEGER) {
  finite(value, name, max); if (!Number.isSafeInteger(value)) throw new Error('Invalid integer ' + name); return value;
}
function bytes(value, name, max) {
  const view = value instanceof ArrayBuffer ? new Uint8Array(value) : value;
  if (!(view instanceof Uint8Array) || !view.length || view.length > max) throw new Error('Invalid bytes ' + name);
  return view;
}
function reply(request, value, transfer = []) {
  self.postMessage({ type: 'reply', id: request.id, ok: true, result: value, value }, transfer);
}
function failure(request, error) {
  self.postMessage({ type: 'reply', id: request.id, ok: false, error: String(error?.message ?? error) });
}
function heapCopy(view, use) {
  const ptr = mod._malloc(view.byteLength); if (!ptr) throw new Error('Core allocation failed');
  try { mod.HEAPU8.set(view, ptr); return use(ptr); } finally { mod._free(ptr); }
}
function syncRate() {
  const rate = mod._mgbawasm_sample_rate();
  if (rate > 0 && rate !== coreRate) { coreRate = rate; port.postMessage({ rate }); }
}
function drainAudio(send = true) {
  let drained = 0;
  for (let reads = 0; reads < 32; ++reads) {
    const count = mod._mgbawasm_read_audio(audioPtr, 4096);
    if (!count) return drained;
    if (!Number.isSafeInteger(count) || count < 0 || count > 4096) throw new Error('Invalid core audio count');
    drained += count;
    if (send) {
      const chunk = mod.HEAP16.slice(audioPtr >> 1, (audioPtr >> 1) + count * 2);
      port.postMessage(chunk, [chunk.buffer]); enqueued += count;
      if (measurement) measurement.sourceFramesPosted += count;
    }
    if (count < 4096) return drained;
  }
  throw new Error('Unbounded core audio drain');
}
function audioMessage(event) {
  const data = event.data;
  if (typeof data === 'number') { consumed = data; return; }
  if (data?.type === 'playback-reset' && data.epoch === playbackEpoch) { playbackAcknowledged = true; return; }
  if (data?.type === 'diagnostics') {
    lastAudio = data; lastAudioAt = absoluteNow();
    if (measurement && data.epoch === measurement.epoch) {
      if (measurement.audioSnapshots.length === LIMITS.audioSnapshots) closeMeasurement('audio-snapshot-capacity');
      else measurement.audioSnapshots.push({ workerReceivedAt: lastAudioAt, snapshot: data });
    }
    if (closing && data.epoch === closing.epoch && data.final === true) finishMeasurement(data);
  }
}
function snapshot() {
  return { running, counter: mod ? counter() : null, framerate: fps, coreRate,
    workerAt: absoluteNow(), workerTimeOrigin: performance.timeOrigin, clockOriginMs: origin,
    due, backlog, executed, overflowDropped: dropped, latestMask, latestSequence,
    enqueuedSourceFrames: enqueued, consumedSourceFrames: consumed,
    estimatedSourceQueue: Math.max(0, enqueued - consumed),
    audioLatest: lastAudio, audioLatestReceivedAt: lastAudioAt,
    playbackEpoch, playbackAcknowledged, batteryVerified, bootDiscardedSourceFrames,
    measurementActive: measurement !== null, closing: closing !== null,
    scope: 'Worker clock/core counters and raw worklet reports; queue estimate includes messages in flight; no AudioContext/hardware clock claim.' };
}
function finishMeasurement(audioFinalSnapshot) {
  if (!closing) return;
  clearTimeout(finalTimer); finalTimer = null;
  const report = closing; closing = null;
  report.audioFinalSnapshot = audioFinalSnapshot;
  report.audioFinalAcknowledged = audioFinalSnapshot !== null;
  report.audioFinalError = audioFinalSnapshot ? null : 'Raw final worklet acknowledgement timed out after500ms';
  const requests = report.requests; delete report.requests;
  lastReport = report;
  for (const request of requests) reply(request, report);
}
function closeMeasurement(reason = 'duration', request = null) {
  if (closing) { if (request) closing.requests.push(request); return; }
  if (!measurement) { if (request) reply(request, lastReport); return; }
  const active = measurement; measurement = null; clearTimeout(active.timer);
  delete active.timer;
  active.reason = reason; active.endedAtMs = now(); active.endedAt = absoluteNow();
  active.elapsedMs = active.endedAtMs - active.startedAtMs; active.finalGuestCounter = counter();
  active.finalBacklog = backlog; active.pendingInputAtEnd = pendingInput !== null;
  active.finalPacing = { due, executed, overflowDropped: dropped, backlog };
  active.finalSourceFramesPosted = enqueued;
  if (request) active.requests.push(request);
  closing = active;
  // This direct port message is ordered after every measured audio chunk.
  port.postMessage({ type: 'diagnostics', enabled: false, epoch: active.epoch });
  finalTimer = setTimeout(() => finishMeasurement(null), 500);
}
function pause(reason = 'pause') {
  running = false; clearTimeout(loopTimer); clearTimeout(stopTimer); loopTimer = stopTimer = null;
  closeMeasurement(reason);
  const abandoned = backlog;
  origin = null; due = backlog = executed = dropped = 0;
  return { ...snapshot(), abandonedFrames: abandoned, reason };
}
function tick() {
  if (!running) return;
  try {
    const started = now();
    // Admission precedes core execution. A batch admitted before the deadline
    // is recorded in full before close, even if its <=5 frames cross it.
    if (measurement && started >= measurement.deadlineMs) closeMeasurement('duration');
    if (origin === null) origin = started;
    const elapsed = started - origin, nextDue = Math.floor(elapsed / 1000 * fps);
    if (nextDue < due) throw new Error('Worker clock regressed');
    const fresh = nextDue - due, before = backlog, overflow = Math.max(0, before + fresh - 30);
    const pending = before + fresh - overflow, planned = Math.min(5, pending), beforeCounter = counter();
    const observed = measurement;
    if (observed && (observed.rawLedger.length === LIMITS.ticks || fresh > 65535)) {
      closeMeasurement('ledger-capacity');
    }
    syncRate();
    for (let i = 0; i < planned; ++i) { mod._mgbawasm_run_frame(); syncRate(); drainAudio(); }
    const actual = (counter() - beforeCounter) >>> 0;
    if (actual > planned) throw new Error('Core counter exceeds planned execution');
    due = nextDue; backlog = pending - actual; executed += actual; dropped += overflow;
    if (due !== executed + dropped + backlog) throw new Error('Worker debt conservation failed');
    if (observed && measurement === observed) {
      // [fresh, planned, actual, overflow, after, elapsedMsSinceClockOrigin,
      //  nativeCounterBefore, nativeCounterAfter]
      observed.rawLedger.push([fresh, planned, actual, overflow, backlog, elapsed, beforeCounter, counter()]);
      observed.maxPending = Math.max(observed.maxPending, pending);
      observed.maxBacklog = Math.max(observed.maxBacklog, backlog);
      observed.maxWorkerTickGapMs = Math.max(observed.maxWorkerTickGapMs, started - observed.lastTickMs);
      observed.lastTickMs = started;
      if (pendingInput && actual) {
        if (observed.inputs.length === LIMITS.inputs) closeMeasurement('input-capacity');
        else observed.inputs.push({ ...pendingInput, superseded: false, firstGuestCounter: (beforeCounter + 1) >>> 0,
          completedBatchAt: absoluteNow() });
        pendingInput = null;
      }
      if (measurement === observed && now() >= observed.deadlineMs) closeMeasurement('duration');
    } else if (pendingInput && actual) pendingInput = null;
    loopTimer = setTimeout(tick, 5);
  } catch (error) {
    pause('worker-error'); self.postMessage({ type: 'worker-error', error: String(error?.stack ?? error) });
  }
}
async function boot(request) {
  if (mod || booting) throw new Error('Worker already booted or booting');
  booting = true;
  try {
    const rom = bytes(request.rom, 'rom', 32 * 1024 * 1024);
    if (!request.audioPort || typeof request.audioPort.postMessage !== 'function') throw new Error('Transfer the actual worklet MessagePort');
    port = request.audioPort; port.onmessage = audioMessage; port.start?.();
    importScripts(request.jsUrl);
    if (typeof createMgbaModule !== 'function') throw new Error('Unchanged core loader did not define createMgbaModule');
    mod = await createMgbaModule({ locateFile: name => name.endsWith('.wasm') ? request.wasmUrl : new URL(name, request.jsUrl).href });
    mod._mgbawasm_init(); mod._mgbawasm_set_log_level(1);
    if (!heapCopy(rom, ptr => mod._mgbawasm_load(ptr, rom.length, 0, 0, -1, 0, 1))) throw new Error('Native ROM load failed');
    mod._mgbawasm_set_idle_optimization?.(1); mod._mgbawasm_set_allow_opposing_directions?.(0);
    if (request.battery) {
      const battery = bytes(request.battery, 'battery', 1024 * 1024);
      if (![32768, 131072].includes(battery.length)) throw new Error('Unsupported native battery size');
      let initialized = false;
      for (let frame = 0; frame < 120; ++frame) {
        mod._mgbawasm_run_frame();
        if (mod._mgbawasm_sram_save() === battery.length) { initialized = true; break; }
      }
      if (!initialized) throw new Error('Native cartridge Flash did not initialize within120frames');
      if (!heapCopy(battery, ptr => mod._mgbawasm_sram_load(ptr, battery.length))) throw new Error('Native Flash load failed');
      if (mod._mgbawasm_sram_save() !== battery.length) throw new Error('Native Flash restored size differs');
      const ptr = mod._mgbawasm_sram_ptr();
      if (!ptr || battery.some((value, index) => mod.HEAPU8[ptr + index] !== value)) throw new Error('Native Flash round-trip differs');
      batteryVerified = true;
      mod._mgbawasm_reset();
    }
    if (request.state) {
      const state = bytes(request.state, 'state', 4 * 1024 * 1024);
      if (state.length !== mod._mgbawasm_state_size()) throw new Error('State size differs from unchanged core ABI');
      if (!heapCopy(state, ptr => mod._mgbawasm_state_load(ptr))) throw new Error('Native state load failed');
    }
    mod._mgbawasm_set_keys(0); audioPtr = mod._malloc(4096 * 4); if (!audioPtr) throw new Error('Audio scratch allocation failed');
    bootDiscardedSourceFrames = drainAudio(false); port.postMessage({ type: 'playback-reset', epoch: ++playbackEpoch }); syncRate();
    fps = mod._mgbawasm_framerate_micro() / 1e6;
    if (!Number.isFinite(fps) || fps <= 0) throw new Error('Invalid native framerate');
    return { ...snapshot(), width: mod._mgbawasm_video_width(), height: mod._mgbawasm_video_height() };
  } finally { booting = false; }
}
function start(request) {
  if (!mod) throw new Error('Boot first');
  if (running) return snapshot();
  const duration = integer(request.durationMs ?? LIMITS.durationMs, 'finite run duration', LIMITS.runDurationMs);
  if (!duration) throw new Error('Finite run duration must be positive');
  running = true; origin = now(); due = backlog = executed = dropped = 0;
  stopTimer = setTimeout(() => pause('run-duration'), duration); loopTimer = setTimeout(tick, 0);
  return snapshot();
}
function begin(request) {
  if (!running || origin === null) throw new Error('Start Worker first');
  if (measurement || closing) throw new Error('A diagnostic window is already active or closing');
  const durationMs = integer(request.durationMs ?? 10000, 'diagnostic duration', LIMITS.durationMs);
  if (!durationMs) throw new Error('Diagnostic duration must be positive');
  const startedAtMs = now(); pendingInput = null;
  measurement = { epoch: ++epoch, durationMs, startedAtMs, startedAt: absoluteNow(), deadlineMs: startedAtMs + durationMs,
    workerTimeOrigin: performance.timeOrigin, clockOriginMs: origin, framerate: fps, initialDue: due,
    initialBacklog: backlog, initialGuestCounter: counter(), rawLedger: [], inputs: [], audioSnapshots: [],
    initialPacing: { due, executed, overflowDropped: dropped, backlog }, coreRate, playbackEpoch,
    sourceFramesPosted: 0, initialSourceFramesPosted: enqueued, maxPending: 0, maxBacklog: 0,
    maxWorkerTickGapMs: 0, lastTickMs: startedAtMs, requests: [request],
    scope: 'Private Worker proof. Raw native counters, Worker timer ledger and unchanged worklet diagnostics; no main AudioContext clock, physical output, input-consumption or production compatibility claim.' };
  port.postMessage({ type: 'diagnostics', enabled: true, epoch });
  measurement.timer = setTimeout(() => closeMeasurement('duration'), durationMs);
}
function input(request) {
  if (!mod) throw new Error('Boot first');
  if (measurement && now() >= measurement.deadlineMs) closeMeasurement('duration');
  const sequence = integer(request.sequence ?? request.seq, 'input sequence');
  const mask = integer(request.mask, 'input mask', 1023);
  if (sequence <= latestSequence) return { ignored: true, latestSequence };
  if (request.domAt !== undefined) finite(request.domAt, 'absolute main DOM time');
  if (measurement && pendingInput) {
    if (measurement.inputs.length === LIMITS.inputs) closeMeasurement('input-capacity');
    else measurement.inputs.push({ ...pendingInput, superseded: true });
  }
  latestSequence = sequence; latestMask = mask; mod._mgbawasm_set_keys(mask);
  pendingInput = { sequence, mask, domAt: request.domAt ?? null, workerReceivedAt: absoluteNow(),
    guestCounterAtReceipt: counter() };
  return { sequence, mask, workerReceivedAt: pendingInput.workerReceivedAt };
}
function video(request) {
  if (!mod) throw new Error('Boot first');
  // One push-free request returns one latest frame. The host must recycle its
  // buffer before requesting another, so a stalled UI cannot accumulate frames.
  if (videoInFlight) throw new Error('Recycle the previous video buffer before requesting another');
  const width = mod._mgbawasm_video_width(), height = mod._mgbawasm_video_height();
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height) || width < 1 || height < 1 || width > 256 || height > 224) throw new Error('Invalid native geometry');
  const size = width * height * 4, ptr = mod._mgbawasm_video_ptr();
  const buffer = recycled?.byteLength === size ? recycled : new ArrayBuffer(size); recycled = null;
  const rgba = new Uint8Array(buffer); rgba.set(mod.HEAPU8.subarray(ptr, ptr + size)); videoInFlight = true;
  reply(request, { width, height, counter: counter(), rgba, pixels: buffer, workerAt: absoluteNow() }, [buffer]);
}
async function dispatch(request) {
  const op = request.op ?? request.type;
  if (op === 'boot') return reply(request, await boot(request));
  if (op === 'start' || op === 'resume') return reply(request, start(request));
  if (op === 'pause') return reply(request, pause('pause'));
  if (op === 'input') return reply(request, input(request));
  if (op === 'snapshot' || op === 'report') return reply(request, snapshot());
  if (op === 'video') return video(request);
  if (op === 'recycle') {
    const buffer = request.pixels ?? request.rgba?.buffer;
    if (!(buffer instanceof ArrayBuffer) || buffer.byteLength > 256 * 224 * 4) throw new Error('Invalid recycled video buffer');
    recycled = buffer; videoInFlight = false; return reply(request, { recycled: true });
  }
  if (op === 'begin' || op === 'diagnostics-start') return begin(request);
  if (op === 'end' || op === 'diagnostics-stop') return closeMeasurement(request.reason ?? 'manual', request);
  if (op === 'destroy') {
    pause('destroy'); if (closing) finishMeasurement(null);
    if (mod) { if (audioPtr) mod._free(audioPtr); audioPtr = 0; mod._mgbawasm_unload(); mod = null; }
    port?.close(); port = null; reply(request, { destroyed: true }); self.close(); return;
  }
  throw new Error('Unknown private Worker operation: ' + op);
}
self.onmessage = event => { Promise.resolve().then(() => dispatch(event.data)).catch(error => failure(event.data, error)); };
