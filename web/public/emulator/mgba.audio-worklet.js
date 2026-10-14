/* SF Mini Monsters audio sink, extracted from the MPL-2.0 SDK. */
/**
 * AudioWorklet processor: an SPSC float ring fed int16 chunks, resampling on
 * the way out.
 *
 * The resampling is here rather than in the SDK because these cores emit at a
 * rate the SDK does not choose and cannot pin: 131072 Hz on Game Boy, and 32768
 * or 65536 Hz on GBA depending on what the running game has written to
 * SOUNDBIAS. A `rate` message retunes the read cursor mid-stream, so a game
 * changing resolution is a ratio change and not a glitch.
 *
 * `consumed` is reported in *source* frames — that is the unit the SDK's pacing
 * arithmetic works in, since that is what the core produces.
 */
export const WORKLET_SOURCE = `
class MgbaSink extends AudioWorkletProcessor {
  constructor() {
    super();
    this.cap = 32768; // source frames
    this.buf = new Float32Array(this.cap * 2);
    this.pos = 0; // fractional read cursor, in source frames
    this.w = 0;   // source frames written
    this.ratio = 1;
    // Accumulate a short cushion once per playback epoch. This adds audio
    // latency, without advancing the guest or changing the resampling ratio.
    this.prefillFrames = Math.min(this.cap - 1, Math.ceil(sampleRate * .04));
    this.started = false;
    this.lastPost = 0;
    this.diagnostics = null;
    this.playbackEpoch = 0;
    this.port.onmessage = (e) => {
      const msg = e.data;
      if (msg && msg.type === 'playback-reset') {
        if (!Number.isSafeInteger(msg.epoch) || msg.epoch <= this.playbackEpoch) return;
        // SDK ends diagnostics before resetting playback. Observation alone
        // never flushes this ring or changes its interpolation position.
        this.playbackEpoch = msg.epoch;
        this.pos = this.w = this.lastPost = 0;
        this.started = false;
        this.port.postMessage({ type: 'playback-reset', epoch: msg.epoch });
        return;
      }
      if (msg && msg.type === 'diagnostics') {
        if (msg.enabled) {
          this.diagnostics = {
            type: 'diagnostics', epoch: msg.epoch ?? null, firstOutputFrame: currentFrame,
            observedThroughOutputFrame: currentFrame, renderedOutputFrames: 0,
            warmupOutputFrames: 0, underrunOutputFrames: 0,
            droppedSourceFrames: 0, processQuanta: 0,
          };
          this.lastDiagnosticPost = currentFrame;
        } else if (this.diagnostics) {
          this.reportDiagnostics(true);
          this.diagnostics = null;
        }
        return;
      }
      if (msg && msg.rate) {
        this.ratio = msg.rate / sampleRate;
        this.prefillFrames = Math.max(2, Math.min(this.cap - 1, Math.ceil(msg.rate * .04)));
        return;
      }
      const s = msg; // Int16Array, interleaved stereo
      const frames = s.length >> 1;
      for (let i = 0; i < frames; i++) {
        if (this.w - this.pos >= this.cap) {
          if (this.diagnostics) this.diagnostics.droppedSourceFrames += frames - i;
          break; // full: drop excess, preserving normal playback behavior
        }
        const idx = (this.w % this.cap) * 2;
        this.buf[idx] = s[i * 2] / 32768;
        this.buf[idx + 1] = s[i * 2 + 1] / 32768;
        this.w++;
      }
    };
  }
  reportDiagnostics(final) {
    this.port.postMessage({ ...this.diagnostics, final,
      outputSampleRate: sampleRate, queueDepthFrames: Math.max(0, this.w - this.pos),
      prefillTargetSourceFrames: this.prefillFrames, playbackStarted: this.started });
    this.lastDiagnosticPost = this.diagnostics.observedThroughOutputFrame;
  }
  process(inputs, outputs) {
    const out = outputs[0];
    const L = out[0];
    const R = out[1] || out[0];
    const n = L.length;
    if (!this.started && this.w - this.pos >= this.prefillFrames) this.started = true;
    for (let i = 0; i < n; i++) {
      // One source frame must be left past the cursor to interpolate against.
      if (this.started && this.pos + 1 < this.w) {
        const base = Math.floor(this.pos);
        const frac = this.pos - base;
        const a = (base % this.cap) * 2;
        const b = ((base + 1) % this.cap) * 2;
        L[i] = this.buf[a] + (this.buf[b] - this.buf[a]) * frac;
        R[i] = this.buf[a + 1] + (this.buf[b + 1] - this.buf[a + 1]) * frac;
        this.pos += this.ratio;
      } else {
        L[i] = 0;
        R[i] = 0;
        if (this.diagnostics) {
          if (this.started) this.diagnostics.underrunOutputFrames++;
          else this.diagnostics.warmupOutputFrames++;
        }
      }
    }
    const consumed = Math.floor(this.pos);
    if (consumed - this.lastPost >= 1024) {
      this.port.postMessage(consumed);
      this.lastPost = consumed;
    }
    if (this.diagnostics) {
      this.diagnostics.renderedOutputFrames += n;
      this.diagnostics.processQuanta++;
      this.diagnostics.observedThroughOutputFrame = currentFrame + n;
      if (currentFrame + n - this.lastDiagnosticPost >= 4096) this.reportDiagnostics(false);
    }
    return true;
  }
}
registerProcessor('mgba-sink', MgbaSink);
`;

