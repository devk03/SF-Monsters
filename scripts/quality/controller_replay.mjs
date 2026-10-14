/** Finite private QA input replay. Wall-time DOM events are not guest-frame sync. */
const FRAME_MS = 1000 * 280896 / 16777216;
export function parseControllerRoute(text) {
    if (typeof text !== 'string' || text.length > 20000) throw Error('Invalid controller CSV');
    const lines = text.trim().split(/\r?\n/);
    if (!lines.length || lines.length > 1000) throw Error('Controller row bound exceeded');
    let frames = 0;
    const rows = lines.map(line => {
        if (!/^\d+,\d+$/.test(line)) throw Error('Use headerless keyMask,frames rows');
        const [mask, count] = line.split(',').map(Number);
        if (!Number.isSafeInteger(mask) || mask > 1023 || !Number.isSafeInteger(count) || count < 1)
            throw Error('Invalid controller mask or frame duration');
        frames += count;
        if (frames * FRAME_MS > 600000) throw Error('Controller route exceeds ten minutes');
        return { mask, durationMs: count * FRAME_MS };
    });
    return { rows, frames, durationMs: frames * FRAME_MS };
}

export function startControllerReplay(text, applyMask, onDone, environment = {}) {
    const route = parseControllerRoute(text);
    if (typeof applyMask !== 'function' || typeof onDone !== 'function') throw Error('Replay callbacks required');
    const now = environment.now ?? (() => performance.now());
    const schedule = environment.setTimeout ?? ((fn, delay) => setTimeout(fn, delay));
    const cancel = environment.clearTimeout ?? (timer => clearTimeout(timer));
    const startedAtMs = now();
    let due = startedAtMs, index = 0, timer, report, closing = false, maxLatenessMs = 0;
    const dispatches = [];
    function stop(reason = 'manual', failure = null) {
        if (report || closing) return report;
        closing = true;
        cancel(timer);
        try { applyMask(0); } catch (error) { failure ??= error; }
        report = { reason: failure ? 'dispatch-error' : reason, error: failure?.message ?? null,
            startedAtMs, endedAtMs: now(), declaredFrames: route.frames,
            declaredDurationMs: route.durationMs, appliedRows: index,
            totalRows: route.rows.length, maxLatenessMs, dispatches,
            scope: 'Approximate wall-time input dispatch; no guest-frame or scene-detection claim' };
        onDone(report);
        return report;
    }
    function step() {
        if (report) return;
        const actualMs = now(), late = Math.max(0, actualMs - due);
        maxLatenessMs = Math.max(maxLatenessMs, late);
        if (late > 50) return stop('late-timer');
        if (index === route.rows.length) return stop('complete');
        const row = route.rows[index];
        try { applyMask(row.mask); } catch (error) { return stop('dispatch-error', error); }
        if (report) return;
        dispatches.push({ row: index, mask: row.mask, dueMs: due, actualMs });
        ++index;
        due += row.durationMs;
        timer = schedule(step, Math.max(0, due - now()));
    }
    step();
    return { stop, startedAtMs, get active() { return !report && !closing; } };
}
