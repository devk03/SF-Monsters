// Native SF place guide. Reading it never changes story state or saves.
#include "sf_authored_maps.h"
#include "constants/flags.h"

struct SFGuidePlace {
    u8 x, y;
    u8 name[40];
    u8 character[60];
    u8 routes[4][40];
    u8 gym;
    u16 doneFlag, foundFlag;
};
struct SFGuideEdge { u8 from, to, badge, water, count; u8 points[6][2]; };
#include "sf_world_guide_data.h"
EWRAM_DATA static u8 sSFGuideWindow = WINDOW_NONE;
EWRAM_DATA static u8 sSFGuideSelected = 0;
EWRAM_DATA static u8 sSFGuideDrawStep = 0;
EWRAM_DATA static u8 sSFGuideCurrent = 0;
EWRAM_DATA static u8 sSFGuideHereX = 0;
EWRAM_DATA static u8 sSFGuideHereY = 0;
EWRAM_DATA static u8 sSFGuideContext = 0;
EWRAM_DATA static u16 sSFGuideSavedPalette[16];
EWRAM_DATA static bool8 sSFGuideDetails = FALSE;
static const u8 sSFGuideLabel[] = _("SF MAP");
static const u8 sSFGuideTitle[] = _("SAN FRANCISCO");
static const u8 sSFGuideRegion[] = _("REGION MAP");
static const u8 sSFGuideHelp[] = _("ARROWS: PLACE  A: INFO  B: BACK");

static const u8 sSFGuideFinished[] = _("Local discovery: complete");
static const u8 sSFGuideFound[] = _("Local favor: return to your neighbor");
static const u8 sSFGuideExplore[] = _("Look around; talk to the neighbors.");
static const u8 sSFGuideInk[] = {0,2,3};
static const u8 sSFGuidePanelInk[] = {0,1,2};
static const struct WindowTemplate sSFGuideTemplate = {
    .bg=0,.tilemapLeft=1,.tilemapTop=1,.width=28,.height=18,.paletteNum=13,.baseBlock=8
};
static bool8 SFGuideInput(void);

static void SFGuideAt(const u8 *text,u8 x,u8 y,const u8 *ink)
{
    AddTextPrinterParameterized3(sSFGuideWindow,FONT_SMALL,x,y,ink,TEXT_SKIP_DRAW,text);
}
static void SFGuideText(const u8 *text,u8 y) {SFGuideAt(text,8,y,sSFGuideInk);}

#include "sf_world_guide_art.h"

static void SFGuideLabels(void)
{
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),0,120,224,24);
    SFGuideAt(place->name,8,120,sSFGuidePanelInk);
    SFGuideAt(sSFGuideHelp,8,132,sSFGuidePanelInk);
    if (!sSFGuideDetails) SFGuideMapArt();
    CopyWindowToVram(sSFGuideWindow,COPYWIN_FULL);
}

static bool8 SFGuideDraw(void)
{
    u8 i;
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    LoadPalette(sSFGuidePalette,BG_PLTT_ID(13),sizeof(sSFGuidePalette));
    FillWindowPixelBuffer(sSFGuideWindow,PIXEL_FILL(2));
    DrawStdWindowFrame(sSFGuideWindow,FALSE);
    SFGuideAt(sSFGuideTitle,8,1,sSFGuidePanelInk);
    SFGuideAt(sSFGuideRegion,165,1,sSFGuidePanelInk);
    if (sSFGuideDetails)
    {
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),0,16,224,104);
        SFGuideText(place->character,22);
        for (i=0;i<4;i++) SFGuideText(place->routes[i],46+i*13);
        SFGuideText(FlagGet(place->doneFlag)?sSFGuideFinished:
            (place->foundFlag && FlagGet(place->foundFlag)?sSFGuideFound:sSFGuideExplore),104);
    }
    SFGuideLabels();gMenuCallback=SFGuideInput;return FALSE;
}

static bool8 SFGuideInput(void)
{
    bool8 close=JOY_NEW(START_BUTTON);
    if (JOY_NEW(A_BUTTON))
    {
        sSFGuideDetails=!sSFGuideDetails;sSFGuideDrawStep=0;
        PlaySE(SE_SELECT);gMenuCallback=SFGuideDraw;return FALSE;
    }
    if (JOY_NEW(DPAD_LEFT|DPAD_UP|DPAD_RIGHT|DPAD_DOWN))
    {
        if (JOY_NEW(DPAD_LEFT|DPAD_UP))
            sSFGuideSelected=(sSFGuideSelected+ARRAY_COUNT(sSFGuidePlaces)-1)%ARRAY_COUNT(sSFGuidePlaces);
        else sSFGuideSelected=(sSFGuideSelected+1)%ARRAY_COUNT(sSFGuidePlaces);
        PlaySE(SE_SELECT);
        if (sSFGuideDetails) {sSFGuideDrawStep=0;gMenuCallback=SFGuideDraw;}
        else SFGuideLabels();
        return FALSE;
    }
    if (!close && !JOY_NEW(B_BUTTON)) return FALSE;
    if (!close && sSFGuideDetails)
    {
        sSFGuideDetails=FALSE;sSFGuideDrawStep=0;
        PlaySE(SE_SELECT);gMenuCallback=SFGuideDraw;return FALSE;
    }
    PlaySE(SE_SELECT);ClearStdWindowAndFrameToTransparent(sSFGuideWindow,TRUE);
    RemoveWindow(sSFGuideWindow);sSFGuideWindow=WINDOW_NONE;
    LoadPalette(sSFGuideSavedPalette,BG_PLTT_ID(13),sizeof(sSFGuideSavedPalette));
    if (close) {ScriptUnfreezeObjectEvents();UnlockPlayerFieldControls();return TRUE;}
    InitStartMenu();gMenuCallback=HandleStartMenuInput;return FALSE;
}

static bool8 StartMenuSFGuideCallback(void)
{
    u8 i;
    sSFGuideWindow=AddWindow(&sSFGuideTemplate);
    if (sSFGuideWindow==WINDOW_NONE) {gMenuCallback=HandleStartMenuInput;return FALSE;}
    sSFGuideSelected=0;sSFGuideDetails=FALSE;sSFGuideDrawStep=0;
    for (i=0;i<ARRAY_COUNT(sSFGuideBindings);i++)
        if (sSFGuideBindings[i][0]==gSaveBlock1Ptr->location.mapGroup
            && sSFGuideBindings[i][1]==gSaveBlock1Ptr->location.mapNum)
        {
            sSFGuideSelected=sSFGuideCurrent=sSFGuideBindings[i][2];
            sSFGuideHereX=sSFGuideBindings[i][3];sSFGuideHereY=sSFGuideBindings[i][4];
            sSFGuideContext=sSFGuideBindings[i][5];
        }
    for (i=0;i<16;i++) sSFGuideSavedPalette[i]=gPlttBufferUnfaded[BG_PLTT_ID(13)+i];
    ClearStdWindowAndFrameToTransparent(GetStartMenuWindowId(),FALSE);
    RemoveStartMenuWindow();gMenuCallback=SFGuideDraw;return FALSE;
}
