"""World-only SF entry menu; retain the native save loader and naming flow."""


def apply_world_boot(engine, original):
    intro = original('src/intro.c')
    intro = intro.replace('#include "intro.h"', '#include "intro.h"\n#include "main_menu.h"')
    start = intro.index('void CB2_InitCopyrightScreenAfterBootup(void)\n{')
    end = intro.index('\nvoid CB2_InitCopyrightScreenAfterTitleScreen', start)
    intro = intro[:start] + '''void CB2_InitCopyrightScreenAfterBootup(void)
{
    // Use the normal native loader before opening the SF Continue/New Game menu.
    // An ordinary battery save is still the only source of campaign progress.
    SetVBlankCallback(NULL);
    SetSaveBlocksPointers(GetSaveBlocksPointersBaseOffset());
    ResetMenuAndMonGlobals();
    Save_ResetSaveCounters();
    LoadGameSave(SAVE_NORMAL);
    if (gSaveFileStatus == SAVE_STATUS_EMPTY || gSaveFileStatus == SAVE_STATUS_CORRUPT)
        Sav2_ClearSetDefault();
    SetPokemonCryStereo(gSaveBlock2Ptr->optionsSound);
    InitHeap(gHeap, HEAP_SIZE);
    SetMainCallback2(CB2_InitMainMenu);
}
''' + intro[end:]
    (engine / 'src/intro.c').write_text(intro)

    # Engine guards already added the SF save-identity check to this file.
    path = engine / 'src/main_menu.c'
    menu = path.read_text()
    labels = {
        'gText_MainMenuNewGame': 'sSFNewAdventure',
        'gText_MainMenuContinue': 'sSFContinue',
        'gText_Birch_Welcome': 'sSFWelcome',
        'gText_ThisIsAPokemon': 'sSFCompanion',
        'gText_Birch_MainSpeech': 'sSFCitySpeech',
        'gText_Birch_AreYouReady': 'sSFAreYouReady',
    }
    for before, after in labels.items():
        if before not in menu:
            raise ValueError('Missing native SF menu anchor: ' + before)
        menu = menu.replace(before, after)
    menu = menu.replace('// .rodata', r'''// .rodata
static const u8 sSFNewAdventure[] = _("NEW SF ADVENTURE");
static const u8 sSFContinue[] = _("CONTINUE SF WORLD");
static const u8 sSFWelcome[] = _("Welcome to SAN FRANCISCO!\nYour adventure starts in DOGPATCH.");
static const u8 sSFCompanion[] = _("These companions are MINI MONSTERS.\nThey share the city with us.");
static const u8 sSFCitySpeech[] = _("Follow the streets, meet the neighbors,\nand explore the city together.\pFrom the ocean to the bay islands,\nthere is always another story.");
static const u8 sSFAreYouReady[] = _("Ready, {PLAYER}?\nYour SF adventure is about to begin!");
''', 1)
    # Back from this menu must not expose the stock title/attract sequence.
    menu = menu.replace('SetMainCallback2(CB2_InitTitleScreen);',
                        'SetMainCallback2(CB2_InitMainMenu);')
    path.write_text(menu)
    return ['src/intro.c', 'src/main_menu.c']
