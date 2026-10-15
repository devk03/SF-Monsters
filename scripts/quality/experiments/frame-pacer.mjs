/** Bounded foreground frame-credit ledger. Not a performance-acceptance claim. */
export const MAX_FRAMES_PER_TICK = 5;
export const MAX_PENDING_FRAMES = 30;

function integer(value, name) {
    if (!Number.isSafeInteger(value) || value < 0) {
        throw new RangeError(`${name} must be a nonnegative safe integer`);
    }
}

/**
 * plan() adds newly due work once. settle() retires actual guest-counter progress,
 * not the proposed budget. Only an explicit bounded overflow or epoch reset may
 * abandon work. Callers must report both, plus planned/actual counter mismatches.
 * A reset is a lifecycle boundary; it must never be presented as a clean sample.
 */
export function createFramePacer() {
    let due = 0, backlog = 0, executed = 0, dropped = 0, epoch = 0;
    let pending = null;

    function snapshot() {
        return Object.freeze({ epoch, due, backlog, executed, dropped,
            pendingBudget: pending?.frames ?? null,
            firstPendingOrdinal: backlog ? due - backlog + 1 : null });
    }

    function plan(nextDue) {
        integer(nextDue, 'due');
        if (pending) throw new Error('Settle the existing frame budget first');
        if (nextDue < due) throw new RangeError('Due credits cannot regress within an epoch');
        const requestedFrames = nextDue - due;
        const backlogBefore = backlog;
        const available = backlogBefore + requestedFrames;
        integer(available, 'available credits');
        const discardedFrames = Math.max(0, available - MAX_PENDING_FRAMES);
        backlog = available - discardedFrames;
        dropped += discardedFrames;
        due = nextDue;
        pending = Object.freeze({ epoch, requestedFrames, backlogBefore,
            discardedFrames, pendingBeforeExecution: backlog,
            frames: Math.min(MAX_FRAMES_PER_TICK, backlog),
            firstExecutionOrdinal: backlog ? due - backlog + 1 : null,
            // This preserves the old loop's fresh-demand cap warning. It is
            // separate from actual overflow loss and repeated carry deferrals.
            newlyDueOverTickCapFrames: Math.max(0, requestedFrames - MAX_FRAMES_PER_TICK) });
        return pending;
    }

    function settle(actualVideoFrames) {
        integer(actualVideoFrames, 'actual guest-counter progress');
        if (!pending) throw new Error('Plan a frame budget before settling it');
        if (actualVideoFrames > pending.frames) {
            throw new RangeError('Guest counter advanced beyond its planned budget');
        }
        const planned = pending;
        backlog -= actualVideoFrames;
        executed += actualVideoFrames;
        if (due !== executed + dropped + backlog) {
            throw new Error('Frame-credit conservation failed');
        }
        pending = null;
        return Object.freeze({ epoch,
            requestedFrames: planned.requestedFrames,
            plannedFrames: planned.frames,
            executedFrames: actualVideoFrames,
            discardedFrames: planned.discardedFrames,
            backlogBefore: planned.backlogBefore, backlogAfter: backlog,
            pendingBeforeExecution: planned.pendingBeforeExecution,
            newlyDueOverTickCapFrames: planned.newlyDueOverTickCapFrames,
            coreFrameMismatch: planned.frames !== actualVideoFrames,
            dueTotal: due, executedTotal: executed, droppedTotal: dropped,
            firstPendingOrdinal: backlog ? due - backlog + 1 : null });
    }

    function reset() {
        const result = Object.freeze({ previousEpoch: epoch,
            abandonedFrames: backlog, hadUnsettledPlan: pending !== null,
            dueTotal: due, executedTotal: executed, overflowDroppedTotal: dropped });
        ++epoch;
        due = backlog = executed = dropped = 0;
        pending = null;
        return result;
    }

    return Object.freeze({ plan, settle, reset, snapshot });
}
