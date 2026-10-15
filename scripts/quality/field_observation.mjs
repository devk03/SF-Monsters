/** Bounded private QA events. Never infer guest movement or hardware timing. */
const CODES = new Set(['KeyX','KeyZ','ShiftRight','Enter','ArrowRight','ArrowLeft',
    'ArrowUp','ArrowDown','KeyS','KeyA']);
const LIMIT = 2048;

export function createFieldObservation(now = () => performance.now()) {
    let active = false, events = [], dropped = 0, lastStart = 0;
    function append(event) {
        if (!active) return;
        if (events.length < LIMIT) events.push(event);
        else ++dropped;
    }
    return {
        start() {
            if (active) throw Error('Field observation already active');
            active = true; events = []; dropped = 0; lastStart = now();
        },
        keyboard(event) {
            if (!CODES.has(event.code) || !['keydown','keyup'].includes(event.type)) return;
            append({type:event.type,atMs:now(),code:event.code,
                trusted:event.isTrusted === true,repeat:event.repeat === true});
        },
        focus(type) {
            if (type === 'blur' || type === 'focus') append({type,atMs:now()});
        },
        longTask(entry) {
            if (Number.isFinite(entry.startTime) && Number.isFinite(entry.duration)
                    && entry.startTime >= lastStart && entry.duration >= 0)
                append({type:'longtask',atMs:entry.startTime,durationMs:entry.duration});
        },
        stop(startedAtMs,endedAtMs) {
            if (!active || !Number.isFinite(startedAtMs) || !Number.isFinite(endedAtMs)
                    || endedAtMs < startedAtMs) throw Error('Invalid observation interval');
            active = false;
            const within = events.filter(event=>event.atMs >= startedAtMs && event.atMs <= endedAtMs);
            const counts = {};
            for (const event of within) counts[event.type]=(counts[event.type]??0)+1;
            return {startedAtMs,endedAtMs,events:within,counts,droppedEvents:dropped,
                eventLimit:LIMIT,scope:'Mapped DOM keys, window focus and browser long tasks only. '
                    +'Not SDK mask transitions, guest consumption, movement, hardware input or causal proof.'};
        },
        cancel() { active=false;events=[];dropped=0; },
    };
}
