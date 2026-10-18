// SF-only schematic guide. Reading it never changes story state or saves.
#include "sf_authored_maps.h"
#include "constants/flags.h"

struct SFGuidePlace {
    u8 x, y;
    u8 name[40];
    u8 character[60];
    u8 routes[4][40];
    u16 doneFlag, foundFlag;
};
struct SFGuideEdge { u8 from, to, badge; };
#include "sf_world_guide_data.h"
EWRAM_DATA static u8 sSFGuideWindow = WINDOW_NONE;
EWRAM_DATA static u8 sSFGuideSelected = 0;
EWRAM_DATA static u8 sSFGuideDrawStep = 0;
EWRAM_DATA static bool8 sSFGuideDetails = FALSE;
static const u8 sSFGuideLabel[] = _("SF MAP");
static const u8 sSFGuideTitle[] = _("SAN FRANCISCO");
static const u8 sSFGuideHelp[] = _("ARROWS: PLACE   A: INFO   B: MENU");
static const u8 sSFGuideSchematic[] = _("SCHEMATIC ROUTES / BAY CROSSINGS");
static const u8 sSFGuideFinished[] = _("Local discovery: complete");
static const u8 sSFGuideFound[] = _("Local favor: return to your neighbor");
static const u8 sSFGuideExplore[] = _("Look around; talk to the neighbors.");
static const u8 sSFGuideInk[] = {TEXT_COLOR_WHITE,TEXT_COLOR_DARK_GRAY,TEXT_COLOR_LIGHT_GRAY};
static const struct WindowTemplate sSFGuideTemplate = {
    .bg=0,.tilemapLeft=2,.tilemapTop=1,.width=26,.height=17,.paletteNum=15,.baseBlock=8
};
static bool8 SFGuideInput(void);

static void SFGuideText(const u8 *text,u8 y)
{
    AddTextPrinterParameterized3(sSFGuideWindow,FONT_SMALL,8,y,sSFGuideInk,TEXT_SKIP_DRAW,text);
}

static void SFGuideLine(u8 x0,u8 y0,u8 x1,u8 y1,u8 color)
{
    s16 x=x0,y=y0,dx=x1>x0?x1-x0:x0-x1,dy=y1>y0?y1-y0:y0-y1;
    s16 sx=x0<x1?1:-1,sy=y0<y1?1:-1,error=dx-dy,e2;
    for (;;)
    {
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(color),x,y,1,1);
        if (x==x1 && y==y1) break;
        e2=2*error;
        if (e2>-dy) {error-=dy;x+=sx;}
        if (e2<dx) {error+=dx;y+=sy;}
    }
}

static void SFGuideLabels(void)
{
    u8 i;
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_WHITE),4,16,200,15);
    SFGuideText(place->name,17);
    if (!sSFGuideDetails)
    {
        for (i=0;i<ARRAY_COUNT(sSFGuidePlaces);i++)
            FillWindowPixelRect(sSFGuideWindow,
                PIXEL_FILL(i==sSFGuideSelected?TEXT_COLOR_RED:TEXT_COLOR_DARK_GRAY),
                sSFGuidePlaces[i].x-2,sSFGuidePlaces[i].y-2,4,4);
    }
    CopyWindowToVram(sSFGuideWindow,COPYWIN_FULL);
}

static bool8 SFGuideDraw(void)
{
    u8 i,step=sSFGuideDrawStep++;
    const struct SFGuidePlace *place=&sSFGuidePlaces[sSFGuideSelected];
    if (step==0)
    {
        FillWindowPixelBuffer(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_WHITE));
        DrawStdWindowFrame(sSFGuideWindow,FALSE);
        SFGuideText(sSFGuideTitle,2);
        SFGuideText(sSFGuideHelp,122);
        if (sSFGuideDetails)
        {
            SFGuideText(place->character,36);
            for (i=0;i<4;i++) SFGuideText(place->routes[i],53+i*13);
            SFGuideText(FlagGet(place->doneFlag)?sSFGuideFinished:
                (place->foundFlag && FlagGet(place->foundFlag)?sSFGuideFound:sSFGuideExplore),108);
            SFGuideLabels();gMenuCallback=SFGuideInput;return FALSE;
        }
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_LIGHT_BLUE),8,34,192,68);
        for (i=0;i<64;i++)
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_WHITE),12,35+i,120+i/9,1);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_LIGHT_GREEN),27,56,35,10);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_LIGHT_GREEN),158,35,25,9);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(TEXT_COLOR_LIGHT_GREEN),158,57,25,12);
        SFGuideText(sSFGuideSchematic,108);
    }
    else if (step<=ARRAY_COUNT(sSFGuideEdges))
    {
        const struct SFGuideEdge *edge=&sSFGuideEdges[step-1];
        const struct SFGuidePlace *from=&sSFGuidePlaces[edge->from],*to=&sSFGuidePlaces[edge->to];
        SFGuideLine(from->x,from->y,to->x,to->y,edge->badge?TEXT_COLOR_BLUE:TEXT_COLOR_DARK_GRAY);
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
    PlaySE(SE_SELECT);ClearStdWindowAndFrameToTransparent(sSFGuideWindow,TRUE);
    RemoveWindow(sSFGuideWindow);sSFGuideWindow=WINDOW_NONE;
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
            sSFGuideSelected=sSFGuideBindings[i][2];
    ClearStdWindowAndFrameToTransparent(GetStartMenuWindowId(),FALSE);
    RemoveStartMenuWindow();gMenuCallback=SFGuideDraw;return FALSE;
}
