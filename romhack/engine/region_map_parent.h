// Resolve all five authored maps without consulting stale escape/dynamic warps.
#include "sf_city_map_parents.h"

static bool8 SFInitRegionMapPlayer(void)
{
    u8 i, section;
    for (i = 0; i < ARRAY_COUNT(sSFRegionMapParents); i++)
    {
        if (gSaveBlock1Ptr->location.mapGroup != sSFRegionMapParents[i][0]
            || gSaveBlock1Ptr->location.mapNum != sSFRegionMapParents[i][1])
            continue;
        section = sSFRegionMapParents[i][2];
        sRegionMap->mapSecId = section;
        sRegionMap->cursorPosX = gRegionMapEntries[section].x + 1;
        sRegionMap->cursorPosY = gRegionMapEntries[section].y + 2;
        sRegionMap->playerIsInCave = FALSE;
        return TRUE;
    }
    return FALSE;
}
