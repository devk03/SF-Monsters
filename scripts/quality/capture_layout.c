// Compile with the pinned cartridge compiler. Modern ARM GCC packs some nested
// save structures differently; its offsets cannot initialize the native engine.
#include "global.h"
#include "battle.h"
#include <stddef.h>

const unsigned capture_layout[] = {
    sizeof(struct SaveBlock1), sizeof(struct SaveBlock2),
    offsetof(struct BattleStruct, safariCatchFactor),
    offsetof(struct SaveBlock1, location), offsetof(struct SaveBlock1, seen1),
    offsetof(struct SaveBlock1, seen2), offsetof(struct SaveBlock2, pokedex.owned),
    offsetof(struct SaveBlock2, pokedex.seen)
};
