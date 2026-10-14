/* Discard presentation PCM only; never advance or modify guest gameplay. */
const MAX_PENDING_FRAMES = 65536; // Pinned shim AUDIO_CAPACITY, in stereo frames.

export function discardPendingAudio(mod, pointer, capacityFrames) {
    if (!Number.isSafeInteger(pointer) || pointer <= 0 ||
        !Number.isSafeInteger(capacityFrames) || capacityFrames <= 0 ||
        capacityFrames > MAX_PENDING_FRAMES || typeof mod?._mgbawasm_read_audio !== 'function') {
        throw new TypeError('Invalid native audio scratch buffer or reader');
    }
    let total = 0;
    const limit = Math.ceil(MAX_PENDING_FRAMES / capacityFrames) + 1;
    for (let call = 0; call < limit; ++call) {
        const count = mod._mgbawasm_read_audio(pointer, capacityFrames);
        if (!Number.isSafeInteger(count) || count < 0 || count > capacityFrames) {
            throw new Error('Invalid native audio read count');
        }
        if (count === 0) return total;
        total += count;
        if (total > MAX_PENDING_FRAMES) throw new Error('Native audio queue exceeds its bound');
    }
    throw new Error('Native audio queue did not reach an empty sentinel');
}
