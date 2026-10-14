// Read only the SF encounter whitelist. Legacy roamers/special places are excluded.
#include "sf_habitat_maps.h"

static void FindMapsWithMon(u16 species)
{
    u16 i, j;
    const struct WildPokemonHeader *header;
    sPokedexAreaScreen->numOverworldAreas = 0;
    sPokedexAreaScreen->numSpecialAreas = 0;
    for (i = 0; gWildMonHeaders[i].mapGroup != MAP_GROUP(MAP_UNDEFINED); i++)
    {
        header = &gWildMonHeaders[i];
        for (j = 0; j < ARRAY_COUNT(sSFHabitatMapIds); j++)
            if (header->mapGroup == sSFHabitatMapIds[j][0]
                && header->mapNum == sSFHabitatMapIds[j][1])
                break;
        if (j == ARRAY_COUNT(sSFHabitatMapIds))
            continue;
        if (MonListHasSpecies(header->landMonsInfo, species, NUM_LAND_MONS_ENCOUNTER_SLOTS)
            || MonListHasSpecies(header->waterMonsInfo, species, NUM_WATER_MONS_ENCOUNTER_SLOTS)
            || MonListHasSpecies(header->fishingMonsInfo, species, NUM_FISHING_MONS_ENCOUNTER_SLOTS)
            || MonListHasSpecies(header->rockSmashMonsInfo, species, NUM_ROCK_SMASH_MONS_ENCOUNTER_SLOTS))
            SetAreaHasMon(header->mapGroup, header->mapNum);
    }
}
