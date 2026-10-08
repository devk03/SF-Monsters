// Refresh static named-cast appearance before saved objects create sprites.
// Keep positions, facing, movement state, flags and all gameplay data intact.
static void SFResumeNamedCastGraphics(void)
{
    u8 i, j;
    const struct MapEvents *events = gMapHeader.events;
    if (!SFMapUsesAuthoredLayout())
        return;
    for (i = 0; i < events->objectEventCount; i++)
    {
        const struct ObjectEventTemplate *current = &events->objectEvents[i];
        if (!SFIsNamedCastGraphics(current->graphicsId))
            continue;
        for (j = 0; j < ARRAY_COUNT(gSaveBlock1Ptr->objectEventTemplates); j++)
            if (gSaveBlock1Ptr->objectEventTemplates[j].localId == current->localId)
                gSaveBlock1Ptr->objectEventTemplates[j].graphicsId = current->graphicsId;
        for (j = 0; j < OBJECT_EVENTS_COUNT; j++)
        {
            struct ObjectEvent *object = &gObjectEvents[j];
            if (object->active && object->localId == current->localId
                && object->mapNum == gSaveBlock1Ptr->location.mapNum
                && object->mapGroup == gSaveBlock1Ptr->location.mapGroup
                && object->movementType != MOVEMENT_TYPE_PLAYER)
                object->graphicsId = current->graphicsId;
        }
    }
}
