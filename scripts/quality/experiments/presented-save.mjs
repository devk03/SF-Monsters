/** Private save-before-canvas protocol; no latest-live or physical-durability claim. */
const SIZES = new Set([32768, 131072]);
const HEX = /^[a-f0-9]{64}$/;
const uint = (value, name, max = Number.MAX_SAFE_INTEGER) => {
    if (!Number.isSafeInteger(value) || value < 0 || value > max) throw Error(`Invalid ${name}`);
    return value;
};
export function encodeRaw(bytes) {
    let text = '';
    for (let start = 0; start < bytes.length; start += 16384)
        text += String.fromCharCode(...bytes.subarray(start, start + 16384));
    return btoa(text);
}
export function decodeRaw(text) {
    const raw = atob(text);
    return Uint8Array.from(raw, character => character.charCodeAt(0));
}
const digest = async bytes => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)),
    byte => byte.toString(16).padStart(2, '0')).join('');

/**
 * A single owner must hold this storage key. An epoch/generation fence precedes
 * account, cartridge, import or state changes. Every drawing references raw bytes
 * read back from browser storage earlier in this session. Unchanged revisions
 * reuse that verified copy; a native completed-save counter is never consulted.
 * A synchronous pagehide handler needs no new write: successful frame writes
 * already preceded drawing. cachedPresented() is explicitly NOT a fresh export.
 */
export function createPresentedSaveStore({ storage, key, epoch, hash = digest }) {
    if (!storage || typeof storage.getItem !== 'function' || typeof storage.setItem !== 'function' ||
        typeof key !== 'string' || !key || key.length > 512 || typeof hash !== 'function')
        throw Error('Provide an isolated, singly owned storage key and storage adapter');
    uint(epoch, 'save epoch');
    let generation = 1, expectedEpoch = epoch, busy = null, verified = null, presented = null;
    let writeSerial = 0, drawCount = 0, lastFailure = null;
    function fence(nextEpoch = null) {
        if (nextEpoch !== null) uint(nextEpoch, 'save epoch');
        generation++; expectedEpoch = nextEpoch; verified = null;
        return generation;
    }
    function current(token, packetEpoch) {
        if (token !== generation || packetEpoch !== expectedEpoch)
            throw Error('Stale adapter generation or save epoch');
    }
    function identity(frame) {
        if (!frame || frame.ready !== true) throw Error('A completed native video frame is required');
        for (const name of ['frameId', 'saveEpoch', 'counter']) uint(frame[name], name, name === 'counter' ? 0xffffffff : undefined);
        if (!frame.flash || frame.flash.saveEpoch !== frame.saveEpoch || frame.flash.counter !== frame.counter)
            throw Error('Video and raw Flash do not share an epoch and guest counter');
        if (typeof frame.flash.available !== 'boolean') throw Error('Invalid Flash availability');
    }
    async function present(frame, { acknowledge, draw }) {
        if (busy === generation) throw Error('One save/frame presentation may be in flight');
        if (typeof acknowledge !== 'function' || typeof draw !== 'function' || draw.constructor.name === 'AsyncFunction')
            throw Error('Provide an acknowledgement and a synchronous canvas submission');
        identity(frame); const token = generation, packet = frame.flash;
        current(token, frame.saveEpoch);
        let storageAttempted = false, storageConfirmed = false;
        if (presented?.saveEpoch === frame.saveEpoch && frame.frameId <= presented.frameId)
            throw Error('Previously submitted frame identifier was replayed');
        busy = token;
        try {
            let snapshot = null, wrote = false;
            if (packet.available) {
                uint(packet.rawRevision, 'raw revision'); uint(packet.size, 'raw Flash size');
                if (!SIZES.has(packet.size) || !HEX.test(packet.sha256)) throw Error('Invalid raw Flash identity');
                if (verified && packet.rawRevision < verified.rawRevision) throw Error('Raw revision regressed');
                if (packet.bytes !== undefined) {
                    if (!(packet.bytes instanceof Uint8Array) || packet.bytes.length !== packet.size)
                        throw Error('Raw Flash payload size differs');
                    const bytes = packet.bytes.slice();
                    if (await hash(bytes) !== packet.sha256) throw Error('Raw Flash hash differs');
                    current(token, frame.saveEpoch);
                    if (verified && packet.rawRevision === verified.rawRevision && packet.sha256 !== verified.sha256)
                        throw Error('One raw revision describes different bytes');
                    snapshot = { bytes, saveEpoch: frame.saveEpoch, rawRevision: packet.rawRevision,
                        sha256: packet.sha256, size: packet.size };
                } else {
                    if (!verified || verified.saveEpoch !== frame.saveEpoch || verified.rawRevision !== packet.rawRevision ||
                        verified.size !== packet.size || verified.sha256 !== packet.sha256)
                        throw Error('Omitted Flash payload has no matching verified owner');
                    snapshot = verified;
                }
                const unchanged = verified && verified.saveEpoch === snapshot.saveEpoch &&
                    verified.rawRevision === snapshot.rawRevision && verified.sha256 === snapshot.sha256;
                if (!unchanged) {
                    const encoded = encodeRaw(snapshot.bytes);
                    current(token, frame.saveEpoch);
                    // Browser setItem is atomic on quota failure. A subsequent
                    // read failure/mismatch is uncertain; do not invent rollback.
                    storageAttempted = true;
                    storage.setItem(key, encoded);
                    if (storage.getItem(key) !== encoded) throw Error('Browser storage readback differs or has another writer');
                    storageConfirmed = true;
                    snapshot.writeSerial = ++writeSerial; wrote = true; verified = snapshot;
                } else snapshot = verified;
            } else {
                if (packet.size !== 0 || packet.rawRevision !== 0 || packet.bytes !== undefined)
                    throw Error('Uninitialized Flash cannot claim a payload');
            }
            current(token, frame.saveEpoch);
            const receipt = await acknowledge({ frameId: frame.frameId, saveEpoch: frame.saveEpoch,
                rawRevision: packet.rawRevision });
            current(token, frame.saveEpoch);
            if (!receipt || receipt.receiptAcknowledged !== true || receipt.storageVerified !== false ||
                receipt.frameId !== frame.frameId || receipt.saveEpoch !== frame.saveEpoch ||
                receipt.rawRevision !== packet.rawRevision)
                throw Error('Worker receipt is stale or falsely attests browser storage');
            // No await between this fence, the synchronous draw and recording
            // the cached presented copy. A reset cannot interleave this block.
            const result = draw(frame);
            if (result && typeof result.then === 'function') throw Error('Canvas submission must be synchronous');
            presented = snapshot ? { ...snapshot, counter: frame.counter, frameId: frame.frameId } : null;
            drawCount++; lastFailure = null;
            return { frameId: frame.frameId, saveEpoch: frame.saveEpoch, counter: frame.counter,
                rawRevision: packet.rawRevision, sha256: snapshot?.sha256 ?? null,
                writeSerial: snapshot?.writeSerial ?? 0, wrote, storageReadbackVerified: snapshot !== null,
                workerReceiptObserved: true, canvasSubmitted: true, physicalPaintProven: false };
        } catch (error) {
            if (token === generation) {
                if (storageAttempted && !storageConfirmed) verified = null;
                lastFailure = String(error?.message ?? error);
            }
            throw error; // Host withholds draw/ACK as applicable and pauses on failure.
        } finally { if (busy === token) busy = null; }
    }
    return Object.freeze({ present, fence,
        known: () => verified ? { knownEpoch: verified.saveEpoch, knownRevision: verified.rawRevision } : {},
        cachedPresented: () => presented ? { bytes: presented.bytes.slice(), saveEpoch: presented.saveEpoch,
            rawRevision: presented.rawRevision, counter: presented.counter, sha256: presented.sha256,
            frameId: presented.frameId, writeSerial: presented.writeSerial, scope: 'Cached previously submitted frame; not latest Worker state' } : null,
        snapshot: () => ({ generation, expectedEpoch, busy: busy === generation, writeSerial, drawCount, lastFailure,
            scope: 'Verified browser-storage readback before canvas submission; no guest-save detection, physical paint, unseen Worker-tail or OS-fsync guarantee' }),
    });
}
