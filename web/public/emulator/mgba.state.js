/* Canonical output storage for the pinned core's partial-field serializer. */
export function serializeCoreState(mod) {
    const size = mod._mgbawasm_state_size();
    if (!Number.isSafeInteger(size) || size <= 0) throw new Error('Invalid native state size');
    const pointer = mod._malloc(size);
    if (!Number.isSafeInteger(pointer) || pointer <= 0) throw new Error('Could not allocate native state output');
    try {
        const end = pointer + size;
        if (!Number.isSafeInteger(end) || end > mod.HEAPU8.length) throw new Error('Native state output exceeds memory');
        // Only output scratch is initialized. Guest RAM/registers are untouched.
        mod.HEAPU8.fill(0, pointer, end);
        if (mod._mgbawasm_state_save(pointer) !== 1) throw new Error('Could not serialize native state');
        return mod.HEAPU8.slice(pointer, end);
    } finally {
        mod._free(pointer);
    }
}
