// Read existing chapter state. Opening this page never advances a quest or saves.
#include "constants/vars.h"
#include "sf_authored_maps.h"

EWRAM_DATA static u8 sSFJournalWindowId = WINDOW_NONE;
EWRAM_DATA static u8 sSFJournalStage = 0;
EWRAM_DATA static u8 sSFJournalDrawStep = 0;

static const u8 sSFJournalLabel[] = _("JOURNAL");
static const u8 sSFJournalTitle[] = _("FIELD JOURNAL");
static const u8 sSFJournalNext[] = _("NEXT OBJECTIVE");
static const u8 sSFJournalHelp[] = _("SELECT: MAP  B: MENU  START: FIELD");
static const u8 sSFJournalSunset[] = _("OUTER SUNSET");
static const u8 sSFJournalApartment[] = _("YOUR APARTMENT / SUNSET");
static const u8 sSFJournalPark[] = _("SOUTH PARK / SOMA");
static const u8 sSFJournalClinic[] = _("SOUTH PARK FIELD CLINIC");
static const u8 sSFJournalCognition[] = _("COGNITION / SOUTH PARK");
static const u8 sSFJournalInk[] = {TEXT_COLOR_WHITE, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY};
static const u8 sSFJournalAccent[] = {TEXT_COLOR_WHITE, TEXT_COLOR_BLUE, TEXT_COLOR_LIGHT_BLUE};

static const struct WindowTemplate sSFJournalWindow = {
    .bg = 0, .tilemapLeft = 2, .tilemapTop = 1,
    .width = 26, .height = 17, .paletteNum = 15, .baseBlock = 8
};

static const struct {
    u8 title[32];
    u8 directions[3][40];
} sSFJournalObjectives[] = {
    {_("CHOOSE A COMPANION"), {_("Meet KARPATHY near JUDAH."), _("Pick one of the three"), _("companions beside him.")}},
    {_("FIND ROON'S SENSOR"), {_("Head west to OCEAN BEACH."), _("Check the missing parcel."), _("Bring a companion with you.")}},
    {_("RETURN THE SENSOR"), {_("Find ROON near the beach."), _("He is south of the parcel."), _("Show him what you recovered.")}},
    {_("DELIVER TO COGNITION"), {_("JONATHAN waits east on JUDAH."), _("Take MUNI, then find SCOTT"), _("inside COGNITION by THIRD.")}},
    {_("STABILIZE THE INPUT"), {_("Find the blue INPUT relay"), _("inside COGNITION. Restore it"), _("before the green OUTPUT.")}},
    {_("RESTORE THE OUTPUT"), {_("The blue INPUT is stable."), _("Use the green OUTPUT relay"), _("to open the safety gate.")}},
    {_("CHALLENGE SCOTT"), {_("Both safety relays are stable."), _("Meet SCOTT beyond the gate."), _("Clinic: east of COGNITION.")}},
    {_("BUILD BADGE EARNED"), {_("Chapter preview complete!"), _("Explore, train or visit friends."), _("The MISSION chapter is coming.")}}
};

static u8 SFJournalObjective(void)
{
    u16 parcel = VarGet(VAR_UNUSED_0x40F7);
    u16 relays = VarGet(VAR_UNUSED_0x40DB);
    if (FlagGet(FLAG_BADGE01_GET))
        return 7;
    if (!FlagGet(FLAG_SYS_POKEMON_GET))
        return 0;
    if (relays >= 3)
        return 6;
    if (relays == 2)
        return 5;
    if (relays == 1)
        return 4;
    if (parcel >= 4)
        return 3;
    if (parcel == 3)
        return 2;
    return 1;
}

static const u8 *SFJournalLocation(void)
{
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_RUSTBORO_CITY_GYM)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_RUSTBORO_CITY_GYM))
        return sSFJournalCognition;
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB))
        return sSFJournalClinic;
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_OLDALE_TOWN)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_OLDALE_TOWN))
        return sSFJournalPark;
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F))
        return sSFJournalApartment;
    return sSFJournalSunset;
}

static const u8 sSFJournalParkDirections[3][40] = {
    _("Find SCOTT inside COGNITION."),
    _("West of SOUTH PARK by THIRD."),
    _("Take the recovered sensor inside.")
};

static const u8 *SFJournalDirections(u8 line)
{
    const u8 *location = SFJournalLocation();
    if (sSFJournalStage == 3 && location != sSFJournalSunset && location != sSFJournalApartment)
        return sSFJournalParkDirections[line];
    return sSFJournalObjectives[sSFJournalStage].directions[line];
}

bool8 SFTryOpenFieldMap(void (*callback)(void));
static bool8 SFJournalInput(void);

static void SFJournalRemoveWindow(bool8 clear)
{
    if (clear)
        ClearStdWindowAndFrameToTransparent(sSFJournalWindowId, TRUE);
    RemoveWindow(sSFJournalWindowId);
    sSFJournalWindowId = WINDOW_NONE;
}

static bool8 SFJournalOpenMapAfterFade(void)
{
    if (gPaletteFade.active)
        return FALSE;
    // On failure the journal still owns its window; restore it without unlocking.
    if (!SFTryOpenFieldMap(CB2_ReturnToFieldWithOpenMenu))
    {
        FadeScreen(FADE_FROM_BLACK, 0);
        gMenuCallback = SFJournalInput;
        return FALSE;
    }
    // Already black: do not queue window DMA after the map disables VBlank.
    SFJournalRemoveWindow(FALSE);
    RemoveExtraStartMenuWindows();
    CleanupOverworldWindowsAndTilemaps();
    return TRUE; // Native Start-menu task is destroyed; the field map owns main.
}

static bool8 SFJournalInput(void)
{
    bool8 close = JOY_NEW(START_BUTTON);
    if (gPaletteFade.active)
        return FALSE;
    if (!close && !JOY_NEW(B_BUTTON) && JOY_NEW(SELECT_BUTTON))
    {
        PlaySE(SE_SELECT);
        FadeScreen(FADE_TO_BLACK, 0);
        gMenuCallback = SFJournalOpenMapAfterFade;
        return FALSE;
    }
    if (!close && !JOY_NEW(B_BUTTON))
        return FALSE;
    PlaySE(SE_SELECT);
    SFJournalRemoveWindow(TRUE);
    if (close)
    {
        ScriptUnfreezeObjectEvents();
        UnlockPlayerFieldControls();
        return TRUE;
    }
    InitStartMenu();
    gMenuCallback = HandleStartMenuInput;
    return FALSE;
}

// Native text blitting is synchronous. Limit work to one short line per frame.
static bool8 SFJournalDraw(void)
{
    u8 step = sSFJournalDrawStep++;
    const u8 *text;
    u8 font = FONT_NORMAL, y;
    const u8 *colors = sSFJournalInk;
    if (JOY_NEW(B_BUTTON | START_BUTTON))
        return SFJournalInput();
    switch (step)
    {
    case 0: text = sSFJournalTitle; y = 3; break;
    case 1: text = SFJournalLocation(); y = 20; font = FONT_SMALL; colors = sSFJournalAccent; break;
    case 2: text = sSFJournalNext; y = 38; font = FONT_SMALL; colors = sSFJournalAccent; break;
    case 3: text = sSFJournalObjectives[sSFJournalStage].title; y = 51; break;
    case 7: text = sSFJournalHelp; y = 122; font = FONT_SMALL; break;
    default: text = SFJournalDirections(step - 4); y = 69 + (step - 4) * 16; break;
    }
    AddTextPrinterParameterized3(sSFJournalWindowId, font, 8, y, colors, TEXT_SKIP_DRAW, text);
    if (step == 7)
    {
        CopyWindowToVram(sSFJournalWindowId, COPYWIN_FULL);
        gMenuCallback = SFJournalInput;
    }
    return FALSE;
}

static bool8 StartMenuSFJournalCallback(void)
{
    u8 i;
    // Allocate before removing the menu so allocation failure remains recoverable.
    sSFJournalWindowId = AddWindow(&sSFJournalWindow);
    if (sSFJournalWindowId == WINDOW_NONE)
    {
        gMenuCallback = HandleStartMenuInput;
        return FALSE;
    }
    sSFJournalStage = SFJournalObjective();
    sSFJournalDrawStep = 0;
    ClearStdWindowAndFrameToTransparent(GetStartMenuWindowId(), FALSE);
    RemoveStartMenuWindow();
    DrawStdWindowFrame(sSFJournalWindowId, FALSE);
    FillWindowPixelRect(sSFJournalWindowId, PIXEL_FILL(TEXT_COLOR_LIGHT_GRAY), 8, 35, 192, 1);
    for (i = 0; i < ARRAY_COUNT(sSFJournalObjectives); i++)
        FillWindowPixelRect(sSFJournalWindowId,
            PIXEL_FILL(i <= sSFJournalStage ? TEXT_COLOR_BLUE : TEXT_COLOR_LIGHT_GRAY),
            8 + i * 24, 119, 18, 2);
    gMenuCallback = SFJournalDraw;
    return FALSE;
}
