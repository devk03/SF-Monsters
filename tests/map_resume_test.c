// Exercise the production position resolver at its native map/warp boundary.
#include <assert.h>
#include <stdint.h>
#include <string.h>
typedef uint8_t bool8;
typedef uint8_t u8;
typedef int16_t s16;
#define TRUE 1
#define FALSE 0
#define MAP_OFFSET 7
#define WARP_ID_NONE -1
#define OBJECT_EVENTS_COUNT 16
struct Coords { s16 x, y; };
struct WarpData { int mapGroup, mapNum; };
struct ObjectEvent { bool8 active, isPlayer; u8 currentMetatileBehavior; };
struct SaveBlock { struct Coords pos; struct WarpData location; int money; struct ObjectEvent objectEvents[16]; };
struct MapLayout { int width, height; };
struct ObjectEventTemplate { s16 x, y; u8 movementRangeX, movementRangeY; };
struct CoordEvent { s16 x, y; };
struct WarpEvent { s16 x, y; };
struct MapEvents {
    u8 objectEventCount, warpCount, coordEventCount;
    const struct ObjectEventTemplate *objectEvents;
    const struct WarpEvent *warps;
    const struct CoordEvent *coordEvents;
};
struct MapHeader { const struct MapLayout *mapLayout; const struct MapEvents *events; };
static struct SaveBlock sSave;
static struct SaveBlock *gSaveBlock1Ptr = &sSave;
static const struct MapLayout sLayout = {5, 5};
static const struct ObjectEventTemplate sObjects[] = {{2, 1, 0, 0}};
static const struct WarpEvent sWarps[] = {{1, 2}};
static const struct MapEvents sEvents = {1, 1, 0, sObjects, sWarps, NULL};
static const struct MapHeader gMapHeader = {&sLayout, &sEvents};
static u8 sCollision[5][5], sBehavior[5][5];
static bool8 sSurfBadge;
static bool8 FlagGet(int flag) { (void)flag;return sSurfBadge; }
static bool8 MetatileBehavior_IsSurfableWaterOrUnderwater(u8 value) {return value==1 || value==2;}
static bool8 MetatileBehavior_IsWaterfall(u8 value) {return value==2;}
static u8 MapGridGetMetatileBehaviorAt(s16 x,s16 y) {return sBehavior[y-MAP_OFFSET][x-MAP_OFFSET];}
static int sWarpCalls, sWarpGroup, sWarpNum, sWarpId, sWarpX, sWarpY;
static u8 MapGridGetCollisionAt(s16 x, s16 y)
{
    return sCollision[y - MAP_OFFSET][x - MAP_OFFSET];
}
static void SetWarpDestination(int group, int num, int id, s16 x, s16 y)
{
    sWarpCalls++;
    sWarpGroup = group; sWarpNum = num; sWarpId = id; sWarpX = x; sWarpY = y;
}
#include "../romhack/engine/map_resume.h"

static void reset(void)
{
    memset(sCollision, 0, sizeof(sCollision));
    memset(sBehavior, 0, sizeof(sBehavior));
    memset(sSave.objectEvents,0,sizeof(sSave.objectEvents));
    sSave.objectEvents[0]=(struct ObjectEvent){TRUE,TRUE,0};sSurfBadge=FALSE;
    sSave.pos = (struct Coords){2, 2};
    sSave.location = (struct WarpData){1, 2};
    sSave.money = 4000;
    sWarpCalls = 0;
}
int main(void)
{
    reset();
    assert(!SFMapResumeWarpIfNeeded());
    assert(sWarpCalls == 0 && sSave.pos.x == 2 && sSave.pos.y == 2);
    // New actors on an older save must not overlap the resumed player.
    sSave.pos = (struct Coords){2, 1};
    assert(SFMapResumeWarpIfNeeded() && sWarpY != 1);
    reset();
    sCollision[2][2] = 3;
    assert(SFMapResumeWarpIfNeeded());
    // The equally near north/left tiles hold an NPC and door; east is safe.
    assert(sWarpCalls == 1 && sWarpX == 3 && sWarpY == 2);
    assert(sWarpGroup == 1 && sWarpNum == 2 && sWarpId == WARP_ID_NONE);
    assert(sSave.pos.x == 2 && sSave.pos.y == 2 && sSave.money == 4000);
    reset();
    sCollision[2][2] = 3;
    sSave.location.mapGroup = 9;
    assert(!SFMapResumeWarpIfNeeded() && sWarpCalls == 0);
    reset();
    sSave.pos = (struct Coords){-1, 2};
    assert(SFMapResumeWarpIfNeeded() && sWarpX == 0 && sWarpY == 2);
    reset();
    sSave.pos = (struct Coords){1000, 1000};
    assert(SFMapResumeWarpIfNeeded() && sWarpX == 4 && sWarpY == 4);
    reset();
    memset(sCollision, 3, sizeof(sCollision));
    assert(!SFMapResumeWarpIfNeeded() && sWarpCalls == 0);
    // A newly flooded old land tile cannot grant Surf, with or without a badge.
    reset();sBehavior[2][2]=1;
    assert(SFMapResumeWarpIfNeeded() && sBehavior[sWarpY][sWarpX]==0);
    reset();sBehavior[2][2]=1;sSurfBadge=TRUE;
    assert(SFMapResumeWarpIfNeeded() && sBehavior[sWarpY][sWarpX]==0);
    // Actual water saves keep their mode; an NPC forces relocation to water,
    // even when there is closer dry ground. Falls are never safe spawn tiles.
    reset();sSave.objectEvents[0].currentMetatileBehavior=1;sSurfBadge=TRUE;
    sBehavior[2][2]=1;
    assert(!SFMapResumeWarpIfNeeded());
    sCollision[2][2]=3;sBehavior[1][2]=1;sBehavior[2][1]=1;sBehavior[4][2]=1;
    assert(SFMapResumeWarpIfNeeded() && sWarpX==2 && sWarpY==4);
    reset();sSave.objectEvents[0].currentMetatileBehavior=1;sSurfBadge=TRUE;
    sBehavior[2][2]=2;sBehavior[3][2]=1;
    assert(SFMapResumeWarpIfNeeded() && sWarpX==2 && sWarpY==3);
    return 0;
}
