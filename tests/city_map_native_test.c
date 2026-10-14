// Production whitelist and parent resolver; poisoned foreign lists must never be read.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint8_t bool8;
#define TRUE 1
#define FALSE 0
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define MAP_GROUP(id) ((id)>>8)
#define MAP_UNDEFINED 0x7f7f
#define NUM_LAND_MONS_ENCOUNTER_SLOTS 12
#define NUM_WATER_MONS_ENCOUNTER_SLOTS 5
#define NUM_FISHING_MONS_ENCOUNTER_SLOTS 10
#define NUM_ROCK_SMASH_MONS_ENCOUNTER_SLOTS 5
struct WildPokemon {u8 minLevel,maxLevel;u16 species;};
struct WildPokemonInfo {u8 encounterRate;const struct WildPokemon *wildPokemon;};
struct WildPokemonHeader {u8 mapGroup,mapNum;const struct WildPokemonInfo *landMonsInfo,*waterMonsInfo,*rockSmashMonsInfo,*fishingMonsInfo;};
static const struct WildPokemon landSunset[12]={{1,2,101},{1,2,303}};
static const struct WildPokemon landPark[12]={{1,2,202},{1,2,303}};
static const struct WildPokemon water[5]={[4]={1,2,606}};
static const struct WildPokemon rock[5]={[4]={1,2,505}};
static const struct WildPokemon fish[10]={[9]={1,2,404}};
static const struct WildPokemonInfo sunInfo={20,landSunset},parkInfo={20,landPark};
static const struct WildPokemonInfo waterInfo={20,water},rockInfo={20,rock},fishInfo={20,fish};
static const struct WildPokemonHeader gWildMonHeaders[]={
    {0,3,(void *)1,(void *)1,(void *)1,(void *)1},
    {0,9,&sunInfo,NULL,&rockInfo,NULL},
    {0,10,&parkInfo,&waterInfo,NULL,&fishInfo},
    {24,1,(void *)1,(void *)1,(void *)1,(void *)1},
    {0x7f,0x7f,NULL,NULL,NULL,NULL}
};
static struct {u16 numOverworldAreas,numSpecialAreas;} screen,*sPokedexAreaScreen=&screen;
static u8 found[2];
static bool8 MonListHasSpecies(const struct WildPokemonInfo *info,u16 species,u16 count) {
    if(info) for(u16 i=0;i<count;i++) if(info->wildPokemon[i].species==species)return TRUE;
    return FALSE;
}
static void SetAreaHasMon(u16 group,u16 number) {
    assert(group==0 && (number==9 || number==10));
    assert(screen.numOverworldAreas<2);found[screen.numOverworldAreas++]=number;
}
#include "../romhack/engine/habitat_map.h"
struct SaveBlock {
    struct {u8 mapGroup,mapNum;} location;
    struct {int mapGroup,mapNum,x,y;} escapeWarp,dynamicWarp;
    u8 flags[300],party[600],items[300];
};
static struct SaveBlock save,*gSaveBlock1Ptr=&save;
static struct RegionMap {u16 mapSecId,cursorPosX,cursorPosY;bool8 playerIsInCave;} region,*sRegionMap=&region;
static const struct {u8 x,y,width,height;} gRegionMapEntries[]={{7,8,1,1},{18,5,1,1}};
#include "../romhack/engine/region_map_parent.h"

int main(void) {
    const struct {u16 species;u8 count,first,last;} cases[]={
        {101,1,9,9},{202,1,10,10},{303,2,9,10},
        {404,1,10,10},{505,1,9,9},{606,1,10,10},{999,0,0,0}
    };
    for(unsigned i=0;i<ARRAY_COUNT(cases);i++) {
        screen.numOverworldAreas=55;screen.numSpecialAreas=32;
        FindMapsWithMon(cases[i].species);
        assert(screen.numSpecialAreas==0 && screen.numOverworldAreas==cases[i].count);
        if(cases[i].count)assert(found[0]==cases[i].first && found[cases[i].count-1]==cases[i].last);
    }
    const struct {u8 group,number,section,x,y;} locations[]={
        {0,9,0,8,10},{1,0,0,8,10},{0,10,1,19,7},{1,4,1,19,7},{11,3,1,19,7},{2,0,1,19,7}
    };
    memset(&save,0xa5,sizeof(save));
    for(unsigned i=0;i<ARRAY_COUNT(locations);i++) {
        struct SaveBlock before;
        save.location.mapGroup=locations[i].group;save.location.mapNum=locations[i].number;
        before=save;memset(&region,0x55,sizeof(region));
        assert(SFInitRegionMapPlayer()==TRUE);
        assert(region.mapSecId==locations[i].section && !region.playerIsInCave);
        assert(region.cursorPosX==locations[i].x && region.cursorPosY==locations[i].y);
        assert(memcmp(&save,&before,sizeof(save))==0);
    }
    save.location.mapGroup=0;save.location.mapNum=3;
    struct RegionMap before=region;
    assert(SFInitRegionMapPlayer()==FALSE && memcmp(&region,&before,sizeof(region))==0);
    puts("SF habitat whitelist, all four encounter bounds, stale-count reset and six read-only player parents passed.");
}
