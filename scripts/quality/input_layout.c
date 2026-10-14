/* Compile with the pinned cartridge compiler, never the host pointer ABI. */
#include "global.h"
#include "main.h"
#include <stddef.h>

const unsigned input_layout[] = {
    sizeof(void*), offsetof(struct Main, heldKeysRaw),
    offsetof(struct Main, newKeysRaw), offsetof(struct Main, heldKeys),
    offsetof(struct Main, newKeys)
};
