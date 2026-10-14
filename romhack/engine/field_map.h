// Small SF entry point into the unchanged native field-map display/return loop.
#include "sf_authored_maps.h"

static const u8 sSFFieldMapTitle[] = _("SF MAP");

static const u8 *SFFieldMapTitle(void)
{
    return SFMapUsesAuthoredLayout() ? sSFFieldMapTitle : gText_Hoenn;
}

bool8 SFTryOpenFieldMap(void (*callback)(void))
{
    if (!SFMapUsesAuthoredLayout() || callback == NULL || sFieldRegionMapHandler != NULL)
        return FALSE;
    sFieldRegionMapHandler = Alloc(sizeof(*sFieldRegionMapHandler));
    if (sFieldRegionMapHandler == NULL)
        return FALSE;
    sFieldRegionMapHandler->state = 0;
    sFieldRegionMapHandler->callback = callback;
    SetVBlankCallback(NULL);
    SetMainCallback2(MCB2_InitRegionMapRegisters);
    return TRUE;
}
