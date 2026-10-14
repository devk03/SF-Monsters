"""Install an SF-only, read-only objective page in the native Start menu."""
import shutil


def apply_field_journal(root, engine, original):
    path = 'src/start_menu.c'
    source = original(path)
    edits = [
        ('    if (FlagGet(FLAG_SYS_POKENAV_GET) == TRUE)\n    {\n        AddStartMenuAction(MENU_ACTION_POKENAV);\n    }\n\n    AddStartMenuAction(MENU_ACTION_PLAYER);\n    AddStartMenuAction(MENU_ACTION_SAVE);',
         '    if (!SFMapUsesAuthoredLayout() && FlagGet(FLAG_SYS_POKENAV_GET) == TRUE)\n    {\n        AddStartMenuAction(MENU_ACTION_POKENAV);\n    }\n\n    AddStartMenuAction(MENU_ACTION_PLAYER);\n    AddStartMenuAction(MENU_ACTION_SAVE);'),
        ('    MENU_ACTION_PYRAMID_BAG\n', '    MENU_ACTION_PYRAMID_BAG,\n    MENU_ACTION_SF_JOURNAL\n'),
        ('static bool8 StartMenuPokedexCallback(void);',
         'static bool8 StartMenuSFJournalCallback(void);\nstatic const u8 sSFJournalLabel[];\nstatic bool8 StartMenuPokedexCallback(void);'),
        ('    [MENU_ACTION_POKEDEX]         =',
         '    [MENU_ACTION_SF_JOURNAL]      = {sSFJournalLabel, {.u8_void = StartMenuSFJournalCallback}},\n    [MENU_ACTION_POKEDEX]         ='),
        ('void SetDexPokemonPokenavFlags(void) // unused',
         '#include "sf_field_journal.h"\n\nvoid SetDexPokemonPokenavFlags(void) // unused'),
        ('    AddStartMenuAction(MENU_ACTION_SAVE);\n    AddStartMenuAction(MENU_ACTION_OPTION);\n    AddStartMenuAction(MENU_ACTION_EXIT);',
         '    AddStartMenuAction(MENU_ACTION_SAVE);\n    AddStartMenuAction(MENU_ACTION_OPTION);\n    if (SFMapUsesAuthoredLayout())\n        AddStartMenuAction(MENU_ACTION_SF_JOURNAL);\n    AddStartMenuAction(MENU_ACTION_EXIT);'),
        ('        if (gMenuCallback != StartMenuSaveCallback\n',
         '        if (gMenuCallback != StartMenuSFJournalCallback\n            && gMenuCallback != StartMenuSaveCallback\n')
    ]
    for before, after in edits:
        if source.count(before) != 1:
            raise ValueError('Pinned journal menu anchor changed: ' + before)
        source = source.replace(before, after, 1)
    (engine / path).write_text(source)
    shutil.copyfile(root / 'romhack/engine/field_journal.h', engine / 'src/sf_field_journal.h')
    map_path = 'src/field_region_map.c'
    source = original(map_path)
    edits = [
        ('void FieldInitRegionMap(MainCallback callback)',
         '#include "sf_field_map.h"\n\nvoid FieldInitRegionMap(MainCallback callback)'),
        ('GetStringCenterAlignXOffset(FONT_NORMAL, gText_Hoenn, 0x38)',
         'GetStringCenterAlignXOffset(FONT_NORMAL, SFFieldMapTitle(), 0x38)'),
        ('AddTextPrinterParameterized(WIN_TITLE, FONT_NORMAL, gText_Hoenn, offset, 1, 0, NULL)',
         'AddTextPrinterParameterized(WIN_TITLE, FONT_NORMAL, SFFieldMapTitle(), offset, 1, 0, NULL)')
    ]
    for before, after in edits:
        if source.count(before) != 1:
            raise ValueError('Pinned journal field-map anchor changed: ' + before)
        source = source.replace(before, after, 1)
    (engine / map_path).write_text(source)
    shutil.copyfile(root / 'romhack/engine/field_map.h', engine / 'src/sf_field_map.h')
    return [path, map_path]
