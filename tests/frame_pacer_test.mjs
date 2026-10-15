import assert from 'node:assert/strict';
import test from 'node:test';
import { createFramePacer, MAX_FRAMES_PER_TICK, MAX_PENDING_FRAMES }
    from '../scripts/quality/experiments/frame-pacer.mjs';

function run(pacer, due, actual) {
    const budget = pacer.plan(due);
    assert.ok(budget.frames <= MAX_FRAMES_PER_TICK);
    assert.ok(budget.pendingBeforeExecution <= MAX_PENDING_FRAMES);
    const row = pacer.settle(actual ?? budget.frames);
    assert.equal(row.backlogBefore + row.requestedFrames,
        row.executedFrames + row.discardedFrames + row.backlogAfter);
    assert.equal(row.dueTotal, row.executedTotal + row.droppedTotal + row.backlogAfter);
    return row;
}

test('normal cadence keeps its previous one-frame execution behavior', () => {
    const p = createFramePacer();
    const rows = [0, 1, 2, 3].map(due => run(p, due));
    assert.deepEqual(rows.map(r => r.executedFrames), [0, 1, 1, 1]);
    assert.ok(rows.every(r => !r.backlogAfter && !r.discardedFrames && !r.coreFrameMismatch));
});

test('a twelve-frame stall catches up without counting carried work as fresh demand', () => {
    const p = createFramePacer();
    const rows = [0, 12, 13, 13].map(due => run(p, due));
    assert.deepEqual(rows.map(r => r.executedFrames), [0, 5, 5, 3]);
    assert.deepEqual(rows.map(r => r.requestedFrames), [0, 12, 1, 0]);
    assert.deepEqual(rows.map(r => r.backlogAfter), [0, 7, 3, 0]);
    assert.equal(rows.reduce((sum, r) => sum + r.newlyDueOverTickCapFrames, 0), 7);
    assert.equal(rows.reduce((sum, r) => sum + r.discardedFrames, 0), 0);
    assert.equal(p.snapshot().executed, 13);
});

test('overflow remains explicit loss while subsequent zero-demand ticks drain bounded debt', () => {
    const p = createFramePacer();
    run(p, 0);
    const first = run(p, 50);
    assert.equal(first.discardedFrames, 20);
    assert.equal(first.pendingBeforeExecution, 30);
    assert.equal(first.backlogAfter, 25);
    assert.equal(first.newlyDueOverTickCapFrames, 45);
    assert.equal(first.firstPendingOrdinal, 26);
    const drains = Array.from({ length: 5 }, () => run(p, 50));
    assert.deepEqual(drains.map(r => r.requestedFrames), [0, 0, 0, 0, 0]);
    assert.deepEqual(drains.map(r => r.backlogAfter), [20, 15, 10, 5, 0]);
    assert.deepEqual(p.snapshot(), { epoch: 0, due: 50, backlog: 0,
        executed: 30, dropped: 20, pendingBudget: null, firstPendingOrdinal: null });
});

test('partial guest-counter progress retains unexecuted work and exposes the mismatch', () => {
    const p = createFramePacer();
    const row = run(p, 12, 3);
    assert.equal(row.plannedFrames, 5);
    assert.equal(row.executedFrames, 3);
    assert.equal(row.backlogAfter, 9);
    assert.equal(row.coreFrameMismatch, true);
    assert.equal(run(p, 12).backlogAfter, 4);
    assert.equal(run(p, 12).backlogAfter, 0);
    assert.equal(p.snapshot().executed, 12);
});

test('zero progress cannot silently retire a scheduled batch', () => {
    const p = createFramePacer();
    const row = run(p, 2, 0);
    assert.equal(row.backlogAfter, 2);
    assert.equal(row.coreFrameMismatch, true);
    assert.equal(run(p, 2).executedFrames, 2);
});

test('pause/load epoch resets expose abandoned debt and never leak it into the new clock', () => {
    const p = createFramePacer();
    run(p, 12);
    assert.deepEqual(p.reset(), { previousEpoch: 0, abandonedFrames: 7,
        hadUnsettledPlan: false, dueTotal: 12, executedTotal: 5, overflowDroppedTotal: 0 });
    assert.equal(run(p, 0).executedFrames, 0);
    assert.equal(run(p, 1).executedFrames, 1);
    p.plan(50);
    const abandoned = p.reset();
    assert.equal(abandoned.abandonedFrames, 30);
    assert.equal(abandoned.hadUnsettledPlan, true);
    assert.equal(abandoned.dueTotal, abandoned.executedTotal + abandoned.overflowDroppedTotal + 30);
    assert.equal(p.snapshot().epoch, 2);
    assert.equal(run(p, 0).executedFrames, 0);
});

test('invalid or duplicate transitions do not mutate the active ledger', () => {
    const p = createFramePacer();
    for (const bad of [-1, .5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1, '5', null]) {
        const before = p.snapshot();
        assert.throws(() => p.plan(bad));
        assert.deepEqual(p.snapshot(), before);
    }
    assert.throws(() => p.settle(0));
    p.plan(10);
    const before = p.snapshot();
    assert.throws(() => p.plan(10));
    for (const actual of [-1, 6, .5, Infinity]) assert.throws(() => p.settle(actual));
    assert.deepEqual(p.snapshot(), before);
    p.settle(5);
    assert.throws(() => p.plan(9));
    assert.equal(run(p, 10).backlogAfter, 0);
});

test('returned budgets and snapshots cannot alter internal state', () => {
    const p = createFramePacer();
    const budget = p.plan(2);
    assert.throws(() => { budget.frames = 99; });
    assert.throws(() => { p.snapshot().backlog = 0; });
    assert.equal(p.settle(2).executedTotal, 2);
});
