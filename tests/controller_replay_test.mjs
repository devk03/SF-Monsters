import assert from 'node:assert/strict';
import test from 'node:test';
import { controllerMeasurementDuration, parseControllerRoute, startControllerReplay } from '../scripts/quality/controller_replay.mjs';

test('route measurement retains a completion margin within its finite ten-minute limit', () => {
    for (const [routeMs, expected] of [[1,180000],[179000,180000],[179000.01,181000],
        [240000,241000],[598652.2064208984,600000],[599000,600000]]) {
        const windowMs = controllerMeasurementDuration(routeMs);
        assert.equal(windowMs,expected);
        assert.ok(windowMs-routeMs>=1000);
        assert.ok(windowMs<=600000);
    }
    for (const invalid of [0,-1,599000.01,600000,NaN,Infinity,'1000',null])
        assert.throws(()=>controllerMeasurementDuration(invalid));
});

function clock() {
    let time = 100, next = 0;
    const pending = new Map();
    return { pending, environment: { now: () => time,
        setTimeout(fn, delay) {
            assert.equal(pending.size, 0, 'Only one route timer can be outstanding');
            pending.set(++next, { fn, due: time + delay }); return next;
        }, clearTimeout(id) { pending.delete(id); } },
        fire(lateness = 0) {
            const [id, task] = pending.entries().next().value;
            pending.delete(id); time = task.due + lateness; task.fn(); return task.fn;
        } };
}

test('native keyMask,frames syntax has finite row, mask and duration bounds', () => {
    const parsed = parseControllerRoute('8,8\n0,24\n');
    assert.equal(parsed.frames, 32);
    assert.equal(parsed.rows[0].mask, 8);
    assert.equal(parsed.durationMs, 32 * 1000 * 280896 / 16777216);
    for (const invalid of ['', 'frame,keys', '1024,1', '-1,1', '1,0', '1,1.5',
        '1,35837', '0,1\n'.repeat(1001), '1,1\n\n0,1']) {
        assert.throws(() => parseControllerRoute(invalid), invalid);
    }
});

test('finite replay preserves every mask row and always releases the final held key', () => {
    const fake = clock(), masks = [], reports = [];
    const replay = startControllerReplay('8,8\n0,24\n1,8', mask => masks.push(mask),
        report => reports.push(report), fake.environment);
    while (fake.pending.size) fake.fire();
    assert.deepEqual(masks, [8, 0, 1, 0]);
    assert.equal(reports.length, 1);
    assert.equal(reports[0].reason, 'complete');
    assert.equal(reports[0].appliedRows, 3);
    assert.equal(reports[0].declaredFrames, 40);
    assert.equal(reports[0].dispatches.length, 3);
    assert.equal(reports[0].maxLatenessMs, 0);
    assert.equal(replay.active, false);
    assert.equal(replay.stop(), reports[0]);
});

test('late timers abort with a key release instead of compressing remaining inputs', () => {
    const fake = clock(), masks = [], reports = [];
    startControllerReplay('8,8\n1,8', mask => masks.push(mask), report => reports.push(report), fake.environment);
    fake.fire(51);
    assert.deepEqual(masks, [8, 0]);
    assert.equal(reports[0].reason, 'late-timer');
    assert.equal(reports[0].appliedRows, 1);
    assert.equal(fake.pending.size, 0);
});

test('hidden/manual stop cancels the timer and a late callback cannot press another key', () => {
    const fake = clock(), masks = [], reports = [];
    const replay = startControllerReplay('8,8\n1,8', mask => masks.push(mask), report => reports.push(report), fake.environment);
    const lateCallback = fake.pending.values().next().value.fn;
    replay.stop('hidden'); lateCallback(); replay.stop('manual');
    assert.deepEqual(masks, [8, 0]);
    assert.equal(reports.length, 1);
    assert.equal(reports[0].reason, 'hidden');
    assert.equal(fake.pending.size, 0);
});

test('dispatch failure stops immediately and attempts a final release', () => {
    const fake = clock(), masks = [], reports = [];
    const replay = startControllerReplay('8,8', mask => {
        masks.push(mask); if (mask) throw Error('Dispatch unavailable');
    }, report => reports.push(report), fake.environment);
    assert.deepEqual(masks, [8, 0]);
    assert.equal(replay.active, false);
    assert.equal(reports[0].reason, 'dispatch-error');
    assert.equal(reports[0].appliedRows, 0);
    assert.equal(fake.pending.size, 0);
});
