// Authored SF layouts replace cached scenery. Preserve valid saved positions;
// use the native same-map warp only when an updated layout occupies that tile.
#include "sf_authored_maps.h"

static bool8 SFResumeTileIsWalkable(s16 x, s16 y)
{
    if (x < 0 || y < 0 || x >= gMapHeader.mapLayout->width
        || y >= gMapHeader.mapLayout->height)
        return FALSE;
    return MapGridGetCollisionAt(x + MAP_OFFSET, y + MAP_OFFSET) == 0;
}

static bool8 SFResumeTileIsSafe(s16 x, s16 y)
{
    u8 i;
    const struct MapEvents *events = gMapHeader.events;
    if (!SFResumeTileIsWalkable(x, y))
        return FALSE;
    for (i = 0; i < events->warpCount; i++)
        if (events->warps[i].x == x && events->warps[i].y == y)
            return FALSE;
    for (i = 0; i < events->objectEventCount; i++)
        if (events->objectEvents[i].x == x && events->objectEvents[i].y == y)
            return FALSE;
    return TRUE;
}

static bool8 SFMapResumeWarpIfNeeded(void)
{
    s16 radius, dy, dx, x, y;
    s16 oldX = gSaveBlock1Ptr->pos.x;
    s16 oldY = gSaveBlock1Ptr->pos.y;
    if (!SFMapUsesAuthoredLayout() || SFResumeTileIsWalkable(oldX, oldY))
        return FALSE;
    // A smaller authored layout may leave an older coordinate out of bounds.
    if (oldX < 0) oldX = 0;
    if (oldY < 0) oldY = 0;
    if (oldX >= gMapHeader.mapLayout->width) oldX = gMapHeader.mapLayout->width - 1;
    if (oldY >= gMapHeader.mapLayout->height) oldY = gMapHeader.mapLayout->height - 1;
    // Manhattan rings prefer nearby tiles. Avoid door warps and NPC anchors.
    for (radius = 0; radius <= gMapHeader.mapLayout->width
                                   + gMapHeader.mapLayout->height; radius++)
    {
        for (dy = -radius; dy <= radius; dy++)
        {
            dx = radius - (dy < 0 ? -dy : dy);
            y = oldY + dy;
            x = oldX - dx;
            if (!SFResumeTileIsSafe(x, y))
            {
                x = oldX + dx;
                if (!SFResumeTileIsSafe(x, y))
                    continue;
            }
            SetWarpDestination(gSaveBlock1Ptr->location.mapGroup,
                               gSaveBlock1Ptr->location.mapNum,
                               WARP_ID_NONE, x, y);
            return TRUE;
        }
    }
    return FALSE;
}
