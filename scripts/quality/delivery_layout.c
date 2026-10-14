#include "global.h"
#include "pokemon_storage_system.h"
#include <stddef.h>

const unsigned delivery_layout[] = {
    sizeof(struct PokemonStorage), sizeof(struct Pokemon), sizeof(struct BoxPokemon),
    offsetof(struct PokemonStorage, boxes), offsetof(struct SaveBlock1, vars),
    offsetof(struct SaveBlock2, playerGender), offsetof(struct SaveBlock2, playerTrainerId)
};
