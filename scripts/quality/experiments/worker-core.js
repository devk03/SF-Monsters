/* Private feasibility proof only. Classic Worker; unchanged core/WASM/worklet. */
'use strict';
const LIMITS = Object.freeze({ durationMs: 600000, runDurationMs: 900000, ticks: 160000, inputs: 40000, audioSnapshots: 32000 });
let mod = null, port = null, audioPtr = 0, fps = 0, coreRate = 0, booting = false;
let running = false, loopTimer = null, stopTimer = null, origin = null;
let pausedAtMs = null, pausedPhase = null, runDeadlineMs = null, runExpired = false;
let phaseAnchorMs = null, phaseAnchorElapsedMs = 0;
let due = 0, backlog = 0, executed = 0, dropped = 0, playbackEpoch = 0;
let enqueued = 0, consumed = 0, lastAudio = null, lastAudioAt = null;
let measurement = null, closing = null, finalTimer = null, lastReport = null, epoch = 0;
let latestSequence = -1, latestMask = 0, pendingInput = null, videoInFlight = false, recycled = null;
let bootDiscardedSourceFrames = 0, batteryVerified = false;
let playbackAcknowledged = false;
let retainedRom = null, saveEpoch = 0, rawRevision = 0, flashCache = null;
let frameSerial = 0, flight = null, controlBusy = false, fatalSaveError = null, videoFrameReady = false;
let lastHostReceipt = null;
const lifecycleFacts = [];
let lifecycleFactOverflow = false;
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
function cloneFlash() {
  const size = mod._mgbawasm_sram_save();
  if (!size) return null;
  if (![32768, 131072].includes(size)) throw new Error('Unexpected native battery size');
  const ptr = mod._mgbawasm_sram_ptr();
  if (!ptr || ptr + size > mod.HEAPU8.length) throw new Error('Native battery output is outside heap');
  return mod.HEAPU8.slice(ptr, ptr + size);
}
function refreshFlash() {
  const current = cloneFlash();
  if (!current) {
    if (flashCache) throw new Error('Previously initialized native Flash disappeared');
    return null;
  }
  if (!flashCache || current.length !== flashCache.bytes.length || current.some((v, i) => v !== flashCache.bytes[i])) {
    flashCache = { bytes: current, rawRevision: ++rawRevision, saveEpoch, digest: null };
  }
  return flashCache;
}
async function flashPacket(cache, atCounter, includeBytes = true) {
  if (!cache) return { available: false, saveEpoch, rawRevision: 0, counter: atCounter, size: 0 };
  // Internal immutable cache is never transferred/detached. Hashes bind its
  // entire raw content, including incomplete/inactive slots and unused bytes.
  cache.digest ??= crypto.subtle.digest('SHA-256', cache.bytes).then(value =>
    Array.from(new Uint8Array(value), byte => byte.toString(16).padStart(2, '0')).join('')).catch(error => {
      cache.digest = null; throw error;
    });
  const packet = { available: true, saveEpoch: cache.saveEpoch, rawRevision: cache.rawRevision,
    counter: atCounter, size: cache.bytes.length, sha256: await cache.digest };
  if (includeBytes) packet.bytes = cache.bytes.slice();
  return packet;
}
function requirePaused() {
  if (!mod) throw new Error('Boot first');
  if (running) throw new Error('Pause and await its acknowledgement before save operations');
  if (measurement || closing) throw new Error('Finish diagnostic window and final acknowledgement first');
  if (fatalSaveError) throw new Error('Worker save state is uncertain: ' + fatalSaveError);
}
function canonicalState() {
  const size = mod._mgbawasm_state_size(); integer(size, 'native state size', 4 * 1024 * 1024);
  if (!size) throw new Error('Native state unavailable');
  const ptr = mod._malloc(size); if (!ptr) throw new Error('Native state scratch allocation failed');
  try {
    if (ptr + size > mod.HEAPU8.length) throw new Error('Native state scratch exceeds heap');
    mod.HEAPU8.fill(0, ptr, ptr + size);
    if (mod._mgbawasm_state_save(ptr) !== 1) throw new Error('Native state export failed');
    return mod.HEAPU8.slice(ptr, ptr + size);
  } finally { mod._free(ptr); }
}
function nativeBootRom() {
  if (!heapCopy(retainedRom, ptr => mod._mgbawasm_load(ptr, retainedRom.length, 0, 0, -1, 0, 1))) throw new Error('Native ROM reboot failed');
  mod._mgbawasm_set_log_level(1); mod._mgbawasm_set_idle_optimization?.(1); mod._mgbawasm_set_allow_opposing_directions?.(0);
}
function restoreRawBattery(raw, reboot = true) {
  if (![32768, 131072].includes(raw.length)) throw new Error('Unsupported native battery size');
  if (reboot) nativeBootRom();
  let initialized = false;
  for (let frame = 0; frame < 120; ++frame) {
    mod._mgbawasm_run_frame();
    if (mod._mgbawasm_sram_save() === raw.length) { initialized = true; break; }
  }
  if (!initialized) throw new Error('Native save memory did not initialize within120frames');
  if (!heapCopy(raw, ptr => mod._mgbawasm_sram_load(ptr, raw.length))) throw new Error('Native battery restore failed');
  const restored = cloneFlash();
  if (!restored || restored.length !== raw.length || restored.some((v, i) => v !== raw[i])) throw new Error('Native battery round-trip differs');
  mod._mgbawasm_reset(); mod._mgbawasm_set_idle_optimization?.(1); mod._mgbawasm_set_allow_opposing_directions?.(0);
  batteryVerified = true;
}
function restoreState(raw) {
  if (raw.length !== mod._mgbawasm_state_size()) throw new Error('State size differs from unchanged core ABI');
  if (!heapCopy(raw, ptr => mod._mgbawasm_state_load(ptr))) throw new Error('Native state load failed');
}
function pacingPhase(at = now()) {
  if (origin === null) return null;
  const frozenAt = pausedAtMs ?? at;
  const elapsedMs = activeElapsed(frozenAt), earned = elapsedMs / 1000 * fps;
  const earnedDue = Math.floor(earned), fractionalFrame = earned - earnedDue;
  if (elapsedMs < 0 || earnedDue < due) throw new Error('Pacing phase regressed');
  return { pausedAtMs: frozenAt, originMs: origin, elapsedMs, plannedDue: due, earnedDue,
    earnedUnplannedFrames: earnedDue - due, fractionalFrame,
    nextDueInMs: (1 - fractionalFrame) * 1000 / fps, retainedBacklog: backlog,
    totalRetainedFrames: backlog + earnedDue - due };
}
function activeElapsed(at = now()) {
  if (phaseAnchorMs === null) return 0;
  // Add nonnegative segment time to the frozen active duration. Subtracting a
  // large shifted origin can otherwise round a frame-boundary credit backwards.
  const delta = at - phaseAnchorMs;
  if (delta < 0) throw new Error('Worker active-clock segment regressed');
  return phaseAnchorElapsedMs + delta;
}
function lifecycle(fact) {
  if (lifecycleFacts.length < 64) lifecycleFacts.push(fact); else lifecycleFactOverflow = true;
}
function advanceSaveEpoch(reason) {
  const phase = pacingPhase();
  const old = { saveEpoch, due, executed, overflowDropped: dropped,
    abandonedFrames: backlog + (phase?.earnedUnplannedFrames ?? 0), abandonedBacklog: backlog,
    abandonedEarnedUnplannedFrames: phase?.earnedUnplannedFrames ?? 0,
    discardedFractionalFrame: phase?.fractionalFrame ?? 0, pausedPhase: phase,
    queuedSourceFramesEstimate: Math.max(0, enqueued - consumed), workerAt: absoluteNow(), reason };
  if (lifecycleFacts.length === 64) throw new Error('Lifecycle fact capacity reached; create a fresh Worker');
  lifecycleFacts.push(old);
  saveEpoch++; rawRevision = 0; flashCache = null; lastHostReceipt = null;
  flight = null; videoInFlight = false; videoFrameReady = false; recycled = null;
  pendingInput = null; latestMask = 0; mod._mgbawasm_set_keys(0);
  origin = null; pausedAtMs = null; pausedPhase = null; phaseAnchorMs = null; phaseAnchorElapsedMs = 0;
  due = backlog = executed = dropped = 0;
  const drainedSourceFrames = drainAudio(false); old.discardedShimSourceFrames = drainedSourceFrames;
  old.playbackReset = { previousEpoch: playbackEpoch, nextEpoch: playbackEpoch + 1 };
  enqueued = consumed = 0; coreRate = 0; playbackAcknowledged = false;
  port.postMessage({ type: 'playback-reset', epoch: ++playbackEpoch }); syncRate();
  refreshFlash();
}
async function saveOperation(request, op) {
  requirePaused();
  if (controlBusy) throw new Error('A paused save operation is already in flight');
  controlBusy = true;
  try {
    if (op === 'export-battery') {
      const packet = await flashPacket(refreshFlash(), counter());
      if (!packet.available) throw new Error('No native battery exists yet');
      return reply(request, packet, [packet.bytes.buffer]);
    }
    if (op === 'export-state') {
      const state = canonicalState(), atCounter = counter();
      const flash = await flashPacket(refreshFlash(), atCounter);
      const result = { saveEpoch, counter: atCounter, state, flash };
      return reply(request, result, [state.buffer, ...(flash.bytes ? [flash.bytes.buffer] : [])]);
    }
    const raw = op === 'import-battery' ? bytes(request.bytes ?? request.battery, 'raw battery', 131072).slice() : null;
    const state = op === 'load-state' ? bytes(request.state, 'native state', 4 * 1024 * 1024).slice() : null;
    const companion = op === 'load-state' && request.battery ? bytes(request.battery, 'companion battery', 131072).slice() : null;
    if (state && state.length !== mod._mgbawasm_state_size()) throw new Error('State size differs from unchanged core ABI');
    if ((raw && ![32768, 131072].includes(raw.length)) || (companion && ![32768, 131072].includes(companion.length))) throw new Error('Unsupported battery size');
    const previousState = canonicalState(), previousFlash = cloneFlash();
    if (lifecycleFacts.length >= 62) throw new Error('Lifecycle history nearly full; create a fresh Worker before another reset');
    let committed = false;
    try {
      if (raw || companion) restoreRawBattery(raw ?? companion);
      if (state) restoreState(state);
      advanceSaveEpoch(op);
      const flash = await flashPacket(refreshFlash(), counter());
      reply(request, { ...snapshot(), flash, reset: true }, flash.bytes ? [flash.bytes.buffer] : []);
      committed = true;
      return;
    } finally {
      if (!committed) {
        try {
          if (previousFlash) restoreRawBattery(previousFlash); else nativeBootRom();
          restoreState(previousState); advanceSaveEpoch('failed-' + op + '-rolled-back');
        } catch (rollback) { fatalSaveError = String(rollback?.message ?? rollback); }
      }
    }
  } finally { controlBusy = false; }
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
    pausedAtMs, pausedPhase, phaseAnchorMs, phaseAnchorElapsedMs, runDeadlineMs, runExpired,
    due, backlog, executed, overflowDropped: dropped, latestMask, latestSequence,
    enqueuedSourceFrames: enqueued, consumedSourceFrames: consumed,
    estimatedSourceQueue: Math.max(0, enqueued - consumed),
    audioLatest: lastAudio, audioLatestReceivedAt: lastAudioAt,
    playbackEpoch, playbackAcknowledged, batteryVerified, bootDiscardedSourceFrames,
    saveEpoch, rawRevision, flashAvailable: flashCache !== null, videoFrameReady,
    lastHostReceipt, lifecycleFacts: lifecycleFacts.map(value => ({ ...value })), lifecycleFactOverflow, fatalSaveError,
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
  const wasRunning = running;
  if (wasRunning && origin !== null && pausedAtMs === null) {
    pausedAtMs = now(); pausedPhase = pacingPhase(pausedAtMs);
    lifecycle({ reason, saveEpoch, due, executed, overflowDropped: dropped, abandonedFrames: 0,
      retainedBacklog: backlog, earnedUnplannedFrames: pausedPhase.earnedUnplannedFrames,
      fractionalFrame: pausedPhase.fractionalFrame, pausedAtMs, workerAt: absoluteNow(), audioReset: false });
  }
  running = false; clearTimeout(loopTimer); loopTimer = null;
  closeMeasurement(reason);
  return { ...snapshot(), abandonedFrames: 0, retainedBacklog: backlog,
    earnedUnplannedFrames: pausedPhase?.earnedUnplannedFrames ?? 0,
    fractionalFrame: pausedPhase?.fractionalFrame ?? 0, phaseFrozen: pausedAtMs !== null,
    alreadyPaused: !wasRunning, reason };
}
function tick() {
  if (!running) return;
  try {
    const started = now();
    // Admission precedes core execution. A batch admitted before the deadline
    // is recorded in full before close, even if its <=5 frames cross it.
    if (measurement && started >= measurement.deadlineMs) closeMeasurement('duration');
    if (origin === null) { origin = started; phaseAnchorMs = started; phaseAnchorElapsedMs = 0; }
    const elapsed = activeElapsed(started), nextDue = Math.floor(elapsed / 1000 * fps);
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
    if (actual) { refreshFlash(); videoFrameReady = true; }
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
    const rom = bytes(request.rom, 'rom', 32 * 1024 * 1024); retainedRom = rom.slice();
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
    saveEpoch = 1; refreshFlash();
    return { ...snapshot(), width: mod._mgbawasm_video_width(), height: mod._mgbawasm_video_height() };
  } finally { booting = false; }
}
function start(request) {
  if (!mod) throw new Error('Boot first');
  if (controlBusy || fatalSaveError) throw new Error('Save operation is pending or core state is uncertain');
  if (running) return snapshot();
  const duration = integer(request.durationMs ?? LIMITS.durationMs, 'finite run duration', LIMITS.runDurationMs);
  if (!duration) throw new Error('Finite run duration must be positive');
  const resumedAt = now();
  if (runExpired || (runDeadlineMs !== null && resumedAt >= runDeadlineMs)) {
    runExpired = true; throw new Error('Finite Worker wall-clock run lease expired');
  }
  const requestedDeadline = resumedAt + duration;
  runDeadlineMs = runDeadlineMs === null ? requestedDeadline : Math.min(runDeadlineMs, requestedDeadline);
  if (origin !== null && pausedAtMs !== null) {
    const pauseDurationMs = resumedAt - pausedAtMs, oldOrigin = origin;
    if (pauseDurationMs < 0) throw new Error('Pause clock regressed');
    origin += pauseDurationMs;
    phaseAnchorElapsedMs = pausedPhase.elapsedMs; phaseAnchorMs = resumedAt;
    lifecycle({ reason: 'resume-retained-phase', saveEpoch, pauseDurationMs, pausedAtMs, resumedAtMs: resumedAt,
      originBeforeMs: oldOrigin, originAfterMs: origin, retainedBacklog: backlog,
      earnedUnplannedFrames: pausedPhase?.earnedUnplannedFrames ?? 0,
      fractionalFrame: pausedPhase?.fractionalFrame ?? 0, abandonedFrames: 0, audioReset: false });
  } else {
    origin = resumedAt; phaseAnchorMs = resumedAt; phaseAnchorElapsedMs = 0;
    due = backlog = executed = dropped = 0;
  }
  pausedAtMs = null; pausedPhase = null; running = true;
  clearTimeout(stopTimer);
  stopTimer = setTimeout(() => {
    stopTimer = null; runExpired = true;
    lifecycle({ reason: 'finite-wall-lease-expired', saveEpoch, workerAt: absoluteNow(), runDeadlineMs });
    pause('run-duration');
  }, Math.max(0, runDeadlineMs - resumedAt));
  loopTimer = setTimeout(tick, 0);
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
    initialPacing: { due, executed, overflowDropped: dropped, backlog }, coreRate, playbackEpoch, saveEpoch, rawRevision,
    sourceFramesPosted: 0, initialSourceFramesPosted: enqueued, maxPending: 0, maxBacklog: 0,
    maxWorkerTickGapMs: 0, lastTickMs: startedAtMs, requests: [request],
    scope: 'Private Worker proof. Raw native counters, Worker timer ledger and unchanged worklet diagnostics; no main AudioContext clock, physical output, input-consumption or production compatibility claim.' };
  port.postMessage({ type: 'diagnostics', enabled: true, epoch });
  measurement.timer = setTimeout(() => closeMeasurement('duration'), durationMs);
}
function input(request) {
  if (!mod) throw new Error('Boot first');
  if (controlBusy || fatalSaveError) throw new Error('Wait for the paused save operation to finish');
  if (request.saveEpoch !== undefined && request.saveEpoch !== saveEpoch) throw new Error('Stale input epoch');
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
async function video(request) {
  if (!mod) throw new Error('Boot first');
  if (controlBusy || fatalSaveError) throw new Error('Wait for the paused save operation to finish');
  // One push-free request returns one latest frame. The host must recycle its
  // buffer before requesting another, so a stalled UI cannot accumulate frames.
  if (videoInFlight) throw new Error('Recycle the previous video buffer before requesting another');
  if (!videoFrameReady) return reply(request, { ready: false, saveEpoch, counter: counter(), reason: 'Wait for the first completed native frame after reset' });
  const width = mod._mgbawasm_video_width(), height = mod._mgbawasm_video_height();
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height) || width < 1 || height < 1 || width > 256 || height > 224) throw new Error('Invalid native geometry');
  const cache = refreshFlash(), capturedEpoch = saveEpoch, atCounter = counter(), frameId = ++frameSerial;
  const size = width * height * 4, ptr = mod._mgbawasm_video_ptr();
  const buffer = recycled?.byteLength === size ? recycled : new ArrayBuffer(size); recycled = null;
  const rgba = new Uint8Array(buffer); rgba.set(mod.HEAPU8.subarray(ptr, ptr + size)); videoInFlight = true;
  flight = { frameId, saveEpoch: capturedEpoch, rawRevision: cache?.rawRevision ?? 0, bufferSize: size };
  const includeBytes = request.knownEpoch !== capturedEpoch || request.knownRevision !== cache?.rawRevision;
  const workerAt = absoluteNow();
  try {
    const flash = await flashPacket(cache, atCounter, includeBytes);
    reply(request, { ready: true, frameId, saveEpoch: capturedEpoch, width, height, counter: atCounter, rgba, pixels: buffer, workerAt, flash },
      [buffer, ...(flash.bytes ? [flash.bytes.buffer] : [])]);
  } catch (error) {
    if (flight?.frameId === frameId && flight.saveEpoch === capturedEpoch) { flight = null; videoInFlight = false; }
    throw error;
  }
}
async function dispatch(request) {
  const op = request.op ?? request.type;
  if (op === 'boot') return reply(request, await boot(request));
  if (op === 'start' || op === 'resume') return reply(request, start(request));
  if (op === 'pause') return reply(request, pause('pause'));
  if (op === 'input') return reply(request, input(request));
  if (op === 'snapshot' || op === 'report') return reply(request, snapshot());
  if (op === 'video') return video(request);
  if (['export-battery', 'import-battery', 'export-state', 'load-state'].includes(op)) return saveOperation(request, op);
  if (op === 'ack-flash') {
    if (!flight || request.saveEpoch !== saveEpoch || request.frameId !== flight.frameId || request.rawRevision !== flight.rawRevision) throw new Error('Stale or mismatched Flash receipt acknowledgement');
    lastHostReceipt = { saveEpoch, frameId: flight.frameId, rawRevision: flight.rawRevision, acknowledgedAt: absoluteNow() };
    return reply(request, { ...lastHostReceipt, receiptAcknowledged: true, storageVerified: false });
  }
  if (op === 'recycle') {
    if (!flight || request.saveEpoch !== saveEpoch || request.frameId !== flight.frameId) return reply(request, { ignored: true, reason: 'Stale frame epoch or identifier' });
    const buffer = request.pixels ?? request.rgba?.buffer;
    if (!(buffer instanceof ArrayBuffer) || buffer.byteLength !== flight.bufferSize) throw new Error('Invalid recycled video buffer');
    recycled = buffer; videoInFlight = false; flight = null; return reply(request, { recycled: true });
  }
  if (op === 'begin' || op === 'diagnostics-start') return begin(request);
  if (op === 'end' || op === 'diagnostics-stop') return closeMeasurement(request.reason ?? 'manual', request);
  if (op === 'destroy') {
    pause('destroy'); if (closing) finishMeasurement(null);
    const abandonedPhase = pacingPhase();
    const abandonedFrames = backlog + (abandonedPhase?.earnedUnplannedFrames ?? 0);
    clearTimeout(stopTimer); stopTimer = null;
    if (mod) { if (audioPtr) mod._free(audioPtr); audioPtr = 0; mod._mgbawasm_unload(); mod = null; }
    port?.close(); port = null; reply(request, { destroyed: true, abandonedFrames,
      discardedFractionalFrame: abandonedPhase?.fractionalFrame ?? 0 }); self.close(); return;
  }
  throw new Error('Unknown private Worker operation: ' + op);
}
self.onmessage = event => { Promise.resolve().then(() => dispatch(event.data)).catch(error => failure(event.data, error)); };
