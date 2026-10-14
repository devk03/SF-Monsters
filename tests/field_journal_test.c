// Production objective routing and native window lifecycle; rendering is checked in-game.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint8_t bool8;
#define TRUE 1
#define FALSE 0
#define EWRAM_DATA
#define _(s) s
#define ARRAY_COUNT(a) (sizeof(a) / sizeof((a)[0]))
// Native ABI constants; no private engine checkout is required for this unit test.
#define TEXT_COLOR_WHITE 1
#define TEXT_COLOR_DARK_GRAY 2
#define TEXT_COLOR_LIGHT_GRAY 3
#define TEXT_COLOR_BLUE 8
#define TEXT_COLOR_LIGHT_BLUE 9
#define FLAG_SYS_POKEMON_GET 0x860
#define FLAG_BADGE01_GET 0x867
#define MAP_GROUP(map) ((map) >> 8)
#define MAP_NUM(map) ((map) & 255)
#define MAP_LITTLEROOT_TOWN 9
#define MAP_OLDALE_TOWN 10
#define MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F 0x100
#define MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB 0x104
#define MAP_RUSTBORO_CITY_GYM 0xb03
#define WINDOW_NONE 255
#define FONT_NORMAL 1
#define FONT_SMALL 0
#define TEXT_SKIP_DRAW 255
#define COPYWIN_FULL 3
#define SE_SELECT 5
#define B_BUTTON 2
#define START_BUTTON 8
#define JOY_NEW(keys) (buttons & (keys))
#define PIXEL_FILL(n) ((n) | ((n) << 4))
struct WindowTemplate {u8 bg,tilemapLeft,tilemapTop,width,height,paletteNum;u16 baseBlock;};
struct SaveBlock {
    struct {u8 mapGroup,mapNum;} location;
    u16 vars[256];
    u8 flags[0x900], party[600], inventory[300];
};
static struct SaveBlock save, *gSaveBlock1Ptr = &save;
static u16 buttons;
static u8 allocation = 3;
static int removed, unfreezes, unlocks, menuRestores, draws;
static const u8 *drawnObjective;
static bool8 (*gMenuCallback)(void);
static u16 VarGet(u16 id) {return save.vars[id - 0x4000];}
static bool8 FlagGet(u16 id) {return save.flags[id];}
static void PlaySE(int id) {assert(id == SE_SELECT);}
static void ClearStdWindowAndFrameToTransparent(u8 id, bool8 copy) {(void)id;(void)copy;}
static void RemoveWindow(u8 id) {assert(id == 3);removed++;}
static void ScriptUnfreezeObjectEvents(void) {unfreezes++;}
static void UnlockPlayerFieldControls(void) {unlocks++;}
static void InitStartMenu(void) {menuRestores++;}
static bool8 HandleStartMenuInput(void) {return FALSE;}
static u8 AddWindow(const struct WindowTemplate *w) {
    assert(w->tilemapLeft + w->width < 30 && w->tilemapTop + w->height < 20);
    assert(w->baseBlock + w->width * w->height <= 0x200);
    return allocation;
}
static u8 GetStartMenuWindowId(void) {return 1;}
static void RemoveStartMenuWindow(void) {removed++;}
static void DrawStdWindowFrame(u8 id,bool8 copy) {assert(id==3 && !copy);draws=0;}
static void AddTextPrinterParameterized3(u8 id,int font,int x,int y,const u8 *colors,int speed,const u8 *text) {
    assert(id==3 && x>=0 && y>=0 && y+(font==FONT_SMALL?12:16)<=136);
    assert(colors && speed==TEXT_SKIP_DRAW);
    if (draws++ == 3) drawnObjective=text;
}
static void FillWindowPixelRect(u8 id,int fill,int x,int y,int w,int h) {
    assert(id==3 && fill>=0 && x>=0 && y>=0 && x+w<=208 && y+h<=136);
}
static void CopyWindowToVram(u8 id,int mode) {assert(id==3 && mode==COPYWIN_FULL);}
#include "../romhack/engine/field_journal.h"

int main(void) {
    static const struct {u16 parcel,relays;bool8 starter,badge;const char *title;} cases[] = {
        {1,0,FALSE,FALSE,"CHOOSE A COMPANION"},
        {2,0,TRUE,FALSE,"FIND ROON'S SENSOR"},
        {3,0,TRUE,FALSE,"RETURN THE SENSOR"},
        {4,0,TRUE,FALSE,"DELIVER TO COGNITION"},
        {4,1,TRUE,FALSE,"STABILIZE THE INPUT"},
        {4,2,TRUE,FALSE,"RESTORE THE OUTPUT"},
        {4,3,TRUE,FALSE,"CHALLENGE SCOTT"},
        {4,4,TRUE,TRUE,"BUILD BADGE EARNED"},
        // An earned badge must override older quest/relay values.
        {2,0,TRUE,TRUE,"BUILD BADGE EARNED"}
    };
    unsigned i;
    assert(strcmp((const char *)sSFJournalLabel,"JOURNAL")==0);
    for(i=0;i<ARRAY_COUNT(cases);i++) {
        struct SaveBlock before;
        save.vars[0xf7]=cases[i].parcel;save.vars[0xdb]=cases[i].relays;
        save.flags[FLAG_SYS_POKEMON_GET]=cases[i].starter;
        save.flags[FLAG_BADGE01_GET]=cases[i].badge;
        before=save;buttons=0;removed=unfreezes=unlocks=menuRestores=0;
        assert(StartMenuSFJournalCallback()==FALSE);
        for (unsigned line=0;line<8;line++) assert(gMenuCallback()==FALSE);
        assert(strcmp((const char *)drawnObjective,cases[i].title)==0);
        assert(gMenuCallback==SFJournalInput && SFJournalInput()==FALSE);
        buttons=B_BUTTON;assert(SFJournalInput()==FALSE);
        assert(removed==2 && menuRestores==1 && unfreezes==0 && unlocks==0);
        assert(gMenuCallback==HandleStartMenuInput && sSFJournalWindowId==WINDOW_NONE);
        buttons=0;assert(StartMenuSFJournalCallback()==FALSE);
        buttons=START_BUTTON;assert(SFJournalInput()==TRUE);
        assert(unfreezes==1 && unlocks==1 && sSFJournalWindowId==WINDOW_NONE);
        assert(memcmp(&save,&before,sizeof(save))==0);
    }
    {
        const u16 maps[]={9,0x100,10,0x104,0xb03};
        const char *locations[]={"OUTER SUNSET","YOUR APARTMENT / SUNSET","SOUTH PARK / SOMA","SOUTH PARK FIELD CLINIC","COGNITION / SOUTH PARK"};
        for(i=0;i<ARRAY_COUNT(maps);i++) {
            save.location.mapGroup=MAP_GROUP(maps[i]);save.location.mapNum=MAP_NUM(maps[i]);
            assert(strcmp((const char *)SFJournalLocation(),locations[i])==0);
        }
    }
    // Arrival must not send the player back to the Sunset Muni stop.
    sSFJournalStage=3;save.location.mapGroup=0;save.location.mapNum=10;
    assert(strcmp((const char *)SFJournalDirections(0),"Find SCOTT inside COGNITION.")==0);
    save.location.mapNum=9;
    assert(strcmp((const char *)SFJournalDirections(0),"JONATHAN waits east on JUDAH.")==0);
    // A failed allocation must leave the original menu usable, with controls locked.
    allocation=WINDOW_NONE;removed=unfreezes=unlocks=0;
    assert(StartMenuSFJournalCallback()==FALSE && gMenuCallback==HandleStartMenuInput);
    assert(removed==0 && unfreezes==0 && unlocks==0);
    puts("Journal: eight chapter leads, badge precedence, read-only state, B/Start cleanup and allocation failure passed.");
}
