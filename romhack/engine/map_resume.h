// Authored SF layouts replace cached scenery. Preserve valid saved positions;
// use the native same-map warp only when an updated layout occupies that tile.
#include "sf_authored_maps.h"
#include "constants/flags.h"
#ifdef SF_WORLD_RESUME_MASKS
#include "sf_resume_masks.h"
#else
static bool8 SFResumeCanReturn(s16 x, s16 y)
{
    (void)x;
    (void)y;
    return TRUE;
}
static bool8 SFResumeFallback(void)
{
    return FALSE;
}
#endif

static bool8 SFResumeTileIsWalkable(s16 x, s16 y)
{
    if (x < 0 || y < 0 || x >= gMapHeader.mapLayout->width
        || y >= gMapHeader.mapLayout->height)
        return FALSE;
    return MapGridGetCollisionAt(x + MAP_OFFSET, y + MAP_OFFSET) == 0;
}

static bool8 SFResumeSavedSurfing(void)
{
    u8 i;
    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        const struct ObjectEvent *object = &gSaveBlock1Ptr->objectEvents[i];
        if (object->active && object->isPlayer)
            return MetatileBehavior_IsSurfableWaterOrUnderwater(object->currentMetatileBehavior);
    }
    return FALSE;
}

static bool8 SFResumeTileIsSafe(s16 x, s16 y, bool8 surfing)
{
    u8 i;
    const struct MapEvents *events = gMapHeader.events;
    if (!SFResumeTileIsWalkable(x, y) || !SFResumeCanReturn(x, y))
        return FALSE;
    // Updated scenery must not silently put a land save into Surf or bypass
    // its badge gate. Prefer the saved land/water mode and never spawn on a fall.
    {
        u8 behavior = MapGridGetMetatileBehaviorAt(x + MAP_OFFSET, y + MAP_OFFSET);
        if (MetatileBehavior_IsSurfableWaterOrUnderwater(behavior) != surfing
            || MetatileBehavior_IsWaterfall(behavior))
            return FALSE;
    }
    for (i = 0; i < events->warpCount; i++)
        if (events->warps[i].x == x && events->warps[i].y == y)
            return FALSE;
    for (i = 0; i < events->objectEventCount; i++)
    {
        const struct ObjectEventTemplate *object = &events->objectEvents[i];
        if (x >= object->x - object->movementRangeX
            && x <= object->x + object->movementRangeX
            && y >= object->y - object->movementRangeY
            && y <= object->y + object->movementRangeY)
            return FALSE;
    }
    for (i = 0; i < events->coordEventCount; i++)
        if (events->coordEvents[i].x == x && events->coordEvents[i].y == y)
            return FALSE;
    return TRUE;
}

static bool8 SFResumeActorsChanged(void)
{
    u8 i;
    for (i = 0; i < gMapHeader.events->objectEventCount; i++)
    {
        const struct ObjectEventTemplate *current = &gMapHeader.events->objectEvents[i];
        const struct ObjectEventTemplate *saved = &gSaveBlock1Ptr->objectEventTemplates[i];
        if (current->localId != saved->localId || current->graphicsId != saved->graphicsId
            || current->kind != saved->kind
            || current->x != saved->x || current->y != saved->y
            || current->movementType != saved->movementType
            || current->movementRangeX != saved->movementRangeX
            || current->movementRangeY != saved->movementRangeY
            || current->elevation != saved->elevation
            || current->trainerType != saved->trainerType
            || current->trainerRange_berryTreeId != saved->trainerRange_berryTreeId
            || current->flagId != saved->flagId)
            return TRUE;
    }
    for (; i < ARRAY_COUNT(gSaveBlock1Ptr->objectEventTemplates); i++)
        if (gSaveBlock1Ptr->objectEventTemplates[i].localId != 0)
            return TRUE;
    return FALSE;
}

static bool8 SFMapResumeWarpIfNeeded(void)
{
    s16 radius, dy, dx, x, y;
    u8 pass;
    s16 oldX = gSaveBlock1Ptr->pos.x;
    s16 oldY = gSaveBlock1Ptr->pos.y;
    bool8 surfing = SFResumeSavedSurfing() && FlagGet(FLAG_BADGE05_GET);
    if (!SFMapUsesAuthoredLayout())
        return FALSE;
    if (SFResumeTileIsSafe(oldX, oldY, surfing))
    {
        if (!SFResumeActorsChanged()) return FALSE;
        // Keep a valid player coordinate while refreshing an older actor cache.
        SetWarpDestination(gSaveBlock1Ptr->location.mapGroup,
                           gSaveBlock1Ptr->location.mapNum,WARP_ID_NONE,oldX,oldY);
        return TRUE;
    }
    // A smaller authored layout may leave an older coordinate out of bounds.
    if (oldX < 0) oldX = 0;
    if (oldY < 0) oldY = 0;
    if (oldX >= gMapHeader.mapLayout->width) oldX = gMapHeader.mapLayout->width - 1;
    if (oldY >= gMapHeader.mapLayout->height) oldY = gMapHeader.mapLayout->height - 1;
    // Preserve Surf whenever possible. If its entire safe water area was
    // removed, recover onto reachable dry ground and use native on-foot setup.
    for (pass = 0; pass < (surfing ? 2 : 1); pass++)
    for (radius = 0; radius <= gMapHeader.mapLayout->width
                                   + gMapHeader.mapLayout->height; radius++)
    {
        for (dy = -radius; dy <= radius; dy++)
        {
            dx = radius - (dy < 0 ? -dy : dy);
            y = oldY + dy;
            x = oldX - dx;
            if (!SFResumeTileIsSafe(x, y, surfing && pass == 0))
            {
                x = oldX + dx;
                if (!SFResumeTileIsSafe(x, y, surfing && pass == 0))
                    continue;
            }
            if (surfing && pass != 0)
                ResetInitialPlayerAvatarState();
            SetWarpDestination(gSaveBlock1Ptr->location.mapGroup,
                               gSaveBlock1Ptr->location.mapNum,
                               WARP_ID_NONE, x, y);
            return TRUE;
        }
    }
    // No reachable tile remains: world drafts have a validated dry landing.
    return SFResumeFallback();
}
