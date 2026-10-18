// Native SF place guide. Reading it never changes story state or saves.
#include "sf_authored_maps.h"
#include "constants/flags.h"

struct SFGuidePlace {
    u8 x, y;
    u8 name[40];
    u8 character[60];
    u8 routes[4][40];
    u16 doneFlag, foundFlag;
};
struct SFGuideEdge { u8 from, to, badge, water; };
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
static const u8 sSFGuideHelp[] = _("ARROWS: PLACE  A: INFO  B: BACK");

static const u8 sSFGuideFinished[] = _("Local discovery: complete");
static const u8 sSFGuideFound[] = _("Local favor: return to your neighbor");
static const u8 sSFGuideExplore[] = _("Look around; talk to the neighbors.");
static const u8 sSFGuideInk[] = {TEXT_COLOR_WHITE,TEXT_COLOR_DARK_GRAY,TEXT_COLOR_LIGHT_GRAY};
static const u8 sSFGuideWaterInk[] = {0,12,5};
static const struct WindowTemplate sSFGuideTemplate = {
    .bg=0,.tilemapLeft=1,.tilemapTop=1,.width=28,.height=18,.paletteNum=13,.baseBlock=8
};
static bool8 SFGuideInput(void);

static void SFGuideAt(const u8 *text,u8 x,u8 y,const u8 *ink)
{
    AddTextPrinterParameterized3(sSFGuideWindow,FONT_SMALL,x,y,ink,TEXT_SKIP_DRAW,text);
}
static void SFGuideText(const u8 *text,u8 y) {SFGuideAt(text,8,y,sSFGuideInk);}

static void SFGuideLine(u8 x0,u8 y0,u8 x1,u8 y1,u8 color,bool8 dashed)
{
    s16 x=x0,y=y0,dx=x1>x0?x1-x0:x0-x1,dy=y1>y0?y1-y0:y0-y1;
    s16 sx=x0<x1?1:-1,sy=y0<y1?1:-1,error=dx-dy,e2;
    u16 step=0;
    for (;;)
    {
        if (!dashed || step++%3!=2)
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(color),x,y,1,1);
        if (x==x1 && y==y1) break;
        e2=2*error;
        if (e2>-dy) {error-=dy;x+=sx;}
        if (e2<dx) {error+=dx;y+=sy;}
    }
}

#include "sf_world_guide_art.h"

static void SFGuideLabels(void)
{
    u8 i;
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_WHITE),4,16,216,13);
    SFGuideAt(place->name,16,16,sSFGuideInk);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),6,20,6,4);
    if (!sSFGuideDetails)
    {
        for (i=0;i<ARRAY_COUNT(sSFGuidePlaces);i++)
        {
            u8 x=sSFGuidePlaces[i].x,y=sSFGuidePlaces[i].y;
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(i==sSFGuideSelected?15:6),x-3,y-3,6,6);
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-2,y-2,4,4);
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),x-1,y-1,2,2);
        }
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(14),sSFGuideHereX-2,sSFGuideHereY-2,4,4);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),sSFGuideHereX-1,sSFGuideHereY-1,2,2);
    }
    CopyWindowToVram(sSFGuideWindow,COPYWIN_FULL);
}

static bool8 SFGuideDraw(void)
{
    u8 i,step=sSFGuideDrawStep++;
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    if (step==0)
    {
        LoadPalette(sSFGuidePalette,BG_PLTT_ID(13),sizeof(sSFGuidePalette));
        FillWindowPixelBuffer(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_WHITE));
        DrawStdWindowFrame(sSFGuideWindow,FALSE);
        SFGuideText(sSFGuideTitle,2);
        SFGuideText(sSFGuideHelp,130);
        if (sSFGuideDetails)
        {
            SFGuideText(place->character,36);
            for (i=0;i<4;i++) SFGuideText(place->routes[i],53+i*13);
            SFGuideText(FlagGet(place->doneFlag)?sSFGuideFinished:
                (place->foundFlag && FlagGet(place->foundFlag)?sSFGuideFound:sSFGuideExplore),108);
            SFGuideLabels();gMenuCallback=SFGuideInput;return FALSE;
        }
        SFGuideMapArt();
    }
    else if (step<=ARRAY_COUNT(sSFGuideEdges))
    {
        const struct SFGuideEdge *edge=&sSFGuideEdges[step-1];
        const struct SFGuidePlace *from=&sSFGuidePlaces[edge->from],*to=&sSFGuidePlaces[edge->to];
        bool8 locked=edge->badge && !FlagGet(FLAG_BADGE01_GET+edge->badge-1);
        SFGuideLine(from->x,from->y,to->x,to->y,locked?13:edge->water?12:11,edge->water);
    }
    else
    {
        SFGuideLabels();gMenuCallback=SFGuideInput;
    }
    return FALSE;
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
