// Exercise the production cache resolver independently of the ROM compiler.
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef bool bool8;
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define OBJECT_EVENTS_COUNT 8
#define MOVEMENT_TYPE_PLAYER 11

struct ObjectEventTemplate {
    u8 localId, graphicsId, movementType, flagId;
    int16_t x, y;
    uint32_t script;
};
struct ObjectEvent {
    bool active;
    u8 localId, mapNum, mapGroup, movementType, graphicsId;
    int16_t x, y;
    u8 facing, movementStep;
};
struct MapEvents {
    u8 objectEventCount;
    const struct ObjectEventTemplate *objectEvents;
};
struct SaveBlock {
    struct {u8 mapNum, mapGroup;} location;
    struct ObjectEventTemplate objectEventTemplates[64];
    uint32_t money;
    uint16_t partyHp;
    u8 badge;
};
static struct SaveBlock save, *gSaveBlock1Ptr=&save;
static struct ObjectEvent gObjectEvents[OBJECT_EVENTS_COUNT];
static struct {const struct MapEvents *events;} gMapHeader;
static bool8 SFMapUsesAuthoredLayout(void) {
    return save.location.mapNum==2 && save.location.mapGroup==1;
}
static bool8 SFIsNamedCastGraphics(u8 id) {return id==79 || id==80;}
#include "../romhack/engine/cast_resume.h"

int main(void)
{
    const struct ObjectEventTemplate current[] = {
        {1,79,2,4,6,4,0x1234}, {2,80,2,5,9,9,0x5678}, {3,7,2,6,3,3,0x9999}
    };
    const struct MapEvents events={3,current};
    struct SaveBlock expected;
    struct ObjectEvent expectedObjects[OBJECT_EVENTS_COUNT];
    gMapHeader.events=&events;
    save.location.mapNum=2;save.location.mapGroup=1;
    save.money=4000;save.partyHp=4;save.badge=1;
    save.objectEventTemplates[0]=(struct ObjectEventTemplate){1,25,3,12,4,5,0xaabb};
    save.objectEventTemplates[1]=(struct ObjectEventTemplate){2,30,4,13,11,10,0xccdd};
    save.objectEventTemplates[2]=(struct ObjectEventTemplate){3,9,5,14,2,3,0xeeff};
    gObjectEvents[0]=(struct ObjectEvent){true,1,2,1,3,25,4,5,2,8};
    gObjectEvents[1]=(struct ObjectEvent){true,2,2,1,4,30,11,10,3,9};
    gObjectEvents[2]=(struct ObjectEvent){true,1,2,1,MOVEMENT_TYPE_PLAYER,4,6,8,4,10};
    gObjectEvents[3]=(struct ObjectEvent){true,1,9,1,3,25,1,1,2,8};
    gObjectEvents[4]=(struct ObjectEvent){false,2,2,1,4,30,11,10,3,9};
    gObjectEvents[5]=(struct ObjectEvent){true,3,2,1,4,9,2,3,3,9};
    expected=save;memcpy(expectedObjects,gObjectEvents,sizeof(gObjectEvents));
    expected.objectEventTemplates[0].graphicsId=79;
    expected.objectEventTemplates[1].graphicsId=80;
    expectedObjects[0].graphicsId=79;expectedObjects[1].graphicsId=80;
    SFResumeNamedCastGraphics();
    assert(memcmp(&save,&expected,sizeof(save))==0);
    assert(memcmp(gObjectEvents,expectedObjects,sizeof(gObjectEvents))==0);
    // Idempotent on a newer save; does not restart movement or change facing.
    SFResumeNamedCastGraphics();
    assert(memcmp(&save,&expected,sizeof(save))==0);
    assert(memcmp(gObjectEvents,expectedObjects,sizeof(gObjectEvents))==0);
    // Inherited/unrelated maps keep their full saved appearance and state.
    save.location.mapGroup=3;save.objectEventTemplates[0].graphicsId=25;
    gObjectEvents[0].graphicsId=25;expected=save;
    memcpy(expectedObjects,gObjectEvents,sizeof(gObjectEvents));
    SFResumeNamedCastGraphics();
    assert(memcmp(&save,&expected,sizeof(save))==0);
    assert(memcmp(gObjectEvents,expectedObjects,sizeof(gObjectEvents))==0);
    puts("Named-cast cache refresh preserves positions, scripts, gameplay and unrelated objects.");
}
